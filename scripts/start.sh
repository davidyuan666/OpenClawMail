#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "===================================="
echo "  OpenClawMail 启动脚本 v2.0"
echo "===================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[错误]${NC} 未检测到 Python3，请先安装 Python 3.8+"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}[提示]${NC} 未检测到虚拟环境，正在创建..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[错误]${NC} 创建虚拟环境失败"
        exit 1
    fi
    echo -e "${GREEN}[成功]${NC} 虚拟环境创建完成"
    echo ""
fi

# 激活虚拟环境
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}[错误]${NC} 激活虚拟环境失败"
    exit 1
fi

# 检查依赖
echo -e "${BLUE}[检查]${NC} 正在检查依赖包..."
pip show flask &> /dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[提示]${NC} 依赖包未安装，正在安装..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}[错误]${NC} 安装依赖失败"
        exit 1
    fi
    echo -e "${GREEN}[成功]${NC} 依赖安装完成"
    echo ""
fi

# 检查配置文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}[警告]${NC} 未检测到 .env 配置文件"
    echo -e "${YELLOW}[提示]${NC} 请创建 .env 文件并配置 Telegram Token"
    echo ""
fi

# 创建必要的目录
mkdir -p data/logs

# 切换到项目根目录
cd "$(dirname "$0")/.." || exit 1

# 停止已运行的服务
echo -e "${BLUE}[清理]${NC} 停止旧的服务进程..."
pkill -f "src.services.bot_listener" 2>/dev/null
pkill -f "src.web.dashboard" 2>/dev/null
pkill -f "src.services.result_notifier" 2>/dev/null
pkill -f "src.services.auto_executor" 2>/dev/null
pkill -f "src.services.file_watcher" 2>/dev/null
sleep 1

echo ""
echo "===================================="
echo "  启动服务"
echo "===================================="
echo ""

# 启动 Bot 监听器
echo -e "${BLUE}[1/5]${NC} 启动 Bot 监听器..."
nohup python -m src.services.bot_listener > data/logs/bot_listener.out 2>&1 &
BOT_PID=$!
sleep 2
if ps -p $BOT_PID > /dev/null; then
    echo -e "      ${GREEN}✓${NC} Bot 监听器已启动 (PID: $BOT_PID)"
else
    echo -e "      ${RED}✗${NC} Bot 监听器启动失败"
fi

# 启动 Web 管理界面
echo -e "${BLUE}[2/5]${NC} 启动 Web 管理界面..."
nohup python -m src.web.dashboard > data/logs/web_dashboard.out 2>&1 &
WEB_PID=$!
sleep 3
if ps -p $WEB_PID > /dev/null; then
    echo -e "      ${GREEN}✓${NC} Web 管理界面已启动 (PID: $WEB_PID)"
else
    echo -e "      ${RED}✗${NC} Web 管理界面启动失败"
fi

# 启动结果通知器
echo -e "${BLUE}[3/5]${NC} 启动结果通知器..."
nohup python -m src.services.result_notifier > data/logs/result_notifier.out 2>&1 &
NOTIFIER_PID=$!
sleep 2
if ps -p $NOTIFIER_PID > /dev/null; then
    echo -e "      ${GREEN}✓${NC} 结果通知器已启动 (PID: $NOTIFIER_PID)"
else
    echo -e "      ${RED}✗${NC} 结果通知器启动失败"
fi

# 启动自动执行器
echo -e "${BLUE}[4/5]${NC} 启动自动执行器..."
nohup python -m src.services.auto_executor > data/logs/auto_executor.out 2>&1 &
AUTO_PID=$!
sleep 2
if ps -p $AUTO_PID > /dev/null; then
    echo -e "      ${GREEN}✓${NC} 自动执行器已启动 (PID: $AUTO_PID)"
else
    echo -e "      ${RED}✗${NC} 自动执行器启动失败"
fi

# 启动文件监控器
echo -e "${BLUE}[5/5]${NC} 启动文件监控器..."
nohup python -m src.services.file_watcher > data/logs/file_watcher.out 2>&1 &
WATCHER_PID=$!
sleep 2
if ps -p $WATCHER_PID > /dev/null; then
    echo -e "      ${GREEN}✓${NC} 文件监控器已启动 (PID: $WATCHER_PID)"
else
    echo -e "      ${RED}✗${NC} 文件监控器启动失败"
fi

# 保存 PID 到文件
echo $BOT_PID > data/.bot_listener.pid
echo $WEB_PID > data/.web_dashboard.pid
echo $NOTIFIER_PID > data/.result_notifier.pid
echo $AUTO_PID > data/.auto_executor.pid
echo $WATCHER_PID > data/.file_watcher.pid

echo ""
echo "===================================="
echo "  服务状态"
echo "===================================="
echo ""
echo -e "${GREEN}✓${NC} Bot 监听器: 运行中 (监听 Telegram 消息)"
echo -e "${GREEN}✓${NC} Web 管理界面: http://localhost:5000"
echo -e "${GREEN}✓${NC} 结果通知器: 运行中 (自动通知任务结果)"
echo -e "${GREEN}✓${NC} 自动执行器: 运行中 (自动巡航执行)"
echo -e "${GREEN}✓${NC} 文件监控器: 运行中 (监控文件发送)"
echo ""
echo "日志位置: data/logs/"
echo ""
echo "===================================="
echo "  管理命令"
echo "===================================="
echo ""
echo "• 停止服务: ./scripts/stop.sh"
echo "• 重启服务: ./scripts/restart.sh"
echo "• 查看日志: tail -f data/logs/*.log"
echo ""

