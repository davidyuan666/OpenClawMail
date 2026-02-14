#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 切换到项目根目录
cd "$(dirname "$0")/.." || exit 1

echo "===================================="
echo "  OpenClawMail 停止脚本 v3.0"
echo "===================================="
echo ""

echo -e "${BLUE}[停止]${NC} 正在停止所有服务..."
echo ""

# 方法1: 通过 PID 文件停止
if [ -f "data/.bot_listener.pid" ]; then
    BOT_PID=$(cat data/.bot_listener.pid)
    if ps -p $BOT_PID > /dev/null 2>&1; then
        kill $BOT_PID 2>/dev/null
        echo -e "${GREEN}[1/5]${NC} Bot 监听器已停止 (PID: $BOT_PID)"
    else
        echo -e "${YELLOW}[1/5]${NC} Bot 监听器未运行"
    fi
    rm -f data/.bot_listener.pid
else
    echo -e "${YELLOW}[1/5]${NC} Bot 监听器未运行"
fi

if [ -f "data/.web_dashboard.pid" ]; then
    WEB_PID=$(cat data/.web_dashboard.pid)
    if ps -p $WEB_PID > /dev/null 2>&1; then
        kill $WEB_PID 2>/dev/null
        echo -e "${GREEN}[2/5]${NC} Web 管理界面已停止 (PID: $WEB_PID)"
    else
        echo -e "${YELLOW}[2/5]${NC} Web 管理界面未运行"
    fi
    rm -f data/.web_dashboard.pid
else
    echo -e "${YELLOW}[2/5]${NC} Web 管理界面未运行"
fi

if [ -f "data/.result_notifier.pid" ]; then
    NOTIFIER_PID=$(cat data/.result_notifier.pid)
    if ps -p $NOTIFIER_PID > /dev/null 2>&1; then
        kill $NOTIFIER_PID 2>/dev/null
        echo -e "${GREEN}[3/5]${NC} 结果通知器已停止 (PID: $NOTIFIER_PID)"
    else
        echo -e "${YELLOW}[3/5]${NC} 结果通知器未运行"
    fi
    rm -f data/.result_notifier.pid
else
    echo -e "${YELLOW}[3/5]${NC} 结果通知器未运行"
fi

if [ -f "data/.auto_executor.pid" ]; then
    AUTO_PID=$(cat data/.auto_executor.pid)
    if ps -p $AUTO_PID > /dev/null 2>&1; then
        kill $AUTO_PID 2>/dev/null
        echo -e "${GREEN}[4/5]${NC} 自动执行器已停止 (PID: $AUTO_PID)"
    else
        echo -e "${YELLOW}[4/5]${NC} 自动执行器未运行"
    fi
    rm -f data/.auto_executor.pid
else
    echo -e "${YELLOW}[4/5]${NC} 自动执行器未运行"
fi

if [ -f "data/.file_watcher.pid" ]; then
    WATCHER_PID=$(cat data/.file_watcher.pid)
    if ps -p $WATCHER_PID > /dev/null 2>&1; then
        kill $WATCHER_PID 2>/dev/null
        echo -e "${GREEN}[5/5]${NC} 文件监控器已停止 (PID: $WATCHER_PID)"
    else
        echo -e "${YELLOW}[5/5]${NC} 文件监控器未运行"
    fi
    rm -f data/.file_watcher.pid
else
    echo -e "${YELLOW}[5/5]${NC} 文件监控器未运行"
fi

# 方法2: 通过进程名停止（备用方案）
echo ""
echo -e "${BLUE}[清理]${NC} 清理残留进程..."
pkill -f "src.services.bot_listener" 2>/dev/null
pkill -f "src.web.dashboard" 2>/dev/null
pkill -f "src.services.result_notifier" 2>/dev/null
pkill -f "src.services.auto_executor" 2>/dev/null
pkill -f "src.services.file_watcher" 2>/dev/null
echo -e "      ${GREEN}✓${NC} 清理完成"

echo ""
echo "===================================="
echo "  停止完成"
echo "===================================="
echo ""
echo "所有 OpenClawMail 服务已停止"
echo ""
