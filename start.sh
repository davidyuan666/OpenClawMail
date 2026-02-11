#!/bin/bash

echo "===================================="
echo "OpenClaw-Email 启动脚本"
echo "===================================="
echo ""

echo "[1/3] 启动 Bot 监听器..."
python bot_listener_db.py &
sleep 2

echo "[2/3] 启动 Web 管理界面..."
python web_dashboard_db.py &
sleep 2

echo "[3/3] 启动结果通知器..."
python result_notifier_db.py &

echo ""
echo "===================================="
echo "所有服务已启动！"
echo "===================================="
echo ""
echo "Bot 监听器: 监听 Telegram 消息"
echo "Web 管理界面: http://localhost:5000"
echo "结果通知器: 自动通知已完成任务"
echo ""
