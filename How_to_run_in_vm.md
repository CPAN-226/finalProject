# ChatApp Virtual Machine Setup Guide

## 📋 Prerequisites

Before starting, ensure you have:
- VirtualBox installed
- Windows 10 (2022) ISO file downloaded
- Python 3.11.0 installer downloaded
- ChatApp project folder

---

## 🖥️ Step 1: Create Virtual Machines

### 1.1 Create Two VMs
1. Open VirtualBox
2. Create **two new VMs** with the following names:
   - `ChatApp-VM1` (Server)
   - `ChatApp-VM2` (Client)

### 1.2 Configure VM Settings

For **BOTH VMs**, apply the following settings:

#### System Configuration
- **System → Motherboard**
  - Boot Device Order: 
    1. ✅ Hard Disk
    2. ✅ Optical
    3. ❌ Uncheck everything else
  - Base Memory: `4096 MB` (4 GB)
  - Extended Features:
    - ✅ Enable I/O APIC
    - ❌ Disable UEFI

#### Network Configuration
- **Network → Adapter 1**
  - ✅ Enable Network Adapter
  - Attached to: `NAT Network`
  - Name: `ChatAppNetwork`

- **Network → Adapter 2**
  - ✅ Enable Network Adapter
  - Attached to: `NAT`

#### Storage Configuration
- **Storage → Controller: IDE**
  - Attach Windows 10 (2022) ISO file to Optical Drive

---

## 💿 Step 2: Install Windows 10

1. **Start both VMs**
2. Install Windows 10 on both VMs following the on-screen instructions
3. Complete the Windows setup process
4. **Install Python 3.11.0** on both VMs
   - ⚠️ **Important**: Check "Add Python to PATH" during installation

---

## 📁 Step 3: Transfer ChatApp Project

1. Upload `ChatApp` folder to Google Drive (or other file sharing service)
2. Download the folder on **both VMs**
3. Save it to: `C:\Users\[YourUsername]\Desktop\ChatApp`

---

## 🔧 Step 4: VM1 Setup (Server)

### 4.1 Run Setup Script

1. **Right-click PowerShell** → **Run as Administrator**
2. Execute the following commands:

```powershell
# Navigate to ChatApp folder
cd $HOME\Desktop\ChatApp

# Allow script execution
Set-ExecutionPolicy Bypass -Scope Process
# When prompted, press Y

# Run VM1 setup script
.\vm1-setup.ps1
```

### 4.2 Note the IP Address

The script will display the **VM1 IP address**. 

📝 **IMPORTANT**: Write down this IP address (e.g., `10.0.2.3`) — you'll need it for VM2 setup!

Example output:
```
VM1 IP Address: 10.0.2.3
```

---

## 🔧 Step 5: VM2 Setup (Client)

### 5.1 Update Server IP

Before running the setup, update the server IP in `client.py`:

1. Open `ChatApp\client\client.py`
2. Find **line 16**:
   ```python
   SERVER_IP = '10.0.2.3'  # Replace with your VM1 IP address
   ```
3. Replace `10.0.2.3` with the IP address from VM1
4. Save the file

### 5.2 Run Setup Script

1. **Right-click PowerShell** → **Run as Administrator**
2. Execute the following commands (replace IP with VM1's IP):

```powershell
# Navigate to ChatApp folder
cd $HOME\Desktop\ChatApp

# Allow script execution
Set-ExecutionPolicy Bypass -Scope Process
# When prompted, press Y

# Run VM2 setup script (use VM1's IP address)
.\vm2-setup.ps1 -ServerIP "10.0.2.3"
```

---

## 🚀 Step 6: Running the Application

### Desktop Shortcuts

After running the setup scripts, you'll find these shortcuts on the desktop:

| VM | Shortcut Name | Description |
|----|---------------|-------------|
| **VM1** | `Start ChatApp Server` | Starts the chat server |
| **VM2** | `Start ChatApp Client` | Starts the chat client GUI |

### Starting the Chat Application

1. **On VM1 (Server)**:
   - Double-click **`Start ChatApp Server`** shortcut
   - Server console will appear showing:
     ```
     [SERVER] Listening on 0.0.0.0:5555
     [SERVER] Max clients: 2
     ```

2. **On VM2 (Client)**:
   - Double-click **`Start ChatApp Client`** shortcut
   - Login dialog will appear
   - Enter the following:
     - **Username**: Choose any username (e.g., `Alice`)
     - **Server IP**: Enter VM1's IP address (e.g., `10.0.2.3`)
     - **Port**: `5555` (default)
   - Click **Connect**

3. **Start a Second Client** (optional):
   - Double-click the client shortcut again on VM2
   - Use a **different username** (e.g., `Bob`)
   - Enter the same server IP and port

---

## 💬 Using ChatApp

Once connected:
1. Type your message in the text field
2. Press **Enter** or click **Send**
3. Messages will appear on:
   - Both client windows
   - Server console (VM1)

### ⚠️ Important Notes

- **Server must be running** before clients connect
- **Maximum 2 clients** can connect simultaneously
- **Usernames must be different** for each client
- **Server IP must match** VM1's IP address in the login dialog

---

## 🔍 Troubleshooting

### Connection Refused
- ✅ Ensure server is running on VM1
- ✅ Verify IP address matches VM1's IP
- ✅ Check that port 5555 is not blocked
- ✅ Confirm both VMs are on the same NAT network

### Server Full
- Maximum 2 clients allowed
- Wait for a client to disconnect or restart the server

### Messages Not Appearing
- Check server console for errors
- Verify network connectivity between VMs
- Ensure firewall is not blocking connections

---

## 📊 Network Topology

```
ChatApp-VM1 (Server)          ChatApp-VM2 (Client)
    10.0.2.3                      10.0.2.4
       │                              │
       └──────── NAT Network ─────────┘
            (ChatAppNetwork)
```

---

## 🎓 Team Setup Complete!

You're all set! Your team can now test the ChatApp on separate virtual machines and see real-time message exchange between clients.