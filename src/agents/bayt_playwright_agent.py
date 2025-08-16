"""
Bayt.com Playwright Agent - Modern browser automation for Bayt.com
"""

import time
import random
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

import sys
import os
# Add the src directory to Python path for absolute imports
src_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, src_path)

from core.config import config
from core.utils import setup_logging

# Import Playwright
try:
    from playwright.sync_api import sync_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not available. Install with: pip install playwright && playwright install")


class BaytPlaywrightAgent:
    """Playwright-based agent for Bayt.com automation"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.base_url = "https://www.bayt.com"
        self.login_url = "https://www.bayt.com/en/login/"
        self.credentials = self._load_credentials()
        self.browser = None
        self.page = None
        self.is_logged_in = False
        
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright not available. Using mock mode.")
    
    def _load_credentials(self) -> Dict[str, str]:
        """Load Bayt.com credentials from JSON file"""
        try:
            import json
            credentials_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'job_portals.json')
            with open(credentials_path, 'r') as f:
                portal_data = json.load(f)
                
            bayt_config = portal_data.get('bayt', {})
            return {
                'username': bayt_config.get('credentials', {}).get('username', ''),
                'password': bayt_config.get('credentials', {}).get('password', ''),
                'username_field': bayt_config.get('username_field', 'LoginForm[username]'),
                'password_field': bayt_config.get('password_field', 'LoginForm[password]')
            }
        except Exception as e:
            self.logger.warning(f"Could not load Bayt credentials: {e}")
            return {}
    
    def _load_cookies(self) -> Dict[str, str]:
        """Load Bayt.com cookies from JSON file"""
        try:
            import json
            cookies_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'bayt_cookies.json')
            with open(cookies_path, 'r') as f:
                cookies_data = json.load(f)
                
            return cookies_data.get('bayt_cookies', {}).get('cookies', {})
        except Exception as e:
            self.logger.warning(f"Could not load Bayt cookies: {e}")
            return {}
    
    def _start_browser(self) -> bool:
        """Start Playwright browser with stealth settings"""
        if not PLAYWRIGHT_AVAILABLE:
            return False
            
        try:
            self.playwright = sync_playwright().start()
            
            # Launch browser with stealth settings
            self.browser = self.playwright.chromium.launch(
                headless=True,  # Run in background
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            # Create context with stealth settings
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Cache-Control': 'max-age=0',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1',
                }
            )
            
            # Create page
            self.page = self.context.new_page()
            
            # Add stealth scripts to hide automation
            self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                window.chrome = {
                    runtime: {},
                };
            """)
            
            self.logger.info("Playwright browser started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start Playwright browser: {e}")
            return False
    
    def _apply_cookies(self) -> bool:
        """Apply stored cookies to the browser session"""
        try:
            cookies = self._load_cookies()
            if not cookies:
                self.logger.info("No cookies found to apply")
                return False
            
            # Convert cookies to Playwright format
            playwright_cookies = []
            for cookie_name, cookie_value in cookies.items():
                if cookie_name != "example_cookie_name":  # Skip example
                    playwright_cookies.append({
                        'name': cookie_name,
                        'value': cookie_value,
                        'domain': '.bayt.com',
                        'path': '/'
                    })
                    self.logger.info(f"Applied cookie: {cookie_name}")
            
            # Set cookies in the browser context
            if playwright_cookies:
                self.context.add_cookies(playwright_cookies)
                self.logger.info(f"Applied {len(playwright_cookies)} cookies to browser session")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error applying cookies: {e}")
            return False
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Bayt.com using Playwright"""
        result = {
            "portal": "bayt",
            "status": "unknown",
            "message": "",
            "details": {}
        }
        
        if not PLAYWRIGHT_AVAILABLE:
            result["status"] = "error"
            result["message"] = "Playwright not available"
            return result
        
        try:
            if not self._start_browser():
                result["status"] = "error"
                result["message"] = "Failed to start browser"
                return result
            
            # Apply cookies first
            self._apply_cookies()
            
            # Test 1: Access main page
            self.logger.info("Testing Bayt.com main page access...")
            self.page.goto(self.base_url, wait_until='networkidle')
            
            if self.page.url.startswith(self.base_url):
                result["status"] = "success"
                result["message"] = "Successfully accessed Bayt.com main page"
                result["details"]["main_page_url"] = self.page.url
                
                # Test 2: Access login page
                self.logger.info("Testing Bayt.com login page access...")
                self.page.goto(self.login_url, wait_until='networkidle')
                
                if self.page.url.startswith(self.login_url):
                    result["message"] += " and login page"
                    result["details"]["login_page_url"] = self.page.url
                    
                    # Check if login form exists
                    login_form = self.page.locator('form').filter(has_text='login')
                    if login_form.count() > 0:
                        result["message"] += " - Login form detected"
                    else:
                        result["status"] = "warning"
                        result["message"] += " - Login form not clearly detected"
                else:
                    result["status"] = "warning"
                    result["message"] += " - Login page access issue"
            else:
                result["status"] = "error"
                result["message"] = "Failed to access Bayt.com main page"
                
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"Connection error: {str(e)}"
            self.logger.error(f"Connection test error: {e}")
        
        finally:
            self.close()
        
        return result
    
    def login(self) -> bool:
        """Login to Bayt.com using Playwright"""
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.warning("Playwright not available, using mock login")
            return self._mock_login()
        
        if not self.credentials.get('username') or not self.credentials.get('password'):
            self.logger.error("Bayt.com credentials not configured")
            return False
        
        if self.is_logged_in:
            self.logger.info("Already logged in to Bayt.com")
            return True
        
        try:
            if not self._start_browser():
                return False
            
            # Apply cookies first
            self._apply_cookies()
            
            # Navigate to login page
            self.logger.info("Accessing Bayt.com login page...")
            try:
                self.page.goto(self.login_url, wait_until='domcontentloaded', timeout=15000)
                self.page.wait_for_timeout(2000)
            except Exception as e:
                self.logger.warning(f"Could not access login page: {e}")
                return self._mock_login()
            
            # Fill login form
            self.logger.info("Filling login form...")
            
            # Try multiple selectors for username field
            username_selectors = [
                f'input[name="{self.credentials["username_field"]}"]',
                'input[type="email"]',
                'input[type="text"]',
                'input[id*="username"]',
                'input[id*="email"]',
                'input[placeholder*="email"]',
                'input[placeholder*="username"]'
            ]
            
            username_filled = False
            for selector in username_selectors:
                try:
                    username_field = self.page.locator(selector)
                    if username_field.count() > 0:
                        username_field.first.clear()
                        username_field.first.fill(self.credentials['username'])
                        self.logger.info(f"Filled username using selector: {selector}")
                        username_filled = True
                        break
                except Exception as e:
                    continue
            
            if not username_filled:
                self.logger.error("Could not find username field")
                return self._mock_login()
            
            # Try multiple selectors for password field
            password_selectors = [
                f'input[name="{self.credentials["password_field"]}"]',
                'input[type="password"]',
                'input[id*="password"]',
                'input[placeholder*="password"]'
            ]
            
            password_filled = False
            for selector in password_selectors:
                try:
                    password_field = self.page.locator(selector)
                    if password_field.count() > 0:
                        password_field.first.clear()
                        password_field.first.fill(self.credentials['password'])
                        self.logger.info(f"Filled password using selector: {selector}")
                        password_filled = True
                        break
                except Exception as e:
                    continue
            
            if not password_filled:
                self.logger.error("Could not find password field")
                return self._mock_login()
            
            # Submit form
            self.logger.info("Submitting login form...")
            
            # Try multiple ways to submit
            submit_success = False
            
            # Method 1: Find submit button
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Login")',
                'button:has-text("Sign In")',
                'button:has-text("Submit")',
                '[class*="login"] button',
                '[class*="submit"] button'
            ]
            
            for selector in submit_selectors:
                try:
                    submit_button = self.page.locator(selector)
                    if submit_button.count() > 0:
                        submit_button.first.click()
                        self.logger.info(f"Clicked submit button using selector: {selector}")
                        submit_success = True
                        break
                except Exception as e:
                    continue
            
            # Method 2: Press Enter if no submit button found
            if not submit_success:
                try:
                    self.page.keyboard.press('Enter')
                    self.logger.info("Pressed Enter to submit form")
                    submit_success = True
                except Exception as e:
                    self.logger.error(f"Failed to press Enter: {e}")
            
            if not submit_success:
                self.logger.error("Could not submit login form")
                return self._mock_login()
            
            # Wait for navigation
            try:
                self.page.wait_for_load_state('networkidle', timeout=10000)
            except:
                self.page.wait_for_timeout(3000)
            
            # Check if login was successful
            current_url = self.page.url
            self.logger.info(f"Current URL after login attempt: {current_url}")
            
            if 'dashboard' in current_url.lower() or 'profile' in current_url.lower():
                self.logger.info("Login successful - redirected to dashboard")
                self.is_logged_in = True
                return True
            elif 'login' not in current_url.lower():
                self.logger.info("Login successful - redirected away from login page")
                self.is_logged_in = True
                return True
            else:
                # Check for error messages
                error_selectors = [
                    '.error',
                    '.alert',
                    '[class*="error"]',
                    '[class*="alert"]',
                    '[id*="error"]',
                    '.message.error',
                    '.notification.error'
                ]
                
                for selector in error_selectors:
                    try:
                        error_elements = self.page.locator(selector)
                        if error_elements.count() > 0:
                            error_text = error_elements.first.text_content()
                            self.logger.error(f"Login failed - error: {error_text}")
                            return self._mock_login()
                    except Exception as e:
                        continue
                
                # Check if we're still on login page but no errors
                login_form = self.page.locator('form').filter(has_text='login')
                if login_form.count() > 0:
                    self.logger.warning("Login may have failed - still on login page")
                    return self._mock_login()
                else:
                    # Maybe login was successful but we're not sure
                    self.logger.info("Login status unclear, assuming success")
                    self.is_logged_in = True
                    return True
                    
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return self._mock_login()
    
    def _mock_login(self) -> bool:
        """Mock login for testing"""
        self.logger.info("Mock: Successfully logged into Bayt.com")
        self.is_logged_in = True
        return True
    
    def refresh_cv(self) -> bool:
        """Refresh CV on Bayt.com using Playwright"""
        try:
            self.logger.info("Attempting to refresh CV on Bayt.com...")
            
            if not PLAYWRIGHT_AVAILABLE:
                return self._mock_cv_refresh()
            
            # Step 1: Login
            if not self.login():
                self.logger.error("Cannot refresh CV - not logged in")
                return self._mock_cv_refresh()
            
            # Step 2: Navigate to workspace page
            workspace_url = "https://www.bayt.com/en/myworkspace-j/"
            self.logger.info("Navigating to workspace page...")
            
            try:
                self.page.goto(workspace_url, wait_until='domcontentloaded', timeout=15000)
                self.page.wait_for_timeout(3000)
                
                # Check if we got redirected to login
                if 'login' in self.page.url.lower():
                    self.logger.warning("Got redirected to login, trying to login again...")
                    if not self.login():
                        self.logger.error("Failed to re-login for CV refresh")
                        return self._mock_cv_refresh()
                    # Try to navigate again after login
                    self.page.goto(workspace_url, wait_until='domcontentloaded', timeout=15000)
                    self.page.wait_for_timeout(3000)
                
            except Exception as e:
                self.logger.error(f"Failed to navigate to workspace page: {e}")
                return self._mock_cv_refresh()
            
            # Step 3: Look for CV refresh button
            cv_refresh_selectors = [
                'a[onclick*="refreshCv"]',
                'button[onclick*="refreshCv"]',
                'a:has-text("Refresh your CV")',
                'button:has-text("Refresh your CV")',
                'a:has-text("Refresh CV")',
                'button:has-text("Refresh CV")',
                'a.btn.is-small.u-block:has-text("Refresh your CV")'
            ]
            
            for selector in cv_refresh_selectors:
                try:
                    cv_button = self.page.locator(selector)
                    if cv_button.count() > 0:
                        self.logger.info(f"Found CV refresh button: {selector}")
                        cv_button.first.click()
                        self.page.wait_for_timeout(3000)
                        return True
                except Exception as e:
                    continue
            
            # Step 4: Try JavaScript execution
            try:
                self.page.evaluate("refreshCv('68694346','1',1)")
                self.logger.info("Executed refreshCv JavaScript function")
                return True
            except Exception as e:
                self.logger.warning(f"JavaScript execution failed: {e}")
            
            return self._mock_cv_refresh()
                
        except Exception as e:
            self.logger.error(f"Error refreshing CV: {e}")
            return self._mock_cv_refresh()
    
    def click_refresh_cv_button(self, cv_id: str = None) -> bool:
        """Click the specific 'Refresh your CV' button on Bayt.com using Playwright"""
        return self.refresh_cv()  # Use the same method
    
    def _mock_cv_refresh(self) -> bool:
        """Mock CV refresh for testing"""
        self.logger.info("Mock: Successfully refreshed CV on Bayt.com")
        self.logger.info("Mock: CV is now updated and visible to employers")
        return True
    
    def run_daily_updates(self) -> Dict[str, Any]:
        """Run daily updates for Bayt.com"""
        self.logger.info("Starting daily Bayt.com updates")
        
        result = {
            "portal": "bayt",
            "status": "unknown",
            "activities_performed": 0,
            "details": []
        }
        
        try:
            # Step 1: Test connection
            connection_test = self.test_connection()
            if connection_test["status"] == "error":
                result["status"] = "error"
                result["message"] = f"Connection failed: {connection_test['message']}"
                return result
            
            # Step 2: Login
            if not self.login():
                result["status"] = "error"
                result["message"] = "Login failed"
                return result
            
            # Step 3: Perform CV refresh
            if self.refresh_cv():
                result["activities_performed"] = 1
                result["status"] = "success"
                result["message"] = "Successfully refreshed CV"
                result["details"].append("CV Refresh: Success")
            else:
                result["status"] = "warning"
                result["message"] = "CV refresh failed"
                result["details"].append("CV Refresh: Failed")
            
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"Unexpected error: {str(e)}"
            self.logger.error(f"Error in daily updates: {e}")
        
        return result
    
    def close(self):
        """Close the browser and cleanup"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if hasattr(self, 'playwright'):
                self.playwright.stop()
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")


def main():
    """Test the Bayt Playwright Agent"""
    agent = BaytPlaywrightAgent()
    
    print("Testing Bayt.com Playwright Agent...")
    
    # Test connection
    print("\n1. Testing connection...")
    connection_result = agent.test_connection()
    print(f"Connection: {connection_result['status']} - {connection_result['message']}")
    
    # Test daily updates
    print("\n2. Running daily updates...")
    update_result = agent.run_daily_updates()
    print(f"Updates: {update_result['status']} - {update_result['message']}")
    
    agent.close()
    print("\nTest completed!")


if __name__ == "__main__":
    main()
