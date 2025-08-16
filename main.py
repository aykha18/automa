"""
Main Application - AI Agent & Productivity Tool
"""

import argparse
import logging
import time
import threading
from datetime import datetime
from typing import Dict, List, Any

from src.core.config import config
from src.core.database import db
from src.core.utils import setup_logging
from src.agents.job_portal_agent import JobPortalAgent
from src.agents.email_agent import EmailAgent
from src.agents.scheduler_agent import SchedulerAgent
from src.agents.gcc_job_finder import GCCJobFinder
from src.agents.cv_optimizer import CVOptimizer
from src.agents.email_monitor import EmailMonitor
from src.agents.data_scraper import DataScraper


class AutomaApp:
    """Main application class for the AI Agent & Productivity Tool"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.agents = {}
        self.running_threads = {}
        self.setup_agents()
    
    def setup_agents(self):
        """Initialize all agents"""
        try:
            self.agents = {
                "job_portal": JobPortalAgent(),
                "email": EmailAgent(),
                "scheduler": SchedulerAgent(),
                "gcc_job_finder": GCCJobFinder(),
                "cv_optimizer": CVOptimizer(),
                "email_monitor": EmailMonitor(),
                "data_scraper": DataScraper()
            }
            self.logger.info("All agents initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing agents: {e}")
    
    def run_job_portal_updates(self):
        """Run daily job portal updates"""
        try:
            self.logger.info("Starting job portal updates")
            self.agents["job_portal"].run_daily_updates()
        except Exception as e:
            self.logger.error(f"Error in job portal updates: {e}")
    
    def run_email_monitoring(self):
        """Run email monitoring service"""
        try:
            self.logger.info("Starting email monitoring")
            self.agents["email_monitor"].run_continuous_monitoring()
        except Exception as e:
            self.logger.error(f"Error in email monitoring: {e}")
    
    def run_scheduler_service(self):
        """Run scheduler service"""
        try:
            self.logger.info("Starting scheduler service")
            self.agents["scheduler"].run_scheduler()
        except Exception as e:
            self.logger.error(f"Error in scheduler service: {e}")
    
    def search_gcc_jobs(self, skill: str, countries: List[str] = None, max_results: int = 50):
        """Search for jobs in GCC countries"""
        try:
            self.logger.info(f"Searching for {skill} jobs in GCC countries")
            jobs = self.agents["gcc_job_finder"].search_jobs_by_skill(skill, countries, max_results)
            
            print(f"\nFound {len(jobs)} jobs:")
            for i, job in enumerate(jobs[:10], 1):  # Show first 10 jobs
                print(f"{i}. {job['title']} at {job['company']} in {job['location']}")
            
            # Save to database
            self.agents["gcc_job_finder"].save_jobs_to_database(jobs, skill)
            
            return jobs
        except Exception as e:
            self.logger.error(f"Error searching GCC jobs: {e}")
            return []
    
    def optimize_cv_for_jobs(self, jobs: List[Dict[str, Any]], cv_content: str):
        """Optimize CV for multiple jobs"""
        try:
            self.logger.info(f"Optimizing CV for {len(jobs)} jobs")
            results = self.agents["cv_optimizer"].batch_optimize_cvs(jobs, cv_content)
            
            print(f"\nCV optimization results:")
            for result in results:
                if "error" not in result:
                    print(f"- {result['job_title']} at {result['company']}: Optimized")
                else:
                    print(f"- Error: {result['error']}")
            
            return results
        except Exception as e:
            self.logger.error(f"Error optimizing CV: {e}")
            return []
    
    def scrape_business_data(self, categories: List[str] = None, cities: List[str] = None):
        """Scrape business data"""
        try:
            self.logger.info("Starting business data scraping")
            businesses = self.agents["data_scraper"].scrape_uae_businesses(categories, cities)
            
            print(f"\nScraped {len(businesses)} businesses:")
            for i, business in enumerate(businesses[:10], 1):  # Show first 10 businesses
                print(f"{i}. {business['business_name']} ({business['category']}) in {business['city']}")
            
            # Save to database
            self.agents["data_scraper"].save_businesses_to_database(businesses)
            
            return businesses
        except Exception as e:
            self.logger.error(f"Error scraping business data: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get application statistics"""
        try:
            stats = {
                "job_applications": len(db.get_job_applications()),
                "email_responses": len(db.get_unprocessed_emails()),
                "scraped_businesses": len(db.get_scraped_data()),
                "scheduled_tasks": len(db.get_active_scheduled_tasks()),
                "cv_optimization_stats": self.agents["cv_optimizer"].get_optimization_stats(),
                "email_monitor_stats": self.agents["email_monitor"].get_response_statistics(),
                "scraping_stats": self.agents["data_scraper"].get_scraping_statistics()
            }
            
            print("\n=== Application Statistics ===")
            print(f"Job Applications: {stats['job_applications']}")
            print(f"Email Responses: {stats['email_responses']}")
            print(f"Scraped Businesses: {stats['scraped_businesses']}")
            print(f"Scheduled Tasks: {stats['scheduled_tasks']}")
            
            return stats
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}
    
    def start_background_services(self):
        """Start background services in separate threads"""
        try:
            # Start email monitoring
            email_thread = threading.Thread(target=self.run_email_monitoring, daemon=True)
            email_thread.start()
            self.running_threads["email_monitor"] = email_thread
            
            # Start scheduler service
            scheduler_thread = threading.Thread(target=self.run_scheduler_service, daemon=True)
            scheduler_thread.start()
            self.running_threads["scheduler"] = scheduler_thread
            
            self.logger.info("Background services started")
            
        except Exception as e:
            self.logger.error(f"Error starting background services: {e}")
    
    def stop_background_services(self):
        """Stop background services"""
        try:
            # Close all agents
            for agent_name, agent in self.agents.items():
                if hasattr(agent, 'close'):
                    agent.close()
            
            self.logger.info("All agents closed")
            
        except Exception as e:
            self.logger.error(f"Error stopping services: {e}")
    
    def run_interactive_mode(self):
        """Run interactive command mode"""
        print("\n=== AI Agent & Productivity Tool ===")
        print("Available commands:")
        print("1. search_jobs <skill> [countries] - Search for jobs")
        print("2. optimize_cv <cv_file> - Optimize CV for jobs")
        print("3. scrape_businesses [categories] [cities] - Scrape business data")
        print("4. run_daily_updates - Run daily job portal updates")
        print("5. start_services - Start background services")
        print("6. stats - Show application statistics")
        print("7. help - Show this help")
        print("8. exit - Exit application")
        
        while True:
            try:
                command = input("\nEnter command: ").strip().split()
                
                if not command:
                    continue
                
                cmd = command[0].lower()
                
                if cmd == "search_jobs":
                    if len(command) < 2:
                        print("Usage: search_jobs <skill> [countries]")
                        continue
                    
                    skill = command[1]
                    countries = command[2:] if len(command) > 2 else None
                    self.search_gcc_jobs(skill, countries)
                
                elif cmd == "optimize_cv":
                    if len(command) < 2:
                        print("Usage: optimize_cv <cv_file>")
                        continue
                    
                    cv_file = command[1]
                    # This would read CV content from file
                    cv_content = "Sample CV content..."  # Replace with actual file reading
                    jobs = db.get_job_applications(limit=10)
                    self.optimize_cv_for_jobs(jobs, cv_content)
                
                elif cmd == "scrape_businesses":
                    categories = command[1:] if len(command) > 1 else None
                    self.scrape_business_data(categories)
                
                elif cmd == "run_daily_updates":
                    self.run_job_portal_updates()
                
                elif cmd == "start_services":
                    self.start_background_services()
                
                elif cmd == "stats":
                    self.get_statistics()
                
                elif cmd == "help":
                    print("\nAvailable commands:")
                    print("1. search_jobs <skill> [countries] - Search for jobs")
                    print("2. optimize_cv <cv_file> - Optimize CV for jobs")
                    print("3. scrape_businesses [categories] [cities] - Scrape business data")
                    print("4. run_daily_updates - Run daily job portal updates")
                    print("5. start_services - Start background services")
                    print("6. stats - Show application statistics")
                    print("7. help - Show this help")
                    print("8. exit - Exit application")
                
                elif cmd == "exit":
                    print("Exiting application...")
                    self.stop_background_services()
                    break
                
                else:
                    print(f"Unknown command: {cmd}")
                    print("Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                print("\nExiting application...")
                self.stop_background_services()
                break
            except Exception as e:
                self.logger.error(f"Error in interactive mode: {e}")
                print(f"Error: {e}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Agent & Productivity Tool")
    parser.add_argument("--mode", choices=["interactive", "job_search", "cv_optimize", "scrape", "daily_updates"], 
                       default="interactive", help="Application mode")
    parser.add_argument("--skill", type=str, help="Skill to search for jobs")
    parser.add_argument("--countries", nargs="+", help="Countries to search in")
    parser.add_argument("--categories", nargs="+", help="Business categories to scrape")
    parser.add_argument("--cities", nargs="+", help="Cities to scrape")
    parser.add_argument("--cv_file", type=str, help="CV file to optimize")
    parser.add_argument("--start_services", action="store_true", help="Start background services")
    
    args = parser.parse_args()
    
    app = AutomaApp()
    
    try:
        if args.start_services:
            app.start_background_services()
        
        if args.mode == "interactive":
            app.run_interactive_mode()
        
        elif args.mode == "job_search":
            if not args.skill:
                print("Error: --skill is required for job_search mode")
                return
            app.search_gcc_jobs(args.skill, args.countries)
        
        elif args.mode == "cv_optimize":
            if not args.cv_file:
                print("Error: --cv_file is required for cv_optimize mode")
                return
            # This would read CV content from file
            cv_content = "Sample CV content..."  # Replace with actual file reading
            jobs = db.get_job_applications(limit=10)
            app.optimize_cv_for_jobs(jobs, cv_content)
        
        elif args.mode == "scrape":
            app.scrape_business_data(args.categories, args.cities)
        
        elif args.mode == "daily_updates":
            app.run_job_portal_updates()
        
        if args.start_services:
            # Keep the application running for background services
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                print("\nStopping background services...")
                app.stop_background_services()
    
    except Exception as e:
        app.logger.error(f"Error in main: {e}")
        app.stop_background_services()


if __name__ == "__main__":
    main() 