"""
Database manager untuk menyimpan riwayat pesan dan interaksi.

Menggunakan SQLite untuk menyimpan:
- Riwayat pesan masuk dan keluar
- Data pengguna dan preferensi
- Log aktivitas bot
"""

import sqlite3
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import sys

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Class untuk mengelola database SQLite bot."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize database manager.
        
        Args:
            db_path: Path ke file database SQLite
        """
        if db_path is None:
            # Add project root to path for importing config
            project_root = Path(__file__).parent.parent
            sys.path.insert(0, str(project_root))
            
            from config.settings import DATABASE_CONFIG
            db_path = DATABASE_CONFIG['db_path']
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
    def initialize_database(self):
        """Inisialisasi database dan buat tabel jika belum ada."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabel untuk menyimpan pesan
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        user_name TEXT,
                        message_text TEXT NOT NULL,
                        message_type TEXT NOT NULL DEFAULT 'incoming',
                        sentiment_score REAL,
                        sentiment_label TEXT,
                        response_text TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        processed BOOLEAN DEFAULT 0
                    )
                ''')
                
                # Tabel untuk menyimpan data pengguna
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        user_name TEXT,
                        first_interaction DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_interaction DATETIME DEFAULT CURRENT_TIMESTAMP,
                        message_count INTEGER DEFAULT 0,
                        preferences TEXT DEFAULT '{}'
                    )
                ''')
                
                # Tabel untuk log aktivitas bot
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS activity_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        activity_type TEXT NOT NULL,
                        description TEXT,
                        status TEXT DEFAULT 'success',
                        error_message TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Index untuk performa query
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_processed ON messages(processed)')
                
                conn.commit()
                logger.info("✅ Database berhasil diinisialisasi")
                
        except Exception as e:
            logger.error(f"❌ Error saat inisialisasi database: {e}")
            raise
    
    def save_message(self, user_id: str, user_name: str, message_text: str, 
                    message_type: str = 'incoming', sentiment_score: float = None,
                    sentiment_label: str = None, response_text: str = None) -> int:
        """
        Simpan pesan ke database.
        
        Args:
            user_id: ID pengguna
            user_name: Nama pengguna
            message_text: Teks pesan
            message_type: Tipe pesan ('incoming' atau 'outgoing')
            sentiment_score: Skor sentimen (-1 to 1)
            sentiment_label: Label sentimen ('positive', 'negative', 'neutral')
            response_text: Teks respons bot
            
        Returns:
            ID pesan yang tersimpan
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO messages 
                    (user_id, user_name, message_text, message_type, 
                     sentiment_score, sentiment_label, response_text)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, user_name, message_text, message_type,
                      sentiment_score, sentiment_label, response_text))
                
                message_id = cursor.lastrowid
                conn.commit()
                
                # Update user data
                self._update_user_data(user_id, user_name)
                
                logger.info(f"✅ Pesan disimpan dengan ID: {message_id}")
                return message_id
                
        except Exception as e:
            logger.error(f"❌ Error saat menyimpan pesan: {e}")
            raise
    
    def _update_user_data(self, user_id: str, user_name: str):
        """Update data pengguna di database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, user_name, first_interaction, last_interaction, message_count)
                    VALUES (
                        ?, ?, 
                        COALESCE((SELECT first_interaction FROM users WHERE user_id = ?), CURRENT_TIMESTAMP),
                        CURRENT_TIMESTAMP,
                        COALESCE((SELECT message_count FROM users WHERE user_id = ?), 0) + 1
                    )
                ''', (user_id, user_name, user_id, user_id))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Error saat update user data: {e}")
    
    def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Ambil riwayat pesan pengguna.
        
        Args:
            user_id: ID pengguna
            limit: Jumlah pesan yang diambil
            
        Returns:
            List pesan dalam format dictionary
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM messages 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (user_id, limit))
                
                messages = [dict(row) for row in cursor.fetchall()]
                return messages
                
        except Exception as e:
            logger.error(f"❌ Error saat mengambil riwayat: {e}")
            return []
    
    def get_unprocessed_messages(self) -> List[Dict]:
        """Ambil pesan yang belum diproses."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM messages 
                    WHERE processed = 0 AND message_type = 'incoming'
                    ORDER BY timestamp ASC
                ''')
                
                messages = [dict(row) for row in cursor.fetchall()]
                return messages
                
        except Exception as e:
            logger.error(f"❌ Error saat mengambil pesan belum diproses: {e}")
            return []
    
    def mark_message_processed(self, message_id: int):
        """Tandai pesan sebagai sudah diproses."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE messages 
                    SET processed = 1 
                    WHERE id = ?
                ''', (message_id,))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Error saat menandai pesan processed: {e}")
    
    def log_activity(self, activity_type: str, description: str, 
                    status: str = 'success', error_message: str = None):
        """
        Log aktivitas bot.
        
        Args:
            activity_type: Jenis aktivitas
            description: Deskripsi aktivitas
            status: Status ('success', 'error', 'warning')
            error_message: Pesan error (jika ada)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO activity_log 
                    (activity_type, description, status, error_message)
                    VALUES (?, ?, ?, ?)
                ''', (activity_type, description, status, error_message))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Error saat logging aktivitas: {e}")
    
    def get_statistics(self) -> Dict:
        """Ambil statistik database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total pesan
                cursor.execute('SELECT COUNT(*) FROM messages')
                total_messages = cursor.fetchone()[0]
                
                # Total pengguna
                cursor.execute('SELECT COUNT(*) FROM users')
                total_users = cursor.fetchone()[0]
                
                # Pesan hari ini
                cursor.execute('''
                    SELECT COUNT(*) FROM messages 
                    WHERE date(timestamp) = date('now')
                ''')
                messages_today = cursor.fetchone()[0]
                
                return {
                    'total_messages': total_messages,
                    'total_users': total_users,
                    'messages_today': messages_today
                }
                
        except Exception as e:
            logger.error(f"❌ Error saat mengambil statistik: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 30):
        """
        Bersihkan data lama.
        
        Args:
            days: Hapus data lebih lama dari X hari
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM activity_log 
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"✅ Dihapus {deleted_count} record lama")
                
        except Exception as e:
            logger.error(f"❌ Error saat cleanup data: {e}")