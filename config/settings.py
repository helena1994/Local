"""
Settings configuration for the Messenger bot.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Database settings
DATABASE_SETTINGS = {
    'database_path': BASE_DIR / 'database' / 'messenger_bot.db',
    'table_name': 'messages'
}

# Bot settings
BOT_SETTINGS = {
    'headless_mode': os.getenv('HEADLESS_MODE', 'true').lower() == 'true',
    'wait_timeout': int(os.getenv('WAIT_TIMEOUT', '10')),
    'check_interval': int(os.getenv('CHECK_INTERVAL', '30')),
    'auto_reply': os.getenv('AUTO_REPLY', 'true').lower() == 'true',
    'sentiment_analysis': os.getenv('SENTIMENT_ANALYSIS', 'true').lower() == 'true'
}

# Selenium settings
SELENIUM_SETTINGS = {
    'chrome_driver_path': os.getenv('CHROME_DRIVER_PATH'),
    'window_size': (1920, 1080),
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'implicit_wait': 10
}

# Messenger settings
MESSENGER_SETTINGS = {
    'base_url': 'https://www.messenger.com',
    'login_url': 'https://www.messenger.com',
    'selectors': {
        'email_input': 'input[name="email"]',
        'password_input': 'input[name="pass"]',
        'login_button': 'button[name="login"]',
        'message_input': '[contenteditable="true"][data-text="Type a message..."]',
        'send_button': '[aria-label="Press Enter to send"]',
        'chat_list': '[role="grid"]',
        'message_list': '[role="log"]'
    }
}

# Sentiment analysis settings
SENTIMENT_SETTINGS = {
    'positive_threshold': 0.1,
    'negative_threshold': -0.1,
    'responses': {
        'positive': [
            "That's great to hear! 😊",
            "Wonderful! Thanks for sharing!",
            "I'm glad you're feeling positive! 🌟"
        ],
        'negative': [
            "I'm sorry to hear that. Is there anything I can help with?",
            "That sounds challenging. Let me know if you need support.",
            "I understand this might be difficult. 💙"
        ],
        'neutral': [
            "Thanks for your message!",
            "Got it, thanks for letting me know.",
            "Received your message. 👍"
        ]
    }
}

# Logging settings
LOGGING_SETTINGS = {
    'log_file': BASE_DIR / 'messenger_bot.log',
    'log_level': os.getenv('LOG_LEVEL', 'INFO'),
    'max_log_size': 1024 * 1024 * 10  # 10MB
}