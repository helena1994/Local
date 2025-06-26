#!/usr/bin/env python3
"""
Command-line wrapper for Facebook Messenger Bot
"""
import sys
import os
import argparse

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from messenger_bot import MessengerBot
from config import Config


def check_environment():
    """Check if environment variables are properly set"""
    missing_vars = []
    
    if not Config.FACEBOOK_EMAIL:
        missing_vars.append('FACEBOOK_EMAIL')
    if not Config.FACEBOOK_PASSWORD:
        missing_vars.append('FACEBOOK_PASSWORD')
        
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease:")
        print("1. Copy .env.example to .env")
        print("2. Edit .env and add your Facebook credentials")
        print("3. Run the bot again")
        return False
        
    print("✅ Environment variables configured")
    return True


def main():
    """Main command-line interface"""
    parser = argparse.ArgumentParser(
        description='Facebook Messenger Bot - Automatically reply to unread messages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_bot.py                    # Run bot normally
  python run_bot.py --headless         # Run bot in headless mode
  python run_bot.py --check-config     # Check configuration only
  
Environment variables required:
  FACEBOOK_EMAIL       Your Facebook login email
  FACEBOOK_PASSWORD    Your Facebook login password
  AUTO_REPLY_MESSAGE   Message to send as reply (optional)
        """
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode (no GUI)'
    )
    
    parser.add_argument(
        '--check-config',
        action='store_true',
        help='Check configuration and exit'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='Implicit wait timeout in seconds (default: 10)'
    )
    
    args = parser.parse_args()
    
    print("🤖 Facebook Messenger Bot")
    print("=" * 50)
    
    # Check configuration
    if not check_environment():
        return 1
        
    if args.check_config:
        print("✅ Configuration check passed!")
        print(f"📧 Email: {Config.FACEBOOK_EMAIL}")
        print(f"💬 Reply message: {Config.AUTO_REPLY_MESSAGE}")
        print(f"🖥️  Headless mode: {args.headless or Config.HEADLESS_MODE}")
        return 0
    
    # Override environment settings with command line args
    if args.headless:
        os.environ['HEADLESS_MODE'] = 'True'
    if args.timeout != 10:
        os.environ['IMPLICIT_WAIT'] = str(args.timeout)
        
    print("🚀 Starting bot...")
    print(f"📧 Using email: {Config.FACEBOOK_EMAIL}")
    print(f"🖥️  Headless mode: {args.headless or Config.HEADLESS_MODE}")
    print(f"⏰ Timeout: {args.timeout} seconds")
    print("-" * 50)
    
    try:
        bot = MessengerBot()
        bot.run_bot()
        print("\n✅ Bot execution completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Bot stopped by user (Ctrl+C)")
        return 1
    except Exception as e:
        print(f"\n❌ Bot failed with error: {str(e)}")
        print("💡 Check the log file 'messenger_bot.log' for more details")
        return 1


if __name__ == "__main__":
    sys.exit(main())