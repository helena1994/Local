"""
Konfigurasi pengaturan bot Messenger.

File ini berisi pengaturan default untuk bot.
Kredensial login disimpan secara terpisah di credentials.py
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Database configuration
DATABASE_CONFIG = {
    'db_path': BASE_DIR / 'database' / 'messenger_bot.db',
    'backup_enabled': True,
    'backup_interval': 3600  # seconds
}

# Bot configuration
BOT_CONFIG = {
    'check_interval': 5,  # seconds between message checks
    'response_delay': (2, 5),  # random delay range for responses (min, max)
    'max_retries': 3,
    'timeout': 30,
    'headless': False,  # Set True untuk mode headless
}

# Chrome driver configuration
CHROME_CONFIG = {
    'options': [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-blink-features=AutomationControlled',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-images',  # Untuk performa lebih baik
    ],
    'user_data_dir': BASE_DIR / 'chrome_user_data',
    'download_dir': BASE_DIR / 'downloads'
}

# Sentiment analysis configuration
SENTIMENT_CONFIG = {
    'threshold_positive': 0.1,
    'threshold_negative': -0.1,
    'language': 'id',  # Indonesian
}

# Response templates berdasarkan sentimen
RESPONSE_TEMPLATES = {
    'positive': [
        "Senang mendengar itu! 😊",
        "Wah, bagus sekali! 👍",
        "Itu berita yang menyenangkan! 🎉",
        "Terima kasih sudah berbagi kabar baik! 😄"
    ],
    'negative': [
        "Maaf mendengar itu. Semoga cepat membaik 🙏",
        "Saya ikut prihatin. Tetap semangat ya! 💪",
        "Mudah-mudahan situasinya segera membaik 🤗",
        "Saya di sini kalau kamu butuh bicara 👂"
    ],
    'neutral': [
        "Terima kasih sudah mengirim pesan! 😊",
        "Baik, saya mengerti 👍",
        "OK, noted! 📝",
        "Sip, terima kasih infonya! ✨"
    ]
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_file': BASE_DIR / 'bot.log',
    'max_log_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}