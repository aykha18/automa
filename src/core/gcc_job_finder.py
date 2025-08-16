"""
GCC Job Finder Agent - Finds skills-specific jobs across GCC countries
"""

import time
import random
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup

from ..core.config import config
from ..core.database import db
from ..core.utils import setup_logging


class GCCJobFinder:
    """Agent for finding jobs across GCC countries"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.gcc_countries = config.get_gcc_countries()
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            self.logger.error(f"Failed to setup WebDriver: {e}")
            self.driver = None
    
    def search_jobs_by_skill(self, skill: str, countries: List[str] = None, 
                           max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for jobs by skill across specified GCC countries"""
        if countries is None:
            countries = [country['code'] for country in self.gcc_countries]
        
        all_jobs = []
        
        for country_code in countries:
            country_name = self._get_country_name(country_code)
            self.logger.info(f"Searching for {skill} jobs in {country_name}")
            
            try:
                country_jobs = self._search_country_jobs(skill, country_code, max_results)
                all_jobs.extend(country_jobs)
                
                # Random delay between countries
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                self.logger.error(f"Error searching jobs in {country_name}: {e}")
                continue
        
        return all_jobs
    
    def _get_country_name(self, country_code: str) -> str:
        """Get country name from country code"""
        for country in self.gcc_countries:
            if country['code'] == country_code:
                return country['name']
        return country_code
    
    def _search_country_jobs(self, skill: str, country_code: str, 
                            max_results: int) -> List[Dict[str, Any]]:
        """Search for jobs in a specific country"""
        jobs = []
        
        # Get job sites for this country
        country_config = next((c for c in self.gcc_countries if c['code'] == country_code), None)
        if not country_config:
            return jobs
        
        job_sites = country_config.get('job_sites', [])
        
        for site in job_sites:
            try:
                site_jobs = self._search_site_jobs(skill, site, country_code, max_results)
                jobs.extend(site_jobs)
                
                # Random delay between sites
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                self.logger.error(f"Error searching {site}: {e}")
                continue
        
        return jobs
    
    def _search_site_jobs(self, skill: str, site: str, country_code: str, 
                         max_results: int) -> List[Dict[str, Any]]:
        """Search for jobs on a specific site"""
        jobs = []
        
        try:
            if "bayt.com" in site:
                jobs = self._search_bayt_jobs(skill, country_code, max_results)
            elif "naukrigulf.com" in site:
                jobs = self._search_naukrigulf_jobs(skill, country_code, max_results)
            elif "gulftalent.com" in site:
                jobs = self._search_gulftalent_jobs(skill, country_code, max_results)
            else:
                # Generic search for other sites
                jobs = self._generic_job_search(skill, site, country_code, max_results)
                
        except Exception as e:
            self.logger.error(f"Error searching {site}: {e}")
        
        return jobs
    
    def _search_bayt_jobs(self, skill: str, country_code: str, max_results: int) -> List[Dict[str, Any]]:
        """Search jobs on Bayt.com"""
        jobs = []
        
        try:
            # Construct search URL
            search_url = f"https://www.bayt.com/en/{country_code.lower()}/jobs/{skill.lower().replace(' ', '-')}-jobs/"
            
            if self.driver:
                self.driver.get(search_url)
                time.sleep(random.uniform(2, 4))
                
                # Wait for job listings to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "job-card"))
                )
                
                # Extract job listings
                job_elements = self.driver.find_elements(By.CLASS_NAME, "job-card")
                
                for job_element in job_elements[:max_results]:
                    try:
                        job_data = self._extract_bayt_job_data(job_element)
                        if job_data:
                            jobs.append(job_data)
                    except Exception as e:
                        self.logger.warning(f"Error extracting job data: {e}")
                        continue
                        
        except Exception as e:
            self.logger.error(f"Error searching Bayt jobs: {e}")
        
        return jobs
    
    def _extract_bayt_job_data(self, job_element) -> Dict[str, Any]:
        """Extract job data from Bayt job element"""
        try:
            # Extract job title
            title_element = job_element.find_element(By.CSS_SELECTOR, ".job-title a")
            title = title_element.text.strip()
            job_url = title_element.get_attribute("href")
            
            # Extract company name
            company_element = job_element.find_element(By.CSS_SELECTOR, ".company-name")
            company = company_element.text.strip()
            
            # Extract location
            location_element = job_element.find_element(By.CSS_SELECTOR, ".job-location")
            location = location_element.text.strip()
            
            # Extract job type
            job_type_element = job_element.find_element(By.CSS_SELECTOR, ".job-type")
            job_type = job_type_element.text.strip()
            
            # Extract posted date
            date_element = job_element.find_element(By.CSS_SELECTOR, ".job-date")
            posted_date = date_element.text.strip()
            
            return {
                "title": title,
                "company": company,
                "location": location,
                "job_type": job_type,
                "posted_date": posted_date,
                "job_url": job_url,
                "source": "bayt.com",
                "scraped_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"Error extracting Bayt job data: {e}")
            return None
    
    def _search_naukrigulf_jobs(self, skill: str, country_code: str, max_results: int) -> List[Dict[str, Any]]:
        """Search jobs on NaukriGulf.com"""
        jobs = []
        
        try:
            # Construct search URL
            search_url = f"https://www.naukrigulf.com/jobs-in-{country_code.lower()}/{skill.lower().replace(' ', '-')}-jobs"
            
            if self.driver:
                self.driver.get(search_url)
                time.sleep(random.uniform(2, 4))
                
                # Wait for job listings to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "jobTuple"))
                )
                
                # Extract job listings
                job_elements = self.driver.find_elements(By.CLASS_NAME, "jobTuple")
                
                for job_element in job_elements[:max_results]:
                    try:
                        job_data = self._extract_naukrigulf_job_data(job_element)
                        if job_data:
                            jobs.append(job_data)
                    except Exception as e:
                        self.logger.warning(f"Error extracting job data: {e}")
                        continue
                        
        except Exception as e:
            self.logger.error(f"Error searching NaukriGulf jobs: {e}")
        
        return jobs
    
    def _extract_naukrigulf_job_data(self, job_element) -> Dict[str, Any]:
        """Extract job data from NaukriGulf job element"""
        try:
            # Extract job title
            title_element = job_element.find_element(By.CSS_SELECTOR, ".jobTuple h2 a")
            title = title_element.text.strip()
            job_url = title_element.get_attribute("href")
            
            # Extract company name
            company_element = job_element.find_element(By.CSS_SELECTOR, ".companyInfo")
            company = company_element.text.strip()
            
            # Extract location
            location_element = job_element.find_element(By.CSS_SELECTOR, ".location")
            location = location_element.text.strip()
            
            # Extract experience
            exp_element = job_element.find_element(By.CSS_SELECTOR, ".experience")
            experience = exp_element.text.strip()
            
            return {
                "title": title,
                "company": company,
                "location": location,
                "experience": experience,
                "job_url": job_url,
                "source": "naukrigulf.com",
                "scraped_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"Error extracting NaukriGulf job data: {e}")
            return None
    
    def _search_gulftalent_jobs(self, skill: str, country_code: str, max_results: int) -> List[Dict[str, Any]]:
        """Search jobs on GulfTalent.com"""
        jobs = []
        
        try:
            # Construct search URL
            search_url = f"https://www.gulftalent.com/{country_code.lower()}/jobs/{skill.lower().replace(' ', '-')}"
            
            if self.driver:
                self.driver.get(search_url)
                time.sleep(random.uniform(2, 4))
                
                # Wait for job listings to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "job-listing"))
                )
                
                # Extract job listings
                job_elements = self.driver.find_elements(By.CLASS_NAME, "job-listing")
                
                for job_element in job_elements[:max_results]:
                    try:
                        job_data = self._extract_gulftalent_job_data(job_element)
                        if job_data:
                            jobs.append(job_data)
                    except Exception as e:
                        self.logger.warning(f"Error extracting job data: {e}")
                        continue
                        
        except Exception as e:
            self.logger.error(f"Error searching GulfTalent jobs: {e}")
        
        return jobs
    
    def _extract_gulftalent_job_data(self, job_element) -> Dict[str, Any]:
        """Extract job data from GulfTalent job element"""
        try:
            # Extract job title
            title_element = job_element.find_element(By.CSS_SELECTOR, ".job-title a")
            title = title_element.text.strip()
            job_url = title_element.get_attribute("href")
            
            # Extract company name
            company_element = job_element.find_element(By.CSS_SELECTOR, ".company-name")
            company = company_element.text.strip()
            
            # Extract location
            location_element = job_element.find_element(By.CSS_SELECTOR, ".job-location")
            location = location_element.text.strip()
            
            # Extract salary
            salary_element = job_element.find_element(By.CSS_SELECTOR, ".salary")
            salary = salary_element.text.strip()
            
            return {
                "title": title,
                "company": company,
                "location": location,
                "salary": salary,
                "job_url": job_url,
                "source": "gulftalent.com",
                "scraped_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"Error extracting GulfTalent job data: {e}")
            return None
    
    def _generic_job_search(self, skill: str, site: str, country_code: str, max_results: int) -> List[Dict[str, Any]]:
        """Generic job search for other sites"""
        jobs = []
        
        try:
            # Use requests for simple sites
            search_url = f"https://{site}/search?q={skill}&location={country_code}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Generic extraction patterns
            job_elements = soup.find_all(['div', 'article'], class_=lambda x: x and 'job' in x.lower())
            
            for job_element in job_elements[:max_results]:
                try:
                    job_data = self._extract_generic_job_data(job_element, site)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    self.logger.warning(f"Error extracting generic job data: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error in generic job search for {site}: {e}")
        
        return jobs
    
    def _extract_generic_job_data(self, job_element, site: str) -> Dict[str, Any]:
        """Extract job data from generic job element"""
        try:
            # Try to find title
            title = ""
            title_selectors = ['h1', 'h2', 'h3', '.title', '.job-title', '[class*="title"]']
            for selector in title_selectors:
                title_elem = job_element.find(selector)
                if title_elem:
                    title = title_elem.get_text().strip()
                    break
            
            # Try to find company
            company = ""
            company_selectors = ['.company', '.employer', '[class*="company"]']
            for selector in company_selectors:
                company_elem = job_element.find(selector)
                if company_elem:
                    company = company_elem.get_text().strip()
                    break
            
            # Try to find location
            location = ""
            location_selectors = ['.location', '.place', '[class*="location"]']
            for selector in location_selectors:
                location_elem = job_element.find(selector)
                if location_elem:
                    location = location_elem.get_text().strip()
                    break
            
            if title:  # Only return if we found at least a title
                return {
                    "title": title,
                    "company": company,
                    "location": location,
                    "source": site,
                    "scraped_date": datetime.now().isoformat()
                }
            
        except Exception as e:
            self.logger.warning(f"Error extracting generic job data: {e}")
        
        return None
    
    def save_jobs_to_database(self, jobs: List[Dict[str, Any]], skill: str):
        """Save found jobs to database"""
        for job in jobs:
            try:
                # Add job to database
                db.add_job_application(
                    job_title=job.get('title', ''),
                    company=job.get('company', ''),
                    portal=job.get('source', ''),
                    country=job.get('location', '').split(',')[0] if job.get('location') else '',
                    notes=f"Skill: {skill}, Found via: {job.get('source', '')}"
                )
            except Exception as e:
                self.logger.error(f"Error saving job to database: {e}")
    
    def get_available_countries(self) -> List[Dict[str, str]]:
        """Get list of available GCC countries"""
        return [{"code": country["code"], "name": country["name"]} for country in self.gcc_countries]
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None


def main():
    """Main function to run GCC job finder"""
    finder = GCCJobFinder()
    
    try:
        # Example: Search for PLSQL jobs in UAE and Saudi Arabia
        countries = ["AE", "SA"]
        jobs = finder.search_jobs_by_skill("PLSQL Developer", countries, max_results=20)
        
        print(f"Found {len(jobs)} jobs")
        for job in jobs[:5]:  # Show first 5 jobs
            print(f"- {job['title']} at {job['company']} in {job['location']}")
        
        # Save to database
        finder.save_jobs_to_database(jobs, "PLSQL Developer")
        
    finally:
        finder.close()


if __name__ == "__main__":
    main() 