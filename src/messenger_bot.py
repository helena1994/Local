"""
Facebook Messenger Bot using Selenium
Automatically logs into Facebook, reads unread messages, and replies with predetermined text.
"""
import time
import logging
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException
)
from webdriver_manager.chrome import ChromeDriverManager

from config import Config


class MessengerBot:
    """Facebook Messenger Bot for automatic message replies"""
    
    def __init__(self, skip_validation=False):
        """Initialize the messenger bot"""
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.logger = self._setup_logging()
        
        # Validate configuration
        Config.validate_config(skip_validation=skip_validation)
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('messenger_bot.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
        
    def _setup_driver(self) -> None:
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            
            # Add Chrome options for stability
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            if Config.HEADLESS_MODE:
                chrome_options.add_argument('--headless')
                
            # Setup ChromeDriver service
            service = Service(ChromeDriverManager().install())
            
            # Initialize driver
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(Config.IMPLICIT_WAIT)
            self.driver.set_page_load_timeout(Config.PAGE_LOAD_TIMEOUT)
            
            # Setup WebDriverWait
            self.wait = WebDriverWait(self.driver, Config.IMPLICIT_WAIT)
            
            self.logger.info("Chrome WebDriver initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to setup WebDriver: {str(e)}")
            raise
            
    def login_to_facebook(self) -> bool:
        """
        Login to Facebook using provided credentials
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            self.logger.info("Attempting to login to Facebook...")
            
            # Navigate to Facebook
            self.driver.get(Config.FACEBOOK_URL)
            
            # Wait for login form to load
            email_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, Config.EMAIL_SELECTOR))
            )
            
            # Enter credentials
            email_input.clear()
            email_input.send_keys(Config.FACEBOOK_EMAIL)
            
            password_input = self.driver.find_element(By.CSS_SELECTOR, Config.PASSWORD_SELECTOR)
            password_input.clear()
            password_input.send_keys(Config.FACEBOOK_PASSWORD)
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, Config.LOGIN_BUTTON_SELECTOR)
            login_button.click()
            
            # Wait for login to complete (check for home page elements)
            self.wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="search"]')),
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Facebook"]')),
                    EC.url_contains('facebook.com/home')
                )
            )
            
            self.logger.info("Successfully logged into Facebook")
            return True
            
        except TimeoutException:
            self.logger.error("Login timeout - Facebook may have changed their interface")
            return False
        except NoSuchElementException as e:
            self.logger.error(f"Login element not found: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during login: {str(e)}")
            return False
            
    def navigate_to_messenger(self) -> bool:
        """
        Navigate to Messenger
        
        Returns:
            bool: True if navigation successful, False otherwise
        """
        try:
            self.logger.info("Navigating to Messenger...")
            
            # Navigate to Messenger
            self.driver.get(Config.MESSENGER_URL)
            
            # Wait for Messenger to load
            self.wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Chats"]')),
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="messenger-inbox"]')),
                    EC.url_contains('messenger.com')
                )
            )
            
            self.logger.info("Successfully navigated to Messenger")
            return True
            
        except TimeoutException:
            self.logger.error("Navigation timeout - Messenger may not have loaded properly")
            return False
        except Exception as e:
            self.logger.error(f"Error navigating to Messenger: {str(e)}")
            return False
            
    def get_unread_conversations(self) -> List[str]:
        """
        Get list of unread conversations
        
        Returns:
            List[str]: List of conversation identifiers for unread messages
        """
        try:
            self.logger.info("Scanning for unread conversations...")
            
            # Wait a moment for the page to fully load
            time.sleep(3)
            
            # Look for unread message indicators
            # This selector may need to be updated based on Facebook's current DOM
            unread_selectors = [
                '[aria-label*="unread"]',
                '[data-testid*="unread"]',
                '.unread',
                '[style*="font-weight: bold"]'  # Bold text often indicates unread
            ]
            
            unread_conversations = []
            
            for selector in unread_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        # Try to find the parent conversation element
                        conversation_element = element.find_element(By.XPATH, './ancestor::*[@role="button"]')
                        if conversation_element and conversation_element not in unread_conversations:
                            unread_conversations.append(conversation_element)
                except NoSuchElementException:
                    continue
                    
            self.logger.info(f"Found {len(unread_conversations)} unread conversations")
            return unread_conversations
            
        except Exception as e:
            self.logger.error(f"Error getting unread conversations: {str(e)}")
            return []
            
    def reply_to_conversation(self, conversation_element) -> bool:
        """
        Reply to a specific conversation
        
        Args:
            conversation_element: WebElement representing the conversation
            
        Returns:
            bool: True if reply sent successfully, False otherwise
        """
        try:
            # Click on the conversation
            conversation_element.click()
            
            # Wait for the conversation to open
            time.sleep(2)
            
            # Look for message input field
            message_input_selectors = [
                '[aria-label*="Type a message"]',
                '[data-testid="message-input"]',
                '[placeholder*="Type a message"]',
                'textarea[aria-label*="message"]'
            ]
            
            message_input = None
            for selector in message_input_selectors:
                try:
                    message_input = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue
                    
            if not message_input:
                self.logger.error("Could not find message input field")
                return False
                
            # Clear and type the reply message
            message_input.clear()
            message_input.send_keys(Config.AUTO_REPLY_MESSAGE)
            
            # Look for send button
            send_button_selectors = [
                '[aria-label*="Send"]',
                '[data-testid*="send"]',
                'button[type="submit"]'
            ]
            
            send_button = None
            for selector in send_button_selectors:
                try:
                    send_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if send_button.is_enabled():
                        break
                except NoSuchElementException:
                    continue
                    
            if send_button and send_button.is_enabled():
                send_button.click()
                self.logger.info("Reply sent successfully")
                return True
            else:
                # Try pressing Enter as alternative
                from selenium.webdriver.common.keys import Keys
                message_input.send_keys(Keys.RETURN)
                self.logger.info("Reply sent using Enter key")
                return True
                
        except Exception as e:
            self.logger.error(f"Error replying to conversation: {str(e)}")
            return False
            
    def run_bot(self) -> None:
        """Main bot execution loop"""
        try:
            self.logger.info("Starting Facebook Messenger Bot...")
            
            # Setup WebDriver
            self._setup_driver()
            
            # Login to Facebook
            if not self.login_to_facebook():
                self.logger.error("Failed to login to Facebook")
                return
                
            # Navigate to Messenger
            if not self.navigate_to_messenger():
                self.logger.error("Failed to navigate to Messenger")
                return
                
            # Get unread conversations
            unread_conversations = self.get_unread_conversations()
            
            if not unread_conversations:
                self.logger.info("No unread conversations found")
                return
                
            # Reply to each unread conversation
            replies_sent = 0
            for conversation in unread_conversations:
                if self.reply_to_conversation(conversation):
                    replies_sent += 1
                    time.sleep(2)  # Wait between replies to avoid being flagged
                    
            self.logger.info(f"Bot completed. Sent {replies_sent} replies out of {len(unread_conversations)} unread conversations")
            
        except Exception as e:
            self.logger.error(f"Unexpected error in bot execution: {str(e)}")
        finally:
            self.cleanup()
            
    def cleanup(self) -> None:
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing WebDriver: {str(e)}")


def main():
    """Main entry point"""
    bot = MessengerBot()
    bot.run_bot()


if __name__ == "__main__":
    main()