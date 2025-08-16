"""
GCC Job Finder Agent - Identifies skills-specific jobs across GCC countries
"""

import time
import random
import logging
from datetime import datetime
from typing import Dict, List, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import sys
import os
# Add the src directory to Python path for absolute imports
src_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, src_path)

from core.config import config
from core.database import db
from core.utils import setup_logging


class GCCJobFinder:
    """Agent for finding jobs across GCC countries"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.gcc_countries = config.get_gcc_countries()
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome WebDriver with basic options"""
        try:
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-javascript")
            chrome_options.add_argument("--headless")
            
            # Use webdriver-manager to automatically download and manage ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.logger.info("Chrome WebDriver setup successfully for GCC Job Finder")
            return
            
        except Exception as e:
            self.logger.error(f"Failed to setup Chrome WebDriver: {e}")
            self.logger.error("Please install Chrome browser to enable job finding automation")
            self.driver = None
    
    def search_jobs_by_skill(self, skill: str, country: str = None) -> List[Dict[str, Any]]:
        """Search for jobs by skill across GCC countries"""
        if not self.driver:
            self.logger.error("WebDriver not available")
            return []
        
        jobs = []
        countries_to_search = [country] if country else self.gcc_countries
        
        for country_code in countries_to_search:
            try:
                self.logger.info(f"Searching for {skill} jobs in {country_code}")
                
                # Search on major job portals
                portal_jobs = self._search_on_portal("indeed", skill, country_code)
                jobs.extend(portal_jobs)
                
                portal_jobs = self._search_on_portal("linkedin", skill, country_code)
                jobs.extend(portal_jobs)
                
                portal_jobs = self._search_on_portal("bayt", skill, country_code)
                jobs.extend(portal_jobs)
                
                time.sleep(random.uniform(2, 4))  # Random delay between countries
                
            except Exception as e:
                self.logger.error(f"Error searching {skill} jobs in {country_code}: {e}")
                continue
        
        return jobs
    
    def _search_on_portal(self, portal: str, skill: str, country: str) -> List[Dict[str, Any]]:
        """Search for jobs on a specific portal"""
        jobs = []
        
        try:
            # Define search URLs for different portals
            search_urls = {
                "indeed": f"https://{country}.indeed.com/jobs?q={skill}",
                "linkedin": f"https://www.linkedin.com/jobs/search/?keywords={skill}&location={country}",
                "bayt": f"https://www.bayt.com/en/{country}/jobs/{skill}-jobs/"
            }
            
            if portal not in search_urls:
                return jobs
            
            search_url = search_urls[portal]
            self.driver.get(search_url)
            time.sleep(random.uniform(3, 5))
            
            # Extract job listings
            job_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-jobid], .job-listing, .job-card")
            
            for job_element in job_elements[:10]:  # Limit to 10 jobs per portal
                try:
                    job_data = self._extract_job_data(job_element, portal)
                    if job_data:
                        job_data["portal"] = portal
                        job_data["country"] = country
                        job_data["skill"] = skill
                        jobs.append(job_data)
                except Exception as e:
                    self.logger.warning(f"Error extracting job data: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error searching on {portal}: {e}")
        
        return jobs
    
    def _extract_job_data(self, job_element, portal: str) -> Dict[str, Any]:
        """Extract job data from a job element"""
        try:
            # Common selectors for job data
            title_selectors = [".job-title", "h2", "h3", ".title"]
            company_selectors = [".company", ".employer", ".company-name"]
            location_selectors = [".location", ".job-location", ".city"]
            
            job_data = {
                "title": "",
                "company": "",
                "location": "",
                "url": "",
                "posted_date": "",
                "salary": "",
                "description": ""
            }
            
            # Extract title
            for selector in title_selectors:
                try:
                    title_element = job_element.find_element(By.CSS_SELECTOR, selector)
                    job_data["title"] = title_element.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            # Extract company
            for selector in company_selectors:
                try:
                    company_element = job_element.find_element(By.CSS_SELECTOR, selector)
                    job_data["company"] = company_element.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            # Extract location
            for selector in location_selectors:
                try:
                    location_element = job_element.find_element(By.CSS_SELECTOR, selector)
                    job_data["location"] = location_element.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            # Extract URL
            try:
                link_element = job_element.find_element(By.TAG_NAME, "a")
                job_data["url"] = link_element.get_attribute("href")
            except NoSuchElementException:
                pass
            
            return job_data
            
        except Exception as e:
            self.logger.warning(f"Error extracting job data: {e}")
            return None
    
    def optimize_cv_for_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize CV based on job requirements"""
        # This is a placeholder for CV optimization logic
        # In a real implementation, this would use AI/ML to analyze job requirements
        # and suggest CV improvements
        
        optimization_suggestions = {
            "skills_to_highlight": [],
            "keywords_to_add": [],
            "experience_to_emphasize": [],
            "formatting_suggestions": []
        }
        
        # Simple keyword matching for demonstration
        job_title = job_data.get("title", "").lower()
        job_description = job_data.get("description", "").lower()
        
        if "developer" in job_title or "developer" in job_description:
            optimization_suggestions["skills_to_highlight"].extend(["Programming", "Software Development", "Problem Solving"])
        
        if "manager" in job_title or "management" in job_description:
            optimization_suggestions["skills_to_highlight"].extend(["Leadership", "Team Management", "Project Management"])
        
        return optimization_suggestions
    
    def auto_apply_to_job(self, job_data: Dict[str, Any], cv_data: Dict[str, Any]) -> bool:
        """Automatically apply to a job"""
        # This is a placeholder for auto-application logic
        # In a real implementation, this would:
        # 1. Fill out application forms
        # 2. Upload optimized CV
        # 3. Submit application
        
        self.logger.info(f"Auto-applying to {job_data.get('title', 'Unknown')} at {job_data.get('company', 'Unknown')}")
        
        # Simulate application process
        time.sleep(random.uniform(2, 4))
        
        # Log the application
        db.add_scheduled_task(
            task_name=f"auto_apply_{job_data.get('company', 'unknown')}",
            task_type="job_application",
            schedule_time=datetime.now().strftime("%H:%M"),
            config={
                "job_title": job_data.get("title", ""),
                "company": job_data.get("company", ""),
                "portal": job_data.get("portal", ""),
                "status": "applied"
            }
        )
        
        return True
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None


def main():
    """Main function to run GCC job finding"""
    finder = GCCJobFinder()
    try:
        # Example: Search for PLSQL Developer jobs
        jobs = finder.search_jobs_by_skill("PLSQL Developer", "UAE")
        print(f"Found {len(jobs)} jobs")
        
        for job in jobs[:5]:  # Show first 5 jobs
            print(f"Job: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
            
    finally:
        finder.close()


if __name__ == "__main__":
    main() 