#!/usr/bin/env python3
"""
Railway Deployment Configuration
Handles automatic job portal updates on Railway
"""

import os
import sys
import time
import threading
from datetime import datetime, timedelta
import schedule

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def setup_railway_scheduler():
    """Setup scheduler specifically for Railway deployment"""
    try:
        from src.agents.scheduler_agent import SchedulerAgent
        from src.core.config import config
        
        print("🚂 Setting up Railway scheduler...")
        
        # Create scheduler agent
        scheduler = SchedulerAgent()
        
        # Get configuration
        scheduler_config = config.get_scheduler_config()
        daily_updates_time = scheduler_config.get('daily_updates', {}).get('time', '09:00')
        
        print(f"📅 Daily updates scheduled for: {daily_updates_time}")
        
        # Schedule job portal updates
        schedule.every().day.at(daily_updates_time).do(run_job_portal_updates)
        
        # Also schedule for immediate testing (within 5 minutes)
        test_time = (datetime.now() + timedelta(minutes=5)).strftime("%H:%M")
        schedule.every().day.at(test_time).do(run_job_portal_updates)
        
        print(f"🧪 Test run scheduled for: {test_time}")
        
        return scheduler
        
    except Exception as e:
        print(f"❌ Error setting up Railway scheduler: {e}")
        return None

def run_job_portal_updates():
    """Run job portal updates (Railway version)"""
    try:
        print(f"🔄 Running job portal updates at {datetime.now()}")
        
        from src.agents.bayt_playwright_agent import BaytPlaywrightAgent
        from src.agents.bayt_http_agent import BaytHttpAgent
        from src.agents.job_portal_agent import JobPortalAgent
        
        # Run Bayt.com updates
        try:
            if BaytPlaywrightAgent is not None:
                bayt_agent = BaytPlaywrightAgent()
                bayt_result = bayt_agent.run_daily_updates()
                bayt_agent.close()
                print(f"✅ Bayt.com updates (Playwright): {bayt_result['status']} - {bayt_result['message']}")
            elif BaytHttpAgent is not None:
                bayt_agent = BaytHttpAgent()
                bayt_result = bayt_agent.run_daily_updates()
                bayt_agent.close()
                print(f"✅ Bayt.com updates (HTTP): {bayt_result['status']} - {bayt_result['message']}")
        except Exception as e:
            print(f"❌ Error in Bayt.com updates: {e}")
        
        # Run updates for other portals
        try:
            job_portal_agent = JobPortalAgent()
            job_portal_agent.run_daily_updates()
            job_portal_agent.close()
            print("✅ Other portal updates completed")
        except Exception as e:
            print(f"❌ Error in other portal updates: {e}")
        
        print(f"✅ Job portal updates completed at {datetime.now()}")
        
    except Exception as e:
        print(f"❌ Error in job portal updates: {e}")

def run_railway_scheduler():
    """Run the scheduler loop for Railway"""
    print("🚂 Starting Railway scheduler service...")
    
    try:
        while True:
            # Run pending scheduled tasks
            schedule.run_pending()
            
            # Sleep for a short interval
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        print("🚂 Railway scheduler stopped by user")
    except Exception as e:
        print(f"❌ Error in Railway scheduler: {e}")

def start_railway_background_services():
    """Start background services for Railway deployment"""
    try:
        print("🚂 Starting Railway background services...")
        
        # Start scheduler in background thread
        scheduler_thread = threading.Thread(target=run_railway_scheduler, daemon=True)
        scheduler_thread.start()
        
        print("✅ Railway background services started")
        return scheduler_thread
        
    except Exception as e:
        print(f"❌ Error starting Railway services: {e}")
        return None

def main():
    """Main function for Railway deployment"""
    print("🚂 RAILWAY DEPLOYMENT STARTUP")
    print("=" * 50)
    
    # Check if we're on Railway
    is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None
    print(f"🌍 Environment: {'Railway' if is_railway else 'Local'}")
    
    # Setup scheduler
    scheduler = setup_railway_scheduler()
    
    if scheduler:
        # Start background services
        background_thread = start_railway_background_services()
        
        if background_thread:
            print("✅ Railway deployment ready!")
            print("📋 Services running:")
            print("  - Job portal updates (daily at 9:00 AM)")
            print("  - Test run (within 5 minutes)")
            print("  - Web interface (if started)")
            
            # Keep the main thread alive
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                print("🚂 Railway deployment shutting down...")
        else:
            print("❌ Failed to start background services")
    else:
        print("❌ Failed to setup scheduler")

if __name__ == "__main__":
    main()
