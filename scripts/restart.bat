@echo off
setlocal
chcp 65001 >nul
title OpenClawMail Restart Script
color 0E

REM Change to project root directory
cd /d "%~dp0\.."

REM Disable AutoRun to prevent errors
reg delete "HKCU\Software\Microsoft\Command Processor" /v AutoRun /f >nul 2>&1
reg delete "HKLM\Software\Microsoft\Command Processor" /v AutoRun /f >nul 2>&1

echo ====================================
echo   OpenClawMail Restart Script v3.0
echo ====================================
echo.

echo [Step 1/2] Stopping all services...
call scripts\stop.bat
timeout /t 2 >nul

echo.
echo [Step 2/2] Starting all services...
call scripts\start.bat

echo.
echo ====================================
echo   Restart Complete
echo ====================================
echo.

