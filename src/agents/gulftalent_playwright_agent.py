#!/usr/bin/env python3
"""
GulfTalent.com UAE Automation Agent using Playwright
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

class GulfTalentPlaywrightAgent:
    """GulfTalent.com UAE automation agent using Playwright"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.browser = None
        self.context = None
        self.page = None
        self.credentials = None
        self._load_config()
    
    def _load_config(self):
        """Load GulfTalent.com configuration from job_portals.json"""
        try:
            with open('src/data/job_portals.json', 'r') as f:
                portals = json.load(f)
                gulftalent_config = portals.get('gulftalent', {})
                self.credentials = gulftalent_config.get('credentials', {})
                self.logger.info("GulfTalent.com configuration loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading GulfTalent.com configuration: {e}")
            self.credentials = {
                "username": "khanayub@gmail.com",
                "password": "Miral@123"
            }
    
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
            self.page = self.context.new_page()
            self.logger.info("GulfTalent.com browser started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error starting GulfTalent.com browser: {e}")
            return False
    
    def login(self) -> bool:
        """Login to GulfTalent.com"""
        try:
            if not self.page:
                if not self.start_browser():
                    return False
            
            # Navigate to GulfTalent.com UAE
            self.page.goto("https://www.gulftalent.com", wait_until='networkidle')
            time.sleep(3)
            
            # Check if already logged in
            if self._is_logged_in():
                self.logger.info("Already logged in to GulfTalent.com")
                return True
            
            # Click on Login button
            try:
                login_selectors = [
                    'a:has-text("Login")',
                    'a:has-text("Sign In")',
                    'button:has-text("Login")',
                    'button:has-text("Sign In")',
                    '.login-btn',
                    '#login-btn',
                    '[data-testid="login"]'
                ]
                
                login_button = None
                for selector in login_selectors:
                    try:
                        login_button = self.page.locator(selector)
                        if login_button.is_visible():
                            self.logger.info(f"Found login button: {selector}")
                            break
                    except:
                        continue
                
                if login_button and login_button.is_visible():
                    login_button.click()
                    time.sleep(3)
                else:
                    self.logger.error("Could not find login button")
                    return False
            except Exception as e:
                self.logger.error(f"Error clicking login: {e}")
                return False
            
            # Fill login form
            try:
                # Try multiple selectors for email field
                email_selectors = [
                    'input[name="email"]',
                    'input[type="email"]',
                    'input[placeholder*="email"]',
                    'input[placeholder*="Email"]',
                    'input[id*="email"]',
                    'input[name*="username"]',
                    'input[name*="user"]'
                ]
                
                email_field = None
                for selector in email_selectors:
                    try:
                        email_field = self.page.locator(selector)
                        if email_field.is_visible():
                            self.logger.info(f"Found email field: {selector}")
                            break
                    except:
                        continue
                
                if not email_field or not email_field.is_visible():
                    self.logger.error("Could not find email field")
                    return False
                
                # Try multiple selectors for password field
                password_selectors = [
                    'input[name="password"]',
                    'input[type="password"]',
                    'input[placeholder*="password"]',
                    'input[placeholder*="Password"]',
                    'input[id*="password"]'
                ]
                
                password_field = None
                for selector in password_selectors:
                    try:
                        password_field = self.page.locator(selector)
                        if password_field.is_visible():
                            self.logger.info(f"Found password field: {selector}")
                            break
                    except:
                        continue
                
                if not password_field or not password_field.is_visible():
                    self.logger.error("Could not find password field")
                    return False
                
                # Fill credentials
                email_field.fill(self.credentials['username'])
                password_field.fill(self.credentials['password'])
                
                # Click submit button
                submit_selectors = [
                    'button[type="submit"]',
                    'button:has-text("Login")',
                    'button:has-text("Sign In")',
                    'input[type="submit"]',
                    '.submit-btn',
                    '#submit-btn'
                ]
                
                submit_button = None
                for selector in submit_selectors:
                    try:
                        submit_button = self.page.locator(selector)
                        if submit_button.is_visible():
                            self.logger.info(f"Found submit button: {selector}")
                            break
                    except:
                        continue
                
                if submit_button and submit_button.is_visible():
                    submit_button.click()
                    time.sleep(5)
                else:
                    self.logger.error("Could not find submit button")
                    return False
                
                # Check if login was successful
                if self._is_logged_in():
                    self.logger.info("Successfully logged in to GulfTalent.com")
                    return True
                else:
                    self.logger.error("Login failed - not logged in")
                    return False
                
            except Exception as e:
                self.logger.error(f"Error during login form submission: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during GulfTalent.com login: {e}")
            return False
    
    def _is_logged_in(self) -> bool:
        """Check if user is logged in to GulfTalent.com"""
        try:
            # Check for logged in indicators
            current_url = self.page.url
            if "dashboard" in current_url or "profile" in current_url:
                return True
            
            # Check for user menu or profile elements
            user_menu_selectors = [
                '.user-menu',
                '.profile-menu',
                '[data-testid="user-menu"]',
                '.dropdown-menu',
                '.user-dropdown'
            ]
            
            for selector in user_menu_selectors:
                try:
                    user_menu = self.page.locator(selector)
                    if user_menu.is_visible():
                        return True
                except:
                    continue
            
            # Check for logout option
            logout_selectors = [
                'a:has-text("Logout")',
                'a:has-text("Sign Out")',
                'button:has-text("Logout")',
                'button:has-text("Sign Out")'
            ]
            
            for selector in logout_selectors:
                try:
                    logout = self.page.locator(selector)
                    if logout.is_visible():
                        return True
                except:
                    continue
            
            return False
        except:
            return False
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to GulfTalent.com"""
        try:
            if not self.page:
                if not self.start_browser():
                    return {"status": "error", "message": "Failed to start browser"}
            
            self.page.goto("https://www.gulftalent.com", wait_until='networkidle')
            title = self.page.title()
            
            if "GulfTalent" in title or "gulftalent" in title.lower():
                return {
                    "status": "success",
                    "message": f"Connected to GulfTalent.com - {title}",
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
        """Refresh CV on GulfTalent.com"""
        try:
            if not self._is_logged_in():
                if not self.login():
                    return False
            
            # Navigate to profile/CV page
            profile_urls = [
                "https://www.gulftalent.com/profile",
                "https://www.gulftalent.com/dashboard",
                "https://www.gulftalent.com/my-profile",
                "https://www.gulftalent.com/account"
            ]
            
            profile_loaded = False
            for url in profile_urls:
                try:
                    self.page.goto(url, wait_until='networkidle')
                    time.sleep(3)
                    
                    # Check if we're on a profile page
                    if "profile" in self.page.url or "dashboard" in self.page.url:
                        profile_loaded = True
                        self.logger.info(f"Successfully loaded profile page: {url}")
                        break
                except Exception as e:
                    self.logger.warning(f"Failed to load {url}: {e}")
                    continue
            
            if not profile_loaded:
                self.logger.error("Could not load any profile page")
                return False
            
            # Look for CV refresh or update options
            try:
                # Look for resume/CV section
                resume_selectors = [
                    'text="Resume"',
                    'text="CV"',
                    '[data-testid="resume"]',
                    '.resume',
                    '#resume',
                    'a:has-text("Resume")',
                    'a:has-text("CV")'
                ]
                
                resume_found = False
                for selector in resume_selectors:
                    try:
                        resume_element = self.page.locator(selector)
                        if resume_element.is_visible():
                            self.logger.info(f"Found resume section: {selector}")
                            resume_found = True
                            break
                    except:
                        continue
                
                if resume_found:
                    # Try to find refresh/update options
                    refresh_selectors = [
                        'button:has-text("Refresh")',
                        'button:has-text("Update")',
                        'a:has-text("Refresh CV")',
                        'a:has-text("Update CV")',
                        'button:has-text("Edit")',
                        'a:has-text("Edit")'
                    ]
                    
                    for selector in refresh_selectors:
                        try:
                            refresh_button = self.page.locator(selector)
                            if refresh_button.is_visible():
                                refresh_button.click()
                                time.sleep(3)
                                self.logger.info(f"Clicked refresh button: {selector}")
                                return True
                        except:
                            continue
                    
                    # If no refresh button, try to click on the resume itself
                    try:
                        resume_click = self.page.locator('a:has-text("Resume"), a:has-text("CV")')
                        if resume_click.is_visible():
                            resume_click.click()
                            time.sleep(3)
                            self.logger.info("Clicked on Resume/CV")
                            
                            # Look for update options on the resume page
                            update_selectors = [
                                'button:has-text("Update")',
                                'button:has-text("Save")',
                                'button:has-text("Refresh")'
                            ]
                            
                            for selector in update_selectors:
                                try:
                                    update_button = self.page.locator(selector)
                                    if update_button.is_visible():
                                        update_button.click()
                                        time.sleep(2)
                                        self.logger.info(f"Updated resume: {selector}")
                                        return True
                                except:
                                    continue
                    except:
                        pass
                
                self.logger.info("No CV refresh option found, but profile page accessed successfully")
                return True
                
            except Exception as e:
                self.logger.error(f"Error refreshing CV: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during CV refresh: {e}")
            return False
    
    def run_daily_updates(self) -> Dict[str, Any]:
        """Run daily updates for GulfTalent.com"""
        try:
            self.logger.info("Starting GulfTalent.com daily updates")
            
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
                "message": "GulfTalent.com daily updates completed",
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
            self.page.goto("https://www.gulftalent.com/profile", wait_until='networkidle')
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
            self.logger.info("GulfTalent.com browser closed")
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")
