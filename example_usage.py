#!/usr/bin/env python3
"""
Example usage of the Messenger Bot
This script demonstrates how to use the bot components
"""

from messenger_bot import MessengerBot
from database import DatabaseManager
from sentiment_analyzer import SentimentAnalyzer
import config


def example_basic_usage():
    """Example of basic bot functionality without Selenium"""
    print("🤖 Basic Bot Usage Example")
    print("=" * 50)
    
    # Initialize components
    db = DatabaseManager()
    analyzer = SentimentAnalyzer()
    
    # Example messages
    messages = [
        "Halo! Apa kabar hari ini?",
        "Saya sangat senang dengan layanan ini!",
        "Saya merasa kecewa dengan hasilnya.",
        "Bisakah Anda membantu saya?"
    ]
    
    user_id = "example_user"
    
    for message in messages:
        # Analyze sentiment and generate response
        response, score, label = analyzer.analyze_and_respond(message)
        
        # Save to database
        db.save_conversation(user_id, message, response, score, label)
        
        # Display interaction
        sentiment_info = analyzer.format_sentiment_info(score, label)
        print(f"\nUser: {message}")
        print(f"Bot: {response}")
        print(f"Sentiment: {sentiment_info}")
    
    # Show conversation history
    print("\n📚 Conversation History:")
    print("-" * 30)
    history = db.get_user_history(user_id)
    for i, (user_msg, bot_resp, score, label, timestamp) in enumerate(history, 1):
        emoji = analyzer.get_sentiment_emoji(label)
        print(f"{i}. {emoji} {user_msg[:40]}...")
        print(f"   → {bot_resp[:40]}...")


def example_selenium_setup():
    """Example of setting up the Selenium bot (without actual login)"""
    print("\n🌐 Selenium Bot Setup Example")
    print("=" * 50)
    
    # Initialize bot
    bot = MessengerBot(headless=True)  # Use headless mode for demo
    
    try:
        # Setup Chrome WebDriver
        bot.setup_driver()
        print("✅ Chrome WebDriver setup successful")
        
        # In real usage, you would login:
        # success = bot.login_to_messenger("your_email@example.com", "your_password")
        # if success:
        #     bot.monitor_and_respond("Friend Name")
        
        print("ℹ️  In real usage, you would call:")
        print("   bot.login_to_messenger(email, password)")
        print("   bot.monitor_and_respond('Friend Name')")
        
    except Exception as e:
        print(f"❌ Error setting up Selenium: {e}")
        print("This is expected in a headless environment without a browser")
    finally:
        bot.close()


def example_database_operations():
    """Example of database operations"""
    print("\n🗄️ Database Operations Example")
    print("=" * 50)
    
    db = DatabaseManager()
    
    # Add sample data
    sample_conversations = [
        ("user1", "Hello world", "Hi there!", 0.2, "neutral"),
        ("user1", "I love this!", "Great to hear!", 0.8, "positive"),
        ("user2", "This is bad", "Sorry about that", -0.5, "negative"),
        ("user2", "Thanks for help", "You're welcome!", 0.3, "positive")
    ]
    
    for conv in sample_conversations:
        db.save_conversation(*conv)
    
    # Show statistics
    print("User 1 stats:", db.get_user_stats("user1"))
    print("User 2 stats:", db.get_user_stats("user2"))
    
    # Show recent conversations
    recent = db.get_all_conversations(5)
    print(f"\nRecent conversations ({len(recent)}):")
    for user_id, user_msg, bot_resp, score, label, timestamp in recent:
        print(f"  {user_id}: {user_msg[:20]}... → {bot_resp[:20]}... [{label}]")


def main():
    """Run all examples"""
    try:
        example_basic_usage()
        example_database_operations()
        example_selenium_setup()
        
        print("\n🎉 All examples completed successfully!")
        print("\nNext steps:")
        print("1. Run 'python demo_bot.py' for interactive testing")
        print("2. Run 'python test_bot.py' to execute unit tests")
        print("3. Run 'python messenger_bot.py' for actual Messenger automation")
        print("   (requires Facebook credentials and Chrome browser)")
        
    except Exception as e:
        print(f"❌ Error in examples: {e}")


if __name__ == "__main__":
    main()