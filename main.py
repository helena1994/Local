#!/usr/bin/env python3
"""
Main entry point for the Python Messenger Bot.

This bot provides automated Messenger functionality using Selenium
with sentiment analysis and SQLite database storage.
"""

import sys
import time
import logging
from pathlib import Path

# Add scripts directory to Python path
sys.path.append(str(Path(__file__).parent / "scripts"))

from scripts.messenger_automation import MessengerBot
from scripts.database_manager import DatabaseManager
from config.settings import BOT_SETTINGS


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('messenger_bot.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main function to run the Messenger bot."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Python Messenger Bot...")
    
    try:
        # Initialize database
        db_manager = DatabaseManager()
        db_manager.initialize_database()
        
        # Initialize and start the bot
        bot = MessengerBot()
        
        logger.info("Bot initialized successfully. Starting automation...")
        bot.start()
        
        # Keep the bot running
        while True:
            time.sleep(10)
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        sys.exit(1)
    finally:
        logger.info("Shutting down bot...")


if __name__ == "__main__":
    main()