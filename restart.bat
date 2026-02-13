@echo off
setlocal
chcp 65001 >nul
title OpenClawMail Restart Script
color 0E

REM Disable AutoRun to prevent errors
reg delete "HKCU\Software\Microsoft\Command Processor" /v AutoRun /f >nul 2>&1
reg delete "HKLM\Software\Microsoft\Command Processor" /v AutoRun /f >nul 2>&1

echo ====================================
echo   OpenClawMail Restart Script
echo ====================================
echo.

echo [Step 1/2] Stopping all services...
call stop.bat
timeout /t 2 >nul

echo.
echo [Step 2/2] Starting all services...
call start.bat

echo.
echo ====================================
echo   Restart Complete
echo ====================================
echo.

