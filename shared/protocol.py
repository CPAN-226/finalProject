"""
Message Protocol - Simplified
Description: Basic JSON message protocol for chat communication
"""

import json
from datetime import datetime

def create_message(username, content):
    """Create a basic message object"""
    return {
        'type': 'message',
        'username': username,
        'content': content,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def encode_message(message_obj):
    """Encode message to JSON string"""
    try:
        return json.dumps(message_obj)
    except Exception:
        return None

def decode_message(message_str):
    """Decode JSON string to message object"""
    try:
        return json.loads(message_str)
    except json.JSONDecodeError:
        return None

def format_message_for_display(message_obj):
    """Format message for display"""
    username = message_obj.get('username', 'Unknown')
    content = message_obj.get('content', '')
    timestamp = message_obj.get('timestamp', '')
    return f"[{timestamp}] {username}: {content}"
