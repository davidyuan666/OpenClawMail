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
echo "  OpenClawMail 重启脚本 v3.0"
echo "===================================="
echo ""

echo -e "${BLUE}[步骤 1/2]${NC} 停止所有服务..."
./scripts/stop.sh
sleep 2

echo ""
echo -e "${BLUE}[步骤 2/2]${NC} 启动所有服务..."
./scripts/start.sh

echo ""
echo "===================================="
echo "  重启完成"
echo "===================================="
echo ""
