#!/usr/bin/env python3
"""
Main file untuk menjalankan bot Messenger otomatis.

Bot ini menggunakan Selenium untuk otomatisasi browser Chrome,
menyimpan riwayat pesan menggunakan SQLite, dan menganalisis
sentimen pesan untuk memberikan respons yang sesuai.
"""

import sys
import time
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.messenger_automation import MessengerBot
from scripts.database_manager import DatabaseManager
from config.settings import BOT_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main function untuk menjalankan bot Messenger."""
    logger.info("🤖 Memulai bot Messenger...")
    
    try:
        # Initialize database
        db_manager = DatabaseManager()
        db_manager.initialize_database()
        logger.info("✅ Database berhasil diinisialisasi")
        
        # Initialize bot
        bot = MessengerBot(db_manager)
        logger.info("✅ Bot berhasil diinisialisasi")
        
        # Start bot
        bot.start()
        
    except KeyboardInterrupt:
        logger.info("❌ Bot dihentikan oleh pengguna")
    except Exception as e:
        logger.error(f"❌ Error dalam menjalankan bot: {e}")
    finally:
        logger.info("🔄 Membersihkan resources...")
        try:
            bot.cleanup()
        except:
            pass


if __name__ == "__main__":
    main()