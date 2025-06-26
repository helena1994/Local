"""
Database module for storing conversation memory using SQLite
"""

import sqlite3
import datetime
from typing import List, Tuple, Optional
import config


class DatabaseManager:
    """Manages SQLite database operations for conversation memory"""
    
    def __init__(self, db_path: str = config.DATABASE_PATH):
        """Initialize database connection and create tables if they don't exist"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self) -> None:
        """Create necessary tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    bot_response TEXT NOT NULL,
                    sentiment_score REAL,
                    sentiment_label TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create users table for user metadata
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_interaction DATETIME DEFAULT CURRENT_TIMESTAMP,
                    total_messages INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()
    
    def save_conversation(self, user_id: str, user_message: str, 
                         bot_response: str, sentiment_score: float, 
                         sentiment_label: str) -> None:
        """Save a conversation to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert conversation
            cursor.execute('''
                INSERT INTO conversations 
                (user_id, user_message, bot_response, sentiment_score, sentiment_label)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, user_message, bot_response, sentiment_score, sentiment_label))
            
            # Update or insert user record
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, first_seen, last_interaction, total_messages)
                VALUES (
                    ?, 
                    COALESCE((SELECT first_seen FROM users WHERE user_id = ?), CURRENT_TIMESTAMP),
                    CURRENT_TIMESTAMP,
                    COALESCE((SELECT total_messages FROM users WHERE user_id = ?), 0) + 1
                )
            ''', (user_id, user_id, user_id))
            
            conn.commit()
    
    def get_user_history(self, user_id: str, limit: int = 10) -> List[Tuple]:
        """Get conversation history for a specific user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_message, bot_response, sentiment_score, sentiment_label, timestamp
                FROM conversations 
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, limit))
            return cursor.fetchall()
    
    def get_all_conversations(self, limit: int = 50) -> List[Tuple]:
        """Get all conversations from the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, user_message, bot_response, sentiment_score, sentiment_label, timestamp
                FROM conversations 
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
    
    def get_user_stats(self, user_id: str) -> Optional[Tuple]:
        """Get statistics for a specific user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT first_seen, last_interaction, total_messages
                FROM users 
                WHERE user_id = ?
            ''', (user_id,))
            return cursor.fetchone()
    
    def cleanup_old_conversations(self, days: int = 30) -> int:
        """Remove conversations older than specified days"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM conversations 
                WHERE timestamp < datetime('now', '-' || ? || ' days')
            ''', (days,))
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count