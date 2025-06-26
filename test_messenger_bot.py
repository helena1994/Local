#!/usr/bin/env python3
"""
Test script for Facebook Messenger Bot
Tests basic functionality without actually running the bot
"""
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_config_import():
    """Test that config can be imported and has required attributes"""
    try:
        from config import Config
        print("✅ Config module imported successfully")
        
        # Test required attributes exist
        required_attrs = [
            'FACEBOOK_EMAIL', 'FACEBOOK_PASSWORD', 'AUTO_REPLY_MESSAGE',
            'HEADLESS_MODE', 'IMPLICIT_WAIT', 'PAGE_LOAD_TIMEOUT',
            'FACEBOOK_URL', 'MESSENGER_URL'
        ]
        
        for attr in required_attrs:
            if hasattr(Config, attr):
                print(f"✅ Config.{attr} exists")
            else:
                print(f"❌ Config.{attr} missing")
                return False
                
        print("✅ All required config attributes present")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import config: {e}")
        return False


def test_messenger_bot_import():
    """Test that MessengerBot can be imported"""
    try:
        from messenger_bot import MessengerBot
        print("✅ MessengerBot module imported successfully")
        
        # Test required methods exist
        required_methods = [
            'login_to_facebook', 'navigate_to_messenger', 
            'get_unread_conversations', 'reply_to_conversation',
            'run_bot', 'cleanup'
        ]
        
        for method in required_methods:
            if hasattr(MessengerBot, method):
                print(f"✅ MessengerBot.{method} exists")
            else:
                print(f"❌ MessengerBot.{method} missing")
                return False
                
        print("✅ All required MessengerBot methods present")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import MessengerBot: {e}")
        return False


def test_bot_instantiation():
    """Test that bot can be instantiated with mock credentials"""
    try:
        # Mock environment variables first, before importing
        with patch.dict(os.environ, {
            'FACEBOOK_EMAIL': 'test@example.com',
            'FACEBOOK_PASSWORD': 'testpassword',
            'AUTO_REPLY_MESSAGE': 'Test message'
        }):
            from messenger_bot import MessengerBot
            
            # Mock selenium imports to avoid ChromeDriver requirement
            with patch('messenger_bot.webdriver') as mock_webdriver:
                with patch('messenger_bot.WebDriverWait') as mock_wait:
                    with patch('messenger_bot.ChromeDriverManager') as mock_chromedriver:
                        # Use skip_validation=True for testing
                        bot = MessengerBot(skip_validation=True)
                        print("✅ MessengerBot instantiated successfully with mock credentials")
                        
                        # Test that logger is set up
                        if hasattr(bot, 'logger') and bot.logger:
                            print("✅ Logger initialized")
                        else:
                            print("❌ Logger not initialized")
                            return False
                            
        return True
        
    except Exception as e:
        print(f"❌ Failed to instantiate MessengerBot: {e}")
        return False


def test_dependencies():
    """Test that all required dependencies are installed"""
    required_packages = [
        'selenium', 'python-dotenv', 'webdriver-manager'
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            if package == 'python-dotenv':
                import dotenv
            elif package == 'webdriver-manager':
                import webdriver_manager
            else:
                __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} not installed")
            all_installed = False
            
    return all_installed


def main():
    """Run all tests"""
    print("🧪 Running Facebook Messenger Bot Tests\n")
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Config Import", test_config_import),
        ("MessengerBot Import", test_messenger_bot_import),
        ("Bot Instantiation", test_bot_instantiation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}:")
        print("-" * 40)
        result = test_func()
        results.append((test_name, result))
        
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
            
    print(f"\nPassed: {passed}/{len(tests)} tests")
    
    if passed == len(tests):
        print("🎉 All tests passed! Bot is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())