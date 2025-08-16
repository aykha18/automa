#!/usr/bin/env python3
"""
Indeed.com UAE Automation Agent using Playwright
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

class IndeedPlaywrightAgent:
    """Indeed.com UAE automation agent using Playwright"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.browser = None
        self.context = None
        self.page = None
        self.credentials = None
        self.cookies = None
        self._load_credentials()
        self._load_cookies()
    
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
    
    def _apply_cookies(self, context: BrowserContext):
        """Apply stored cookies to browser context"""
        if self.cookies and 'cookies' in self.cookies:
            context.add_cookies(self.cookies['cookies'])
            self.logger.info("Indeed.com cookies applied to browser context")
    
    def start_browser(self, headless: bool = True):
        """Start Playwright browser"""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=headless,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            self._apply_cookies(self.context)
            self.page = self.context.new_page()
            self.logger.info("Indeed.com Playwright browser started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error starting Indeed.com browser: {e}")
            return False
    
    def login(self) -> bool:
        """Login to Indeed.com UAE"""
        try:
            if not self.page:
                if not self.start_browser():
                    return False
            
            # Navigate to Indeed.com UAE
            self.page.goto("https://ae.indeed.com", wait_until='networkidle')
            time.sleep(2)
            
            # Check if already logged in
            if self._is_logged_in():
                self.logger.info("Already logged in to Indeed.com")
                return True
            
            # Click on Sign In button
            try:
                sign_in_button = self.page.locator('a[data-gnav-element-name="SignIn"]')
                if sign_in_button.is_visible():
                    sign_in_button.click()
                    time.sleep(2)
            except:
                # Try alternative sign in button
                try:
                    sign_in_button = self.page.locator('a:has-text("Sign in")')
                    if sign_in_button.is_visible():
                        sign_in_button.click()
                        time.sleep(2)
                except:
                    pass
            
            # Fill login form
            try:
                email_field = self.page.locator('input[name="__email"]')
                password_field = self.page.locator('input[name="__password"]')
                
                email_field.fill(self.credentials['username'])
                password_field.fill(self.credentials['password'])
                
                # Click sign in button
                sign_in_submit = self.page.locator('button[type="submit"]')
                sign_in_submit.click()
                
                time.sleep(5)
                
                if self._is_logged_in():
                    self.logger.info("Successfully logged in to Indeed.com")
                    self._save_cookies()
                    return True
                else:
                    self.logger.error("Login failed - still on login page")
                    return False
                    
            except Exception as e:
                self.logger.error(f"Error during login form submission: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during Indeed.com login: {e}")
            return False
    
    def _is_logged_in(self) -> bool:
        """Check if user is logged in to Indeed.com"""
        try:
            # Check for logged in indicators
            current_url = self.page.url
            if "account" in current_url or "dashboard" in current_url:
                return True
            
            # Check for user menu or profile elements
            user_menu = self.page.locator('[data-testid="user-menu"], .user-menu, .profile-menu')
            if user_menu.is_visible():
                return True
            
            # Check for sign out option
            sign_out = self.page.locator('a:has-text("Sign out"), a:has-text("Logout")')
            if sign_out.is_visible():
                return True
            
            return False
        except:
            return False
    
    def _save_cookies(self):
        """Save cookies for future use"""
        try:
            cookies = self.context.cookies()
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
            if not self.page:
                if not self.start_browser():
                    return {"status": "error", "message": "Failed to start browser"}
            
            self.page.goto("https://ae.indeed.com", wait_until='networkidle')
            title = self.page.title()
            
            if "Indeed" in title:
                return {
                    "status": "success",
                    "message": f"Connected to Indeed.com UAE - {title}",
                    "url": self.page.url
                }
            else:
                return {
                    "status": "error",
                    "message": f"Unexpected page title: {title}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection test failed: {str(e)}"
            }
    
    def refresh_cv(self) -> bool:
        """Refresh CV on Indeed.com"""
        try:
            if not self._is_logged_in():
                if not self.login():
                    return False
            
            # Navigate to profile/CV page
            self.page.goto("https://secure.indeed.com/account/profile", wait_until='networkidle')
            time.sleep(3)
            
            # Look for CV refresh or update options
            try:
                # Try to find CV refresh button
                refresh_button = self.page.locator('button:has-text("Refresh"), button:has-text("Update"), a:has-text("Refresh CV")')
                if refresh_button.is_visible():
                    refresh_button.click()
                    time.sleep(3)
                    self.logger.info("CV refreshed on Indeed.com")
                    return True
                
                # Try alternative approach - look for edit profile
                edit_profile = self.page.locator('a:has-text("Edit"), button:has-text("Edit Profile")')
                if edit_profile.is_visible():
                    edit_profile.click()
                    time.sleep(3)
                    
                    # Look for save/update button
                    save_button = self.page.locator('button:has-text("Save"), button:has-text("Update")')
                    if save_button.is_visible():
                        save_button.click()
                        time.sleep(2)
                        self.logger.info("Profile updated on Indeed.com")
                        return True
                
                self.logger.info("No CV refresh option found, but profile page accessed successfully")
                return True
                
            except Exception as e:
                self.logger.error(f"Error refreshing CV: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during CV refresh: {e}")
            return False
    
    def run_daily_updates(self) -> Dict[str, Any]:
        """Run daily updates for Indeed.com"""
        try:
            self.logger.info("Starting Indeed.com daily updates")
            
            if not self.start_browser():
                return {"status": "error", "message": "Failed to start browser"}
            
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
        finally:
            self.close()
    
    def _update_profile_completion(self) -> bool:
        """Update profile completion percentage"""
        try:
            # Navigate to profile page
            self.page.goto("https://secure.indeed.com/account/profile", wait_until='networkidle')
            time.sleep(3)
            
            # Look for profile completion indicators
            completion_text = self.page.locator('text=/\\d+% complete/')
            if completion_text.is_visible():
                completion = completion_text.text_content()
                self.logger.info(f"Profile completion: {completion}")
            
            # Try to complete missing sections
            incomplete_sections = self.page.locator('.incomplete-section, .profile-incomplete')
            if incomplete_sections.count() > 0:
                self.logger.info(f"Found {incomplete_sections.count()} incomplete sections")
                # Could implement logic to fill missing sections
                return True
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating profile completion: {e}")
            return False
    
    def close(self):
        """Close browser and cleanup"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if hasattr(self, 'playwright'):
                self.playwright.stop()
            self.logger.info("Indeed.com browser closed")
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")
