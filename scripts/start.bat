@echo off
setlocal
chcp 65001 >nul
title OpenClawMail Service Manager
color 0A

REM Change to project root directory
cd /d "%~dp0\.."

REM Disable AutoRun to prevent errors
reg delete "HKCU\Software\Microsoft\Command Processor" /v AutoRun /f >nul 2>&1
reg delete "HKLM\Software\Microsoft\Command Processor" /v AutoRun /f >nul 2>&1

echo ====================================
echo   OpenClawMail Startup Script v3.0
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
powershell -NoProfile -Command "Get-Process pythonw -ErrorAction SilentlyContinue | ForEach-Object { $cmd = (Get-WmiObject Win32_Process -Filter \"ProcessId=$($_.Id)\" -ErrorAction SilentlyContinue).CommandLine; if ($cmd -like '*src.services*' -or $cmd -like '*src.web*') { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue } }" >nul 2>&1
timeout /t 2 >nul

echo.
echo ====================================
echo   Starting Services
echo ====================================
echo.

REM Start all services in background without new windows
echo [1/5] Starting Bot Listener...
start /B pythonw -m src.services.bot_listener
timeout /t 2 >nul
echo       OK Bot Listener started

echo [2/5] Starting Web Dashboard...
start /B pythonw -m src.web.dashboard
timeout /t 3 >nul
echo       OK Web Dashboard started

echo [3/5] Starting Result Notifier...
start /B pythonw -m src.services.result_notifier
timeout /t 2 >nul
echo       OK Result Notifier started

echo [4/5] Starting Auto Executor...
start /B pythonw -m src.services.auto_executor
timeout /t 2 >nul
echo       OK Auto Executor started

echo [5/5] Starting File Watcher...
start /B pythonw -m src.services.file_watcher
timeout /t 2 >nul
echo       OK File Watcher started

echo.
echo ====================================
echo   Service Status
echo ====================================
echo.
echo OK Bot Listener: Running (Monitoring Telegram messages)
echo OK Web Dashboard: http://localhost:5000
echo OK Result Notifier: Running (Auto-notify task results)
echo OK Auto Executor: Running (Auto-cruise execution)
echo OK File Watcher: Running (Monitoring file send requests)
echo.
echo Log location: data\logs\
echo.
echo ====================================
echo   Management Commands
echo ====================================
echo.
echo - Stop services: scripts\stop.bat
echo - View logs: type data\logs\*.log
echo - Restart services: scripts\restart.bat
echo.
echo [TIP] All services are running in background
echo [TIP] You can safely close this window
echo.
pause



