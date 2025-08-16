"""
Scheduler Agent - Handles launching applications at specific times
"""

import time
import logging
import subprocess
import os
import schedule
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import psutil

from ..core.config import config
from ..core.database import db
from ..core.utils import setup_logging


class SchedulerAgent:
    """Agent for scheduling and launching applications"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.scheduler_config = config.get_scheduler_config()
        self.running_processes = {}
        self.setup_schedules()
    
    def setup_schedules(self):
        """Setup application schedules from configuration"""
        app_configs = self.scheduler_config.get('app_launcher', {}).get('applications', [])
        
        for app_config in app_configs:
            app_name = app_config.get('name', 'Unknown')
            app_path = app_config.get('path', '')
            schedule_time = app_config.get('schedule', '09:00')
            
            if app_path and os.path.exists(app_path):
                # Schedule the application
                schedule.every().day.at(schedule_time).do(
                    self.launch_application, app_name, app_path
                )
                self.logger.info(f"Scheduled {app_name} to launch at {schedule_time}")
            else:
                self.logger.warning(f"Application path not found: {app_path}")
        
        # Setup job portal daily updates
        self.setup_job_portal_schedules()
    
    def setup_job_portal_schedules(self):
        """Setup job portal daily update schedules"""
        try:
            # Get daily updates time from config (default 9:00 AM)
            daily_updates_time = self.scheduler_config.get('daily_updates', {}).get('time', '09:00')
            
            # Schedule daily job portal updates
            schedule.every().day.at(daily_updates_time).do(
                self.run_job_portal_daily_updates
            )
            
            self.logger.info(f"Scheduled daily job portal updates at {daily_updates_time}")
            
            # Log the scheduled task
            db.add_scheduled_task(
                task_name="daily_job_portal_updates",
                task_type="job_portal_updates",
                schedule_time=daily_updates_time,
                config={"type": "daily_updates", "time": daily_updates_time}
            )
            
        except Exception as e:
            self.logger.error(f"Error setting up job portal schedules: {e}")
    
    def run_job_portal_daily_updates(self):
        """Run daily job portal updates"""
        try:
            self.logger.info("Starting scheduled daily job portal updates")
            
            # Import job portal agents
            from .job_portal_agent import JobPortalAgent
            from .bayt_http_agent import BaytHttpAgent
            from .bayt_playwright_agent import BaytPlaywrightAgent
            
            # Run Bayt.com updates
            try:
                if BaytPlaywrightAgent is not None:
                    bayt_agent = BaytPlaywrightAgent()
                    bayt_result = bayt_agent.run_daily_updates()
                    bayt_agent.close()
                    self.logger.info(f"Bayt.com updates (Playwright): {bayt_result['status']} - {bayt_result['message']}")
                elif BaytHttpAgent is not None:
                    bayt_agent = BaytHttpAgent()
                    bayt_result = bayt_agent.run_daily_updates()
                    bayt_agent.close()
                    self.logger.info(f"Bayt.com updates (HTTP): {bayt_result['status']} - {bayt_result['message']}")
            except Exception as e:
                self.logger.error(f"Error in Bayt.com updates: {e}")
            
            # Run updates for other portals
            try:
                job_portal_agent = JobPortalAgent()
                job_portal_agent.run_daily_updates()
                job_portal_agent.close()
            except Exception as e:
                self.logger.error(f"Error in job portal updates: {e}")
            
            # Update task run time
            self.update_job_portal_task_run_time()
            
            self.logger.info("Completed scheduled daily job portal updates")
            
        except Exception as e:
            self.logger.error(f"Error in scheduled job portal updates: {e}")
    
    def update_job_portal_task_run_time(self):
        """Update the last run time for job portal updates task"""
        try:
            # Get the task from database
            tasks = db.get_active_scheduled_tasks()
            for task in tasks:
                if task['task_name'] == 'daily_job_portal_updates':
                    # Calculate next run time (24 hours from now)
                    last_run = datetime.now()
                    next_run = last_run + timedelta(days=1)
                    
                    # Update the task
                    db.update_task_run_time(task['id'], last_run, next_run)
                    break
                    
        except Exception as e:
            self.logger.error(f"Error updating job portal task run time: {e}")
    
    def launch_application(self, app_name: str, app_path: str) -> bool:
        """Launch an application"""
        try:
            # Check if application is already running
            if self.is_application_running(app_name):
                self.logger.info(f"{app_name} is already running")
                return True
            
            # Launch the application
            if os.name == 'nt':  # Windows
                subprocess.Popen([app_path], shell=True)
            else:  # Unix/Linux
                subprocess.Popen([app_path])
            
            # Wait a moment for the application to start
            time.sleep(2)
            
            # Verify the application started
            if self.is_application_running(app_name):
                self.logger.info(f"Successfully launched {app_name}")
                
                # Log the launch
                db.add_scheduled_task(
                    task_name=f"launch_{app_name}",
                    task_type="app_launcher",
                    schedule_time=datetime.now().strftime("%H:%M"),
                    config={"app_name": app_name, "app_path": app_path}
                )
                
                return True
            else:
                self.logger.error(f"Failed to launch {app_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error launching {app_name}: {e}")
            return False
    
    def is_application_running(self, app_name: str) -> bool:
        """Check if an application is currently running"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    proc_exe = proc.info['exe']
                    
                    # Check by process name
                    if app_name.lower() in proc_name:
                        return True
                    
                    # Check by executable path
                    if proc_exe and app_name.lower() in proc_exe.lower():
                        return True
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking if {app_name} is running: {e}")
            return False
    
    def stop_application(self, app_name: str) -> bool:
        """Stop a running application"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    proc_exe = proc.info['exe']
                    
                    # Check if this is the target application
                    if (app_name.lower() in proc_name or 
                        (proc_exe and app_name.lower() in proc_exe.lower())):
                        
                        proc.terminate()
                        proc.wait(timeout=5)  # Wait up to 5 seconds
                        self.logger.info(f"Stopped {app_name}")
                        return True
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    continue
            
            self.logger.warning(f"Could not find {app_name} to stop")
            return False
            
        except Exception as e:
            self.logger.error(f"Error stopping {app_name}: {e}")
            return False
    
    def get_running_applications(self) -> List[Dict[str, Any]]:
        """Get list of currently running applications"""
        running_apps = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time']):
                try:
                    proc_info = proc.info
                    if proc_info['exe']:  # Only include processes with executable path
                        running_apps.append({
                            'name': proc_info['name'],
                            'pid': proc_info['pid'],
                            'path': proc_info['exe'],
                            'start_time': datetime.fromtimestamp(proc_info['create_time'])
                        })
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error getting running applications: {e}")
        
        return running_apps
    
    def schedule_custom_task(self, task_name: str, task_type: str, 
                           schedule_time: str, task_config: Dict = None) -> bool:
        """Schedule a custom task"""
        try:
            if task_type == "app_launcher":
                app_name = task_config.get('app_name', '')
                app_path = task_config.get('app_path', '')
                
                if app_path and os.path.exists(app_path):
                    schedule.every().day.at(schedule_time).do(
                        self.launch_application, app_name, app_path
                    )
                    
                    # Log the scheduled task
                    db.add_scheduled_task(
                        task_name=task_name,
                        task_type=task_type,
                        schedule_time=schedule_time,
                        config=task_config
                    )
                    
                    self.logger.info(f"Scheduled custom task: {task_name} at {schedule_time}")
                    return True
                else:
                    self.logger.error(f"Invalid app path for task {task_name}")
                    return False
            else:
                self.logger.error(f"Unsupported task type: {task_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error scheduling custom task: {e}")
            return False
    
    def cancel_scheduled_task(self, task_name: str) -> bool:
        """Cancel a scheduled task"""
        try:
            # Clear all jobs with the task name
            schedule.clear(task_name)
            
            # Update database
            # Note: This would require additional database methods to mark tasks as cancelled
            
            self.logger.info(f"Cancelled scheduled task: {task_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cancelling task {task_name}: {e}")
            return False
    
    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """Get list of scheduled tasks"""
        scheduled_tasks = []
        
        try:
            # Get tasks from database
            db_tasks = db.get_active_scheduled_tasks()
            
            for task in db_tasks:
                if task['task_type'] == 'app_launcher':
                    scheduled_tasks.append({
                        'name': task['task_name'],
                        'type': task['task_type'],
                        'schedule_time': task['schedule_time'],
                        'next_run': task['next_run'],
                        'status': task['status']
                    })
                    
        except Exception as e:
            self.logger.error(f"Error getting scheduled tasks: {e}")
        
        return scheduled_tasks
    
    def run_scheduler(self):
        """Run the scheduler loop"""
        self.logger.info("Starting scheduler service")
        
        try:
            while True:
                # Run pending scheduled tasks
                schedule.run_pending()
                
                # Sleep for a short interval
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            self.logger.info("Scheduler stopped by user")
        except Exception as e:
            self.logger.error(f"Error in scheduler: {e}")
    
    def run_once(self):
        """Run scheduled tasks once (for testing)"""
        self.logger.info("Running scheduled tasks once")
        schedule.run_pending()
    
    def add_immediate_task(self, app_name: str, app_path: str) -> bool:
        """Add a task to run immediately"""
        try:
            return self.launch_application(app_name, app_path)
        except Exception as e:
            self.logger.error(f"Error adding immediate task: {e}")
            return False


def main():
    """Main function to run scheduler"""
    agent = SchedulerAgent()
    
    # Example: Add some immediate tasks for testing
    # agent.add_immediate_task("Notepad", "notepad.exe")
    
    # Run the scheduler
    agent.run_scheduler()


if __name__ == "__main__":
    main() 