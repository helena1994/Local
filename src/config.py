"""
Configuration settings for Facebook Messenger Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for the messenger bot"""
    
    # Facebook credentials
    FACEBOOK_EMAIL = os.getenv('FACEBOOK_EMAIL')
    FACEBOOK_PASSWORD = os.getenv('FACEBOOK_PASSWORD')
    
    # Bot settings
    AUTO_REPLY_MESSAGE = os.getenv('AUTO_REPLY_MESSAGE', 
                                  'Terima kasih atas pesan Anda! Saya akan membalas sesegera mungkin.')
    
    # Selenium settings
    HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'False').lower() == 'true'
    IMPLICIT_WAIT = int(os.getenv('IMPLICIT_WAIT', '10'))
    PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))
    
    # VPS/Daemon settings
    DAEMON_MODE = os.getenv('DAEMON_MODE', 'False').lower() == 'true'
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '300'))  # 5 minutes default
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', '60'))  # 1 minute default
    
    # URLs
    FACEBOOK_URL = 'https://www.facebook.com'
    MESSENGER_URL = 'https://www.messenger.com'
    
    # Selectors (may need updates based on Facebook's current DOM structure)
    EMAIL_SELECTOR = 'input[name="email"]'
    PASSWORD_SELECTOR = 'input[name="pass"]'
    LOGIN_BUTTON_SELECTOR = 'button[name="login"]'
    
    @classmethod
    def validate_config(cls, skip_validation=False):
        """Validate required configuration"""
        if skip_validation:
            return True
            
        if not cls.FACEBOOK_EMAIL:
            raise ValueError("FACEBOOK_EMAIL environment variable is required")
        if not cls.FACEBOOK_PASSWORD:
            raise ValueError("FACEBOOK_PASSWORD environment variable is required")
        return True