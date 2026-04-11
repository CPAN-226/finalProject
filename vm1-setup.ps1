# VM1 (Server) Automated Setup Script
# Run this script INSIDE VM1 after Windows is installed


Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ChatApp VM1 (Server) Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""


# Step 1: Install Python
Write-Host "[1/5] Installing Python..." -ForegroundColor Yellow


$pythonInstalled = Get-Command python -ErrorAction SilentlyContinue
if ($pythonInstalled) {
    Write-Host "Python already installed: $(python --version)" -ForegroundColor Green
} else {
    Write-Host "Downloading Python installer..." -ForegroundColor White
    $pythonUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    $installerPath = "$env:TEMP\python-installer.exe"
   
    Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath
   
    Write-Host "Installing Python (this may take a few minutes)..." -ForegroundColor White
    Start-Process -FilePath $installerPath -Args "/quiet InstallAllUsers=1 PrependPath=1" -Wait
   
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
   
    Write-Host "Python installed!" -ForegroundColor Green
}
Write-Host ""


# Step 2: Get ChatApp files location
Write-Host "[2/5] Locating ChatApp files..." -ForegroundColor Yellow


$chatAppPath = "$env:USERPROFILE\Desktop\ChatApp"
if (-not (Test-Path $chatAppPath)) {
    Write-Host "ChatApp folder not found at: $chatAppPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please do ONE of the following:" -ForegroundColor Yellow
    Write-Host "  1. Download ChatApp.zip from your cloud storage" -ForegroundColor White
    Write-Host "  2. Extract it to your Desktop" -ForegroundColor White
    Write-Host "  3. Run this script again" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Found ChatApp at: $chatAppPath" -ForegroundColor Green
Write-Host ""


# Step 3: Get VM1 IP Address
Write-Host "[3/5] Getting server IP address..." -ForegroundColor Yellow


$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "10.0.2.*"}).IPAddress
if (-not $ipAddress) {
    $ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*"})[0].IPAddress
}


Write-Host "VM1 IP Address: $ipAddress" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Use this IP address in VM2's client/client.py (line 16)" -ForegroundColor Yellow
Write-Host "Copy this IP: $ipAddress" -ForegroundColor Green
Write-Host ""


# Step 4: Create database directory
Write-Host "[4/5] Setting up database..." -ForegroundColor Yellow
$dataPath = "$chatAppPath\data"
if (-not (Test-Path $dataPath)) {
    New-Item -ItemType Directory -Path $dataPath | Out-Null
}
Write-Host "Database directory ready" -ForegroundColor Green
Write-Host ""


# Step 5: Configure Windows Firewall
Write-Host "[5/5] Configuring firewall..." -ForegroundColor Yellow
try {
    New-NetFirewallRule -DisplayName "ChatApp Server" -Direction Inbound -Protocol TCP -LocalPort 5555 -Action Allow -ErrorAction SilentlyContinue | Out-Null
    Write-Host "Firewall configured (port 5555 opened)" -ForegroundColor Green
} catch {
    Write-Host "Firewall rule may already exist" -ForegroundColor Yellow
}
Write-Host ""


# Create desktop shortcuts
Write-Host "Creating desktop shortcut..." -ForegroundColor Yellow


$shortcutPath = "$env:USERPROFILE\Desktop\Start ChatApp Server.bat"
$batchCommand = "@echo off`r`ntitle ChatApp Server`r`ncd /d `"$chatAppPath`"`r`necho Starting ChatApp Server...`r`necho.`r`npython -m server.server`r`necho.`r`necho Server stopped.`r`npause"
Set-Content -Path $shortcutPath -Value $batchCommand


Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   VM1 Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server IP Address: $ipAddress" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the server:" -ForegroundColor Yellow
Write-Host "  Option 1: Double-click 'Start ChatApp Server' on Desktop" -ForegroundColor White
Write-Host "  Option 2: Open PowerShell and run:" -ForegroundColor White
Write-Host "            cd Desktop\ChatApp" -ForegroundColor Gray
Write-Host "            python -m server.server" -ForegroundColor Gray
Write-Host ""
Write-Host "NEXT: Configure VM2 with this IP address: $ipAddress" -ForegroundColor Yellow
Write-Host ""




