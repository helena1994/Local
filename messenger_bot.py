"""
Selenium-based Facebook Messenger Bot with sentiment analysis and memory
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from database import DatabaseManager
from sentiment_analyzer import SentimentAnalyzer
import config


class MessengerBot:
    """Selenium-based bot for Facebook Messenger automation"""
    
    def __init__(self, headless: bool = False):
        """
        Initialize Messenger bot
        
        Args:
            headless: Run browser in headless mode
        """
        self.driver = None
        self.wait = None
        self.headless = headless
        self.db_manager = DatabaseManager()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.setup_logging()
        
    def setup_logging(self) -> None:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('messenger_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self) -> None:
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Disable notifications
        prefs = {"profile.default_content_setting_values.notifications": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Remove automation indicators
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.driver.implicitly_wait(config.IMPLICIT_WAIT_TIME)
        self.driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
        self.wait = WebDriverWait(self.driver, config.IMPLICIT_WAIT_TIME)
        
        self.logger.info("Chrome WebDriver setup completed")
    
    def login_to_messenger(self, email: str, password: str) -> bool:
        """
        Login to Facebook Messenger
        
        Args:
            email: Facebook email
            password: Facebook password
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            self.logger.info("Navigating to Messenger...")
            self.driver.get(config.MESSENGER_URL)
            
            # Wait for login form
            email_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            password_input = self.driver.find_element(By.ID, "pass")
            login_button = self.driver.find_element(By.NAME, "login")
            
            # Enter credentials
            email_input.send_keys(email)
            password_input.send_keys(password)
            login_button.click()
            
            # Wait for successful login (look for messenger interface)
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'conversation')]"))
            )
            
            self.logger.info("Successfully logged in to Messenger")
            return True
            
        except TimeoutException:
            self.logger.error("Login timeout - check credentials or internet connection")
            return False
        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            return False
    
    def get_conversation_list(self) -> List[str]:
        """Get list of available conversations"""
        try:
            # Look for conversation elements
            conversations = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'conversation')]//span"
            )
            return [conv.text for conv in conversations if conv.text.strip()]
        except Exception as e:
            self.logger.error(f"Error getting conversations: {str(e)}")
            return []
    
    def select_conversation(self, conversation_name: str) -> bool:
        """
        Select a conversation by name
        
        Args:
            conversation_name: Name of person/group to chat with
            
        Returns:
            True if conversation selected successfully
        """
        try:
            # Find and click conversation
            conversation_element = self.wait.until(
                EC.element_to_be_clickable((
                    By.XPATH, 
                    f"//div[contains(@class, 'conversation')]//span[contains(text(), '{conversation_name}')]"
                ))
            )
            conversation_element.click()
            
            # Wait for message area to load
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label, 'Message')]"))
            )
            
            self.logger.info(f"Selected conversation with {conversation_name}")
            return True
            
        except TimeoutException:
            self.logger.error(f"Could not find conversation with {conversation_name}")
            return False
        except Exception as e:
            self.logger.error(f"Error selecting conversation: {str(e)}")
            return False
    
    def get_latest_messages(self, count: int = 5) -> List[dict]:
        """
        Get latest messages from current conversation
        
        Args:
            count: Number of messages to retrieve
            
        Returns:
            List of message dictionaries
        """
        try:
            # Find message elements
            message_elements = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'message')]//span"
            )
            
            messages = []
            for element in message_elements[-count:]:
                if element.text.strip():
                    # Determine if message is from user or bot (simplified)
                    is_from_user = self._is_message_from_user(element)
                    messages.append({
                        'text': element.text.strip(),
                        'from_user': is_from_user,
                        'timestamp': time.time()
                    })
            
            return messages
            
        except Exception as e:
            self.logger.error(f"Error getting messages: {str(e)}")
            return []
    
    def _is_message_from_user(self, message_element) -> bool:
        """
        Determine if message is from user (not from bot)
        This is a simplified implementation - in practice, you'd need to
        check message positioning, styling, or other indicators
        """
        # This is a placeholder - implement based on actual Messenger DOM structure
        return True  # Assume all messages are from user for now
    
    def send_message(self, message: str) -> bool:
        """
        Send a message in current conversation
        
        Args:
            message: Message text to send
            
        Returns:
            True if message sent successfully
        """
        try:
            # Find message input box
            message_input = self.wait.until(
                EC.element_to_be_clickable((
                    By.XPATH, 
                    "//div[contains(@aria-label, 'Message')]//div[contains(@contenteditable, 'true')]"
                ))
            )
            
            # Type and send message
            message_input.click()
            message_input.clear()
            message_input.send_keys(message)
            
            # Find and click send button
            send_button = self.driver.find_element(
                By.XPATH, "//div[contains(@aria-label, 'Send')]"
            )
            send_button.click()
            
            self.logger.info(f"Sent message: {message}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}")
            return False
    
    def process_and_reply(self, user_message: str, user_id: str = "default_user") -> str:
        """
        Process user message with sentiment analysis and generate reply
        
        Args:
            user_message: Message from user
            user_id: Identifier for user (for memory)
            
        Returns:
            Bot response message
        """
        # Analyze sentiment and generate response
        response, sentiment_score, sentiment_label = self.sentiment_analyzer.analyze_and_respond(user_message)
        
        # Save to database
        self.db_manager.save_conversation(
            user_id, user_message, response, sentiment_score, sentiment_label
        )
        
        # Log the interaction
        sentiment_info = self.sentiment_analyzer.format_sentiment_info(sentiment_score, sentiment_label)
        self.logger.info(f"User: {user_message}")
        self.logger.info(f"Sentiment: {sentiment_info}")
        self.logger.info(f"Bot: {response}")
        
        return response
    
    def monitor_and_respond(self, conversation_name: str, check_interval: int = 5) -> None:
        """
        Monitor conversation for new messages and respond automatically
        
        Args:
            conversation_name: Name of conversation to monitor
            check_interval: Seconds between message checks
        """
        if not self.select_conversation(conversation_name):
            return
        
        self.logger.info(f"Starting to monitor conversation with {conversation_name}")
        last_message_count = 0
        
        try:
            while True:
                # Get current messages
                messages = self.get_latest_messages()
                current_message_count = len(messages)
                
                # Check for new messages from user
                if current_message_count > last_message_count:
                    new_messages = messages[last_message_count:]
                    for message in new_messages:
                        if message['from_user']:
                            # Process and respond to user message
                            response = self.process_and_reply(
                                message['text'], 
                                user_id=conversation_name
                            )
                            self.send_message(response)
                            time.sleep(2)  # Brief delay between responses
                
                last_message_count = current_message_count
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Error during monitoring: {str(e)}")
    
    def close(self) -> None:
        """Close the browser and cleanup resources"""
        if self.driver:
            self.driver.quit()
            self.logger.info("Browser closed")


def main():
    """Main function for testing the bot"""
    bot = MessengerBot(headless=False)
    
    try:
        bot.setup_driver()
        
        # Note: In production, use environment variables or secure config for credentials
        email = input("Enter your Facebook email: ")
        password = input("Enter your Facebook password: ")
        
        if bot.login_to_messenger(email, password):
            conversation_name = input("Enter conversation name to monitor: ")
            bot.monitor_and_respond(conversation_name)
        
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
    finally:
        bot.close()


if __name__ == "__main__":
    main()