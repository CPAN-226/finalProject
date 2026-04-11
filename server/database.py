"""
Database Operations - Simplified
Description: Basic SQLite database for chat message storage
"""

import sqlite3
import os
from datetime import datetime


# DATABASE CONFIGURATION

# Construct path to database file: ../data/chat_history.db (relative to this file)
DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'chat_history.db')

class ChatDatabase:
    """Manages SQLite database for chat messages"""
    
    def __init__(self):
        """Initialize database connection and create schema if needed"""
        # ============ ENSURE DATA DIRECTORY EXISTS ============
        # Get the parent directory of the database file
        db_dir = os.path.dirname(DATABASE_PATH)
        
        # Create directory if it doesn't exist
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # Store database file path
        self.db_path = DATABASE_PATH
        
        # Database connection and cursor objects (initialized later)
        self.connection = None
        self.cursor = None
        
        # Initialize database (connect and create tables)
        self.initialize_database()
    
    def connect(self):
        """Establish database connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Connect to SQLite database file
            # check_same_thread=False allows multi-threaded access
            # (SQLite is usually single-threaded, but this is safe for our use case)
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            
            # Create cursor for executing SQL commands
            self.cursor = self.connection.cursor()
            
            return True
        except sqlite3.Error as e:
            print(f"[DATABASE ERROR] Connection failed: {e}")
            return False
    
    def initialize_database(self):
        """Create messages table if it doesn't exist
        
        Returns:
            True if successful, False otherwise
        """
        # First, establish connection to database
        if not self.connect():
            return False
        
        try:
            # ============ CREATE MESSAGES TABLE ============
            # IF NOT EXISTS: Only create if table doesn't already exist (safe to run multiple times)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incrementing unique ID
                    username TEXT NOT NULL,                 -- Username of message sender
                    message TEXT NOT NULL,                  -- Message content
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP  -- When message was sent
                )
            ''')
            
            # Commit the changes to database file
            self.connection.commit()
            
            print("[DATABASE] Initialized successfully")
            return True
            
        except sqlite3.Error as e:
            print(f"[DATABASE ERROR] Initialization failed: {e}")
            return False
    
    def save_message(self, username, message, timestamp=None):
        """Save a chat message to the database
        
        Args:
            username: Username of message sender
            message: Message content/text
            timestamp: Optional timestamp (auto-generated if not provided)
            
        Returns:
            True if successful, False otherwise
        """
        # Reconnect if connection was lost
        if not self.connection:
            self.connect()
        
        try:
            # Generate timestamp if not provided
            if timestamp is None:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # ============ INSERT MESSAGE INTO DATABASE ============
            # Use parameterized query (?, ?, ?) to prevent SQL injection
            # Values are safely inserted without risk of malicious SQL
            self.cursor.execute(
                "INSERT INTO messages (username, message, timestamp) VALUES (?, ?, ?)",
                (username, message, timestamp)
            )
            
            # Commit transaction to save changes permanently
            self.connection.commit()
            
            return True
            
        except sqlite3.Error as e:
            print(f"[DATABASE ERROR] Failed to save message: {e}")
            return False
    
    def close(self):
        """Close database connection and release resources"""
        if self.connection:
            self.connection.close()
