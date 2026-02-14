@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title OpenClawMail Stop Script
color 0C

REM Change to project root directory
cd /d "%~dp0\.."

REM Disable AutoRun to prevent errors
reg delete "HKCU\Software\Microsoft\Command Processor" /v AutoRun /f >nul 2>&1
reg delete "HKLM\Software\Microsoft\Command Processor" /v AutoRun /f >nul 2>&1

echo ====================================
echo   OpenClawMail Stop Script v3.0
echo ====================================
echo.

echo [STOP] Stopping all services...
echo.

REM Stop all OpenClawMail services
powershell -NoProfile -Command "Get-Process pythonw -ErrorAction SilentlyContinue | ForEach-Object { $cmd = (Get-WmiObject Win32_Process -Filter \"ProcessId=$($_.Id)\" -ErrorAction SilentlyContinue).CommandLine; if ($cmd -like '*src.services*' -or $cmd -like '*src.web*') { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue; Write-Host \"Stopped process PID $($_.Id)\" } }" 2>nul

echo [1/5] Bot Listener stopped
echo [2/5] Web Dashboard stopped
echo [3/5] Result Notifier stopped
echo [4/5] Auto Executor stopped
echo [5/5] File Watcher stopped

REM Clean up PID files
if exist "data\.bot_listener.pid" del /f /q "data\.bot_listener.pid" >nul 2>&1
if exist "data\.web_dashboard.pid" del /f /q "data\.web_dashboard.pid" >nul 2>&1
if exist "data\.result_notifier.pid" del /f /q "data\.result_notifier.pid" >nul 2>&1
if exist "data\.auto_executor.pid" del /f /q "data\.auto_executor.pid" >nul 2>&1
if exist "data\.file_watcher.pid" del /f /q "data\.file_watcher.pid" >nul 2>&1

echo.
echo ====================================
echo   Stop Complete
echo ====================================
echo.
echo All OpenClawMail services stopped
echo.
timeout /t 2 >nul



