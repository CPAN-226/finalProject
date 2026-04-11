"""
Chat Server - Simplified
Description: Basic multi-client chat server
"""

import socket
import threading
import json
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import ChatDatabase


# SERVER CONFIGURATION

SERVER_HOST = '0.0.0.0'      # Listen on all available network interfaces
SERVER_PORT = 5555            # Port number for server socket
MAX_CLIENTS = 2               # Maximum number of simultaneous clients allowed
BUFFER_SIZE = 1024            # Size of network buffer for receiving data (bytes)
MESSAGE_ENCODING = 'utf-8'    # Character encoding for messages
MESSAGE_DELIMITER = '\n'      # Delimiter to separate messages in TCP stream

class ChatServer:
    """Simple chat server for 2 clients"""
    
    def __init__(self):
        """Initialize the chat server"""
        # Server socket that listens for incoming connections
        self.server_socket = None
        
        # Dictionary to track connected clients: {socket_object: username}
        self.clients = {}
        
        # Threading lock to prevent race conditions when accessing clients dictionary
        # Multiple threads access this dict, so we need thread-safe operations
        self.clients_lock = threading.Lock()
        
        # Database instance for storing chat history
        self.database = ChatDatabase()
        
        # Flag to control server running state
        self.running = False
        
        print("[SERVER] Initializing...")
    
    def start(self):
        """Start the server"""
        try:
            # Create a TCP socket (SOCK_STREAM) using IPv4 (AF_INET)
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Allow the address to be reused immediately after server restart
            # Without this, you might get "Address already in use" errors
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind the socket to the specified host and port
            self.server_socket.bind((SERVER_HOST, SERVER_PORT))
            
            # Start listening for connections (backlog queue of 5)
            self.server_socket.listen(5)
            
            # Mark server as running
            self.running = True
            
            print(f"[SERVER] Listening on {SERVER_HOST}:{SERVER_PORT}")
            print(f"[SERVER] Max clients: {MAX_CLIENTS}")
            
            # Main server loop - continuously accept new connections
            while self.running:
                try:
                    # Accept incoming connection (this blocks until a client connects)
                    # Returns: client socket and (IP address, port) tuple
                    client_socket, client_address = self.server_socket.accept()
                    
                    # Check if server has reached maximum capacity
                    if len(self.clients) >= MAX_CLIENTS:
                        print(f"[SERVER] Connection refused from {client_address} - Server full")
                        # Notify client that server is full
                        client_socket.send("SERVER_FULL".encode(MESSAGE_ENCODING))
                        # Close the connection immediately
                        client_socket.close()
                        continue  # Go back to accepting new connections
                    
                    print(f"[SERVER] New connection from {client_address}")
                    
                    # Create a new thread to handle this client independently
                    # daemon=True means thread will exit when main program exits
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    # Start the client handler thread
                    client_thread.start()
                    
                except Exception as e:
                    if self.running:
                        print(f"[SERVER ERROR] {e}")
        
        except Exception as e:
            print(f"[SERVER ERROR] Failed to start: {e}")
            self.stop()
    
    def handle_client(self, client_socket, client_address):
        """Handle individual client connection - runs in separate thread for each client"""
        username = None  # Track username for cleanup on disconnect
        
        try:
            # ============ AUTHENTICATION PHASE ============
            # Send username request to client
            client_socket.send("USERNAME_REQUEST".encode(MESSAGE_ENCODING))
            
            # Wait for client to send their username
            username_data = client_socket.recv(BUFFER_SIZE).decode(MESSAGE_ENCODING)
            
            # If no data received, client disconnected
            if not username_data:
                client_socket.close()
                return
            
            # Try to parse as JSON first (client sends {"username": "Alice"})
            try:
                data = json.loads(username_data)
                username = data.get('username', 'Unknown')
            except json.JSONDecodeError:
                # If not JSON, treat as plain text username
                username = username_data.strip()
            
            # Add client to the connected clients dictionary (thread-safe)
            with self.clients_lock:  # Acquire lock before modifying shared dictionary
                self.clients[client_socket] = username
            
            print(f"[SERVER] {username} joined the chat")
            
            # ============ SEND WELCOME MESSAGE ============
            # Create a welcome message from the server
            welcome_msg = {
                'type': 'message',
                'username': 'SERVER',  # Message appears to be from server
                'content': f'Welcome {username}!',
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            # Send welcome message with delimiter appended
            client_socket.send((json.dumps(welcome_msg) + MESSAGE_DELIMITER).encode(MESSAGE_ENCODING))
            
            # ============ MESSAGE LOOP ============
            # Continuously listen for messages from this client
            while self.running:
                try:
                    # Receive data from client (blocks until data arrives)
                    message_data = client_socket.recv(BUFFER_SIZE)
                    
                    # Empty data means client disconnected
                    if not message_data:
                        break  # Exit the message loop
                    
                    # Decode bytes to string and remove whitespace
                    message_text = message_data.decode(MESSAGE_ENCODING).strip()
                    
                    # Ignore empty messages
                    if not message_text:
                        continue
                    
                    # Try to parse message as JSON to extract content
                    try:
                        message_obj = json.loads(message_text)
                        content = message_obj.get('content', message_text)
                    except json.JSONDecodeError:
                        # If not JSON, treat entire text as content
                        content = message_text
                    
                    # Generate timestamp for this message
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # ============ SAVE MESSAGE TO DATABASE ============
                    self.database.save_message(username, content, timestamp)
                    
                    # ============ BROADCAST TO ALL CLIENTS ============
                    # Create message object to broadcast
                    broadcast_msg = {
                        'type': 'message',
                        'username': username,
                        'content': content,
                        'timestamp': timestamp
                    }
                    
                    # Send to all connected clients
                    self.broadcast_message(json.dumps(broadcast_msg))
                    
                    # Log message to console
                    print(f"[MESSAGE] {username}: {content}")
                
                except socket.error:
                    break
                except Exception as e:
                    print(f"[ERROR] {e}")
                    break
        
        except Exception as e:
            print(f"[ERROR] Handling client: {e}")
        
        finally:
            # ============ CLEANUP ON DISCONNECT ============
            # This runs when client disconnects or error occurs
            if username:
                print(f"[SERVER] {username} has left")
                
                # Remove client from connected clients dictionary (thread-safe)
                with self.clients_lock:
                    if client_socket in self.clients:
                        del self.clients[client_socket]
            
            # Close the socket connection
            try:
                client_socket.close()
            except:
                pass  # Ignore errors if socket already closed
    
    def broadcast_message(self, message, exclude_socket=None):
        """Broadcast message to all connected clients
        
        Args:
            message: JSON string to send to all clients
            exclude_socket: Optional socket to skip (e.g., don't echo to sender)
        """
        # Acquire lock for thread-safe access to clients dictionary
        with self.clients_lock:
            disconnected = []  # Track clients that fail to receive
            
            # Iterate through all connected clients
            for client_socket in self.clients.keys():
                # Skip excluded socket if specified
                if client_socket == exclude_socket:
                    continue
                
                try:
                    # Send message with delimiter appended
                    client_socket.send((message + MESSAGE_DELIMITER).encode(MESSAGE_ENCODING))
                except:
                    # If send fails, mark client as disconnected
                    disconnected.append(client_socket)
            
            # Clean up disconnected clients
            for socket_obj in disconnected:
                if socket_obj in self.clients:
                    del self.clients[socket_obj]
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        if self.database:
            self.database.close()

def main():
    """Main function"""
    server = ChatServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
        server.stop()

if __name__ == "__main__":
    main()



