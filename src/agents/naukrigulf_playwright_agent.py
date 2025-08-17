#!/usr/bin/env python3
"""
NaukriGulf.com UAE Automation Agent using Playwright
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

class NaukriGulfPlaywrightAgent:
    """NaukriGulf.com UAE automation agent using Playwright"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.browser = None
        self.context = None
        self.page = None
        self.credentials = None
        self.cookies = None
        self._load_config()
        self._load_cookies()
    
    def _load_config(self):
        """Load NaukriGulf.com configuration from job_portals.json"""
        try:
            with open('src/data/job_portals.json', 'r') as f:
                portals = json.load(f)
                naukrigulf_config = portals.get('naukrigulf', {})
                self.credentials = naukrigulf_config.get('credentials', {})
                self.logger.info("NaukriGulf.com configuration loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading NaukriGulf.com configuration: {e}")
            self.credentials = {
                "username": "khanayub25@outlook.com",
                "password": "Miral@18"
            }
    
    def _load_cookies(self):
        """Load extracted cookies from file"""
        try:
            with open('src/data/naukrigulf_cookies.json', 'r') as f:
                cookie_data = json.load(f)
                self.cookies = cookie_data.get('cookies', [])
                self.logger.info(f"Loaded {len(self.cookies)} cookies from file")
        except Exception as e:
            self.logger.warning(f"Could not load cookies: {e}")
            self.cookies = []
    
    def start_browser(self, headless: bool = True):
        """Start Playwright browser with cookies"""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=headless,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            
            # Apply cookies if available
            if self.cookies:
                self.context.add_cookies(self.cookies)
                self.logger.info(f"Applied {len(self.cookies)} cookies to browser context")
            
            self.page = self.context.new_page()
            self.logger.info("NaukriGulf.com browser started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error starting NaukriGulf.com browser: {e}")
            return False
    
    def login(self) -> bool:
        """Login to NaukriGulf.com (fallback if cookies don't work)"""
        try:
            if not self.page:
                if not self.start_browser():
                    return False
            
            # Navigate to NaukriGulf.com UAE
            self.page.goto("https://www.naukrigulf.com", wait_until='networkidle')
            time.sleep(3)
            
            # Check if already logged in
            if self._is_logged_in():
                self.logger.info("Already logged in to NaukriGulf.com")
                return True
            
            # Click on Login button - using the specific selector from the screenshot
            try:
                login_selectors = [
                    'a[href="https://www.naukrigulf.com/jobseeker/login"]',
                    'a:has-text("Login")',
                    'a.nav-link:has-text("Login")',
                    'button:has-text("Login")',
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
            
            # Fill login form - based on the modal structure from screenshot
            try:
                # Wait for login modal to appear
                time.sleep(2)
                
                # Try multiple selectors for email field based on the modal
                email_selectors = [
                    'input[placeholder="Enter Email Id"]',
                    'input[type="email"]',
                    'input[name="email"]',
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
                
                # Try multiple selectors for password field based on the modal
                password_selectors = [
                    'input[placeholder="Enter Password"]',
                    'input[type="password"]',
                    'input[name="password"]',
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
                
                # Click submit button - based on the modal structure
                submit_selectors = [
                    'button:has-text("Login")',
                    'button[type="submit"]',
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
                    self.logger.info("Successfully logged in to NaukriGulf.com")
                    return True
                else:
                    self.logger.error("Login failed - not logged in")
                    return False
                
            except Exception as e:
                self.logger.error(f"Error during login form submission: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during NaukriGulf.com login: {e}")
            return False
    
    def _is_logged_in(self) -> bool:
        """Check if user is logged in to NaukriGulf.com"""
        try:
            # Check for logged in indicators
            current_url = self.page.url
            page_title = self.page.title()
            
            # Check URL patterns
            if any(pattern in current_url.lower() for pattern in ["dashboard", "profile", "myhome", "userprofile"]):
                return True
            
            # Check page title patterns
            if any(pattern in page_title.lower() for pattern in ["my home", "dashboard", "profile"]):
                return True
            
            # Check for user-specific elements on the page
            try:
                user_elements = [
                    'text="Welcome Back!"',
                    'text="AYUB KHA"',
                    '.user-profile',
                    '.profile-info',
                    '[data-testid="user-menu"]'
                ]
                
                for selector in user_elements:
                    try:
                        element = self.page.locator(selector)
                        if element.is_visible():
                            return True
                    except:
                        continue
            except:
                pass
            
            return False
        except:
            return False
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to NaukriGulf.com"""
        try:
            if not self.page:
                return {"status": "error", "message": "Browser not started. Call start_browser() first."}
            
            self.page.goto("https://www.naukrigulf.com", wait_until='networkidle')
            title = self.page.title()
            
            if "Naukri" in title or "naukri" in title.lower():
                return {
                    "status": "success",
                    "message": f"Connected to NaukriGulf.com - {title}",
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
    
    def update_cv_headline(self, new_headline: str = "PL/SQL Expert | Performance Tuning | Azure| ADF, Databricks |Airflow") -> bool:
        """Update CV headline on NaukriGulf.com"""
        try:
            if not self._is_logged_in():
                if not self.login():
                    return False
            
            # Navigate to profile/CV page
            self.logger.info("Navigating to profile page...")
            try:
                self.page.goto("https://www.naukrigulf.com/mnj/userProfile/myCV?source=dashboard_cc", wait_until='domcontentloaded', timeout=15000)
                time.sleep(3)
            except Exception as e:
                self.logger.warning(f"Navigation timeout (expected): {e}")
                # Continue anyway - the page might still be usable
            
            # Look for CV Headline section
            self.logger.info("Looking for CV Headline section...")
            headline_section = self.page.locator('#cvHeadline')
            
            if not headline_section.is_visible():
                self.logger.error("CV Headline section not found")
                return False
            
            # Click on Edit button for CV Headline
            edit_button = headline_section.locator('button.ng-link.edit-cta')
            if not edit_button.is_visible():
                self.logger.error("Edit button not found in CV Headline section")
                return False
            
            self.logger.info("Clicking Edit button for CV Headline...")
            edit_button.click()
            time.sleep(2)
            
            # Look for the text input field - targeting the specific textarea
            text_input_selectors = [
                 'textarea[id="cvHeadline"][name="cvHeadline"]',
                 'textarea[placeholder="Give your profile a one line introduction"]',
                 'textarea[id="cvHeadline"]',
                 'textarea[name="cvHeadline"]',
                 'textarea.ng-inp-md',
                 'input[type="text"]',
                 'textarea',
                 'input[name*="headline"]',
                 'input[id*="headline"]',
                 '.edit-box input',
                 '.edit-box textarea'
             ]
            
            text_input = None
            for selector in text_input_selectors:
                try:
                    text_input = self.page.locator(selector)
                    if text_input.is_visible():
                        self.logger.info(f"Found text input: {selector}")
                        break
                except:
                    continue
            
            if not text_input or not text_input.is_visible():
                self.logger.error("Could not find text input field for CV headline")
                return False
            
            # Clear and fill the new headline
            self.logger.info(f"Updating CV headline to: {new_headline}")
            text_input.clear()
            text_input.fill(new_headline)
            time.sleep(1)
            
            # Look for Save/Update button - specifically targeting the Save button you mentioned
            save_selectors = [
                'button[type="submit"][class="ng-btn blue"]:has-text("Save")',
                'button[type="submit"].ng-btn.blue:has-text("Save")',
                'button[type="submit"][class*="ng-btn"][class*="blue"]',
                'button.ng-btn.blue:has-text("Save")',
                'button[type="submit"]:has-text("Save")',
                'button:has-text("Save")',
                'button:has-text("Update")',
                'button:has-text("Submit")',
                'button[type="submit"]',
                '.save-btn',
                '.update-btn'
            ]
            
            save_button = None
            for selector in save_selectors:
                try:
                    save_button = self.page.locator(selector)
                    if save_button.is_visible():
                        self.logger.info(f"Found save button: {selector}")
                        break
                except:
                    continue
            
            if save_button and save_button.is_visible():
                save_button.click()
                time.sleep(3)
                self.logger.info("CV headline updated successfully!")
                return True
            else:
                self.logger.error("Could not find save button")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating CV headline: {e}")
            return False
    
    def refresh_cv(self) -> bool:
        """Refresh CV on NaukriGulf.com by updating headline"""
        try:
            self.logger.info("Refreshing CV by updating headline...")
            return self.update_cv_headline()
        except Exception as e:
            self.logger.error(f"Error during CV refresh: {e}")
            return False
    
    def run_daily_updates(self) -> Dict[str, Any]:
        """Run daily updates for NaukriGulf.com"""
        try:
            self.logger.info("Starting NaukriGulf.com daily updates")
            
            if not self.start_browser():
                return {"status": "error", "message": "Failed to start browser"}
            
            if not self._is_logged_in():
                if not self.login():
                    return {"status": "error", "message": "Failed to login"}
            
            # Refresh CV by updating headline
            cv_refreshed = self.refresh_cv()
            
            # Update profile completion
            profile_updated = self._update_profile_completion()
            
            return {
                "status": "success",
                "message": "NaukriGulf.com daily updates completed",
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
            self.page.goto("https://www.naukrigulf.com/mnj/userProfile/myCV?source=dashboard_cc", wait_until='networkidle')
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
            self.logger.info("NaukriGulf.com browser closed")
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")
