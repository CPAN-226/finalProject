"""
Chat GUI Application - Simplified
Description: Basic Tkinter GUI for the chat client
"""


import tkinter as tk
from tkinter import scrolledtext, messagebox
import sys
import os


# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from client.client import ChatClient
from shared.protocol import *
from shared.utils import validate_username


# GUI CONFIGURATION

WINDOW_TITLE = "ChatApp"       # Main window title
WINDOW_WIDTH = 600              # Window width in pixels
WINDOW_HEIGHT = 500             # Window height in pixels
FONT_FAMILY = "Arial"           # Font family for all text
FONT_SIZE_NORMAL = 10           # Normal text size
FONT_SIZE_LARGE = 14            # Large text size (titles)


class ChatGUI:
    """Main GUI class for chat application using Tkinter"""
   
    def __init__(self):
        """Initialize the GUI window and components"""
        # Client connection object (initialized when user connects)
        self.client = None
        
        # Current user's username
        self.username = None
       
        # ============ CREATE MAIN WINDOW ============
        self.window = tk.Tk()
        self.window.title(WINDOW_TITLE)
        self.window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
       
        # Register handler for window close event (X button)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
       
        # Create all GUI widgets (chat display, buttons, etc.)
        self.create_widgets()
       
        # Schedule login dialog to appear after 100ms (after window is visible)
        self.window.after(100, self.show_login_dialog)
   
    def create_widgets(self):
        """Create and layout all GUI widgets"""
       
        # ============ TITLE SECTION ============
        title_frame = tk.Frame(self.window)
        title_frame.pack(pady=10)
       
        # Title label showing app name and connection status
        self.title_label = tk.Label(
            title_frame,
            text="ChatApp - Not Connected",
            font=(FONT_FAMILY, FONT_SIZE_LARGE, "bold")
        )
        self.title_label.pack()
       
        # ============ CHAT DISPLAY SECTION ============
        chat_frame = tk.Frame(self.window)
        chat_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
       
        # ScrolledText widget for displaying chat messages (read-only)
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,            # Wrap text at word boundaries
            width=50,                # Width in characters
            height=20,               # Height in lines
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            state=tk.DISABLED        # Read-only (users can't type in it)
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
       
        # ============ INPUT SECTION ============
        input_frame = tk.Frame(self.window)
        input_frame.pack(padx=10, pady=5, fill=tk.X)
       
        # Text entry field for typing messages
        self.message_entry = tk.Entry(
            input_frame,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL)
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Bind Enter key to send message
        self.message_entry.bind("<Return>", lambda e: self.send_message())
       
        # Send button
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            width=10
        )
        self.send_button.pack(side=tk.LEFT)
       
        # ============ STATUS BAR ============
        # Status label at bottom showing connection info
        self.status_label = tk.Label(
            self.window,
            text="Status: Not connected",
            font=(FONT_FAMILY, 9),
            anchor=tk.W  # Left-aligned text
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
   
    def show_login_dialog(self):
        """Show login dialog to get username and server details"""
        # ============ CREATE MODAL DIALOG ============
        # Toplevel creates a new window on top of main window
        dialog = tk.Toplevel(self.window)
        dialog.title("Login to ChatApp")
        dialog.geometry("300x200")
        dialog.resizable(False, False)  # Fixed size, can't resize
       
        # Make dialog stay on top of main window
        dialog.transient(self.window)
        
        # Make dialog modal (blocks interaction with main window)
        dialog.grab_set()
       
        # ============ DIALOG CONTENT ============
        # Welcome title
        tk.Label(
            dialog,
            text="Welcome to ChatApp!",
            font=(FONT_FAMILY, 14, "bold")
        ).pack(pady=10)
       
        # Username field
        tk.Label(dialog, text="Username:", font=(FONT_FAMILY, FONT_SIZE_NORMAL)).pack()
        username_entry = tk.Entry(dialog, font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=25)
        username_entry.pack(pady=5)
        username_entry.focus()  # Auto-focus on username field
       
        # Server IP field
        tk.Label(dialog, text="Server IP:", font=(FONT_FAMILY, FONT_SIZE_NORMAL)).pack()
        server_entry = tk.Entry(dialog, font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=25)
        server_entry.insert(0, "10.0.2.3")  # Pre-fill with default IP
        server_entry.pack(pady=5)
       
        # Port field
        tk.Label(dialog, text="Port:", font=(FONT_FAMILY, FONT_SIZE_NORMAL)).pack()
        port_entry = tk.Entry(dialog, font=(FONT_FAMILY, FONT_SIZE_NORMAL), width=25)
        port_entry.insert(0, "5555")  # Pre-fill with default port
        port_entry.pack(pady=5)
       
        # Error label (initially empty, shown when validation fails)
        error_label = tk.Label(dialog, text="", font=(FONT_FAMILY, 9), fg="red")
        error_label.pack()
       
        # ============ CONNECTION HANDLER ============
        def attempt_connect():
            """Validate input and attempt to connect to server"""
            # Get input values and strip whitespace
            username = username_entry.get().strip()
            server_ip = server_entry.get().strip()
            server_port = port_entry.get().strip()
           
            # Validate username (not empty)
            valid, error_msg = validate_username(username)
            if not valid:
                error_label.config(text=error_msg)
                return
           
            # Validate port is a valid integer
            try:
                port = int(server_port)
            except ValueError:
                error_label.config(text="Invalid port number")
                return
           
            # Attempt connection to server
            self.connect_to_server(username, server_ip, port)
           
            # If connection successful, close login dialog
            if self.client and self.client.is_connected():
                dialog.destroy()
       
        # Connect button
        tk.Button(
            dialog,
            text="Connect",
            command=attempt_connect,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            width=15
        ).pack(pady=10)
       
        # Allow Enter key to trigger connection
        username_entry.bind("<Return>", lambda e: attempt_connect())
   
    def connect_to_server(self, username, server_ip, server_port):
        """Connect to chat server with given credentials
        
        Args:
            username: User's chosen username
            server_ip: Server IP address
            server_port: Server port number
        """
        # Store username
        self.username = username
       
        # Create chat client instance
        self.client = ChatClient(server_ip, server_port)
        
        # Register callback for when messages are received
        # This will be called from the receive thread!
        self.client.set_message_callback(self.on_message_received)
       
        # Attempt to connect to server
        success, error = self.client.connect(username)
       
        if success:
            # ============ CONNECTION SUCCESSFUL ============
            # Update title to show username
            self.title_label.config(text=f"ChatApp - {username}")
            
            # Update status bar to show connection details
            self.status_label.config(text=f"Status: Connected to {server_ip}:{server_port}")
        else:
            # ============ CONNECTION FAILED ============
            # Show error dialog with the error message
            messagebox.showerror("Connection Error", error)
            
            # Clear client object
            self.client = None
   
    def on_message_received(self, message_obj):
        """Callback for received messages - CALLED FROM RECEIVE THREAD!
        
        Important: This is called from the background receive thread, not the GUI thread.
        We must use window.after() to schedule GUI updates on the main thread.
        
        Args:
            message_obj: Dictionary containing message data
        """
        # Schedule display_message to run on GUI thread (thread-safe)
        # window.after(0, func, args) schedules func to run on next GUI event loop
        self.window.after(0, self.display_message, message_obj)
   
    def display_message(self, message_obj):
        """Display message in chat window - RUNS ON GUI THREAD
        
        Args:
            message_obj: Dictionary with keys: type, username, content, timestamp
        """
        # Format message for display: "[timestamp] username: content"
        formatted = format_message_for_display(message_obj)
       
        # Temporarily enable chat display for editing (normally read-only)
        self.chat_display.config(state=tk.NORMAL)
        
        # Insert formatted message at end of chat display
        self.chat_display.insert(tk.END, formatted + "\n")
        
        # Auto-scroll to bottom to show newest message
        self.chat_display.see(tk.END)
        
        # Disable chat display again (back to read-only)
        self.chat_display.config(state=tk.DISABLED)
   
    def send_message(self):
        """Send message to server - triggered by Send button or Enter key"""
        # Get message from entry field and remove whitespace
        message = self.message_entry.get().strip()
       
        # Ignore empty messages
        if not message:
            return
       
        # Check if client is connected
        if not self.client or not self.client.is_connected():
            messagebox.showwarning("Not Connected", "Not connected to server")
            return
       
        # Send message to server
        if self.client.send_message(message):
            # Success - clear the entry field for next message
            self.message_entry.delete(0, tk.END)
        else:
            # Failed - show error dialog
            messagebox.showerror("Send Error", "Failed to send message")
   
    def on_closing(self):
        """Handle window close event - user clicked X button"""
        # If connected, disconnect gracefully
        if self.client and self.client.is_connected():
            self.client.disconnect()
        
        # Destroy window and exit application
        self.window.destroy()
   
    def run(self):
        """Start the GUI main loop - this blocks until window is closed"""
        self.window.mainloop()


def main():
    """Main function"""
    app = ChatGUI()
    app.run()


if __name__ == "__main__":
    main()





