"""
Sentiment analysis module for analyzing message sentiment.
"""

import logging
import random
from typing import Dict, Tuple, Optional

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    logging.warning("TextBlob not available. Using basic sentiment analysis.")

from config.settings import SENTIMENT_SETTINGS


class SentimentAnalyzer:
    """Analyzes sentiment of text messages."""
    
    def __init__(self):
        """Initialize sentiment analyzer."""
        self.logger = logging.getLogger(__name__)
        self.positive_threshold = SENTIMENT_SETTINGS['positive_threshold']
        self.negative_threshold = SENTIMENT_SETTINGS['negative_threshold']
        self.responses = SENTIMENT_SETTINGS['responses']
        
        if not TEXTBLOB_AVAILABLE:
            self.logger.warning("TextBlob not available. Using basic keyword-based analysis.")
    
    def analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (sentiment_score, sentiment_label)
            Score ranges from -1 (negative) to 1 (positive)
        """
        if TEXTBLOB_AVAILABLE:
            return self._textblob_analysis(text)
        else:
            return self._basic_analysis(text)
    
    def _textblob_analysis(self, text: str) -> Tuple[float, str]:
        """Perform sentiment analysis using TextBlob.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (sentiment_score, sentiment_label)
        """
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > self.positive_threshold:
                label = 'positive'
            elif polarity < self.negative_threshold:
                label = 'negative'
            else:
                label = 'neutral'
            
            self.logger.debug(f"TextBlob analysis: '{text[:50]}...' -> {polarity:.3f} ({label})")
            return polarity, label
            
        except Exception as e:
            self.logger.error(f"Error in TextBlob analysis: {e}")
            return self._basic_analysis(text)
    
    def _basic_analysis(self, text: str) -> Tuple[float, str]:
        """Perform basic keyword-based sentiment analysis.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (sentiment_score, sentiment_label)
        """
        text_lower = text.lower()
        
        positive_keywords = [
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'like', 'happy', 'joy', 'pleased', 'satisfied', 'awesome',
            'perfect', 'brilliant', 'outstanding', 'superb', 'marvelous',
            'delighted', 'excited', 'thrilled', 'glad', 'cheerful', 'positive',
            '😊', '😄', '😃', '😀', '🙂', '😍', '🥰', '😘', '🤗', '👍', '❤️', '💕'
        ]
        
        negative_keywords = [
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'sad',
            'angry', 'frustrated', 'disappointed', 'upset', 'annoyed', 'furious',
            'disgusted', 'depressed', 'worried', 'anxious', 'stressed', 'negative',
            'problem', 'issue', 'error', 'wrong', 'fail', 'broken', 'poor',
            '😢', '😭', '😞', '😔', '😟', '😕', '🙁', '😠', '😡', '🤬', '😤', '👎'
        ]
        
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        
        # Calculate score based on keyword counts
        total_words = len(text.split())
        if total_words == 0:
            return 0.0, 'neutral'
        
        positive_ratio = positive_count / total_words
        negative_ratio = negative_count / total_words
        
        score = positive_ratio - negative_ratio
        
        # Normalize score to -1 to 1 range
        score = max(-1.0, min(1.0, score * 5))  # Multiply by 5 to amplify the signal
        
        if score > self.positive_threshold:
            label = 'positive'
        elif score < self.negative_threshold:
            label = 'negative'
        else:
            label = 'neutral'
        
        self.logger.debug(f"Basic analysis: '{text[:50]}...' -> {score:.3f} ({label})")
        return score, label
    
    def get_response(self, sentiment_label: str) -> str:
        """Get an appropriate response based on sentiment.
        
        Args:
            sentiment_label: Sentiment label (positive/negative/neutral)
            
        Returns:
            Response message
        """
        responses = self.responses.get(sentiment_label, self.responses['neutral'])
        return random.choice(responses)
    
    def analyze_and_respond(self, text: str) -> Dict[str, any]:
        """Analyze sentiment and generate response.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with analysis results and response
        """
        score, label = self.analyze_sentiment(text)
        response = self.get_response(label)
        
        return {
            'sentiment_score': score,
            'sentiment_label': label,
            'response': response,
            'confidence': abs(score)
        }
    
    def batch_analyze(self, texts: list) -> list:
        """Analyze sentiment for multiple texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of analysis results
        """
        results = []
        for text in texts:
            analysis = self.analyze_and_respond(text)
            analysis['text'] = text
            results.append(analysis)
        
        return results
    
    def get_sentiment_summary(self, texts: list) -> Dict[str, any]:
        """Get sentiment summary for a list of texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            Summary statistics
        """
        if not texts:
            return {'total': 0, 'positive': 0, 'negative': 0, 'neutral': 0, 'average_score': 0}
        
        results = self.batch_analyze(texts)
        
        positive_count = sum(1 for r in results if r['sentiment_label'] == 'positive')
        negative_count = sum(1 for r in results if r['sentiment_label'] == 'negative')
        neutral_count = sum(1 for r in results if r['sentiment_label'] == 'neutral')
        
        average_score = sum(r['sentiment_score'] for r in results) / len(results)
        
        return {
            'total': len(texts),
            'positive': positive_count,
            'negative': negative_count,
            'neutral': neutral_count,
            'average_score': average_score,
            'positive_percentage': (positive_count / len(texts)) * 100,
            'negative_percentage': (negative_count / len(texts)) * 100,
            'neutral_percentage': (neutral_count / len(texts)) * 100
        }