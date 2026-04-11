# Server-Side Documentation

## Overview

Two main files work together to provide chat service with message storage:
- **`server.py`** - Handles client connections and message routing
- **`database.py`** - Stores chat history in SQLite

---

## server.py

### Configuration
```python
SERVER_HOST = '0.0.0.0'      # Listen on all interfaces
SERVER_PORT = 5555            # Port number
MAX_CLIENTS = 2               # Max simultaneous clients
BUFFER_SIZE = 1024            # Network buffer size
MESSAGE_ENCODING = 'utf-8'    # Character encoding
MESSAGE_DELIMITER = '\n'      # Message separator
```

### Key Components

**`ChatServer` Class**
- `server_socket` - Listens for connections
- `clients` - Dictionary: `{socket: username}`
- `clients_lock` - Thread safety for clients dict
- `database` - ChatDatabase instance
- `running` - Server state flag

### Main Methods

**`start()`** - Start server and accept connections
1. Create TCP socket
2. Bind to port 5555
3. Listen for connections
4. Check if full (max 2 clients)
5. Spawn thread for each client

**`handle_client()`** - Manage individual client (runs in thread)
1. Request username from client
2. Send welcome message
3. Loop: receive → save to DB → broadcast
4. Cleanup on disconnect

**`broadcast_message()`** - Send to all clients
- Iterates through `clients` dictionary
- Sends message with delimiter
- Thread-safe using `clients_lock`

### Message Flow
```
Client sends "Hello" → Server receives → Parse JSON → Save to DB → Broadcast to all clients
```

---

## database.py

### Configuration
```python
DATABASE_PATH = '../data/chat_history.db'
```

### ChatDatabase Class

**`initialize_database()`** - Create table if not exists
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp DATETIME
)
```

**`save_message(username, message, timestamp)`**
- Inserts message into database
- Uses parameterized queries (SQL injection safe)
- Auto-generates timestamp if not provided

**`connect()`** - Connect to SQLite
- Uses `check_same_thread=False` for multi-threading
- Returns True/False on success/failure

---

## Protocol

**JSON Format:**
```json
{
  "type": "message",
  "username": "Alice",
  "content": "Hello World",
  "timestamp": "2026-04-11 10:30:45"
}
```

**Special Messages:**
- `"USERNAME_REQUEST"` - Server asks for username
- `"SERVER_FULL"` - Server at capacity

---

## Running the Server

```bash
python server.py
```

**Expected Output:**
```
[SERVER] Initializing...
[DATABASE] Initialized successfully
[SERVER] Listening on 0.0.0.0:5555
[SERVER] Max clients: 2
```

---

## Thread Safety

- **`clients_lock`**: Protects `clients` dictionary from race conditions
- **Pattern**: 
  ```python
  with self.clients_lock:
      self.clients[socket] = username
  ```

---

## Limitations

- Max 2 clients (change `MAX_CLIENTS` to increase)
- No chat history sent to new clients
- No encryption (plain text)
- No authentication (usernames not verified)

---

## Troubleshooting

**Port already in use:**
```bash
netstat -an | findstr 5555
```

**Database errors:** Check write permissions on `data/` folder

**Connection refused:** Ensure server is running and firewall allows port 5555
