"""
Shared Utilities - Simplified
Description: Basic utility functions
"""

def validate_username(username):
    """
    Validate username - must not be empty
    
    Args:
        username: Username string to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not username or not username.strip():
        return False, "Username cannot be empty"
    
    return True, ""
