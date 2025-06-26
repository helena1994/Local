"""
Sentiment analysis module using TextBlob for emotional responses
"""

from textblob import TextBlob
import random
from typing import Tuple
import config


class SentimentAnalyzer:
    """Analyzes sentiment of messages and generates appropriate responses"""
    
    def __init__(self):
        """Initialize sentiment analyzer"""
        self.positive_threshold = config.POSITIVE_THRESHOLD
        self.negative_threshold = config.NEGATIVE_THRESHOLD
    
    def analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """
        Analyze sentiment of given text
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (sentiment_score, sentiment_label)
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > self.positive_threshold:
            label = "positive"
        elif polarity < self.negative_threshold:
            label = "negative"
        else:
            label = "neutral"
            
        return polarity, label
    
    def get_emotional_response(self, sentiment_score: float, sentiment_label: str) -> str:
        """
        Generate appropriate response based on sentiment analysis
        
        Args:
            sentiment_score: Numerical sentiment score
            sentiment_label: Sentiment label (positive/negative/neutral)
            
        Returns:
            Appropriate response string
        """
        if sentiment_label == "positive":
            return random.choice(config.POSITIVE_RESPONSES)
        elif sentiment_label == "negative":
            return random.choice(config.NEGATIVE_RESPONSES)
        else:
            return random.choice(config.NEUTRAL_RESPONSES)
    
    def analyze_and_respond(self, text: str) -> Tuple[str, float, str]:
        """
        Analyze text and generate appropriate response
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (response, sentiment_score, sentiment_label)
        """
        sentiment_score, sentiment_label = self.analyze_sentiment(text)
        response = self.get_emotional_response(sentiment_score, sentiment_label)
        return response, sentiment_score, sentiment_label
    
    def get_sentiment_emoji(self, sentiment_label: str) -> str:
        """Get emoji representation of sentiment"""
        emoji_map = {
            "positive": "😊",
            "negative": "😟", 
            "neutral": "😐"
        }
        return emoji_map.get(sentiment_label, "🤖")
    
    def format_sentiment_info(self, sentiment_score: float, sentiment_label: str) -> str:
        """Format sentiment information for logging/display"""
        emoji = self.get_sentiment_emoji(sentiment_label)
        return f"{sentiment_label.capitalize()} {emoji} (Score: {sentiment_score:.2f})"