"""
Selenium-based Messenger automation for the Python bot.
"""

import time
import logging
import random
from typing import List, Dict, Optional, Any
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from scripts.auto_login import AutoLogin
from scripts.sentiment_analysis import SentimentAnalyzer
from scripts.database_manager import DatabaseManager
from config.settings import BOT_SETTINGS, MESSENGER_SETTINGS


class MessengerBot:
    """Main Messenger bot class with Selenium automation."""
    
    def __init__(self):
        """Initialize the Messenger bot."""
        self.logger = logging.getLogger(__name__)
        self.auto_login = AutoLogin()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.db_manager = DatabaseManager()
        
        self.driver = None
        self.is_running = False
        self.wait_timeout = BOT_SETTINGS['wait_timeout']
        self.check_interval = BOT_SETTINGS['check_interval']
        self.auto_reply = BOT_SETTINGS['auto_reply']
        self.sentiment_analysis = BOT_SETTINGS['sentiment_analysis']
        
        self.selectors = MESSENGER_SETTINGS['selectors']
        self.processed_messages = set()  # Track processed message IDs
    
    def start(self) -> bool:
        """Start the bot.
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            self.logger.info("Starting Messenger bot")
            
            # Create driver and login
            self.driver = self.auto_login.create_driver()
            self.auto_login.driver = self.driver
            
            if not self.auto_login.login():
                self.logger.error("Failed to login to Messenger")
                return False
            
            self.is_running = True
            self.logger.info("Bot started successfully")
            
            # Start monitoring loop
            self._monitor_messages()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting bot: {e}")
            return False
    
    def stop(self) -> None:
        """Stop the bot."""
        self.logger.info("Stopping Messenger bot")
        self.is_running = False
        
        if self.auto_login:
            self.auto_login.logout()
            self.auto_login.close_driver()
        
        self.logger.info("Bot stopped")
    
    def _monitor_messages(self) -> None:
        """Monitor for new messages."""
        self.logger.info("Starting message monitoring")
        
        while self.is_running:
            try:
                # Check for new messages
                new_messages = self._get_new_messages()
                
                if new_messages:
                    self.logger.info(f"Found {len(new_messages)} new messages")
                    self._process_messages(new_messages)
                
                # Wait before next check
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.check_interval)
    
    def _get_new_messages(self) -> List[Dict[str, Any]]:
        """Get new messages from Messenger.
        
        Returns:
            List of new message dictionaries
        """
        try:
            new_messages = []
            
            # Find chat conversations
            chat_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "[role='gridcell'] [role='button']"
            )
            
            for chat_element in chat_elements[:5]:  # Check first 5 chats
                try:
                    # Click on chat to open it
                    chat_element.click()
                    time.sleep(2)
                    
                    # Get messages from this chat
                    messages = self._extract_messages_from_chat()
                    new_messages.extend(messages)
                    
                except Exception as e:
                    self.logger.debug(f"Error processing chat: {e}")
                    continue
            
            return new_messages
            
        except Exception as e:
            self.logger.error(f"Error getting new messages: {e}")
            return []
    
    def _extract_messages_from_chat(self) -> List[Dict[str, Any]]:
        """Extract messages from the currently open chat.
        
        Returns:
            List of message dictionaries
        """
        try:
            messages = []
            
            # Find message elements
            message_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                "[data-scope='messages_table'] [role='row']"
            )
            
            for msg_element in message_elements[-10:]:  # Get last 10 messages
                try:
                    message_data = self._parse_message_element(msg_element)
                    if message_data and message_data['id'] not in self.processed_messages:
                        messages.append(message_data)
                        
                except Exception as e:
                    self.logger.debug(f"Error parsing message element: {e}")
                    continue
            
            return messages
            
        except Exception as e:
            self.logger.error(f"Error extracting messages from chat: {e}")
            return []
    
    def _parse_message_element(self, element) -> Optional[Dict[str, Any]]:
        """Parse a message element to extract message data.
        
        Args:
            element: Selenium WebElement representing a message
            
        Returns:
            Message data dictionary or None
        """
        try:
            # This is a simplified parser - actual implementation would need
            # to handle Messenger's specific DOM structure
            
            message_text = element.text.strip()
            if not message_text:
                return None
            
            # Generate a simple message ID based on content and timestamp
            message_id = hash(f"{message_text}{datetime.now().timestamp()}")
            
            # Try to determine sender (simplified approach)
            sender = "unknown"
            recipient = "bot"
            
            # Check if message is from user or bot
            classes = element.get_attribute("class") or ""
            if "incoming" in classes.lower():
                sender = "user"
            elif "outgoing" in classes.lower():
                sender = "bot"
                recipient = "user"
            
            return {
                'id': message_id,
                'sender': sender,
                'recipient': recipient,
                'message': message_text,
                'timestamp': datetime.now(),
                'element': element
            }
            
        except Exception as e:
            self.logger.debug(f"Error parsing message element: {e}")
            return None
    
    def _process_messages(self, messages: List[Dict[str, Any]]) -> None:
        """Process new messages.
        
        Args:
            messages: List of message dictionaries
        """
        for message in messages:
            try:
                self._process_single_message(message)
                self.processed_messages.add(message['id'])
                
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
    
    def _process_single_message(self, message: Dict[str, Any]) -> None:
        """Process a single message.
        
        Args:
            message: Message dictionary
        """
        self.logger.info(f"Processing message from {message['sender']}: {message['message'][:50]}...")
        
        # Perform sentiment analysis if enabled
        sentiment_data = {}
        if self.sentiment_analysis and message['sender'] != 'bot':
            analysis = self.sentiment_analyzer.analyze_and_respond(message['message'])
            sentiment_data = {
                'sentiment': analysis['sentiment_score'],
                'sentiment_label': analysis['sentiment_label']
            }
            
            self.logger.info(f"Sentiment: {analysis['sentiment_label']} ({analysis['sentiment_score']:.3f})")
        
        # Store message in database
        self.db_manager.store_message(
            sender=message['sender'],
            recipient=message['recipient'],
            message=message['message'],
            sentiment=sentiment_data.get('sentiment'),
            sentiment_label=sentiment_data.get('sentiment_label'),
            metadata={'processed_at': datetime.now().isoformat()}
        )
        
        # Send automatic reply if enabled and message is from user
        if self.auto_reply and message['sender'] != 'bot':
            if self.sentiment_analysis:
                response = sentiment_data.get('response', analysis['response'])
            else:
                response = self._generate_basic_response(message['message'])
            
            self._send_message(response)
    
    def _generate_basic_response(self, message: str) -> str:
        """Generate a basic response when sentiment analysis is disabled.
        
        Args:
            message: Input message
            
        Returns:
            Response message
        """
        basic_responses = [
            "Thanks for your message!",
            "I received your message.",
            "Got it!",
            "Thank you for reaching out.",
            "Message received! 👍"
        ]
        
        return random.choice(basic_responses)
    
    def _send_message(self, message: str) -> bool:
        """Send a message through Messenger.
        
        Args:
            message: Message to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            self.logger.info(f"Sending response: {message}")
            
            # Find message input field
            message_input = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['message_input']))
            )
            
            # Clear and type message
            message_input.clear()
            message_input.send_keys(message)
            
            # Send message (try Enter key first, then button if available)
            try:
                message_input.send_keys(Keys.RETURN)
            except:
                # Try to find and click send button
                send_button = self.driver.find_element(By.CSS_SELECTOR, self.selectors['send_button'])
                send_button.click()
            
            # Wait a bit for message to be sent
            time.sleep(2)
            
            # Store bot's message in database
            self.db_manager.store_message(
                sender='bot',
                recipient='user',
                message=message,
                metadata={'auto_reply': True, 'sent_at': datetime.now().isoformat()}
            )
            
            self.logger.info("Message sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False
    
    def send_custom_message(self, recipient: str, message: str) -> bool:
        """Send a custom message to a specific recipient.
        
        Args:
            recipient: Recipient name or identifier
            message: Message to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            self.logger.info(f"Sending custom message to {recipient}: {message}")
            
            # This would need implementation specific to finding and opening
            # a chat with the specified recipient
            
            # For now, just send to current chat
            return self._send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error sending custom message: {e}")
            return False
    
    def get_chat_history(self, contact: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat history with a specific contact.
        
        Args:
            contact: Contact name
            limit: Number of messages to retrieve
            
        Returns:
            List of messages
        """
        return self.db_manager.get_conversation_history('user', 'bot', limit)
    
    def get_bot_statistics(self) -> Dict[str, Any]:
        """Get bot statistics.
        
        Returns:
            Statistics dictionary
        """
        db_stats = self.db_manager.get_statistics()
        
        return {
            'is_running': self.is_running,
            'auto_reply_enabled': self.auto_reply,
            'sentiment_analysis_enabled': self.sentiment_analysis,
            'processed_messages_count': len(self.processed_messages),
            'database_stats': db_stats,
            'check_interval': self.check_interval
        }