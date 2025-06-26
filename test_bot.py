"""
Basic tests for the Messenger Bot components
"""

import unittest
import tempfile
import os
from database import DatabaseManager
from sentiment_analyzer import SentimentAnalyzer


class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager"""
    
    def setUp(self):
        """Set up test database"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        self.test_db.close()
        self.db_manager = DatabaseManager(self.test_db.name)
    
    def tearDown(self):
        """Clean up test database"""
        os.unlink(self.test_db.name)
    
    def test_database_initialization(self):
        """Test database tables are created properly"""
        # Try to save a conversation to test if tables exist
        self.db_manager.save_conversation(
            "test_user", "Hello", "Hi there!", 0.5, "positive"
        )
        
        # Retrieve the conversation
        history = self.db_manager.get_user_history("test_user")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0][0], "Hello")
        self.assertEqual(history[0][1], "Hi there!")
    
    def test_conversation_storage(self):
        """Test conversation storage and retrieval"""
        # Save multiple conversations
        conversations = [
            ("user1", "Hello", "Hi!", 0.2, "positive"),
            ("user1", "How are you?", "I'm good!", 0.1, "neutral"),
            ("user2", "Bad day", "Sorry to hear", -0.3, "negative")
        ]
        
        for conv in conversations:
            self.db_manager.save_conversation(*conv)
        
        # Test user-specific history
        user1_history = self.db_manager.get_user_history("user1")
        self.assertEqual(len(user1_history), 2)
        
        # Test all conversations
        all_conversations = self.db_manager.get_all_conversations()
        self.assertEqual(len(all_conversations), 3)
    
    def test_user_stats(self):
        """Test user statistics tracking"""
        # Save conversations for a user
        self.db_manager.save_conversation("test_user", "Hi", "Hello!", 0.1, "neutral")
        self.db_manager.save_conversation("test_user", "Bye", "Goodbye!", 0.0, "neutral")
        
        # Check user stats
        stats = self.db_manager.get_user_stats("test_user")
        self.assertIsNotNone(stats)
        self.assertEqual(stats[2], 2)  # total_messages should be 2


class TestSentimentAnalyzer(unittest.TestCase):
    """Test cases for SentimentAnalyzer"""
    
    def setUp(self):
        """Set up sentiment analyzer"""
        self.analyzer = SentimentAnalyzer()
    
    def test_positive_sentiment(self):
        """Test positive sentiment detection"""
        positive_text = "I love this! It's amazing and wonderful!"
        score, label = self.analyzer.analyze_sentiment(positive_text)
        self.assertEqual(label, "positive")
        self.assertGreater(score, 0)
    
    def test_negative_sentiment(self):
        """Test negative sentiment detection"""
        negative_text = "I hate this. It's terrible and awful."
        score, label = self.analyzer.analyze_sentiment(negative_text)
        self.assertEqual(label, "negative")
        self.assertLess(score, 0)
    
    def test_neutral_sentiment(self):
        """Test neutral sentiment detection"""
        neutral_text = "This is a book. It has pages."
        score, label = self.analyzer.analyze_sentiment(neutral_text)
        self.assertEqual(label, "neutral")
    
    def test_emotional_response_generation(self):
        """Test emotional response generation"""
        # Test positive response
        pos_response = self.analyzer.get_emotional_response(0.5, "positive")
        positive_emojis = ["😊", "🌟", "😄"]
        self.assertTrue(any(emoji in pos_response for emoji in positive_emojis))
        
        # Test negative response  
        neg_response = self.analyzer.get_emotional_response(-0.5, "negative")
        negative_emojis = ["💙", "🤗", "💭"]
        self.assertTrue(any(emoji in neg_response for emoji in negative_emojis))
        
        # Test neutral response
        neu_response = self.analyzer.get_emotional_response(0.0, "neutral")
        neutral_emojis = ["😊", "👍", "📝"]
        self.assertTrue(any(emoji in neu_response for emoji in neutral_emojis))
    
    def test_analyze_and_respond(self):
        """Test complete analysis and response workflow"""
        test_message = "I'm having a great day!"
        response, score, label = self.analyzer.analyze_and_respond(test_message)
        
        self.assertIsInstance(response, str)
        self.assertIsInstance(score, float)
        self.assertIn(label, ["positive", "negative", "neutral"])
        self.assertGreater(len(response), 0)
    
    def test_sentiment_emoji(self):
        """Test sentiment emoji generation"""
        self.assertEqual(self.analyzer.get_sentiment_emoji("positive"), "😊")
        self.assertEqual(self.analyzer.get_sentiment_emoji("negative"), "😟")
        self.assertEqual(self.analyzer.get_sentiment_emoji("neutral"), "😐")
        self.assertEqual(self.analyzer.get_sentiment_emoji("unknown"), "🤖")


if __name__ == "__main__":
    unittest.main()