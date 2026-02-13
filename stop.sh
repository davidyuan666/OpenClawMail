#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "===================================="
echo "  OpenClawMail 停止脚本 v2.0"
echo "===================================="
echo ""

echo -e "${BLUE}[停止]${NC} 正在停止所有服务..."
echo ""

# 方法1: 通过 PID 文件停止
if [ -f "data/.bot_listener.pid" ]; then
    BOT_PID=$(cat data/.bot_listener.pid)
    if ps -p $BOT_PID > /dev/null 2>&1; then
        kill $BOT_PID 2>/dev/null
        echo -e "${GREEN}[1/3]${NC} Bot 监听器已停止 (PID: $BOT_PID)"
    else
        echo -e "${YELLOW}[1/3]${NC} Bot 监听器未运行"
    fi
    rm -f data/.bot_listener.pid
else
    echo -e "${YELLOW}[1/3]${NC} Bot 监听器未运行"
fi

if [ -f "data/.web_dashboard.pid" ]; then
    WEB_PID=$(cat data/.web_dashboard.pid)
    if ps -p $WEB_PID > /dev/null 2>&1; then
        kill $WEB_PID 2>/dev/null
        echo -e "${GREEN}[2/3]${NC} Web 管理界面已停止 (PID: $WEB_PID)"
    else
        echo -e "${YELLOW}[2/3]${NC} Web 管理界面未运行"
    fi
    rm -f data/.web_dashboard.pid
else
    echo -e "${YELLOW}[2/3]${NC} Web 管理界面未运行"
fi

if [ -f "data/.result_notifier.pid" ]; then
    NOTIFIER_PID=$(cat data/.result_notifier.pid)
    if ps -p $NOTIFIER_PID > /dev/null 2>&1; then
        kill $NOTIFIER_PID 2>/dev/null
        echo -e "${GREEN}[3/3]${NC} 结果通知器已停止 (PID: $NOTIFIER_PID)"
    else
        echo -e "${YELLOW}[3/3]${NC} 结果通知器未运行"
    fi
    rm -f data/.result_notifier.pid
else
    echo -e "${YELLOW}[3/3]${NC} 结果通知器未运行"
fi

# 方法2: 通过进程名停止（备用方案）
echo ""
echo -e "${BLUE}[清理]${NC} 清理残留进程..."
pkill -f "bot_listener_db.py" 2>/dev/null
pkill -f "web_dashboard_db.py" 2>/dev/null
pkill -f "result_notifier_db.py" 2>/dev/null
echo -e "      ${GREEN}✓${NC} 清理完成"

echo ""
echo "===================================="
echo "  停止完成"
echo "===================================="
echo ""
echo "所有 OpenClawMail 服务已停止"
echo ""
