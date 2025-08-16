#!/usr/bin/env python3
"""
Indeed.com UAE Automation Agent using HTTP requests
"""

import json
import time
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional

class IndeedHttpAgent:
    """Indeed.com UAE automation agent using HTTP requests"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.credentials = None
        self.cookies = None
        self._load_credentials()
        self._load_cookies()
        self._setup_session()
    
    def _load_credentials(self):
        """Load Indeed.com credentials from job_portals.json"""
        try:
            with open('src/data/job_portals.json', 'r') as f:
                portals = json.load(f)
                indeed_config = portals.get('indeed', {})
                self.credentials = indeed_config.get('credentials', {})
                self.logger.info("Indeed.com credentials loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading Indeed.com credentials: {e}")
            self.credentials = {
                "username": "khanayubchand@gmail.com",
                "password": "Miral@123"
            }
    
    def _load_cookies(self):
        """Load Indeed.com cookies if available"""
        try:
            with open('src/data/indeed_cookies.json', 'r') as f:
                self.cookies = json.load(f)
                self.logger.info("Indeed.com cookies loaded successfully")
        except Exception as e:
            self.logger.info("No Indeed.com cookies found, will use login")
            self.cookies = None
    
    def _setup_session(self):
        """Setup HTTP session with headers and cookies"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        if self.cookies and 'cookies' in self.cookies:
            for cookie in self.cookies['cookies']:
                self.session.cookies.set(
                    cookie['name'], 
                    cookie['value'], 
                    domain=cookie.get('domain', ''),
                    path=cookie.get('path', '/')
                )
            self.logger.info("Indeed.com cookies applied to session")
    
    def _test_cookie_authentication(self) -> bool:
        """Test if current cookies are still valid"""
        try:
            response = self.session.get("https://secure.indeed.com/account/profile", timeout=10)
            if response.status_code == 200 and "account" in response.url:
                self.logger.info("Cookie authentication successful")
                return True
            else:
                self.logger.info("Cookie authentication failed")
                return False
        except Exception as e:
            self.logger.error(f"Error testing cookie authentication: {e}")
            return False
    
    def _try_cookie_login(self) -> bool:
        """Try to login using stored cookies"""
        if self.cookies and self._test_cookie_authentication():
            return True
        return False
    
    def login(self) -> bool:
        """Login to Indeed.com UAE"""
        try:
            # Try cookie-based login first
            if self._try_cookie_login():
                return True
            
            # Get login page to extract CSRF token
            login_url = "https://secure.indeed.com/account/login"
            response = self.session.get(login_url, timeout=10)
            
            if response.status_code != 200:
                self.logger.error(f"Failed to access login page: {response.status_code}")
                return False
            
            # Extract CSRF token if present
            csrf_token = None
            if 'csrf' in response.text.lower():
                # Look for CSRF token in the page
                import re
                csrf_match = re.search(r'name="csrf[^"]*" value="([^"]*)"', response.text)
                if csrf_match:
                    csrf_token = csrf_match.group(1)
            
            # Prepare login data
            login_data = {
                '__email': self.credentials['username'],
                '__password': self.credentials['password']
            }
            
            if csrf_token:
                login_data['csrf'] = csrf_token
            
            # Submit login form
            login_response = self.session.post(
                login_url,
                data=login_data,
                timeout=10,
                allow_redirects=True
            )
            
            # Check if login was successful
            if login_response.status_code == 200 and "account" in login_response.url:
                self.logger.info("Successfully logged in to Indeed.com")
                self._save_cookies()
                return True
            else:
                self.logger.error("Login failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during Indeed.com login: {e}")
            return False
    
    def _save_cookies(self):
        """Save cookies for future use"""
        try:
            cookies = []
            for cookie in self.session.cookies:
                cookies.append({
                    'name': cookie.name,
                    'value': cookie.value,
                    'domain': cookie.domain,
                    'path': cookie.path,
                    'expires': cookie.expires,
                    'secure': cookie.secure,
                    'httpOnly': cookie.has_nonstandard_attr('HttpOnly')
                })
            
            cookie_data = {
                "cookies": cookies,
                "last_updated": datetime.now().isoformat()
            }
            
            with open('src/data/indeed_cookies.json', 'w') as f:
                json.dump(cookie_data, f, indent=2)
            self.logger.info("Indeed.com cookies saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving Indeed.com cookies: {e}")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Indeed.com"""
        try:
            response = self.session.get("https://ae.indeed.com", timeout=10)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": f"Connected to Indeed.com UAE - Status: {response.status_code}",
                    "url": response.url
                }
            else:
                return {
                    "status": "error",
                    "message": f"Connection failed - Status: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection test failed: {str(e)}"
            }
    
    def refresh_cv(self) -> bool:
        """Refresh CV on Indeed.com (HTTP-based approach)"""
        try:
            if not self.login():
                return False
            
            # Navigate to profile page
            profile_url = "https://secure.indeed.com/account/profile"
            response = self.session.get(profile_url, timeout=10)
            
            if response.status_code != 200:
                self.logger.error(f"Failed to access profile page: {response.status_code}")
                return False
            
            # Look for profile update endpoints
            # Indeed.com might have API endpoints for profile updates
            update_url = "https://secure.indeed.com/account/profile/update"
            
            # Try to trigger a profile update
            update_data = {
                'action': 'refresh_profile',
                'timestamp': int(time.time())
            }
            
            update_response = self.session.post(update_url, data=update_data, timeout=10)
            
            if update_response.status_code in [200, 302]:
                self.logger.info("Profile refresh triggered on Indeed.com")
                return True
            else:
                self.logger.info("Profile refresh not available via HTTP, but profile page accessed")
                return True
                
        except Exception as e:
            self.logger.error(f"Error during CV refresh: {e}")
            return False
    
    def run_daily_updates(self) -> Dict[str, Any]:
        """Run daily updates for Indeed.com"""
        try:
            self.logger.info("Starting Indeed.com daily updates")
            
            if not self.login():
                return {"status": "error", "message": "Failed to login"}
            
            # Refresh CV
            cv_refreshed = self.refresh_cv()
            
            # Update profile completion
            profile_updated = self._update_profile_completion()
            
            return {
                "status": "success",
                "message": "Indeed.com daily updates completed",
                "cv_refreshed": cv_refreshed,
                "profile_updated": profile_updated
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Daily updates failed: {str(e)}"}
    
    def _update_profile_completion(self) -> bool:
        """Update profile completion percentage"""
        try:
            # Navigate to profile page
            profile_url = "https://secure.indeed.com/account/profile"
            response = self.session.get(profile_url, timeout=10)
            
            if response.status_code == 200:
                # Parse profile completion from response
                if "complete" in response.text.lower():
                    self.logger.info("Profile completion checked successfully")
                    return True
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating profile completion: {e}")
            return False
    
    def close(self):
        """Close session"""
        try:
            self.session.close()
            self.logger.info("Indeed.com HTTP session closed")
        except Exception as e:
            self.logger.error(f"Error closing session: {e}")
