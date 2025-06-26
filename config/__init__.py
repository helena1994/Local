"""
Configuration package initialization.
"""

from .settings import (
    BOT_SETTINGS,
    DATABASE_SETTINGS,
    SELENIUM_SETTINGS,
    MESSENGER_SETTINGS,
    SENTIMENT_SETTINGS,
    LOGGING_SETTINGS
)

try:
    from .credentials import MESSENGER_CREDENTIALS, DATABASE_KEY, API_KEYS
except ImportError:
    print("Warning: credentials.py not found. Please copy credentials_template.py to credentials.py and configure it.")
    MESSENGER_CREDENTIALS = {}
    DATABASE_KEY = None
    API_KEYS = {}

__all__ = [
    'BOT_SETTINGS',
    'DATABASE_SETTINGS',
    'SELENIUM_SETTINGS',
    'MESSENGER_SETTINGS',
    'SENTIMENT_SETTINGS',
    'LOGGING_SETTINGS',
    'MESSENGER_CREDENTIALS',
    'DATABASE_KEY',
    'API_KEYS'
]