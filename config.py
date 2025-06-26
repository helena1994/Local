"""
Configuration settings for the Messenger Bot
"""

import os

# Database settings
DATABASE_NAME = "messenger_bot.db"
DATABASE_PATH = os.path.join(os.path.dirname(__file__), DATABASE_NAME)

# Selenium settings
CHROME_DRIVER_PATH = None  # Will use webdriver-manager for automatic management
MESSENGER_URL = "https://www.messenger.com"
IMPLICIT_WAIT_TIME = 10
PAGE_LOAD_TIMEOUT = 30

# Bot settings
DEFAULT_RESPONSE = "Terima kasih atas pesan Anda!"
POSITIVE_RESPONSES = [
    "Senang mendengar itu! 😊",
    "Terima kasih atas pesan positif Anda! 🌟",
    "Itu kabar baik! 😄"
]
NEGATIVE_RESPONSES = [
    "Maaf mendengar itu. Semoga hari Anda membaik. 💙",
    "Saya mengerti perasaan Anda. 🤗", 
    "Terima kasih sudah berbagi. Saya di sini untuk mendengarkan. 💭"
]
NEUTRAL_RESPONSES = [
    "Terima kasih atas pesan Anda. 😊",
    "Saya mengerti. 👍",
    "Baik, terima kasih telah memberi tahu saya. 📝"
]

# Sentiment thresholds
POSITIVE_THRESHOLD = 0.1
NEGATIVE_THRESHOLD = -0.1