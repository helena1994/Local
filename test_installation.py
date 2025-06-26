#!/usr/bin/env python3
"""
Script untuk test instalasi dan konfigurasi bot Messenger.

Menguji:
- Import semua modul
- Koneksi database
- Analisis sentimen
- Konfigurasi
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test import semua modul."""
    print("🔍 Testing imports...")
    
    try:
        from scripts.database_manager import DatabaseManager
        print("✅ DatabaseManager import OK")
    except ImportError as e:
        print(f"❌ DatabaseManager import error: {e}")
        return False
    
    try:
        from scripts.sentiment_analysis import SentimentAnalyzer
        print("✅ SentimentAnalyzer import OK")
    except ImportError as e:
        print(f"❌ SentimentAnalyzer import error: {e}")
        return False
    
    try:
        from scripts.auto_login import FacebookAutoLogin
        print("✅ FacebookAutoLogin import OK")
    except ImportError as e:
        print(f"❌ FacebookAutoLogin import error: {e}")
        return False
    
    try:
        from config.settings import BOT_CONFIG
        print("✅ Config import OK")
    except ImportError as e:
        print(f"❌ Config import error: {e}")
        return False
    
    return True

def test_database():
    """Test database functionality."""
    print("\n🗄️  Testing database...")
    
    try:
        from scripts.database_manager import DatabaseManager
        
        # Test dengan database temporary
        test_db_path = "/tmp/test_messenger_bot.db"
        db_manager = DatabaseManager(test_db_path)
        
        # Initialize database
        db_manager.initialize_database()
        print("✅ Database initialization OK")
        
        # Test save message
        message_id = db_manager.save_message(
            user_id="test_user",
            user_name="Test User",
            message_text="Test message",
            sentiment_score=0.5,
            sentiment_label="positive"
        )
        print(f"✅ Save message OK (ID: {message_id})")
        
        # Test get statistics
        stats = db_manager.get_statistics()
        print(f"✅ Database statistics: {stats}")
        
        # Cleanup
        os.remove(test_db_path)
        print("✅ Database test cleanup OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

def test_sentiment_analysis():
    """Test sentiment analysis functionality."""
    print("\n🎭 Testing sentiment analysis...")
    
    try:
        from scripts.sentiment_analysis import SentimentAnalyzer
        
        analyzer = SentimentAnalyzer()
        
        # Test cases
        test_cases = [
            ("Senang sekali hari ini!", "positive"),
            ("Sedih banget nih", "negative"),
            ("Apa kabar?", "neutral")
        ]
        
        for text, expected_label in test_cases:
            score, label = analyzer.analyze_sentiment(text)
            response = analyzer.get_response(label, "Test User")
            
            print(f"✅ '{text}' → {score:.2f} ({label}) → '{response}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Sentiment analysis test error: {e}")
        return False

def test_selenium_dependencies():
    """Test Selenium dependencies."""
    print("\n🌐 Testing Selenium dependencies...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        print("✅ Selenium import OK")
        
        # Test Chrome options (tanpa initialize driver)
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        print("✅ Chrome options OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Selenium import error: {e}")
        return False

def test_configuration():
    """Test configuration files."""
    print("\n⚙️  Testing configuration...")
    
    try:
        from config.settings import BOT_CONFIG, SENTIMENT_CONFIG, RESPONSE_TEMPLATES
        
        print(f"✅ BOT_CONFIG loaded: {len(BOT_CONFIG)} settings")
        print(f"✅ SENTIMENT_CONFIG loaded: {len(SENTIMENT_CONFIG)} settings")
        print(f"✅ RESPONSE_TEMPLATES loaded: {len(RESPONSE_TEMPLATES)} templates")
        
        # Check if credentials exist
        credentials_path = Path("config/credentials.py")
        if credentials_path.exists():
            print("✅ credentials.py found")
            try:
                from config.credentials import FACEBOOK_CREDENTIALS
                if FACEBOOK_CREDENTIALS['email'] != 'your_email@example.com':
                    print("✅ Credentials configured")
                else:
                    print("⚠️  Credentials not configured (using template values)")
            except ImportError:
                print("⚠️  Credentials import error")
        else:
            print("⚠️  credentials.py not found")
            print("   Copy credentials_template.py to credentials.py and configure it")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False

def main():
    """Main test function."""
    print("🤖 Bot Messenger - Installation Test")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Database", test_database),
        ("Sentiment Analysis", test_sentiment_analysis),
        ("Selenium Dependencies", test_selenium_dependencies),
        ("Configuration", test_configuration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Bot is ready to run.")
        print("\nNext steps:")
        print("1. Configure credentials.py with your Facebook login")
        print("2. Run: python main.py")
    else:
        print("❌ Some tests failed. Please fix the issues before running the bot.")
        
        if passed < total:
            print("\nCommon fixes:")
            print("- Install missing dependencies: pip install -r requirements.txt")
            print("- Copy and configure credentials: cp config/credentials_template.py config/credentials.py")
            print("- Install ChromeDriver: https://chromedriver.chromium.org/")

if __name__ == "__main__":
    main()