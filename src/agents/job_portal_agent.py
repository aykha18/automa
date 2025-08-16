"""
Job Portal Agent - Handles daily updates to job portals
"""

import time
import random
import logging
from datetime import datetime
from typing import Dict, List, Any

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
        # Disable WebDriver for now to avoid Chrome driver issues
        self.driver = None
        self.logger.info("WebDriver disabled - using mock mode for job portal automation")
        return
    
    def login_to_portal(self, portal_name: str, credentials: Dict[str, str]) -> bool:
        """Login to a job portal (mock mode)"""
        self.logger.info(f"Mock: Successfully logged into {portal_name}")
        return True
    
    def update_profile_field(self, portal_name: str, field_name: str, value: Any) -> bool:
        """Update a specific profile field (mock mode)"""
        self.logger.info(f"Mock: Updated {field_name} on {portal_name} with value: {value}")
        return True
    
    def perform_random_activity(self, portal_name: str) -> bool:
        """Perform a random activity to show active engagement (mock mode)"""
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
                self.logger.info(f"Mock: Performed random activity on {portal_name}")
                return True
            else:
                self.logger.warning(f"Mock: Failed to perform activity on {portal_name}")
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
        self.logger.info("Starting daily job portal updates (mock mode)")
        
        for portal_name, portal_config in self.job_portals.items():
            try:
                self.logger.info(f"Processing {portal_name} (mock mode)")
                
                # Mock successful update
                activities_performed = random.randint(1, 3)
                self.logger.info(f"Mock: Performed {activities_performed} activities on {portal_name}")
                
                # Log the activity
                try:
                    db.add_scheduled_task(
                        task_name=f"daily_update_{portal_name}",
                        task_type="job_portal_update",
                        schedule_time=datetime.now().strftime("%H:%M"),
                        config={"portal": portal_name, "activities_performed": activities_performed, "mode": "mock"}
                    )
                except Exception as db_error:
                    self.logger.warning(f"Could not save to database: {db_error}")
                
                self.logger.info(f"Completed mock updates for {portal_name}")
                
            except Exception as e:
                self.logger.error(f"Error processing {portal_name}: {e}")
                continue
        
        self.logger.info("Completed daily job portal updates (mock mode)")
    
    def close(self):
        """Close the agent (mock mode)"""
        self.logger.info("Mock: JobPortalAgent closed")
    
    def reinitialize_driver(self):
        """Reinitialize the driver (mock mode)"""
        self.logger.info("Mock: Driver reinitialized")
        return True

    def test_portal_connection(self, portal_name: str) -> Dict[str, Any]:
        """Test connection to a specific job portal"""
        result = {
            "portal": portal_name,
            "status": "mock",
            "message": "WebDriver disabled - using mock mode",
            "driver_available": False
        }
        
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
        
        # Mock successful connection test
        result["status"] = "success"
        result["message"] = f"Portal {portal_name} configuration verified (mock mode)"
        
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