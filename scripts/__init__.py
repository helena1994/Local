"""
Scripts package for the Messenger bot.
"""

# Import core modules that don't require external dependencies
from .sentiment_analysis import SentimentAnalyzer
from .database_manager import DatabaseManager

__all__ = ['SentimentAnalyzer', 'DatabaseManager']

# Try to import Selenium-dependent modules
try:
    from .messenger_automation import MessengerBot
    from .auto_login import AutoLogin
    __all__.extend(['MessengerBot', 'AutoLogin'])
except ImportError as e:
    import logging
    logging.warning(f"Selenium-dependent modules not available: {e}")
    # Create placeholder classes for documentation/development
    class MessengerBot:
        def __init__(self):
            raise ImportError("Selenium is required for MessengerBot. Install with: pip install selenium")
    
    class AutoLogin:
        def __init__(self):
            raise ImportError("Selenium is required for AutoLogin. Install with: pip install selenium")