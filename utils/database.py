# utils/database.py
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any

class Database:
    def __init__(self, db_path: str = "database/bot.db"):
        """Initialize database with all required tables."""
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self) -> None:
        """Create all required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Channels table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_name TEXT UNIQUE NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Filters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS filters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phrases TEXT NOT NULL,
                exclude TEXT,
                weight INTEGER DEFAULT 5,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Vacancies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_name TEXT NOT NULL,
                message_id INTEGER NOT NULL,
                category TEXT,
                matched_phrase TEXT,
                weight INTEGER,
                text TEXT,
                link TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(channel_name, message_id)
            )
        """)
        
        # Processed messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_name TEXT NOT NULL,
                message_id INTEGER NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(channel_name, message_id)
            )
        """)
        
        # Error log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_type TEXT NOT NULL,
                error_message TEXT,
                channel_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _get_conn(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # Channel operations
    def add_channel(self, channel_name: str) -> int:
        """Add a new channel."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO channels (channel_name) VALUES (?)",
            (channel_name,)
        )
        conn.commit()
        channel_id = cursor.lastrowid
        conn.close()
        return channel_id
    
    def get_channels(self) -> List[Dict[str, Any]]:
        """Get all channels."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM channels")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def delete_channel(self, channel_id: int) -> bool:
        """Delete a channel."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM channels WHERE id = ?", (channel_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    
    # Filter operations
    def add_filter(self, name: str, phrases: List[str], exclude: List[str] = None, weight: int = 5) -> int:
        """Add a new filter."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO filters (name, phrases, exclude, weight) VALUES (?, ?, ?, ?)",
            (name, json.dumps(phrases), json.dumps(exclude) if exclude else None, weight)
        )
        conn.commit()
        filter_id = cursor.lastrowid
        conn.close()
        return filter_id
    
    def get_filters(self) -> List[Dict[str, Any]]:
        """Get all filters."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM filters")
        rows = cursor.fetchall()
        conn.close()
        
        filters = []
        for row in rows:
            filter_dict = dict(row)
            filter_dict["phrases"] = json.loads(filter_dict["phrases"])
            if filter_dict["exclude"]:
                filter_dict["exclude"] = json.loads(filter_dict["exclude"])
            filters.append(filter_dict)
        return filters
    
    def delete_filter(self, filter_id: int) -> bool:
        """Delete a filter."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM filters WHERE id = ?", (filter_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    
    # Vacancy operations
    def add_vacancy(self, channel_name: str, message_id: int, category: str, 
                    matched_phrase: str, weight: int, text: str, link: str) -> int:
        """Add a new vacancy."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO vacancies (channel_name, message_id, category, matched_phrase, weight, text, link) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (channel_name, message_id, category, matched_phrase, weight, text, link)
        )
        conn.commit()
        vacancy_id = cursor.lastrowid
        conn.close()
        return vacancy_id
    
    def get_vacancies(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get vacancies."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vacancies ORDER BY sent_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # Processed messages operations
    def is_message_processed(self, channel_name: str, message_id: int) -> bool:
        """Check if message was already processed."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM processed_messages WHERE channel_name = ? AND message_id = ?",
            (channel_name, message_id)
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def mark_message_processed(self, channel_name: str, message_id: int) -> None:
        """Mark message as processed."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO processed_messages (channel_name, message_id) VALUES (?, ?)",
            (channel_name, message_id)
        )
        conn.commit()
        conn.close()
    
    # Error logging
    def log_error(self, error_type: str, error_message: str, channel_name: str = None) -> None:
        """Log an error."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO error_log (error_type, error_message, channel_name) VALUES (?, ?, ?)",
            (error_type, error_message, channel_name)
        )
        conn.commit()
        conn.close()
    
    # Statistics
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Total vacancies
        cursor.execute("SELECT COUNT(*) FROM vacancies")
        total_vacancies = cursor.fetchone()[0]
        
        # Vacancies today
        cursor.execute("SELECT COUNT(*) FROM vacancies WHERE DATE(sent_at) = DATE('now')")
        vacancies_today = cursor.fetchone()[0]
        
        # Total channels
        cursor.execute("SELECT COUNT(*) FROM channels")
        total_channels = cursor.fetchone()[0]
        
        # Total filters
        cursor.execute("SELECT COUNT(*) FROM filters")
        total_filters = cursor.fetchone()[0]
        
        # Errors today
        cursor.execute("SELECT COUNT(*) FROM error_log WHERE DATE(created_at) = DATE('now')")
        errors_today = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_vacancies": total_vacancies,
            "vacancies_today": vacancies_today,
            "total_channels": total_channels,
            "total_filters": total_filters,
            "errors_today": errors_today
        }
