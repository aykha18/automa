"""
Flask Web Application for AI Agent & Productivity Tool
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# Import agents
import sys
import os
# Add the src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, src_path)

# Import core modules first (these work)
from core.database import db
from core.config import config

# Try to import real DataScraper (this one works)
try:
    # from agents.data_scraper import DataScraper
    # print("✓ Real DataScraper imported successfully")
    DataScraper = None
    print("✓ DataScraper disabled for testing")
except ImportError as e:
    print(f"DataScraper import error: {e}")
    DataScraper = None

# Try to import other agents, but fall back to mocks if they fail
try:
    from agents.job_portal_agent import JobPortalAgent
    print("✓ Real JobPortalAgent imported successfully")
except ImportError as e:
    print(f"JobPortalAgent import error: {e}")
    JobPortalAgent = None

# Import BaytHttpAgent
try:
    from agents.bayt_http_agent import BaytHttpAgent
    print("✓ Real BaytHttpAgent imported successfully")
except ImportError as e:
    print(f"BaytHttpAgent import error: {e}")
    BaytHttpAgent = None

# Import BaytPlaywrightAgent
try:
    from agents.bayt_playwright_agent import BaytPlaywrightAgent
    print("✓ Real BaytPlaywrightAgent imported successfully")
except ImportError as e:
    print(f"BaytPlaywrightAgent import error: {e}")
    BaytPlaywrightAgent = None

# Import IndeedPlaywrightAgent
try:
    from agents.indeed_playwright_agent import IndeedPlaywrightAgent
    print("✓ Real IndeedPlaywrightAgent imported successfully")
except ImportError as e:
    print(f"IndeedPlaywrightAgent import error: {e}")
    IndeedPlaywrightAgent = None

# Import IndeedHttpAgent
try:
    from agents.indeed_http_agent import IndeedHttpAgent
    print("✓ Real IndeedHttpAgent imported successfully")
except ImportError as e:
    print(f"IndeedHttpAgent import error: {e}")
    IndeedHttpAgent = None

try:
    # from agents.email_agent import EmailAgent
    # print("✓ Real EmailAgent imported successfully")
    EmailAgent = None
    print("✓ EmailAgent disabled for testing")
except ImportError as e:
    print(f"EmailAgent import error: {e}")
    EmailAgent = None

try:
    from agents.scheduler_agent import SchedulerAgent
    print("✓ Real SchedulerAgent imported successfully")
except ImportError as e:
    print(f"SchedulerAgent import error: {e}")
    # Try alternative import path
    try:
        import sys
        import os
        agents_path = os.path.join(os.path.dirname(__file__), '..', 'agents')
        sys.path.insert(0, agents_path)
        from scheduler_agent import SchedulerAgent
        print("✓ Real SchedulerAgent imported with alternative path")
    except ImportError as e2:
        print(f"SchedulerAgent alternative import error: {e2}")
        SchedulerAgent = None

try:
    # from agents.gcc_job_finder import GCCJobFinder
    # print("✓ Real GCCJobFinder imported successfully")
    GCCJobFinder = None
    print("✓ GCCJobFinder disabled for testing")
except ImportError as e:
    print(f"GCCJobFinder import error: {e}")
    GCCJobFinder = None

try:
    # from agents.cv_optimizer import CVOptimizer
    # print("✓ Real CVOptimizer imported successfully")
    CVOptimizer = None
    print("✓ CVOptimizer disabled for testing")
except ImportError as e:
    print(f"CVOptimizer import error: {e}")
    CVOptimizer = None

try:
    # from agents.email_monitor import EmailMonitor
    # print("✓ Real EmailMonitor imported successfully")
    EmailMonitor = None
    print("✓ EmailMonitor disabled for testing")
except ImportError as e:
    print(f"EmailMonitor import error: {e}")
    EmailMonitor = None

# Create mock classes for agents that failed to import
class MockAgent:
    def __init__(self):
        pass
    def run_daily_updates(self):
        return True
    def search_jobs_by_skill(self, skill, countries=None, max_results=50):
        return []
    def optimize_cv_with_ai(self, cv_content, job_requirements, job_title, company):
        return cv_content
    def scrape_uae_businesses(self, categories=None, cities=None):
        return []

# Use real agents if available, otherwise use mocks
JobPortalAgent = JobPortalAgent if JobPortalAgent else MockAgent
EmailAgent = EmailAgent if EmailAgent else MockAgent
SchedulerAgent = SchedulerAgent if SchedulerAgent else MockAgent
GCCJobFinder = GCCJobFinder if GCCJobFinder else MockAgent
CVOptimizer = CVOptimizer if CVOptimizer else MockAgent
EmailMonitor = EmailMonitor if EmailMonitor else MockAgent

DataScraper = DataScraper if DataScraper else MockAgent


# Set up Flask app with correct template directory
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'automa_secret_key_2024'

# Initialize agents
agents = {
    "job_portal": JobPortalAgent(),
    "email": EmailAgent(),
    "scheduler": SchedulerAgent(),
    "gcc_job_finder": GCCJobFinder(),
    "cv_optimizer": CVOptimizer(),
    "email_monitor": EmailMonitor(),
    "data_scraper": DataScraper()
}


@app.route('/')
def index():
    """Main dashboard page"""
    try:
        print(f"DEBUG: Template directory: {template_dir}")
        print(f"DEBUG: Template exists: {os.path.exists(os.path.join(template_dir, 'index.html'))}")
        return render_template('index.html')
    except Exception as e:
        print(f"DEBUG: Template error: {e}")
        return f"Error loading template: {str(e)}"

@app.route('/test')
def test():
    """Test route to check if Flask is working"""
    return "Flask app is working! Test successful."


@app.route('/job-portal')
def job_portal():
    """Job portal management page"""
    return render_template('job_portal.html')


@app.route('/email-monitor')
def email_monitor():
    """Email monitoring page"""
    return render_template('email_monitor.html')


@app.route('/gcc-jobs')
def gcc_jobs():
    """GCC job search page"""
    return render_template('gcc_jobs.html')


@app.route('/cv-optimizer')
def cv_optimizer():
    """CV optimizer page"""
    return render_template('cv_optimizer.html')


@app.route('/data-scraper')
def data_scraper():
    """Data scraper page"""
    return render_template('data_scraper.html')


@app.route('/scheduler')
def scheduler():
    """Scheduler management page"""
    return render_template('scheduler.html')


@app.route('/api/run-daily-updates', methods=['POST'])
def run_daily_updates():
    """API endpoint to run daily job portal updates"""
    try:
        results = {}
        
        # Run updates for Bayt.com
        if BaytPlaywrightAgent is not None:
            # Use Playwright agent for better automation
            bayt_agent = BaytPlaywrightAgent()
            bayt_result = bayt_agent.run_daily_updates()
            bayt_agent.close()
            results["bayt"] = bayt_result
            print(f"Bayt.com updates (Playwright): {bayt_result['status']} - {bayt_result['message']}")
        elif BaytHttpAgent is not None:
            # Fallback to HTTP agent
            bayt_agent = BaytHttpAgent()
            bayt_result = bayt_agent.run_daily_updates()
            bayt_agent.close()
            results["bayt"] = bayt_result
            print(f"Bayt.com updates (HTTP): {bayt_result['status']} - {bayt_result['message']}")
        
        # Run updates for Indeed.com
        if IndeedPlaywrightAgent is not None:
            # Use Playwright agent for better automation
            indeed_agent = IndeedPlaywrightAgent()
            indeed_result = indeed_agent.run_daily_updates()
            indeed_agent.close()
            results["indeed"] = indeed_result
            print(f"Indeed.com updates (Playwright): {indeed_result['status']} - {indeed_result['message']}")
        elif IndeedHttpAgent is not None:
            # Fallback to HTTP agent
            indeed_agent = IndeedHttpAgent()
            indeed_result = indeed_agent.run_daily_updates()
            indeed_agent.close()
            results["indeed"] = indeed_result
            print(f"Indeed.com updates (HTTP): {indeed_result['status']} - {indeed_result['message']}")
        
        # Run updates for other portals
        agents["job_portal"].run_daily_updates()
        
        return jsonify({
            "success": True, 
            "message": "Daily updates completed successfully",
            "results": results
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/refresh-cv', methods=['POST'])
def refresh_cv():
    """API endpoint to refresh CV on job portals"""
    try:
        data = request.get_json()
        portal_name = data.get('portal_name', 'bayt')
        
        if portal_name.lower() == 'bayt':
            if BaytPlaywrightAgent is not None:
                # Use Playwright agent for better automation
                agent = BaytPlaywrightAgent()
                success = agent.refresh_cv()
                agent.close()
            elif BaytHttpAgent is not None:
                # Fallback to HTTP agent
                agent = BaytHttpAgent()
                success = agent.refresh_cv()
                agent.close()
            else:
                return jsonify({
                    'success': False,
                    'error': 'No Bayt agent available'
                })

            if success:
                return jsonify({
                    "success": True,
                    "message": "CV refreshed successfully on Bayt.com"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to refresh CV on Bayt.com"
                })
        
        elif portal_name.lower() == 'indeed':
            if IndeedPlaywrightAgent is not None:
                # Use Playwright agent for better automation
                agent = IndeedPlaywrightAgent()
                success = agent.refresh_cv()
                agent.close()
            elif IndeedHttpAgent is not None:
                # Fallback to HTTP agent
                agent = IndeedHttpAgent()
                success = agent.refresh_cv()
                agent.close()
            else:
                return jsonify({
                    'success': False,
                    'error': 'No Indeed agent available'
                })

            if success:
                return jsonify({
                    "success": True,
                    "message": "CV refreshed successfully on Indeed.com"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to refresh CV on Indeed.com"
                })
        else:
            return jsonify({
                "success": False,
                "error": f"CV refresh not implemented for {portal_name}"
            })
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/test-portal-connection', methods=['POST'])
def test_portal_connection():
    """API endpoint to test job portal connection"""
    try:
        data = request.get_json()
        portal_name = data.get('portal_name', 'indeed')
        
        # Use specific agents for supported portals
        if portal_name.lower() == 'bayt':
            if BaytPlaywrightAgent is not None:
                # Use Playwright agent for better automation
                agent = BaytPlaywrightAgent()
                result = agent.test_connection()
                agent.close()
            elif BaytHttpAgent is not None:
                # Fallback to HTTP agent
                agent = BaytHttpAgent()
                result = agent.test_connection()
                agent.close()
            else:
                return jsonify({
                    'success': False,
                    'error': 'No Bayt agent available'
                })
        
        elif portal_name.lower() == 'indeed':
            if IndeedPlaywrightAgent is not None:
                # Use Playwright agent for better automation
                agent = IndeedPlaywrightAgent()
                result = agent.test_connection()
                agent.close()
            elif IndeedHttpAgent is not None:
                # Fallback to HTTP agent
                agent = IndeedHttpAgent()
                result = agent.test_connection()
                agent.close()
            else:
                return jsonify({
                    'success': False,
                    'error': 'No Indeed agent available'
                })
        else:
            result = agents["job_portal"].test_portal_connection(portal_name)
        
        return jsonify({
            "success": True,
            "result": result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/search-jobs', methods=['POST'])
def search_jobs():
    """API endpoint to search for jobs"""
    try:
        data = request.get_json()
        skill = data.get('skill', '')
        countries = data.get('countries', [])
        max_results = data.get('max_results', 50)
        
        jobs = agents["gcc_job_finder"].search_jobs_by_skill(skill, countries, max_results)
        
        return jsonify({
            "success": True,
            "jobs": jobs,
            "count": len(jobs)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/optimize-cv', methods=['POST'])
def optimize_cv():
    """API endpoint to optimize CV"""
    try:
        data = request.get_json()
        cv_content = data.get('cv_content', '')
        job_data = data.get('job_data', {})
        
        result = agents["cv_optimizer"].process_job_application(job_data, cv_content)
        
        return jsonify({
            "success": True,
            "result": result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/scrape-businesses', methods=['POST'])
def scrape_businesses():
    """API endpoint to scrape business data"""
    try:
        data = request.get_json()
        categories = data.get('categories', [])
        cities = data.get('cities', [])
        
        print(f"DEBUG: Received categories: {categories}")
        print(f"DEBUG: Received cities: {cities}")
        
        # Initialize the data scraper
        scraper = agents["data_scraper"]
        print(f"DEBUG: Scraper type: {type(scraper)}")
        
        # Perform real scraping
        businesses = scraper.scrape_uae_businesses(categories, cities)
        print(f"DEBUG: Scraped {len(businesses)} businesses")
        
        # Save to database if available
        try:
            scraper.save_businesses_to_database(businesses)
        except Exception as save_error:
            print(f"Warning: Could not save to database: {save_error}")
        
        return jsonify({
            "success": True,
            "businesses": businesses,
            "count": len(businesses),
            "categories": categories,
            "cities": cities
        })
    except Exception as e:
        print(f"Scraping error: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/get-statistics')
def get_statistics():
    """API endpoint to get application statistics"""
    try:
        stats = {
            "job_applications": len(db.get_job_applications()),
            "email_responses": len(db.get_unprocessed_emails()),
            "scraped_businesses": len(db.get_scraped_data()),
            "scheduled_tasks": len(db.get_active_scheduled_tasks())
        }
        
        return jsonify({
            "success": True,
            "statistics": stats
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/get-countries')
def get_countries():
    """API endpoint to get available GCC countries"""
    try:
        countries = agents["gcc_job_finder"].get_available_countries()
        return jsonify({
            "success": True,
            "countries": countries
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/start-email-monitoring', methods=['POST'])
def start_email_monitoring():
    """API endpoint to start email monitoring"""
    try:
        # This would start email monitoring in a background thread
        # For now, just return success
        return jsonify({
            "success": True,
            "message": "Email monitoring started"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/schedule-task', methods=['POST'])
def schedule_task():
    """API endpoint to schedule a task"""
    try:
        data = request.get_json()
        task_name = data.get('task_name', '')
        task_type = data.get('task_type', '')
        schedule_time = data.get('schedule_time', '')
        task_config = data.get('config', {})
        
        success = agents["scheduler"].schedule_custom_task(
            task_name, task_type, schedule_time, task_config
        )
        
        return jsonify({
            "success": success,
            "message": "Task scheduled successfully" if success else "Failed to schedule task"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/get-scheduled-tasks')
def get_scheduled_tasks():
    """API endpoint to get scheduled tasks"""
    try:
        tasks = agents["scheduler"].get_scheduled_tasks()
        return jsonify({
            "success": True,
            "tasks": tasks
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/get-job-applications')
def get_job_applications():
    """API endpoint to get job applications"""
    try:
        applications = db.get_job_applications(limit=100)
        return jsonify({
            "success": True,
            "applications": applications
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/get-email-responses')
def get_email_responses():
    """API endpoint to get email responses"""
    try:
        responses = db.get_unprocessed_emails()
        return jsonify({
            "success": True,
            "responses": responses
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/get-scraped-data')
def get_scraped_data():
    """API endpoint to get scraped data"""
    try:
        data = db.get_scraped_data(limit=100)
        return jsonify({
            "success": True,
            "data": data
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 