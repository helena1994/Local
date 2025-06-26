#!/usr/bin/env python3
"""
Simple test script to demonstrate bot functionality without Selenium.
This can be used to test core features before setting up the full automation.
"""

import sys
import logging
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from scripts.database_manager import DatabaseManager
from scripts.sentiment_analysis import SentimentAnalyzer


def setup_logging():
    """Setup basic logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def test_sentiment_analysis():
    """Test sentiment analysis functionality."""
    print("\n🧠 Testing Sentiment Analysis")
    print("=" * 40)
    
    analyzer = SentimentAnalyzer()
    
    test_messages = [
        "I love this new feature! It's amazing! 😍",
        "This is terrible, I hate it so much 😠",
        "The weather is okay today",
        "Thanks for your help, much appreciated! 👍",
        "I'm having a really bad day 😢",
        "Everything is working perfectly!",
        "I need some help with this problem",
        "Great job on the implementation! 🌟"
    ]
    
    for message in test_messages:
        result = analyzer.analyze_and_respond(message)
        print(f"Message: \"{message}\"")
        print(f"  Sentiment: {result['sentiment_label']} ({result['sentiment_score']:.3f})")
        print(f"  Response: \"{result['response']}\"")
        print()


def test_database_operations():
    """Test database functionality."""
    print("\n💾 Testing Database Operations")
    print("=" * 40)
    
    # Use temporary database
    db = DatabaseManager('/tmp/messenger_bot_test.db')
    db.initialize_database()
    print("✓ Database initialized")
    
    # Store some test messages
    messages_data = [
        ("alice", "bot", "Hello bot!", 0.3, "positive"),
        ("bob", "bot", "I'm having issues", -0.5, "negative"),
        ("bot", "alice", "Hi Alice! How can I help?", 0.2, "positive"),
        ("bot", "bob", "I'm sorry to hear that. Let me help.", 0.1, "neutral"),
        ("alice", "bot", "Thanks for the help! 😊", 0.8, "positive")
    ]
    
    stored_ids = []
    for sender, recipient, message, sentiment, label in messages_data:
        msg_id = db.store_message(sender, recipient, message, sentiment, label)
        stored_ids.append(msg_id)
        print(f"✓ Stored message {msg_id}: {sender} -> {recipient}")
    
    # Retrieve and display messages
    print(f"\n📊 Retrieved Messages:")
    messages = db.get_messages(limit=10)
    for msg in messages:
        print(f"  {msg['timestamp']}: {msg['sender']} -> {msg['recipient']}")
        print(f"    \"{msg['message']}\" ({msg['sentiment_label']})")
    
    # Show conversation history
    print(f"\n💬 Conversation History (alice <-> bot):")
    history = db.get_conversation_history("alice", "bot")
    for msg in history:
        direction = "→" if msg['sender'] == "alice" else "←"
        print(f"  {msg['sender']} {direction} {msg['recipient']}: \"{msg['message']}\"")
    
    # Display statistics
    print(f"\n📈 Database Statistics:")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")


def demo_bot_workflow():
    """Demonstrate complete bot workflow."""
    print("\n🤖 Bot Workflow Demonstration")
    print("=" * 40)
    
    # Initialize components
    analyzer = SentimentAnalyzer()
    db = DatabaseManager('/tmp/messenger_demo.db')
    db.initialize_database()
    
    # Simulate incoming messages
    incoming_messages = [
        "Hi bot! How are you doing today?",
        "I'm really frustrated with this software 😠",
        "Can you help me with my problem?",
        "Thank you so much for your assistance! 🙏",
        "I don't understand how this works"
    ]
    
    print("Simulating incoming messages and bot responses:\n")
    
    for i, message in enumerate(incoming_messages, 1):
        print(f"📨 Message {i} from user: \"{message}\"")
        
        # Analyze sentiment
        analysis = analyzer.analyze_and_respond(message)
        
        # Store user message
        user_msg_id = db.store_message(
            sender="user",
            recipient="bot", 
            message=message,
            sentiment=analysis['sentiment_score'],
            sentiment_label=analysis['sentiment_label']
        )
        
        # Generate and store bot response
        bot_response = analysis['response']
        bot_msg_id = db.store_message(
            sender="bot",
            recipient="user",
            message=bot_response,
            metadata={'auto_reply': True, 'in_response_to': user_msg_id}
        )
        
        print(f"🤖 Bot response: \"{bot_response}\"")
        print(f"   Sentiment detected: {analysis['sentiment_label']} ({analysis['sentiment_score']:.3f})")
        print(f"   Stored as messages {user_msg_id} and {bot_msg_id}")
        print()
    
    # Show final statistics
    print("📊 Final Statistics:")
    stats = db.get_statistics()
    print(f"  Total messages processed: {stats['total_messages']}")
    print(f"  Sentiment distribution: {stats['sentiment_distribution']}")


def main():
    """Main test function."""
    print("🧪 Python Messenger Bot - Test Suite")
    print("=" * 50)
    
    setup_logging()
    
    try:
        test_sentiment_analysis()
        test_database_operations()
        demo_bot_workflow()
        
        print("\n✅ All tests completed successfully!")
        print("\n📝 Next steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Configure credentials: cp config/credentials_template.py config/credentials.py")
        print("  3. Run the full bot: python main.py")
        
    except Exception as e:
        logging.error(f"Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()