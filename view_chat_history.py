"""
View Chat History
Quick script to display all messages from the database
"""

import sqlite3
import os

# Path to database
db_path = os.path.join('data', 'chat_history.db')

# Check if database exists
if not os.path.exists(db_path):
    print("No chat history found. Database doesn't exist yet.")
    input("Press Enter to exit...")
    exit()

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all messages
cursor.execute("SELECT username, message, timestamp FROM messages ORDER BY timestamp")
messages = cursor.fetchall()

# Display messages
if messages:
    print("=" * 60)
    print("CHAT HISTORY")
    print("=" * 60)
    for username, message, timestamp in messages:
        print(f"[{timestamp}] {username}: {message}")
    print("=" * 60)
    print(f"Total messages: {len(messages)}")
else:
    print("No messages in database yet.")

conn.close()
input("\nPress Enter to exit...")
