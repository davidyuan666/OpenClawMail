@echo off
setlocal
chcp 65001 >nul
title OpenClawMail Service Manager
color 0A

REM Disable AutoRun to prevent errors
reg delete "HKCU\Software\Microsoft\Command Processor" /v AutoRun /f >nul 2>&1
reg delete "HKLM\Software\Microsoft\Command Processor" /v AutoRun /f >nul 2>&1

echo ====================================
echo   OpenClawMail Startup Script v2.0
echo ====================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not detected, please install Python 3.8+
    pause
    exit /b 1
)

REM Check virtual environment
if not exist "venv\" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

REM Check dependencies
echo [CHECK] Checking dependencies...
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed
    echo.
)

REM Check config file
if not exist ".env" (
    echo [WARNING] .env config file not found
    echo [INFO] Please create .env file and configure Telegram Token
    echo.
)

REM Create necessary directories
if not exist "data\" mkdir data
if not exist "data\logs\" mkdir data\logs

REM Stop old services
echo [CLEANUP] Stopping old service processes...
powershell -NoProfile -Command "Get-Process pythonw -ErrorAction SilentlyContinue | ForEach-Object { $cmd = (Get-WmiObject Win32_Process -Filter \"ProcessId=$($_.Id)\" -ErrorAction SilentlyContinue).CommandLine; if ($cmd -like '*bot_listener_db*' -or $cmd -like '*web_dashboard_db*' -or $cmd -like '*result_notifier_db*') { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue } }" >nul 2>&1
timeout /t 2 >nul

echo.
echo ====================================
echo   Starting Services
echo ====================================
echo.

REM Start all services in background without new windows
echo [1/3] Starting Bot Listener...
start /B pythonw bot_listener_db.py
timeout /t 2 >nul
echo       OK Bot Listener started

echo [2/3] Starting Web Dashboard...
start /B pythonw web_dashboard_db.py
timeout /t 3 >nul
echo       OK Web Dashboard started

echo [3/3] Starting Result Notifier...
start /B pythonw result_notifier_db.py
timeout /t 2 >nul
echo       OK Result Notifier started

echo.
echo ====================================
echo   Service Status
echo ====================================
echo.
echo OK Bot Listener: Running (Monitoring Telegram messages)
echo OK Web Dashboard: http://localhost:5000
echo OK Result Notifier: Running (Auto-notify task results)
echo.
echo Log location: data\logs\
echo.
echo ====================================
echo   Management Commands
echo ====================================
echo.
echo - Stop services: stop.bat
echo - View logs: type data\logs\*.log
echo - Restart services: restart.bat
echo - Check status: status.bat
echo.
echo [TIP] All services are running in background
echo [TIP] You can safely close this window
echo.
pause



