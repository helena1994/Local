"""
Auto-login functionality for Messenger using Selenium.
"""

import time
import logging
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config.settings import SELENIUM_SETTINGS, MESSENGER_SETTINGS
from config import MESSENGER_CREDENTIALS


class AutoLogin:
    """Handles automatic login to Messenger."""
    
    def __init__(self, driver: Optional[webdriver.Chrome] = None):
        """Initialize auto-login.
        
        Args:
            driver: Optional existing WebDriver instance
        """
        self.driver = driver
        self.logger = logging.getLogger(__name__)
        self.wait_timeout = SELENIUM_SETTINGS['implicit_wait']
        self.messenger_url = MESSENGER_SETTINGS['base_url']
        self.selectors = MESSENGER_SETTINGS['selectors']
        
        if not MESSENGER_CREDENTIALS:
            self.logger.warning("No credentials found. Please configure credentials.py")
    
    def create_driver(self) -> webdriver.Chrome:
        """Create Chrome WebDriver with appropriate settings.
        
        Returns:
            Chrome WebDriver instance
        """
        chrome_options = Options()
        
        # Add Chrome options
        chrome_options.add_argument(f"--user-agent={SELENIUM_SETTINGS['user_agent']}")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Set window size
        width, height = SELENIUM_SETTINGS['window_size']
        chrome_options.add_argument(f"--window-size={width},{height}")
        
        # Headless mode if configured
        if SELENIUM_SETTINGS.get('headless_mode', False):
            chrome_options.add_argument("--headless")
        
        # Create driver
        driver_path = SELENIUM_SETTINGS.get('chrome_driver_path')
        if driver_path:
            driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)
        
        # Set implicit wait
        driver.implicitly_wait(SELENIUM_SETTINGS['implicit_wait'])
        
        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.logger.info("Chrome WebDriver created successfully")
        return driver
    
    def login(self, email: Optional[str] = None, password: Optional[str] = None) -> bool:
        """Perform login to Messenger.
        
        Args:
            email: Email address (uses config if not provided)
            password: Password (uses config if not provided)
            
        Returns:
            True if login successful, False otherwise
        """
        if not self.driver:
            self.driver = self.create_driver()
        
        # Use provided credentials or fall back to config
        login_email = email or MESSENGER_CREDENTIALS.get('email')
        login_password = password or MESSENGER_CREDENTIALS.get('password')
        
        if not login_email or not login_password:
            self.logger.error("Email or password not provided")
            return False
        
        try:
            self.logger.info("Navigating to Messenger login page")
            self.driver.get(self.messenger_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Check if already logged in
            if self._is_logged_in():
                self.logger.info("Already logged in")
                return True
            
            # Find and fill email field
            self.logger.debug("Looking for email input field")
            email_input = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['email_input']))
            )
            email_input.clear()
            email_input.send_keys(login_email)
            
            # Find and fill password field
            self.logger.debug("Looking for password input field")
            password_input = self.driver.find_element(By.CSS_SELECTOR, self.selectors['password_input'])
            password_input.clear()
            password_input.send_keys(login_password)
            
            # Click login button
            self.logger.debug("Clicking login button")
            login_button = self.driver.find_element(By.CSS_SELECTOR, self.selectors['login_button'])
            login_button.click()
            
            # Wait for login to complete
            self.logger.info("Waiting for login to complete")
            time.sleep(5)
            
            # Check if login was successful
            if self._is_logged_in():
                self.logger.info("Login successful")
                return True
            else:
                self.logger.error("Login failed - not redirected to main page")
                return False
                
        except TimeoutException:
            self.logger.error("Timeout waiting for login elements")
            return False
        except NoSuchElementException as e:
            self.logger.error(f"Could not find login element: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during login: {e}")
            return False
    
    def _is_logged_in(self) -> bool:
        """Check if currently logged in to Messenger.
        
        Returns:
            True if logged in, False otherwise
        """
        try:
            # Check for elements that only appear when logged in
            current_url = self.driver.current_url
            
            # If we're on the main messenger page (not login), we're probably logged in
            if 'messenger.com' in current_url and 'login' not in current_url:
                return True
            
            # Try to find chat list or other logged-in elements
            try:
                self.driver.find_element(By.CSS_SELECTOR, self.selectors['chat_list'])
                return True
            except NoSuchElementException:
                pass
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Error checking login status: {e}")
            return False
    
    def logout(self) -> bool:
        """Logout from Messenger.
        
        Returns:
            True if logout successful, False otherwise
        """
        if not self.driver:
            return True
        
        try:
            self.logger.info("Logging out from Messenger")
            
            # Try to find and click logout button
            # This is a simplified approach - actual implementation may vary
            # based on Messenger's current UI
            
            # Navigate to a logout URL or find logout button
            self.driver.get("https://www.messenger.com/logout")
            time.sleep(2)
            
            # Clear cookies and local storage
            self.driver.delete_all_cookies()
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
            
            self.logger.info("Logout completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during logout: {e}")
            return False
    
    def close_driver(self) -> None:
        """Close the WebDriver instance."""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver closed")
            except Exception as e:
                self.logger.error(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None
    
    def check_connection(self) -> bool:
        """Check if connection to Messenger is working.
        
        Returns:
            True if connection is working, False otherwise
        """
        if not self.driver:
            return False
        
        try:
            # Try to access a simple element or check page title
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            if 'messenger' in current_url.lower() or 'messenger' in page_title.lower():
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking connection: {e}")
            return False
    
    def handle_2fa_prompt(self) -> bool:
        """Handle two-factor authentication if prompted.
        
        Returns:
            True if 2FA handled successfully, False otherwise
        """
        try:
            # Look for 2FA elements
            # This is a placeholder - actual implementation would need
            # to handle specific 2FA UI elements
            
            self.logger.info("Checking for 2FA prompt")
            
            # Wait a bit to see if 2FA prompt appears
            time.sleep(5)
            
            # For now, just wait for user to manually handle 2FA
            self.logger.warning("If 2FA is required, please complete it manually")
            
            # Wait for potential 2FA completion
            for _ in range(30):  # Wait up to 30 seconds
                if self._is_logged_in():
                    return True
                time.sleep(1)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling 2FA: {e}")
            return False