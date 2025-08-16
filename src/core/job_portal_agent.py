"""
Job Portal Agent - Handles daily updates to job portals
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
from core.utils import generate_random_profile_update, setup_logging


class JobPortalAgent:
    """Agent for managing job portal updates"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.job_portals = config.get_job_portals()
        self.driver = None
        self.setup_driver()
        # Load credentials from JSON file
        self.load_credentials()
    
    def load_credentials(self):
        """Load job portal credentials from JSON file"""
        try:
            import json
            credentials_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'job_portals.json')
            with open(credentials_path, 'r') as f:
                portal_data = json.load(f)
                
            # Update job portals with credentials
            for portal_name, portal_config in portal_data.items():
                if portal_name in self.job_portals:
                    self.job_portals[portal_name].update(portal_config)
                    
            self.logger.info("Job portal credentials loaded successfully")
        except Exception as e:
            self.logger.warning(f"Could not load job portal credentials: {e}")
    
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
            
            self.logger.info("Chrome WebDriver setup successfully")
            return
            
        except Exception as e:
            self.logger.error(f"Failed to setup Chrome WebDriver: {e}")
            self.logger.error("Please install Chrome browser to enable job portal automation")
            self.driver = None
    
    def login_to_portal(self, portal_name: str, credentials: Dict[str, str]) -> bool:
        """Login to a job portal"""
        if not self.driver:
            return False
        
        portal_config = self.job_portals.get(portal_name, {})
        login_url = portal_config.get('login_url', portal_config.get('url', ''))
        
        try:
            self.driver.get(login_url)
            time.sleep(random.uniform(2, 4))  # Random delay
            
            # Find and fill username field
            username_field = self.driver.find_element(By.NAME, credentials.get('username_field', 'email'))
            username_field.clear()
            username_field.send_keys(credentials.get('username', ''))
            time.sleep(random.uniform(1, 2))
            
            # Find and fill password field
            password_field = self.driver.find_element(By.NAME, credentials.get('password_field', 'password'))
            password_field.clear()
            password_field.send_keys(credentials.get('password', ''))
            time.sleep(random.uniform(1, 2))
            
            # Submit login form
            submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit']")
            submit_button.click()
            
            # Wait for login to complete
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Profile')] | //a[contains(text(), 'Dashboard')]"))
            )
            
            self.logger.info(f"Successfully logged into {portal_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to login to {portal_name}: {e}")
            return False
    
    def update_profile_field(self, portal_name: str, field_name: str, value: Any) -> bool:
        """Update a specific profile field"""
        if not self.driver:
            return False
        
        try:
            # Navigate to profile page
            profile_link = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Profile')] | //a[contains(@href, 'profile')]")
            profile_link.click()
            time.sleep(random.uniform(2, 4))
            
            # Find and update the specific field
            field_selectors = [
                f"//input[@name='{field_name}']",
                f"//textarea[@name='{field_name}']",
                f"//select[@name='{field_name}']",
                f"//div[@data-field='{field_name}']//input",
                f"//div[@data-field='{field_name}']//textarea"
            ]
            
            field_element = None
            for selector in field_selectors:
                try:
                    field_element = self.driver.find_element(By.XPATH, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if field_element:
                field_element.clear()
                field_element.send_keys(str(value))
                time.sleep(random.uniform(1, 2))
                
                # Save changes
                save_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Save')] | //input[@value='Save']")
                save_button.click()
                time.sleep(random.uniform(2, 3))
                
                self.logger.info(f"Updated {field_name} on {portal_name}")
                return True
            else:
                self.logger.warning(f"Could not find field {field_name} on {portal_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to update {field_name} on {portal_name}: {e}")
            return False
    
    def perform_random_activity(self, portal_name: str) -> bool:
        """Perform a random activity to show active engagement"""
        if not self.driver:
            return False
        
        activities = [
            self._update_profile_completion,
            self._add_skill_endorsement,
            self._update_job_preferences,
            self._enhance_profile_visibility,
            self._update_contact_info
        ]
        
        try:
            # Choose a random activity
            activity = random.choice(activities)
            success = activity(portal_name)
            
            if success:
                self.logger.info(f"Performed random activity on {portal_name}")
                return True
            else:
                self.logger.warning(f"Failed to perform activity on {portal_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error performing random activity on {portal_name}: {e}")
            return False
    
    def _update_profile_completion(self, portal_name: str) -> bool:
        """Update profile completion percentage"""
        update_data = generate_random_profile_update()
        return self.update_profile_field(portal_name, "profile_completion", update_data["completion_percentage"])
    
    def _add_skill_endorsement(self, portal_name: str) -> bool:
        """Add a skill endorsement"""
        update_data = generate_random_profile_update()
        return self.update_profile_field(portal_name, "skills", update_data["skill"])
    
    def _update_job_preferences(self, portal_name: str) -> bool:
        """Update job preferences"""
        preferences = ["Full-time", "Remote", "Hybrid", "Contract"]
        return self.update_profile_field(portal_name, "job_preferences", random.choice(preferences))
    
    def _enhance_profile_visibility(self, portal_name: str) -> bool:
        """Enhance profile visibility"""
        return self.update_profile_field(portal_name, "profile_visibility", "Public")
    
    def _update_contact_info(self, portal_name: str) -> bool:
        """Update contact information"""
        return self.update_profile_field(portal_name, "contact_info", "Updated")
    
    def run_daily_updates(self):
        """Run daily updates for all configured job portals"""
        self.logger.info("Starting daily job portal updates")
        
        for portal_name, portal_config in self.job_portals.items():
            try:
                self.logger.info(f"Processing {portal_name}")
                
                # Ensure driver is available
                if not self.driver:
                    if not self.reinitialize_driver():
                        self.logger.error(f"Could not initialize WebDriver for {portal_name}")
                        continue
                
                # Login to portal
                if not self.login_to_portal(portal_name, portal_config):
                    continue
                
                # Perform random activities
                for _ in range(random.randint(1, 3)):  # 1-3 activities per portal
                    self.perform_random_activity(portal_name)
                    time.sleep(random.uniform(3, 6))  # Random delay between activities
                
                # Log the activity
                db.add_scheduled_task(
                    task_name=f"daily_update_{portal_name}",
                    task_type="job_portal_update",
                    schedule_time=datetime.now().strftime("%H:%M"),
                    config={"portal": portal_name, "activities_performed": random.randint(1, 3)}
                )
                
                self.logger.info(f"Completed updates for {portal_name}")
                
            except Exception as e:
                self.logger.error(f"Error processing {portal_name}: {e}")
                # Try to reinitialize driver on error
                self.reinitialize_driver()
                continue
        
        self.logger.info("Completed daily job portal updates")
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def reinitialize_driver(self):
        """Reinitialize the WebDriver if it's not available"""
        try:
            if self.driver:
                try:
                    # Test if driver is still responsive
                    self.driver.current_url
                except:
                    self.logger.info("WebDriver session lost, reinitializing...")
                    self.driver.quit()
                    self.driver = None
            
            if not self.driver:
                self.setup_driver()
                return True
        except Exception as e:
            self.logger.error(f"Failed to reinitialize driver: {e}")
            return False
        return True

    def test_portal_connection(self, portal_name: str) -> Dict[str, Any]:
        """Test connection to a specific job portal"""
        result = {
            "portal": portal_name,
            "status": "unknown",
            "message": "",
            "driver_available": self.driver is not None
        }
        
        # Try to reinitialize driver if not available
        if not self.driver:
            if not self.reinitialize_driver():
                result["status"] = "error"
                result["message"] = "WebDriver not available and could not reinitialize"
                return result
        
        portal_config = self.job_portals.get(portal_name, {})
        if not portal_config:
            result["status"] = "error"
            result["message"] = f"Portal {portal_name} not configured"
            return result
        
        credentials = portal_config.get("credentials", {})
        if not credentials.get("username") or credentials.get("username") == "your-indeed-email@example.com":
            result["status"] = "warning"
            result["message"] = f"Credentials not configured for {portal_name}. Please update src/data/job_portals.json"
            return result
        
        try:
            # Try to access the portal
            login_url = portal_config.get('login_url', portal_config.get('url', ''))
            self.driver.get(login_url)
            time.sleep(2)  # Give time for page to load
            
            # Check if we can find login elements
            try:
                username_field = self.driver.find_element(By.NAME, portal_config.get('username_field', 'email'))
                password_field = self.driver.find_element(By.NAME, portal_config.get('password_field', 'password'))
                
                result["status"] = "success"
                result["message"] = f"Portal {portal_name} is accessible and login form found"
                
            except NoSuchElementException:
                # Try to find login elements with different selectors
                try:
                    # Try by ID
                    username_field = self.driver.find_element(By.ID, "email")
                    password_field = self.driver.find_element(By.ID, "password")
                    result["status"] = "success"
                    result["message"] = f"Portal {portal_name} is accessible and login form found (by ID)"
                except NoSuchElementException:
                    try:
                        # Try by CSS selector
                        username_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='email']")
                        password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                        result["status"] = "success"
                        result["message"] = f"Portal {portal_name} is accessible and login form found (by CSS)"
                    except NoSuchElementException:
                        # Simple check - just verify page loaded
                        current_url = self.driver.current_url
                        page_title = self.driver.title
                        
                        result["status"] = "warning"
                        result["message"] = f"Portal {portal_name} is accessible but login form not found. Current URL: {current_url}, Title: {page_title}"
                
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"Failed to access {portal_name}: {str(e)}"
            # Try to reinitialize driver on error
            self.reinitialize_driver()
        
        return result


def main():
    """Main function to run job portal updates"""
    agent = JobPortalAgent()
    try:
        agent.run_daily_updates()
    finally:
        agent.close()


if __name__ == "__main__":
    main() 