"""
Database manager for SQLite storage of messages and bot data.
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from config.settings import DATABASE_SETTINGS


class DatabaseManager:
    """Manages SQLite database operations for the Messenger bot."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database manager.
        
        Args:
            db_path: Optional custom database path
        """
        self.db_path = db_path or DATABASE_SETTINGS['database_path']
        self.table_name = DATABASE_SETTINGS['table_name']
        self.logger = logging.getLogger(__name__)
        
        # Ensure database directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def initialize_database(self) -> None:
        """Initialize database tables."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create messages table
                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender TEXT NOT NULL,
                        recipient TEXT NOT NULL,
                        message TEXT NOT NULL,
                        sentiment REAL,
                        sentiment_label TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        processed BOOLEAN DEFAULT 0,
                        metadata TEXT
                    )
                ''')
                
                # Create index for faster queries
                cursor.execute(f'''
                    CREATE INDEX IF NOT EXISTS idx_timestamp 
                    ON {self.table_name} (timestamp)
                ''')
                
                cursor.execute(f'''
                    CREATE INDEX IF NOT EXISTS idx_sender 
                    ON {self.table_name} (sender)
                ''')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    def store_message(self, sender: str, recipient: str, message: str,
                     sentiment: Optional[float] = None,
                     sentiment_label: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> int:
        """Store a message in the database.
        
        Args:
            sender: Message sender
            recipient: Message recipient
            message: Message content
            sentiment: Sentiment score (-1 to 1)
            sentiment_label: Sentiment label (positive/negative/neutral)
            metadata: Additional metadata as dictionary
            
        Returns:
            Message ID
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                metadata_json = json.dumps(metadata) if metadata else None
                
                cursor.execute(f'''
                    INSERT INTO {self.table_name} 
                    (sender, recipient, message, sentiment, sentiment_label, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (sender, recipient, message, sentiment, sentiment_label, metadata_json))
                
                message_id = cursor.lastrowid
                conn.commit()
                
                self.logger.debug(f"Stored message {message_id} from {sender} to {recipient}")
                return message_id
                
        except sqlite3.Error as e:
            self.logger.error(f"Error storing message: {e}")
            raise
    
    def get_messages(self, sender: Optional[str] = None,
                    recipient: Optional[str] = None,
                    limit: int = 100,
                    processed: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Retrieve messages from database.
        
        Args:
            sender: Filter by sender
            recipient: Filter by recipient
            limit: Maximum number of messages
            processed: Filter by processed status
            
        Returns:
            List of message dictionaries
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = f"SELECT * FROM {self.table_name} WHERE 1=1"
                params = []
                
                if sender:
                    query += " AND sender = ?"
                    params.append(sender)
                
                if recipient:
                    query += " AND recipient = ?"
                    params.append(recipient)
                
                if processed is not None:
                    query += " AND processed = ?"
                    params.append(processed)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                messages = []
                for row in rows:
                    message = dict(row)
                    if message['metadata']:
                        message['metadata'] = json.loads(message['metadata'])
                    messages.append(message)
                
                return messages
                
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving messages: {e}")
            raise
    
    def mark_processed(self, message_id: int) -> None:
        """Mark a message as processed.
        
        Args:
            message_id: ID of the message to mark
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    UPDATE {self.table_name} 
                    SET processed = 1 
                    WHERE id = ?
                ''', (message_id,))
                conn.commit()
                
        except sqlite3.Error as e:
            self.logger.error(f"Error marking message {message_id} as processed: {e}")
            raise
    
    def get_conversation_history(self, sender: str, recipient: str,
                                limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history between two users.
        
        Args:
            sender: First user
            recipient: Second user
            limit: Maximum number of messages
            
        Returns:
            List of messages in chronological order
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(f'''
                    SELECT * FROM {self.table_name}
                    WHERE (sender = ? AND recipient = ?)
                       OR (sender = ? AND recipient = ?)
                    ORDER BY timestamp ASC
                    LIMIT ?
                ''', (sender, recipient, recipient, sender, limit))
                
                rows = cursor.fetchall()
                
                messages = []
                for row in rows:
                    message = dict(row)
                    if message['metadata']:
                        message['metadata'] = json.loads(message['metadata'])
                    messages.append(message)
                
                return messages
                
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving conversation history: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Total messages
                cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
                total_messages = cursor.fetchone()[0]
                
                # Messages by sentiment
                cursor.execute(f'''
                    SELECT sentiment_label, COUNT(*) 
                    FROM {self.table_name} 
                    WHERE sentiment_label IS NOT NULL
                    GROUP BY sentiment_label
                ''')
                sentiment_counts = dict(cursor.fetchall())
                
                # Processed vs unprocessed
                cursor.execute(f'''
                    SELECT processed, COUNT(*) 
                    FROM {self.table_name} 
                    GROUP BY processed
                ''')
                processing_stats = dict(cursor.fetchall())
                
                return {
                    'total_messages': total_messages,
                    'sentiment_distribution': sentiment_counts,
                    'processing_stats': processing_stats,
                    'database_path': str(self.db_path)
                }
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting statistics: {e}")
            raise