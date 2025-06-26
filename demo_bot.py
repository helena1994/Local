#!/usr/bin/env python3
"""
Demo script for the Messenger Bot functionality
This demonstrates the bot's core features without requiring Facebook login
"""

import time
from database import DatabaseManager
from sentiment_analyzer import SentimentAnalyzer


class MessengerBotDemo:
    """Demo version of the Messenger Bot for testing purposes"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.sentiment_analyzer = SentimentAnalyzer()
        print("🤖 Messenger Bot Demo initialized!")
        print("This demo simulates the bot's sentiment analysis and memory features.")
        print("-" * 60)
    
    def simulate_conversation(self, user_id: str = "demo_user"):
        """Simulate a conversation with the bot"""
        print(f"Starting conversation simulation with user: {user_id}")
        print("Type your messages (type 'quit' to exit, 'history' to see conversation history)")
        print("-" * 60)
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye! Thanks for testing the bot.")
                break
            elif user_input.lower() == 'history':
                self.show_conversation_history(user_id)
                continue
            elif not user_input:
                continue
                
            # Process message with sentiment analysis
            response, sentiment_score, sentiment_label = self.sentiment_analyzer.analyze_and_respond(user_input)
            
            # Save to database
            self.db_manager.save_conversation(
                user_id, user_input, response, sentiment_score, sentiment_label
            )
            
            # Display response with sentiment info
            sentiment_info = self.sentiment_analyzer.format_sentiment_info(sentiment_score, sentiment_label)
            print(f"Bot: {response}")
            print(f"     [Sentiment: {sentiment_info}]")
    
    def show_conversation_history(self, user_id: str, limit: int = 10):
        """Display conversation history for a user"""
        history = self.db_manager.get_user_history(user_id, limit)
        
        if not history:
            print("📝 No conversation history found.")
            return
            
        print(f"\n📚 Last {len(history)} conversations:")
        print("-" * 60)
        
        for i, (user_msg, bot_resp, sentiment_score, sentiment_label, timestamp) in enumerate(reversed(history), 1):
            emoji = self.sentiment_analyzer.get_sentiment_emoji(sentiment_label)
            print(f"{i}. You: {user_msg}")
            print(f"   Bot: {bot_resp}")
            print(f"   {emoji} {sentiment_label} ({sentiment_score:.2f}) - {timestamp}")
            print()
    
    def show_all_users_stats(self):
        """Show statistics for all users"""
        conversations = self.db_manager.get_all_conversations(100)
        
        if not conversations:
            print("📊 No conversations found in database.")
            return
            
        # Group by user
        user_stats = {}
        for user_id, user_msg, bot_resp, sentiment_score, sentiment_label, timestamp in conversations:
            if user_id not in user_stats:
                user_stats[user_id] = {
                    'total': 0,
                    'positive': 0,
                    'negative': 0,
                    'neutral': 0
                }
            user_stats[user_id]['total'] += 1
            user_stats[user_id][sentiment_label] += 1
        
        print("\n📊 User Statistics:")
        print("-" * 60)
        for user_id, stats in user_stats.items():
            print(f"👤 {user_id}:")
            print(f"   Total messages: {stats['total']}")
            print(f"   😊 Positive: {stats['positive']}")
            print(f"   😟 Negative: {stats['negative']}")
            print(f"   😐 Neutral: {stats['neutral']}")
            print()
    
    def run_demo_mode(self):
        """Run interactive demo"""
        while True:
            print("\n🤖 Messenger Bot Demo Menu:")
            print("1. Start conversation simulation")
            print("2. View conversation history")
            print("3. View user statistics")
            print("4. Test sentiment analysis")
            print("5. Exit")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                user_id = input("Enter user ID (default: demo_user): ").strip() or "demo_user"
                self.simulate_conversation(user_id)
            elif choice == '2':
                user_id = input("Enter user ID (default: demo_user): ").strip() or "demo_user"
                self.show_conversation_history(user_id)
            elif choice == '3':
                self.show_all_users_stats()
            elif choice == '4':
                self.test_sentiment_analysis()
            elif choice == '5':
                print("👋 Exiting demo. Thank you!")
                break
            else:
                print("❌ Invalid option. Please select 1-5.")
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis with predefined examples"""
        test_cases = [
            "I love this bot! It's amazing and wonderful!",
            "This is terrible and I hate everything about it.",
            "The weather is okay today.",
            "I'm feeling great and excited about today!",
            "I'm sad and disappointed with the results.",
            "This is just a normal message without much emotion.",
            "Wow! This is absolutely fantastic and incredible!",
            "I'm so angry and frustrated right now.",
            "The meeting is scheduled for tomorrow at 3 PM."
        ]
        
        print("\n🧪 Sentiment Analysis Test:")
        print("-" * 60)
        
        for i, text in enumerate(test_cases, 1):
            response, score, label = self.sentiment_analyzer.analyze_and_respond(text)
            emoji = self.sentiment_analyzer.get_sentiment_emoji(label)
            
            print(f"{i}. Text: {text}")
            print(f"   Sentiment: {label} {emoji} (Score: {score:.3f})")
            print(f"   Response: {response}")
            print()


def main():
    """Main function to run the demo"""
    print("🚀 Starting Messenger Bot Demo...")
    print("This demo showcases the bot's sentiment analysis and memory features.")
    print("In a real implementation, this would connect to Facebook Messenger via Selenium.")
    print("=" * 70)
    
    demo = MessengerBotDemo()
    demo.run_demo_mode()


if __name__ == "__main__":
    main()