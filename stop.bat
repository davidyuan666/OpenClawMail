@echo off
chcp 65001 >nul
echo ====================================
echo OpenClaw-Email 停止脚本
echo ====================================
echo.

echo [1/3] 停止 Bot 监听器...
taskkill /FI "WINDOWTITLE eq Bot Listener*" /T /F >nul 2>&1
if %errorlevel% equ 0 (
    echo Bot 监听器已停止
) else (
    echo Bot 监听器未运行或已停止
)
timeout /t 1 >nul

echo [2/3] 停止 Web 管理界面...
taskkill /FI "WINDOWTITLE eq Web Dashboard*" /T /F >nul 2>&1
if %errorlevel% equ 0 (
    echo Web 管理界面已停止
) else (
    echo Web 管理界面未运行或已停止
)
timeout /t 1 >nul

echo [3/3] 停止结果通知器...
taskkill /FI "WINDOWTITLE eq Result Notifier*" /T /F >nul 2>&1
if %errorlevel% equ 0 (
    echo 结果通知器已停止
) else (
    echo 结果通知器未运行或已停止
)

echo.
echo ====================================
echo 清理 Python 进程...
echo ====================================

REM 额外清理：根据进程名称停止相关Python进程
taskkill /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *bot_listener_db*" /T /F >nul 2>&1
taskkill /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *web_dashboard_db*" /T /F >nul 2>&1
taskkill /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *result_notifier_db*" /T /F >nul 2>&1

echo.
echo ====================================
echo 所有服务已停止！
echo ====================================
echo.
timeout /t 3 >nul
exit /b 0
