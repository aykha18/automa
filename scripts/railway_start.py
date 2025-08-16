#!/usr/bin/env python3
"""
Railway Startup Script
Combines web interface with background scheduler for Railway deployment
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
    """Setup scheduler for Railway"""
    try:
        from src.core.config import config
        
        print("🚂 Setting up Railway scheduler...")
        
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
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Railway scheduler: {e}")
        return False

def run_job_portal_updates():
    """Run job portal updates"""
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

def run_scheduler_loop():
    """Run the scheduler loop"""
    print("🚂 Starting Railway scheduler service...")
    
    try:
        while True:
            # Run pending scheduled tasks
            schedule.run_pending()
            
            # Sleep for a short interval
            time.sleep(60)  # Check every minute
            
    except Exception as e:
        print(f"❌ Error in Railway scheduler: {e}")

def start_web_interface():
    """Start the Flask web interface"""
    try:
        from src.web.app import app
        
        # Get port from Railway environment
        port = int(os.environ.get('PORT', 5000))
        
        print(f"🌐 Starting web interface on port {port}")
        
        # Run Flask app
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")

def main():
    """Main function for Railway deployment"""
    print("🚂 RAILWAY DEPLOYMENT STARTUP")
    print("=" * 50)
    
    # Check if we're on Railway
    is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None
    print(f"🌍 Environment: {'Railway' if is_railway else 'Local'}")
    
    # Setup scheduler
    if setup_railway_scheduler():
        # Start scheduler in background thread
        scheduler_thread = threading.Thread(target=run_scheduler_loop, daemon=True)
        scheduler_thread.start()
        
        print("✅ Railway scheduler started in background")
        print("📋 Services running:")
        print("  - Job portal updates (daily at 9:00 AM)")
        print("  - Test run (within 5 minutes)")
        print("  - Web interface (starting now)")
        
        # Start web interface in main thread
        start_web_interface()
        
    else:
        print("❌ Failed to setup scheduler, starting web interface only")
        start_web_interface()

if __name__ == "__main__":
    main()
