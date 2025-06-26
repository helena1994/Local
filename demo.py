#!/usr/bin/env python3
"""
Demo script untuk menunjukkan fungsionalitas bot Messenger.

Script ini akan:
1. Inisialisasi database
2. Demo analisis sentimen
3. Simulasi percakapan bot
4. Menampilkan statistik
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.database_manager import DatabaseManager
from scripts.sentiment_analysis import SentimentAnalyzer
import time

def demo_sentiment_analysis():
    """Demo analisis sentimen dengan berbagai pesan."""
    print("🎭 Demo Analisis Sentimen")
    print("=" * 50)
    
    analyzer = SentimentAnalyzer()
    
    test_messages = [
        "Halo! Selamat pagi, apa kabar?",
        "Senang sekali hari ini bisa bertemu teman lama!",
        "Sedih banget nih, hujan terus dari tadi",
        "Terima kasih ya sudah membantu kemarin",
        "Wah mantap banget hasilnya!",
        "Capek deh kerja terus",
        "Gimana kabarnya? Lagi ngapain?",
        "Maaf ya terlambat reply",
        "Keren banget fotonya!",
        "Stress banget sama deadline"
    ]
    
    print("Menganalisis berbagai pesan:")
    print()
    
    for message in test_messages:
        score, label = analyzer.analyze_sentiment(message)
        response = analyzer.get_advanced_response(message, score, label, "User")
        
        # Color coding untuk terminal
        if label == 'positive':
            color = '\033[92m'  # Green
        elif label == 'negative':
            color = '\033[91m'  # Red
        else:
            color = '\033[93m'  # Yellow
        
        reset_color = '\033[0m'
        
        print(f"📨 '{message}'")
        print(f"   {color}Sentimen: {score:.2f} ({label}){reset_color}")
        print(f"   🤖 Respons: {response}")
        print()

def demo_database():
    """Demo fungsi database."""
    print("🗄️  Demo Database")
    print("=" * 50)
    
    # Initialize database manager
    db_manager = DatabaseManager("/tmp/demo_messenger_bot.db")
    db_manager.initialize_database()
    print("✅ Database diinisialisasi")
    
    # Simulasi percakapan
    conversations = [
        {"user": "Alice", "message": "Halo bot! Apa kabar?"},
        {"user": "Bob", "message": "Hari ini senang banget!"},
        {"user": "Alice", "message": "Terima kasih sudah membantu kemarin"},
        {"user": "Charlie", "message": "Sedih nih lagi galau"},
        {"user": "Bob", "message": "Wah mantap hasilnya!"},
    ]
    
    analyzer = SentimentAnalyzer()
    
    print("\n💬 Simulasi percakapan:")
    print()
    
    for conv in conversations:
        # Analisis sentimen
        score, label = analyzer.analyze_sentiment(conv["message"])
        
        # Simpan pesan ke database
        message_id = db_manager.save_message(
            user_id=conv["user"].lower(),
            user_name=conv["user"],
            message_text=conv["message"],
            message_type='incoming',
            sentiment_score=score,
            sentiment_label=label
        )
        
        # Generate dan simpan respons
        response = analyzer.get_advanced_response(
            conv["message"], score, label, conv["user"]
        )
        
        db_manager.save_message(
            user_id=conv["user"].lower(),
            user_name="Bot",
            message_text=response,
            message_type='outgoing'
        )
        
        print(f"👤 {conv['user']}: {conv['message']}")
        print(f"🤖 Bot: {response}")
        print()
    
    # Tampilkan statistik
    print("📊 Statistik Database:")
    stats = db_manager.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n📋 Riwayat Percakapan Alice:")
    alice_history = db_manager.get_user_history("alice", limit=5)
    for msg in alice_history:
        direction = "📤" if msg['message_type'] == 'outgoing' else "📥"
        print(f"   {direction} {msg['message_text']}")
    
    # Cleanup
    import os
    os.remove("/tmp/demo_messenger_bot.db")
    print("\n✅ Demo database selesai")

def demo_conversation_trend():
    """Demo analisis trend percakapan."""
    print("\n🔍 Demo Analisis Trend Percakapan")
    print("=" * 50)
    
    analyzer = SentimentAnalyzer()
    
    # Simulasi riwayat pesan dengan trend yang berubah
    message_history = [
        {"message_text": "Hari ini biasa aja"},
        {"message_text": "Agak sedih nih"},
        {"message_text": "Mulai membaik kayaknya"},
        {"message_text": "Wah senang banget hari ini!"},
        {"message_text": "Terima kasih ya udah support!"}
    ]
    
    trend_analysis = analyzer.analyze_conversation_trend(message_history)
    
    print("Riwayat pesan:")
    for i, msg in enumerate(message_history, 1):
        score, label = analyzer.analyze_sentiment(msg["message_text"])
        print(f"{i}. '{msg['message_text']}' → {score:.2f} ({label})")
    
    print(f"\n📈 Analisis Trend:")
    print(f"   Trend: {trend_analysis['trend']}")
    print(f"   Rata-rata sentimen: {trend_analysis['average_sentiment']:.2f}")
    print(f"   Jumlah pesan: {trend_analysis['message_count']}")

def demo_response_variations():
    """Demo variasi respons berdasarkan konteks."""
    print("\n🎯 Demo Variasi Respons")
    print("=" * 50)
    
    analyzer = SentimentAnalyzer()
    
    contexts = [
        ("Halo bot!", "Sapaan"),
        ("Terima kasih banyak!", "Ucapan terima kasih"),
        ("Gimana cara pakai fitur ini?", "Pertanyaan"),
        ("Maaf ya telat reply", "Permintaan maaf"),
        ("Keren banget!", "Pujian"),
    ]
    
    for message, context_type in contexts:
        score, label = analyzer.analyze_sentiment(message)
        response = analyzer.get_advanced_response(message, score, label, "User")
        
        print(f"📝 Konteks: {context_type}")
        print(f"   Pesan: '{message}'")
        print(f"   Respons: {response}")
        print()

def main():
    """Main demo function."""
    print("🤖 Demo Bot Messenger Otomatis")
    print("=" * 60)
    print("Demo ini menunjukkan fungsionalitas utama bot tanpa")
    print("memerlukan browser Chrome atau login Facebook.")
    print("=" * 60)
    
    # Run all demos
    demo_sentiment_analysis()
    print("\n" + "="*60 + "\n")
    
    demo_database()
    print("\n" + "="*60 + "\n")
    
    demo_conversation_trend()
    print("\n" + "="*60 + "\n")
    
    demo_response_variations()
    print("\n" + "="*60 + "\n")
    
    print("✨ Demo selesai!")
    print("\nUntuk menjalankan bot secara lengkap:")
    print("1. Install ChromeDriver")
    print("2. Konfigurasi credentials.py dengan login Facebook")
    print("3. Jalankan: python main.py")

if __name__ == "__main__":
    main()