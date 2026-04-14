"""
Chat Client - Simplified
Description: Basic TCP client for chat application
"""


import socket
import threading
import sys
import os


# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from shared.protocol import *


# CLIENT CONFIGURATION

SERVER_IP = '10.0.2.3'        # Default server IP address (VM1's IP)
SERVER_PORT = 5555             # Server port number
BUFFER_SIZE = 1024             # Network buffer size for receiving data (bytes)
MESSAGE_ENCODING = 'utf-8'     # Character encoding for messages
MESSAGE_DELIMITER = '\n'       # Delimiter to separate messages in TCP stream


class ChatClient:
    """Simple chat client for connecting to chat server"""
   
    def __init__(self, server_ip=None, server_port=None):
        """Initialize chat client
        
        Args:
            server_ip: Optional server IP (uses default if not provided)
            server_port: Optional server port (uses default if not provided)
        """
        # Server connection details
        self.server_ip = server_ip if server_ip else SERVER_IP
        self.server_port = server_port if server_port else SERVER_PORT
        
        # TCP socket for server connection
        self.socket = None
        
        # User's chosen username
        self.username = None
        
        # Connection status flag (shared between main and receive thread)
        self.connected = False
        
        # Background thread that listens for incoming messages
        self.receive_thread = None
        
        # Callback function to invoke when message is received
        self.message_callback = None
   
    def connect(self, username):
        """Connect to the chat server and authenticate
        
        Args:
            username: The username to use for this connection
            
        Returns:
            tuple: (success: bool, error_message: str)
                   (True, "") on success
                   (False, "error description") on failure
        """
        try:
            # Store username for later use
            self.username = username
           
            #CREATE SOCKET CONNECTION
            # Create TCP socket (SOCK_STREAM) using IPv4 (AF_INET)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Set 10-second timeout for connection attempt
            # Without this, connection might hang indefinitely
            self.socket.settimeout(10)
           
            # Connect to server at specified IP and port
            self.socket.connect((self.server_ip, self.server_port))
            
            # Remove timeout after successful connection (None = blocking mode)
            self.socket.settimeout(None)
           
            #AUTHENTICATION HANDSHAKE
            # Wait for server to request username
            server_msg = self.socket.recv(BUFFER_SIZE).decode(MESSAGE_ENCODING)
           
            # Check if server is full
            if server_msg == "SERVER_FULL":
                return False, "Server is full"
           
            # Verify server sent expected username request
            if server_msg != "USERNAME_REQUEST":
                return False, f"Unexpected server response"
           
            # Send username to server as JSON object
            username_msg = {'username': username}
            self.socket.send(encode_message(username_msg).encode(MESSAGE_ENCODING))
           
            # Mark connection as established
            self.connected = True
           
            #START RECEIVE THREAD
            # Create daemon thread to listen for incoming messages
            # daemon=True means thread will exit when main program exits
            self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.receive_thread.start()
           
            return True, ""  # Success!
       
        except socket.timeout:
            return False, "Connection timed out"
        except ConnectionRefusedError:
            return False, "Connection refused"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
   
    def _receive_messages(self):
        """Receive messages from server - runs in background thread
        
        This method continuously listens for incoming messages from the server.
        It handles TCP stream buffering (messages may arrive in fragments).
        """
        # Buffer to accumulate partial messages
        buffer = ""
       
        # Keep listening while connected
        while self.connected:
            try:
                # Receive data from server (blocks until data arrives)
                data = self.socket.recv(BUFFER_SIZE)
               
                # Empty data means server closed connection
                if not data:
                    self.connected = False
                    break
               
                # Decode bytes to string and add to buffer
                buffer += data.decode(MESSAGE_ENCODING)
               
                #PROCESS COMPLETE MESSAGES
                # TCP is a stream protocol - messages may be fragmented
                # We use delimiter (\n) to identify complete messages
                while MESSAGE_DELIMITER in buffer:
                    # Split off one complete message
                    message_str, buffer = buffer.split(MESSAGE_DELIMITER, 1)
                   
                    # Only process non-empty messages
                    if message_str:
                        # Parse JSON string to message object
                        message_obj = decode_message(message_str)
                       
                        # If valid message and callback is set, invoke it
                        if message_obj and self.message_callback:
                            self.message_callback(message_obj)
           
            except socket.error:
                # Socket error means connection lost
                if self.connected:
                    self.connected = False
                break
            except Exception:
                # Any other error, exit gracefully
                break
   
    def send_message(self, content):
        """Send message to server
        
        Args:
            content: The message text to send
            
        Returns:
            True if successful, False otherwise
        """
        # Check if connected before sending
        if not self.connected:
            return False
       
        try:
            # Create message object with username, content, and timestamp
            message_obj = create_message(self.username, content)
            
            # Encode message object to JSON string
            encoded = encode_message(message_obj)
            
            # Send encoded message as UTF-8 bytes
            self.socket.send(encoded.encode(MESSAGE_ENCODING))
            
            return True
        except Exception:
            # Send failed (connection lost, etc.)
            return False
   
    def disconnect(self):
        """Disconnect from server and clean up resources"""
        # Only disconnect if currently connected
        if not self.connected:
            return
       
        # Set flag to False (this will stop receive thread)
        self.connected = False
       
        # Close socket connection
        if self.socket:
            try:
                self.socket.close()
            except:
                pass  # Ignore errors if socket already closed
   
    def set_message_callback(self, callback):
        """Set callback function for received messages
        
        Args:
            callback: Function to call when message is received
                     Signature: callback(message_obj)
                     Called from receive thread, not main thread!
        """
        self.message_callback = callback
   
    def is_connected(self):
        """Check if client is currently connected to server
        
        Returns:
            True if connected, False otherwise
        """
        return self.connected




