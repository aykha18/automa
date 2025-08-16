"""
Data Scraper Agent - Scrapes business details from websites and specific cities
"""

import time
import random
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import re
import json

# Import core modules with fallback to mock objects
try:
    from core.config import config
    from core.database import db
    from core.utils import setup_logging, extract_contact_info, validate_url
except ImportError:
    # Mock objects for when core modules are not available
    class MockConfig:
        def get_scraping_config(self):
            return {
                'uae_businesses': {
                    'categories': ['tailor', 'laundry', 'salon'],
                    'sources': ['yellowpages.ae', 'dubizzle.com']
                }
            }
    
    class MockDB:
        def save_businesses(self, businesses):
            pass
    
    class MockUtils:
        @staticmethod
        def setup_logging():
            return logging.getLogger(__name__)
        
        @staticmethod
        def extract_contact_info(text):
            return {'phone': '', 'email': ''}
        
        @staticmethod
        def validate_url(url):
            return True
    
    config = MockConfig()
    db = MockDB()
    setup_logging = MockUtils.setup_logging
    extract_contact_info = MockUtils.extract_contact_info
    validate_url = MockUtils.validate_url


class DataScraper:
    """Agent for scraping business data from websites"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.scraping_config = config.get_scraping_config()
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup WebDriver with anti-detection measures - tries Chrome first, then Edge"""
        
        # Try Chrome first (user has installed Chrome)
        try:
            chrome_options = Options()
            
            # Basic anti-detection measures (removed headless for better compatibility)
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-features=TranslateUI")
            chrome_options.add_argument("--disable-ipc-flooding-protection")
            
            # Random user agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
            chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
            
            # Experimental options
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2
            })
            
            # Use webdriver-manager to automatically download and manage ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Additional anti-detection scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            self.driver.execute_script("Object.defineProperty(navigator, 'platform', {get: () => 'Win32'})")
            
            self.logger.info("Chrome WebDriver setup successfully with webdriver-manager")
            return
            
        except Exception as e:
            self.logger.warning(f"Failed to setup Chrome WebDriver: {e}")
        
        # Fallback to Microsoft Edge
        try:
            from selenium.webdriver.edge.service import Service as EdgeService
            from selenium.webdriver.edge.options import Options as EdgeOptions
            from webdriver_manager.microsoft import EdgeChromiumDriverManager
            
            edge_options = EdgeOptions()
            edge_options.add_argument("--no-sandbox")
            edge_options.add_argument("--disable-dev-shm-usage")
            edge_options.add_argument("--disable-blink-features=AutomationControlled")
            edge_options.add_argument("--disable-web-security")
            edge_options.add_argument("--disable-extensions")
            
            # Random user agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36"
            ]
            edge_options.add_argument(f"--user-agent={random.choice(user_agents)}")
            
            # Experimental options
            edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            edge_options.add_experimental_option('useAutomationExtension', False)
            edge_options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2
            })
            
            service = EdgeService(EdgeChromiumDriverManager().install())
            self.driver = webdriver.Edge(service=service, options=edge_options)
            
            # Additional anti-detection scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            self.driver.execute_script("Object.defineProperty(navigator, 'platform', {get: () => 'Win32'})")
            
            self.logger.info("Microsoft Edge WebDriver setup successfully")
        except Exception as e:
            self.logger.error(f"Failed to setup WebDriver: {e}")
            self.logger.error("Please install Chrome or Edge browser to enable web scraping")
            self.driver = None
    
    def scrape_uae_businesses(self, categories: List[str] = None, 
                            cities: List[str] = None) -> List[Dict[str, Any]]:
        """Scrape business details from UAE using Google Maps as primary source"""
        if categories is None:
            categories = self.scraping_config.get('uae_businesses', {}).get('categories', [])
        
        if cities is None:
            cities = ["Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Umm Al Quwain", "Ras Al Khaimah", "Fujairah"]
        
        # Map frontend categories to search terms
        category_mapping = {
            "🧵 Tailors": "tailor",
            "🧼 Laundry / Dry Cleaners": "laundry",
            "🪒 Salons & Barbers": "salon",
            "📱 Mobile/Repair Shops": "mobile repair",
            "🧯 AC/Electrical Repair": "electrical repair",
            "🧃 Small Cafes/Kiosks": "cafe",
            "👠 Cobbler / Shoe Repair": "cobbler",
            "📚 Tuition / Home Classes": "tuition",
            "📦 Mini Warehouses": "warehouse",
            "🖥️ IT Hardware Shops": "computer shop",
            "🧴 Perfume & Oud Shops": "perfume"
        }
        
        # Convert frontend categories to search terms
        search_categories = []
        for category in categories:
            if category in category_mapping:
                search_categories.append(category_mapping[category])
            else:
                # Use the category as-is if not in mapping
                search_categories.append(category.lower())
        
        all_businesses = []
        
        # Simple approach: Focus on Google Maps first
        try:
            for category in search_categories:
                self.logger.info(f"Scraping {category} businesses in UAE using Google Maps")
                
                for city in cities:
                    try:
                        # Try Google Maps first (primary source)
                        self.logger.info(f"Searching Google Maps for {category} in {city}")
                        google_businesses = self._scrape_google_maps(category, city)
                        
                        if google_businesses:
                            all_businesses.extend(google_businesses)
                            self.logger.info(f"Found {len(google_businesses)} businesses for {category} in {city}")
                        else:
                            self.logger.warning(f"No results found for {category} in {city}")
                        
                        # Random delay between cities to avoid detection
                        time.sleep(random.uniform(3, 6))
                        
                    except Exception as e:
                        self.logger.error(f"Error scraping {category} in {city}: {e}")
                        continue
        except Exception as e:
            self.logger.error(f"Google Maps scraping failed: {e}")
        
        # Return all found businesses (no fallback to mock data)
        if not all_businesses:
            self.logger.warning("No real data found from Google Maps. Real scraping is required.")
            return []
        
        return all_businesses
    
    def _scrape_city_businesses(self, category: str, city: str) -> List[Dict[str, Any]]:
        """Scrape businesses for a specific category and city"""
        businesses = []
        
        # Get sources for UAE businesses
        sources = self.scraping_config.get('uae_businesses', {}).get('sources', [])
        
        for source in sources:
            try:
                if "yellowpages.ae" in source:
                    source_businesses = self._scrape_yellowpages_ae(category, city)
                elif "dubizzle.com" in source:
                    source_businesses = self._scrape_dubizzle(category, city)
                elif "uaebusinessdirectory.com" in source:
                    source_businesses = self._scrape_alternative_sources(category, city)
                elif "gulfbusinessdirectory.com" in source:
                    source_businesses = self._scrape_alternative_sources(category, city)
                else:
                    source_businesses = self._generic_business_scrape(source, category, city)
                
                businesses.extend(source_businesses)
                
                # Random delay between sources
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                self.logger.error(f"Error scraping {source} for {category} in {city}: {e}")
                continue
        
        return businesses
    
    def _scrape_yellowpages_ae(self, category: str, city: str) -> List[Dict[str, Any]]:
        """Scrape businesses from YellowPages.ae with human verification handling"""
        businesses = []
        
        try:
            # Construct search URL - try different URL patterns
            search_urls = [
                f"https://www.yellowpages.ae/search/{category}/{city.lower().replace(' ', '-')}",
                f"https://www.yellowpages.ae/search?q={category}&location={city}",
                f"https://www.yellowpages.ae/search/{category.replace(' ', '-')}/{city.lower().replace(' ', '-')}"
            ]
            
            if self.driver:
                for search_url in search_urls:
                    try:
                        self.driver.get(search_url)
                        time.sleep(random.uniform(3, 6))  # Increased delay
                        
                        # Check for human verification page
                        verification_indicators = [
                            "verify you are human",
                            "captcha",
                            "security check",
                            "robot verification",
                            "human verification",
                            "please verify",
                            "security verification"
                        ]
                        
                        page_text = self.driver.page_source.lower()
                        if any(indicator in page_text for indicator in verification_indicators):
                            self.logger.warning(f"Human verification detected on {search_url}")
                            # Try to wait and see if it auto-resolves
                            time.sleep(10)
                            page_text = self.driver.page_source.lower()
                            if any(indicator in page_text for indicator in verification_indicators):
                                self.logger.error(f"Human verification persists, skipping {search_url}")
                                continue
                        
                        # Try different selectors for business listings
                        business_selectors = [
                            ".business-listing",
                            ".listing-item", 
                            ".company-listing",
                            ".search-result",
                            "[class*='business']",
                            "[class*='listing']",
                            ".result-item",
                            ".company-item",
                            ".business-item"
                        ]
                        
                        business_elements = []
                        for selector in business_selectors:
                            try:
                                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                if elements:
                                    business_elements = elements
                                    self.logger.info(f"Found {len(elements)} business elements with selector: {selector}")
                                    break
                            except Exception as e:
                                self.logger.debug(f"Selector {selector} failed: {e}")
                                continue
                        
                        # If we found elements, extract data
                        if business_elements:
                            for business_element in business_elements[:10]:  # Limit to first 10 to avoid detection
                                try:
                                    business_data = self._extract_yellowpages_business_data(business_element, category, city)
                                    if business_data:
                                        businesses.append(business_data)
                                        # Add random delay between extractions
                                        time.sleep(random.uniform(0.5, 1.5))
                                except Exception as e:
                                    self.logger.warning(f"Error extracting business data: {e}")
                                    continue
                            
                            # If we found businesses, break out of URL loop
                            if businesses:
                                self.logger.info(f"Successfully scraped {len(businesses)} businesses from {search_url}")
                                break
                        else:
                            self.logger.warning(f"No business elements found on {search_url}")
                                
                    except Exception as e:
                        self.logger.warning(f"Error with URL {search_url}: {e}")
                        continue
                        
        except Exception as e:
            self.logger.error(f"Error scraping YellowPages.ae: {e}")
        
        return businesses
    
    def _extract_yellowpages_business_data(self, business_element, category: str, city: str) -> Dict[str, Any]:
        """Extract business data from YellowPages.ae listing"""
        try:
            # Try multiple selectors for business name
            business_name = ""
            name_selectors = [
                ".business-name", ".company-name", ".listing-title", 
                "h1", "h2", "h3", "[class*='name']", "[class*='title']"
            ]
            
            for selector in name_selectors:
                try:
                    name_element = business_element.find_element(By.CSS_SELECTOR, selector)
                    business_name = name_element.text.strip()
                    if business_name:
                        break
                except NoSuchElementException:
                    continue
            
            # Try multiple selectors for phone number
            phone = ""
            phone_selectors = [
                ".phone-number", ".phone", ".tel", "[class*='phone']", 
                "[class*='tel']", "[class*='contact']"
            ]
            
            for selector in phone_selectors:
                try:
                    phone_element = business_element.find_element(By.CSS_SELECTOR, selector)
                    phone = phone_element.text.strip()
                    if phone:
                        break
                except NoSuchElementException:
                    continue
            
            # Try multiple selectors for address
            address = ""
            address_selectors = [
                ".address", ".location", "[class*='address']", 
                "[class*='location']", "[class*='area']"
            ]
            
            for selector in address_selectors:
                try:
                    address_element = business_element.find_element(By.CSS_SELECTOR, selector)
                    address = address_element.text.strip()
                    if address:
                        break
                except NoSuchElementException:
                    continue
            
            # Try to extract website
            website = ""
            website_selectors = [
                ".website a", "a[href*='http']", "[class*='website'] a"
            ]
            
            for selector in website_selectors:
                try:
                    website_element = business_element.find_element(By.CSS_SELECTOR, selector)
                    website = website_element.get_attribute("href")
                    if website:
                        break
                except NoSuchElementException:
                    continue
            
            # Try to extract email
            email = ""
            email_selectors = [
                ".email", "[class*='email']", "a[href^='mailto:']"
            ]
            
            for selector in email_selectors:
                try:
                    email_element = business_element.find_element(By.CSS_SELECTOR, selector)
                    email_text = email_element.text.strip()
                    if email_text and '@' in email_text:
                        email = email_text
                        break
                    elif selector == "a[href^='mailto:']":
                        email = email_element.get_attribute("href").replace("mailto:", "")
                        break
                except NoSuchElementException:
                    continue
            
            # Only return if we have at least a business name
            if business_name:
                return {
                    "business_name": business_name,
                    "category": category,
                    "city": city,
                    "phone": phone or "N/A",
                    "email": email or "N/A",
                    "address": address or "N/A",
                    "website": website or "N/A",
                    "source": "yellowpages.ae",
                    "scraped_date": datetime.now().isoformat()
                }
            
        except Exception as e:
            self.logger.warning(f"Error extracting YellowPages business data: {e}")
        
        return None
    
    def _scrape_dubizzle(self, category: str, city: str) -> List[Dict[str, Any]]:
        """Scrape businesses from Dubizzle"""
        businesses = []
        
        try:
            # Construct search URL
            search_url = f"https://uae.dubizzle.com/businesses/{category}/{city.lower().replace(' ', '-')}"
            
            if self.driver:
                self.driver.get(search_url)
                time.sleep(random.uniform(2, 4))
                
                # Wait for business listings to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "listing-item"))
                )
                
                # Extract business listings
                business_elements = self.driver.find_elements(By.CLASS_NAME, "listing-item")
                
                for business_element in business_elements:
                    try:
                        business_data = self._extract_dubizzle_business_data(business_element, category, city)
                        if business_data:
                            businesses.append(business_data)
                    except Exception as e:
                        self.logger.warning(f"Error extracting business data: {e}")
                        continue
                        
        except Exception as e:
            self.logger.error(f"Error scraping Dubizzle: {e}")
        
        return businesses
    
    def _extract_dubizzle_business_data(self, business_element, category: str, city: str) -> Dict[str, Any]:
        """Extract business data from Dubizzle listing"""
        try:
            # Extract business name
            name_element = business_element.find_element(By.CSS_SELECTOR, ".listing-title")
            business_name = name_element.text.strip()
            
            # Extract description
            desc_element = business_element.find_element(By.CSS_SELECTOR, ".listing-description")
            description = desc_element.text.strip()
            
            # Extract contact info from description
            contact_info = extract_contact_info(description)
            
            return {
                "business_name": business_name,
                "category": category,
                "city": city,
                "phone": contact_info.get("phone", ""),
                "email": contact_info.get("email", ""),
                "website": contact_info.get("website", ""),
                "description": description,
                "source": "dubizzle.com",
                "scraped_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"Error extracting Dubizzle business data: {e}")
            return None
    
    def _scrape_working_sources(self, category: str, city: str) -> List[Dict[str, Any]]:
        """Scrape from working UAE business directories"""
        businesses = []
        
        # Working UAE business directories
        working_sources = [
            f"https://www.yellowpages.ae/search?q={category}&location={city}",
            f"https://www.dubizzle.com/businesses/{category.replace(' ', '-')}/{city.lower().replace(' ', '-')}",
            f"https://www.google.com/maps/search/{category}+{city}+UAE"
        ]
        
        for source_url in working_sources:
            try:
                if self.driver:
                    self.driver.get(source_url)
                    time.sleep(random.uniform(3, 5))
                    
                    # Look for business listings with multiple selectors
                    business_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                        ".business-listing, .company-item, .listing-item, [class*='business'], [class*='company'], .result-item")
                    
                    for element in business_elements[:10]:
                        try:
                            business_data = self._extract_working_source_data(element, category, city, source_url)
                            if business_data:
                                businesses.append(business_data)
                        except Exception as e:
                            self.logger.debug(f"Error extracting working source data: {e}")
                            continue
                            
            except Exception as e:
                self.logger.warning(f"Error scraping working source {source_url}: {e}")
                continue
        
        return businesses
    
    def _extract_working_source_data(self, element, category: str, city: str, source: str) -> Dict[str, Any]:
        """Extract business data from working source element"""
        try:
            business_name = ""
            address = ""
            phone = ""
            website = ""
            
            # Try to extract business name
            try:
                name_selectors = ["h3", "h4", ".business-name", ".company-name", "[class*='name']", ".listing-title"]
                for selector in name_selectors:
                    try:
                        name_element = element.find_element(By.CSS_SELECTOR, selector)
                        business_name = name_element.text.strip()
                        if business_name:
                            break
                    except:
                        continue
            except:
                pass
            
            # Try to extract address
            try:
                address_selectors = [".address", ".location", "[class*='address']", "[class*='location']"]
                for selector in address_selectors:
                    try:
                        address_element = element.find_element(By.CSS_SELECTOR, selector)
                        address = address_element.text.strip()
                        if address:
                            break
                    except:
                        continue
            except:
                pass
            
            # Try to extract phone
            try:
                phone_selectors = [".phone", ".contact", "[class*='phone']", "[class*='contact']"]
                for selector in phone_selectors:
                    try:
                        phone_element = element.find_element(By.CSS_SELECTOR, selector)
                        phone = phone_element.text.strip()
                        if phone:
                            break
                    except:
                        continue
            except:
                pass
            
            if business_name:
                return {
                    "business_name": business_name,
                    "category": category,
                    "city": city,
                    "address": address,
                    "phone": phone,
                    "website": website,
                    "email": "",
                    "source": source,
                    "scraped_date": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.debug(f"Error extracting working source data: {e}")
        
        return None
    
    def _generic_business_scrape(self, source: str, category: str, city: str) -> List[Dict[str, Any]]:
        """Generic business scraping for other sources"""
        businesses = []
        
        try:
            # Use requests for simple sites
            search_url = f"https://{source}/search?q={category}&location={city}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Generic extraction patterns
            business_elements = soup.find_all(['div', 'article'], class_=lambda x: x and 'business' in x.lower())
            
            for business_element in business_elements:
                try:
                    business_data = self._extract_generic_business_data(business_element, source, category, city)
                    if business_data:
                        businesses.append(business_data)
                except Exception as e:
                    self.logger.warning(f"Error extracting generic business data: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error in generic business scraping for {source}: {e}")
        
        return businesses
    
    def _extract_generic_business_data(self, business_element, source: str, category: str, city: str) -> Dict[str, Any]:
        """Extract business data from generic business element"""
        try:
            # Try to find business name
            business_name = ""
            name_selectors = ['h1', 'h2', 'h3', '.business-name', '.company-name', '[class*="name"]']
            for selector in name_selectors:
                name_elem = business_element.find(selector)
                if name_elem:
                    business_name = name_elem.get_text().strip()
                    break
            
            # Try to find contact info
            contact_info = extract_contact_info(business_element.get_text())
            
            # Try to find address
            address = ""
            address_selectors = ['.address', '.location', '[class*="address"]']
            for selector in address_selectors:
                address_elem = business_element.find(selector)
                if address_elem:
                    address = address_elem.get_text().strip()
                    break
            
            if business_name:  # Only return if we found at least a business name
                return {
                    "business_name": business_name,
                    "category": category,
                    "city": city,
                    "phone": contact_info.get("phone", ""),
                    "email": contact_info.get("email", ""),
                    "website": contact_info.get("website", ""),
                    "address": address,
                    "source": source,
                    "scraped_date": datetime.now().isoformat()
                }
            
        except Exception as e:
            self.logger.warning(f"Error extracting generic business data: {e}")
        
        return None
    
    def scrape_custom_websites(self, websites: List[str], categories: List[str] = None) -> List[Dict[str, Any]]:
        """Scrape business data from custom list of websites"""
        all_businesses = []
        
        for website in websites:
            try:
                if not validate_url(website):
                    self.logger.warning(f"Invalid URL: {website}")
                    continue
                
                website_businesses = self._scrape_single_website(website, categories)
                all_businesses.extend(website_businesses)
                
                # Random delay between websites
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                self.logger.error(f"Error scraping {website}: {e}")
                continue
        
        return all_businesses
    
    def _scrape_single_website(self, website: str, categories: List[str] = None) -> List[Dict[str, Any]]:
        """Scrape business data from a single website"""
        businesses = []
        
        try:
            if self.driver:
                self.driver.get(website)
                time.sleep(random.uniform(2, 4))
                
                # Look for business listings
                business_selectors = [
                    ".business-listing", ".company-listing", ".listing-item",
                    ".business-card", ".company-card", "[class*='business']"
                ]
                
                business_elements = []
                for selector in business_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        business_elements.extend(elements)
                    except:
                        continue
                
                for business_element in business_elements:
                    try:
                        business_data = self._extract_website_business_data(business_element, website, categories)
                        if business_data:
                            businesses.append(business_data)
                    except Exception as e:
                        self.logger.warning(f"Error extracting business data: {e}")
                        continue
                        
        except Exception as e:
            self.logger.error(f"Error scraping website {website}: {e}")
        
        return businesses
    
    def _extract_website_business_data(self, business_element, website: str, categories: List[str] = None) -> Dict[str, Any]:
        """Extract business data from website element"""
        try:
            # Extract business name
            business_name = ""
            name_selectors = ['.business-name', '.company-name', 'h1', 'h2', 'h3']
            for selector in name_selectors:
                try:
                    name_elem = business_element.find_element(By.CSS_SELECTOR, selector)
                    business_name = name_elem.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            # Extract contact info
            contact_info = extract_contact_info(business_element.text)
            
            # Determine category
            category = "unknown"
            if categories:
                # Try to match category based on business name or description
                business_text = business_element.text.lower()
                for cat in categories:
                    if cat.lower() in business_text:
                        category = cat
                        break
            
            return {
                "business_name": business_name,
                "category": category,
                "phone": contact_info.get("phone", ""),
                "email": contact_info.get("email", ""),
                "website": contact_info.get("website", ""),
                "source": website,
                "scraped_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"Error extracting website business data: {e}")
            return None
    
    def _scrape_google_maps(self, category: str, city: str) -> List[Dict[str, Any]]:
        """Scrape businesses from Google Maps with enhanced search and extraction"""
        businesses = []
        
        try:
            # Create search query for Google Maps
            search_query = f"{category} in {city}, UAE"
            
            # Try to get data from Google Maps search
            search_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            
            if self.driver:
                try:
                    self.logger.info(f"Searching Google Maps: {search_url}")
                    self.driver.get(search_url)
                    time.sleep(random.uniform(5, 8))  # Longer wait for page load
                    
                    # Wait for page to load and scroll to load more results
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(random.uniform(3, 5))
                    
                    # Try multiple selectors for business listings - updated for current Google Maps structure
                    selectors = [
                        "[data-result-index]",
                        ".section-result",
                        ".section-result-content",
                        "[role='article']",
                        ".fontHeadlineSmall",
                        ".fontBodyMedium",
                        ".DxyBCb",
                        ".hfpxzc",
                        "[jsaction*='mouseover:pane']",
                        ".section-result-title",
                        ".section-result-location"
                    ]
                    
                    business_elements = []
                    for selector in selectors:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if elements and len(elements) > 0:
                                business_elements = elements
                                self.logger.info(f"Found {len(elements)} elements using selector: {selector}")
                                break
                        except Exception as e:
                            self.logger.debug(f"Selector {selector} failed: {e}")
                            continue
                    
                    # If no elements found with specific selectors, try to get all clickable elements
                    if not business_elements:
                        self.logger.info("No specific business elements found, trying general approach")
                        try:
                            # Try to find any clickable elements that might be businesses
                            business_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='maps/place'], [jsaction*='mouseover']")
                            self.logger.info(f"Found {len(business_elements)} potential business elements")
                        except Exception as e:
                            self.logger.warning(f"Failed to find business elements: {e}")
                    
                    # Extract business data from found elements
                    for i, element in enumerate(business_elements[:25]):  # Increased limit
                        try:
                            business_data = self._extract_google_maps_data(element, category, city)
                            if business_data:
                                businesses.append(business_data)
                                self.logger.debug(f"Extracted business {i+1}: {business_data.get('business_name', 'Unknown')}")
                                time.sleep(random.uniform(0.2, 0.5))  # Shorter delay between extractions
                        except Exception as e:
                            self.logger.debug(f"Error extracting Google Maps data for element {i}: {e}")
                            continue
                            
                except Exception as e:
                    self.logger.warning(f"Error scraping Google Maps: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error in Google Maps scraping: {e}")
        
        self.logger.info(f"Extracted {len(businesses)} businesses from Google Maps for {category} in {city}")
        return businesses
    
    def _extract_google_maps_data(self, element, category: str, city: str) -> Dict[str, Any]:
        """Extract business data from Google Maps element with enhanced selectors"""
        try:
            business_name = ""
            address = ""
            phone = ""
            website = ""
            rating = ""
            
            # Try multiple selectors for business name
            name_selectors = [
                "h3", 
                ".fontHeadlineSmall", 
                "[role='heading']",
                ".section-result-title",
                ".fontTitleLarge",
                "[data-tooltip]"
            ]
            
            for selector in name_selectors:
                try:
                    name_element = element.find_element(By.CSS_SELECTOR, selector)
                    business_name = name_element.text.strip()
                    if business_name:
                        break
                except:
                    continue
            
            # Try multiple selectors for address
            address_selectors = [
                "[data-item-id*='address']", 
                ".fontBodyMedium",
                ".section-result-location",
                "[aria-label*='Address']",
                ".section-result-address"
            ]
            
            for selector in address_selectors:
                try:
                    address_element = element.find_element(By.CSS_SELECTOR, selector)
                    address = address_element.text.strip()
                    if address:
                        break
                except:
                    continue
            
            # Try multiple selectors for phone
            phone_selectors = [
                "[data-item-id*='phone']", 
                ".fontBodyMedium",
                ".section-result-phone",
                "[aria-label*='Phone']"
            ]
            
            for selector in phone_selectors:
                try:
                    phone_element = element.find_element(By.CSS_SELECTOR, selector)
                    phone = phone_element.text.strip()
                    if phone:
                        break
                except:
                    continue
            
            # Try to extract rating
            try:
                rating_element = element.find_element(By.CSS_SELECTOR, "[aria-label*='stars'], .section-result-rating")
                rating = rating_element.get_attribute("aria-label") or rating_element.text.strip()
            except:
                pass
            
            # Only return if we have at least a business name
            if business_name and business_name.lower() not in ['loading', 'error', 'not found']:
                return {
                    "business_name": business_name,
                    "category": category,
                    "city": city,
                    "address": address,
                    "phone": phone,
                    "website": website,
                    "email": "",
                    "rating": rating,
                    "source": "Google Maps",
                    "scraped_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.debug(f"Error extracting Google Maps data: {e}")
        
        return None
    
    def _scrape_dubizzle_businesses(self, category: str, city: str) -> List[Dict[str, Any]]:
        """Scrape businesses from Dubizzle business directory with enhanced anti-detection"""
        businesses = []
        
        try:
            search_url = f"https://uae.dubizzle.com/businesses/{category.replace(' ', '-')}/{city.lower().replace(' ', '-')}"
            
            if self.driver:
                try:
                    # Add random delay before request
                    time.sleep(random.uniform(2, 4))
                    self.driver.get(search_url)
                    time.sleep(random.uniform(3, 6))  # Longer wait
                    
                    # Scroll to load more content
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(random.uniform(1, 2))
                    
                    # Look for business listings with multiple selectors
                    selectors = [
                        ".listing-item", 
                        ".business-item", 
                        ".company-item",
                        "[class*='listing']",
                        "[class*='business']",
                        ".result-item"
                    ]
                    
                    business_elements = []
                    for selector in selectors:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if elements:
                                business_elements = elements
                                self.logger.info(f"Found {len(elements)} Dubizzle elements with selector: {selector}")
                                break
                        except Exception:
                            continue
                    
                    for element in business_elements[:15]:  # Increased limit
                        try:
                            business_data = self._extract_dubizzle_business_data(element, category, city)
                            if business_data:
                                businesses.append(business_data)
                                time.sleep(random.uniform(0.5, 1))
                        except Exception as e:
                            self.logger.debug(f"Error extracting Dubizzle data: {e}")
                            continue
                            
                except Exception as e:
                    self.logger.warning(f"Error scraping Dubizzle: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error in Dubizzle scraping: {e}")
        
        return businesses
    
    def _scrape_alternative_sources(self, category: str, city: str) -> List[Dict[str, Any]]:
        """Scrape from alternative sources that are more likely to work"""
        businesses = []
        
        # Alternative sources that might work better
        alternative_sources = [
            f"https://www.yellowpages.ae/search?q={category}&location={city}",
            f"https://www.dubizzle.com/businesses/{category.replace(' ', '-')}/{city.lower().replace(' ', '-')}",
            f"https://www.google.com/maps/search/{category}+{city}+UAE",
            f"https://www.uaebusinessdirectory.com/search?q={category}&location={city}",
            f"https://www.gulfbusinessdirectory.com/search?category={category}&city={city}"
        ]
        
        for source_url in alternative_sources:
            try:
                if self.driver:
                    self.driver.get(source_url)
                    time.sleep(random.uniform(3, 5))
                    
                    # Look for business listings
                    business_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                        ".business-listing, .company-item, .listing-item, [class*='business'], [class*='company']")
                    
                    for element in business_elements[:10]:
                        try:
                            business_data = self._extract_alternative_source_data(element, category, city, source_url)
                            if business_data:
                                businesses.append(business_data)
                        except Exception as e:
                            self.logger.debug(f"Error extracting alternative source data: {e}")
                            continue
                            
            except Exception as e:
                self.logger.warning(f"Error scraping alternative source {source_url}: {e}")
                continue
        
        return businesses
    
    def _extract_alternative_source_data(self, element, category: str, city: str, source: str) -> Dict[str, Any]:
        """Extract business data from alternative source element"""
        try:
            business_name = ""
            address = ""
            phone = ""
            website = ""
            
            # Try to extract business name
            try:
                name_selectors = ["h3", "h4", ".business-name", ".company-name", "[class*='name']"]
                for selector in name_selectors:
                    try:
                        name_element = element.find_element(By.CSS_SELECTOR, selector)
                        business_name = name_element.text.strip()
                        if business_name:
                            break
                    except:
                        continue
            except:
                pass
            
            # Try to extract address
            try:
                address_selectors = [".address", ".location", "[class*='address']", "[class*='location']"]
                for selector in address_selectors:
                    try:
                        address_element = element.find_element(By.CSS_SELECTOR, selector)
                        address = address_element.text.strip()
                        if address:
                            break
                    except:
                        continue
            except:
                pass
            
            # Try to extract phone
            try:
                phone_selectors = [".phone", ".contact", "[class*='phone']", "[class*='contact']"]
                for selector in phone_selectors:
                    try:
                        phone_element = element.find_element(By.CSS_SELECTOR, selector)
                        phone = phone_element.text.strip()
                        if phone:
                            break
                    except:
                        continue
            except:
                pass
            
            if business_name:
                return {
                    "business_name": business_name,
                    "category": category,
                    "city": city,
                    "address": address,
                    "phone": phone,
                    "website": website,
                    "email": "",
                    "source": source,
                    "scraped_date": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.debug(f"Error extracting alternative source data: {e}")
        
        return None
    
    def save_businesses_to_database(self, businesses: List[Dict[str, Any]]):
        """Save scraped business data to database"""
        for business in businesses:
            try:
                db.add_scraped_data(
                    source_url=business.get('source', ''),
                    business_name=business.get('business_name', ''),
                    category=business.get('category', ''),
                    phone=business.get('phone', ''),
                    email=business.get('email', ''),
                    address=business.get('address', ''),
                    city=business.get('city', ''),
                    country=business.get('country', 'UAE'),
                    data_json=business
                )
            except Exception as e:
                self.logger.error(f"Error saving business to database: {e}")
    
    def get_scraping_statistics(self) -> Dict[str, Any]:
        """Get statistics about scraped data"""
        try:
            # Get recent scraped data
            recent_data = db.get_scraped_data(limit=1000)
            
            categories = {}
            cities = {}
            sources = {}
            
            for data in recent_data:
                category = data.get('category', 'unknown')
                city = data.get('city', 'unknown')
                source = data.get('source_url', 'unknown')
                
                categories[category] = categories.get(category, 0) + 1
                cities[city] = cities.get(city, 0) + 1
                sources[source] = sources.get(source, 0) + 1
            
            return {
                "total_businesses": len(recent_data),
                "categories": categories,
                "cities": cities,
                "sources": sources,
                "last_scraped": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting scraping statistics: {e}")
            return {}
    
    def _generate_realistic_mock_data(self, categories: List[str], cities: List[str]) -> List[Dict[str, Any]]:
        """Generate realistic mock data when real scraping fails"""
        businesses = []
        
        # Business names by category
        business_names = {
            "tailor": ["Al Mansoor Tailors", "Dubai Tailoring", "Perfect Stitch", "Royal Tailors", "Elite Tailoring", "Premium Stitch", "Golden Thread", "Master Tailors", "Fashion House", "Luxury Tailors"],
            "laundry": ["Clean & Fresh Laundry", "Quick Wash", "Premium Laundry", "Express Clean", "Royal Laundry", "Spotless Clean", "Fresh & Clean", "Elite Laundry", "Perfect Wash", "Luxury Laundry"],
            "salon": ["Beauty Palace", "Elite Salon", "Royal Beauty", "Premium Hair", "Luxury Salon", "Perfect Style", "Golden Touch", "Master Cuts", "Fashion Hair", "Elite Beauty"],
            "mobile repair": ["Phone Fix Pro", "Mobile Masters", "Quick Repair", "Tech Solutions", "Phone Doctor", "Mobile Experts", "Repair Pro", "Tech Masters", "Phone Clinic", "Mobile Fix"],
            "electrical repair": ["Power Solutions", "Electrical Masters", "Quick Fix", "Power Pro", "Electrical Experts", "Power Clinic", "Electrical Solutions", "Power Masters", "Electrical Pro", "Power Experts"],
            "cafe": ["Coffee Corner", "Cafe Delight", "Urban Cafe", "Coffee House", "Cafe Express", "Coffee Masters", "Urban Delight", "Cafe Corner", "Coffee Express", "Cafe House"],
            "cobbler": ["Shoe Masters", "Perfect Fit", "Shoe Clinic", "Cobbler Pro", "Shoe Experts", "Perfect Shoes", "Shoe Masters", "Cobbler Clinic", "Shoe Pro", "Perfect Cobbler"],
            "tuition": ["Learning Center", "Study Pro", "Education Hub", "Learning Pro", "Study Center", "Education Pro", "Learning Hub", "Study Masters", "Education Center", "Learning Pro"],
            "warehouse": ["Storage Solutions", "Warehouse Pro", "Storage Masters", "Warehouse Solutions", "Storage Pro", "Warehouse Masters", "Storage Hub", "Warehouse Center", "Storage Pro", "Warehouse Solutions"],
            "computer shop": ["Tech Solutions", "Computer Pro", "Tech Masters", "Computer Solutions", "Tech Pro", "Computer Masters", "Tech Hub", "Computer Center", "Tech Pro", "Computer Solutions"],
            "perfume": ["Perfume Palace", "Fragrance House", "Perfume Masters", "Fragrance Pro", "Perfume House", "Fragrance Masters", "Perfume Pro", "Fragrance Palace", "Perfume Masters", "Fragrance House"]
        }
        
        # UAE cities and areas
        uae_cities = ["Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Umm Al Quwain", "Ras Al Khaimah", "Fujairah", "Al Ain"]
        areas = {
            "Dubai": ["Deira", "Bur Dubai", "Jumeirah", "Sheikh Zayed Road", "Al Barsha", "Al Qusais", "Al Karama", "Al Satwa"],
            "Abu Dhabi": ["Al Zahiyah", "Al Khalidiyah", "Al Bateen", "Al Reem Island", "Yas Island", "Saadiyat Island", "Al Raha"],
            "Sharjah": ["Al Majaz", "Al Qasba", "Al Khan", "Al Nahda", "Al Taawun", "Al Rolla", "Al Qasimiya"],
            "Ajman": ["Al Nuaimiya", "Al Rashidiya", "Al Mowaihat", "Al Hamidiya", "Al Zahra"],
            "Umm Al Quwain": ["Al Raas", "Al Salamah", "Al Khor", "Al Haditha"],
            "Ras Al Khaimah": ["Al Nakheel", "Al Hamra", "Al Marjan Island", "Al Qusaidat"],
            "Fujairah": ["Al Faseel", "Al Aqah", "Al Bithnah", "Al Siji"],
            "Al Ain": ["Al Jimi", "Al Qattara", "Al Hili", "Al Yahar"]
        }
        
        # Phone prefixes
        phone_prefixes = ["50", "51", "52", "54", "55", "56"]
        
        for category in categories:
            # Clean up category name (remove leading/trailing spaces and map to known categories)
            clean_category = category.strip().lower()
            if clean_category == " tailors":
                clean_category = "tailor"
            elif clean_category == " laundry / dry cleaners":
                clean_category = "laundry"
            elif clean_category == " salons & barbers":
                clean_category = "salon"
            elif clean_category == " mobile/repair shops":
                clean_category = "mobile repair"
            elif clean_category == " ac/electrical repair":
                clean_category = "electrical repair"
            elif clean_category == " small cafes/kiosks":
                clean_category = "cafe"
            elif clean_category == " cobbler / shoe repair":
                clean_category = "cobbler"
            elif clean_category == " tuition / home classes":
                clean_category = "tuition"
            elif clean_category == " mini warehouses":
                clean_category = "warehouse"
            elif clean_category == " it hardware shops":
                clean_category = "computer shop"
            elif clean_category == " perfume & oud shops":
                clean_category = "perfume"
            
            category_names = business_names.get(clean_category, [f"{category.title()} Business"])
            num_businesses = random.randint(15, 40)  # 15-40 businesses per category
            
            for i in range(num_businesses):
                business_name = category_names[i % len(category_names)]
                if i >= len(category_names):
                    business_name += f" {i // len(category_names) + 1}"
                
                city = random.choice(uae_cities)
                city_areas = areas.get(city, ["Main Street"])
                area = random.choice(city_areas)
                
                phone_prefix = random.choice(phone_prefixes)
                phone_suffix = random.randint(1000000, 9999999)
                
                business = {
                    "business_name": business_name,
                    "category": clean_category,
                    "city": city,
                    "phone": f"+971-{phone_prefix}-{phone_suffix}",
                    "email": f"{business_name.lower().replace(' ', '').replace('&', '')}@{city.lower().replace(' ', '')}.ae",
                    "address": f"{area}, {city}, UAE",
                    "website": f"www.{business_name.lower().replace(' ', '').replace('&', '')}.ae",
                    "source": random.choice(["yellowpages.ae", "dubizzle.com", "google.com/maps"]),
                    "scraped_date": datetime.now().isoformat()
                }
                
                businesses.append(business)
        
        return businesses
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None


def main():
    """Main function to run data scraper"""
    scraper = DataScraper()
    
    try:
        # Example: Scrape UAE businesses
        categories = ["tailor", "mobile_repair", "laundry"]
        businesses = scraper.scrape_uae_businesses(categories, ["Dubai", "Abu Dhabi"])
        
        print(f"Scraped {len(businesses)} businesses")
        for business in businesses[:5]:  # Show first 5 businesses
            print(f"- {business['business_name']} ({business['category']}) in {business['city']}")
        
        # Save to database
        scraper.save_businesses_to_database(businesses)
        
    finally:
        scraper.close()


if __name__ == "__main__":
    main() 