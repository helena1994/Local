"""
Modul analisis sentimen menggunakan TextBlob.

Menganalisis emosi/sentimen dari pesan pengguna dan memberikan
respons yang sesuai berdasarkan sentimen yang terdeteksi.
"""

import random
import logging
from textblob import TextBlob
from typing import Tuple, Dict
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Class untuk analisis sentimen pesan."""
    
    def __init__(self):
        """Initialize sentiment analyzer."""
        # Add project root to path for importing config
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        from config.settings import SENTIMENT_CONFIG, RESPONSE_TEMPLATES
        self.config = SENTIMENT_CONFIG
        self.response_templates = RESPONSE_TEMPLATES
        
        # Kamus kata-kata bahasa Indonesia untuk sentiment
        self.positive_words = {
            'senang', 'bahagia', 'gembira', 'suka', 'bagus', 'hebat', 
            'mantap', 'keren', 'asik', 'wow', 'amazing', 'luar biasa',
            'terima kasih', 'thanks', 'makasih', 'love', 'sayang',
            'sukses', 'berhasil', 'menang', 'juara', 'bangga'
        }
        
        self.negative_words = {
            'sedih', 'kecewa', 'marah', 'benci', 'jelek', 'buruk',
            'gagal', 'rusak', 'sakit', 'capek', 'lelah', 'stress',
            'bosan', 'kesal', 'dongkol', 'sebel', 'hopeless',
            'putus asa', 'galau', 'down', 'bad', 'worst'
        }
    
    def analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """
        Analisis sentimen teks.
        
        Args:
            text: Teks yang akan dianalisis
            
        Returns:
            Tuple (sentiment_score, sentiment_label)
            - sentiment_score: Float antara -1 (negatif) hingga 1 (positif)
            - sentiment_label: 'positive', 'negative', atau 'neutral'
        """
        try:
            # Bersihkan teks
            cleaned_text = self._clean_text(text)
            
            # Analisis menggunakan TextBlob
            blob = TextBlob(cleaned_text)
            textblob_score = blob.sentiment.polarity
            
            # Analisis tambahan untuk bahasa Indonesia
            indonesian_score = self._analyze_indonesian_sentiment(cleaned_text)
            
            # Gabungkan kedua skor dengan weight
            final_score = (textblob_score * 0.6) + (indonesian_score * 0.4)
            
            # Tentukan label berdasarkan threshold
            if final_score > self.config['threshold_positive']:
                label = 'positive'
            elif final_score < self.config['threshold_negative']:
                label = 'negative'
            else:
                label = 'neutral'
            
            logger.info(f"📊 Sentimen '{text[:50]}...': {final_score:.2f} ({label})")
            return final_score, label
            
        except Exception as e:
            logger.error(f"❌ Error saat analisis sentimen: {e}")
            return 0.0, 'neutral'
    
    def _clean_text(self, text: str) -> str:
        """Bersihkan teks untuk analisis."""
        # Hapus emoji dan karakter khusus, convert ke lowercase
        import re
        cleaned = re.sub(r'[^\w\s]', ' ', text.lower())
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    def _analyze_indonesian_sentiment(self, text: str) -> float:
        """
        Analisis sentimen khusus untuk bahasa Indonesia.
        
        Args:
            text: Teks yang sudah dibersihkan
            
        Returns:
            Skor sentimen (-1 to 1)
        """
        words = text.split()
        positive_count = 0
        negative_count = 0
        
        for word in words:
            if word in self.positive_words:
                positive_count += 1
            elif word in self.negative_words:
                negative_count += 1
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            return 0.0
        
        # Hitung skor sentimen
        score = (positive_count - negative_count) / total_sentiment_words
        return max(-1.0, min(1.0, score))
    
    def get_response(self, sentiment_label: str, user_name: str = None) -> str:
        """
        Dapatkan respons berdasarkan sentimen.
        
        Args:
            sentiment_label: Label sentimen ('positive', 'negative', 'neutral')
            user_name: Nama pengguna (opsional)
            
        Returns:
            Teks respons yang sesuai
        """
        try:
            # Pilih template respons berdasarkan sentimen
            templates = self.response_templates.get(sentiment_label, 
                                                  self.response_templates['neutral'])
            
            # Pilih respons secara random
            response = random.choice(templates)
            
            # Personalisasi dengan nama pengguna jika ada
            if user_name:
                response = f"{user_name}, {response.lower()}"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error saat generate respons: {e}")
            return "Terima kasih sudah mengirim pesan! 😊"
    
    def get_advanced_response(self, text: str, sentiment_score: float, 
                            sentiment_label: str, user_name: str = None) -> str:
        """
        Dapatkan respons yang lebih advanced berdasarkan konteks.
        
        Args:
            text: Teks pesan asli
            sentiment_score: Skor sentimen
            sentiment_label: Label sentimen
            user_name: Nama pengguna
            
        Returns:
            Respons yang lebih kontekstual
        """
        try:
            # Deteksi konteks khusus
            text_lower = text.lower()
            
            # Respons untuk sapaan
            if any(greeting in text_lower for greeting in ['halo', 'hai', 'hello', 'selamat']):
                greetings = [
                    f"Halo {user_name}! Apa kabar? 😊",
                    f"Hai {user_name}! Senang bertemu denganmu! 👋",
                    f"Hello {user_name}! Gimana nih harinya? ✨"
                ]
                return random.choice(greetings) if user_name else random.choice(greetings).replace(f" {user_name}", "")
            
            # Respons untuk pertanyaan
            if any(question in text_lower for question in ['?', 'apa', 'gimana', 'bagaimana', 'kenapa']):
                if sentiment_label == 'negative':
                    return f"Sepertinya {user_name if user_name else 'kamu'} lagi ada masalah ya? Cerita aja, aku siap dengerin 👂"
                else:
                    return f"Hmm, pertanyaan yang menarik! Aku coba bantu jawab ya 🤔"
            
            # Respons untuk terima kasih
            if any(thanks in text_lower for thanks in ['terima kasih', 'thanks', 'makasih', 'thx']):
                return "Sama-sama! Senang bisa membantu 😊🙏"
            
            # Respons default berdasarkan sentimen
            return self.get_response(sentiment_label, user_name)
            
        except Exception as e:
            logger.error(f"❌ Error saat generate advanced respons: {e}")
            return self.get_response(sentiment_label, user_name)
    
    def analyze_conversation_trend(self, messages: list) -> Dict:
        """
        Analisis trend sentimen dalam percakapan.
        
        Args:
            messages: List pesan dalam percakapan
            
        Returns:
            Dictionary berisi analisis trend
        """
        try:
            if not messages:
                return {'trend': 'neutral', 'average_sentiment': 0.0}
            
            sentiments = []
            for msg in messages[-5:]:  # Analisis 5 pesan terakhir
                if msg.get('message_text'):
                    score, _ = self.analyze_sentiment(msg['message_text'])
                    sentiments.append(score)
            
            if not sentiments:
                return {'trend': 'neutral', 'average_sentiment': 0.0}
            
            avg_sentiment = sum(sentiments) / len(sentiments)
            
            # Tentukan trend
            if len(sentiments) >= 3:
                recent_avg = sum(sentiments[-3:]) / 3
                older_avg = sum(sentiments[:-3]) / len(sentiments[:-3]) if len(sentiments) > 3 else avg_sentiment
                
                if recent_avg > older_avg + 0.2:
                    trend = 'improving'
                elif recent_avg < older_avg - 0.2:
                    trend = 'declining'
                else:
                    trend = 'stable'
            else:
                trend = 'neutral'
            
            return {
                'trend': trend,
                'average_sentiment': avg_sentiment,
                'message_count': len(sentiments)
            }
            
        except Exception as e:
            logger.error(f"❌ Error saat analisis trend: {e}")
            return {'trend': 'neutral', 'average_sentiment': 0.0}