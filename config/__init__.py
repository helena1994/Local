"""
File __init__.py untuk package config.
"""

from .settings import BOT_CONFIG, SENTIMENT_CONFIG, RESPONSE_TEMPLATES

try:
    from .credentials import FACEBOOK_CREDENTIALS, MESSENGER_CONFIG, SECURITY_CONFIG
except ImportError:
    print("⚠️  Warning: credentials.py tidak ditemukan!")
    print("   Salin credentials_template.py menjadi credentials.py")
    print("   dan isi dengan kredensial login Anda.")