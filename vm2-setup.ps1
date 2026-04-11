# VM2 (Client) Automated Setup Script
# Run this script INSIDE VM2 after Windows is installed


param(
    [string]$ServerIP = ""
)


Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ChatApp VM2 (Client) Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""


# Step 1: Install Python
Write-Host "[1/4] Installing Python..." -ForegroundColor Yellow


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
Write-Host "[2/4] Locating ChatApp files..." -ForegroundColor Yellow


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


# Step 3: Configure server IP
Write-Host "[3/4] Configuring server connection..." -ForegroundColor Yellow


if (-not $ServerIP) {
    Write-Host "Enter the server IP address from VM1:" -ForegroundColor Cyan
    $ServerIP = Read-Host "Server IP"
}


$clientPath = "$chatAppPath\client\client.py"
$clientContent = Get-Content $clientPath -Raw


# Create the replacement string
$replacement = "SERVER_IP = '$ServerIP'"


# Use a simpler regex pattern that works reliably in PowerShell
if ($clientContent -match "SERVER_IP\s*=\s*'[^']*'") {
    $clientContent = $clientContent -replace "SERVER_IP\s*=\s*'[^']*'", $replacement
    Set-Content -Path $clientPath -Value $clientContent -NoNewline
    Write-Host "Server IP configured: $ServerIP" -ForegroundColor Green
} else {
    Write-Host "Warning: Could not update client.py automatically" -ForegroundColor Yellow
    Write-Host "Please manually edit: $clientPath" -ForegroundColor Yellow
    Write-Host "Change SERVER_IP = '10.0.2.4' to SERVER_IP = '$ServerIP'" -ForegroundColor Yellow
}
Write-Host ""


# Step 4: Test connectivity
Write-Host "[4/4] Testing connection to server..." -ForegroundColor Yellow


$pingResult = Test-Connection -ComputerName $ServerIP -Count 2 -Quiet
if ($pingResult) {
    Write-Host "Connection to server successful!" -ForegroundColor Green
} else {
    Write-Host "Warning: Cannot ping server at $ServerIP" -ForegroundColor Yellow
    Write-Host "Make sure VM1 server is running and on the same network" -ForegroundColor Yellow
}
Write-Host ""


# Create desktop shortcut
Write-Host "Creating desktop shortcut..." -ForegroundColor Yellow


$shortcutPath = "$env:USERPROFILE\Desktop\Start ChatApp Client.bat"
$batchCommand = "@echo off`r`ntitle ChatApp Client`r`ncd /d `"$chatAppPath`"`r`necho Starting ChatApp Client...`r`necho.`r`npython -m client.gui`r`necho.`r`necho Client stopped.`r`npause"
Set-Content -Path $shortcutPath -Value $batchCommand


Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   VM2 Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server IP: $ServerIP" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the client:" -ForegroundColor Yellow
Write-Host "  Option 1: Double-click 'Start ChatApp Client' on Desktop" -ForegroundColor White
Write-Host "  Option 2: Open PowerShell and run:" -ForegroundColor White
Write-Host "            cd Desktop\ChatApp" -ForegroundColor Gray
Write-Host "            python -m client.gui" -ForegroundColor Gray
Write-Host ""
Write-Host "IMPORTANT: Make sure the server is running on VM1 first!" -ForegroundColor Yellow
Write-Host ""




