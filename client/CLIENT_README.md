# Client-Side Documentation

## Overview

Two files work together to provide the chat client:
- **`client.py`** - Core networking (TCP socket, send/receive)
- **`gui.py`** - Tkinter GUI for user interaction

---

## client.py

### Configuration
```python
SERVER_IP = '10.0.2.3'        # Default server IP
SERVER_PORT = 5555             # Server port
BUFFER_SIZE = 1024             # Network buffer size
MESSAGE_ENCODING = 'utf-8'     # Character encoding
MESSAGE_DELIMITER = '\n'       # Message separator
```

### ChatClient Class

**Instance Variables:**
- `server_ip`, `server_port` - Server location
- `socket` - TCP socket connection
- `username` - User's username
- `connected` - Connection status flag
- `receive_thread` - Background thread for receiving
- `message_callback` - Function called when message arrives

### Key Methods

**`connect(username)`** - Connect to server
1. Create TCP socket
2. Set 10-second timeout
3. Connect to server
4. Wait for `"USERNAME_REQUEST"`
5. Send username as JSON
6. Start receive thread
- **Returns**: `(success: bool, error_msg: str)`

**`_receive_messages()`** - Listen for messages (background thread)
1. Receive bytes from socket
2. Decode and add to buffer
3. Split by delimiter (`\n`) to extract complete messages
4. Parse JSON and invoke callback
- **Note**: Handles TCP fragmentation with buffering

**`send_message(content)`** - Send message
1. Create message object (username + content + timestamp)
2. Encode to JSON
3. Send via socket
- **Returns**: `True` on success

**`disconnect()`** - Close connection
- Sets `connected = False` (stops receive thread)
- Closes socket

**`set_message_callback(callback)`** - Register message handler
- Callback is invoked from receive thread!

---

## gui.py

### Configuration
```python
WINDOW_TITLE = "ChatApp"
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500
FONT_FAMILY = "Arial"
```

### ChatGUI Class

**Components:**
- Title label (shows username when connected)
- Chat display (ScrolledText, read-only)
- Message entry field
- Send button
- Status bar

### Key Methods

**`show_login_dialog()`** - Modal dialog for connection
- Fields: Username, Server IP, Port
- Validates input
- Calls `connect_to_server()` on submit

**`connect_to_server(username, ip, port)`** - Connect to server
1. Create `ChatClient` instance
2. Set message callback
3. Call `client.connect()`
4. Update UI on success/failure

**`on_message_received(message_obj)`** - Callback from receive thread
- **Critical**: Called from background thread
- Uses `window.after(0, ...)` to schedule on GUI thread
- **Why?** Tkinter is NOT thread-safe

**`display_message(message_obj)`** - Show message in chat
1. Format message: `"[timestamp] username: content"`
2. Enable chat display (temporarily)
3. Insert text at end
4. Auto-scroll to bottom
5. Disable chat display (back to read-only)

**`send_message()`** - Send user's message
1. Get text from entry field
2. Check if connected
3. Call `client.send_message()`
4. Clear entry field on success

**`on_closing()`** - Handle window close
- Disconnect from server
- Destroy window

---

## Threading Model

### Two Threads

**Main/GUI Thread:**
- Runs Tkinter event loop
- Handles user input
- Updates GUI
- Sends messages

**Receive Thread (Daemon):**
- Runs `_receive_messages()`
- Listens on socket
- Parses messages
- Calls callback

### Thread Safety

**Problem:** Tkinter GUI updates must happen on main thread

**Solution:** Use `window.after(0, func, args)`

```python
# WRONG - Called from receive thread
self.chat_display.insert(tk.END, text)  # CRASH!

# RIGHT - Scheduled on GUI thread
self.window.after(0, self.display_message, msg)
```

---

## Message Protocol

**JSON Format:**
```json
{
  "type": "message",
  "username": "Alice",
  "content": "Hello World",
  "timestamp": "2026-04-11 14:30:45"
}
```

**Helper Functions** (from `shared/protocol.py`):
- `create_message(username, content)` - Create message object
- `encode_message(obj)` - Convert to JSON string
- `decode_message(str)` - Parse JSON to object
- `format_message_for_display(obj)` - Format for display

---

## Message Flow

### Sending
```
User types → Presses Enter → send_message() → ChatClient.send_message() 
→ Encode JSON → Send bytes → Server receives
```

### Receiving
```
Server sends → Socket receives bytes → Receive thread decodes → Parse JSON 
→ Callback (receive thread) → window.after() → display_message (GUI thread)
→ Insert into chat display
```

---

## Running the Client

```bash
python client/gui.py
```

**Flow:**
1. GUI opens with login dialog
2. Enter username, IP, port
3. Click "Connect"
4. Chat window becomes active
5. Type and send messages

---

## Common Issues

**"Connection refused"**
- Server not running
- Wrong IP/port
- Firewall blocking

**"Server is full"**
- Max 2 clients connected
- Wait for slot or increase `MAX_CLIENTS` on server

**Messages not appearing**
- Check console for errors
- Verify network connectivity

---

## Using ChatClient Without GUI

```python
from client.client import ChatClient

def on_message(msg):
    print(f"{msg['username']}: {msg['content']}")

client = ChatClient('10.0.2.3', 5555)
client.set_message_callback(on_message)

success, error = client.connect('Alice')
if success:
    client.send_message("Hello!")
    # Keep running...
    import time
    time.sleep(60)
    client.disconnect()
```

---

## Key Takeaways

- **client.py**: Network layer, decoupled from GUI
- **gui.py**: Tkinter interface, uses client.py
- **Threading**: Receive happens in background, GUI updates on main thread
- **Thread Safety**: Always use `window.after()` for cross-thread GUI updates
- **Buffering**: TCP fragmentation handled with delimiter-based parsing
