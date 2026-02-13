@echo off
setlocal
chcp 65001 >nul
title OpenClawMail Stop Script
color 0C

REM Disable AutoRun to prevent errors
reg delete "HKCU\Software\Microsoft\Command Processor" /v AutoRun /f >nul 2>&1
reg delete "HKLM\Software\Microsoft\Command Processor" /v AutoRun /f >nul 2>&1

echo ====================================
echo   OpenClawMail Stop Script v2.0
echo ====================================
echo.

echo [STOP] Stopping all services...
echo.

REM Method 1: Stop by process name and command line
echo [1/3] Stopping Bot Listener...
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq pythonw.exe" /FO LIST ^| findstr /C:"PID:"') do (
    wmic process where "ProcessId=%%i" get CommandLine 2>nul | findstr /C:"bot_listener_db.py" >nul
    if !errorlevel! equ 0 (
        taskkill /F /PID %%i >nul 2>&1
        echo       OK Bot Listener stopped
        goto :bot_done
    )
)
echo       - Bot Listener not running
:bot_done

echo [2/3] Stopping Web Dashboard...
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq pythonw.exe" /FO LIST ^| findstr /C:"PID:"') do (
    wmic process where "ProcessId=%%i" get CommandLine 2>nul | findstr /C:"web_dashboard_db.py" >nul
    if !errorlevel! equ 0 (
        taskkill /F /PID %%i >nul 2>&1
        echo       OK Web Dashboard stopped
        goto :web_done
    )
)
echo       - Web Dashboard not running
:web_done

echo [3/3] Stopping Result Notifier...
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq pythonw.exe" /FO LIST ^| findstr /C:"PID:"') do (
    wmic process where "ProcessId=%%i" get CommandLine 2>nul | findstr /C:"result_notifier_db.py" >nul
    if !errorlevel! equ 0 (
        taskkill /F /PID %%i >nul 2>&1
        echo       OK Result Notifier stopped
        goto :notifier_done
    )
)
echo       - Result Notifier not running
:notifier_done

echo.
echo ====================================
echo   Stop Complete
echo ====================================
echo.
echo All OpenClawMail services stopped
echo.
timeout /t 2 >nul



