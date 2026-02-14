#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OpenClawMail - 统一入口文件
提供命令行接口启动各个服务
"""
import sys
import argparse
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    parser = argparse.ArgumentParser(
        description='OpenClawMail - 智能任务管理系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py web              # 启动 Web 管理界面
  python main.py bot              # 启动 Telegram Bot 监听器
  python main.py notifier         # 启动结果通知器
  python main.py auto             # 启动自动执行器
  python main.py watcher          # 启动文件监控器
  python main.py all              # 启动所有服务
        """
    )

    parser.add_argument(
        'service',
        choices=['web', 'bot', 'notifier', 'auto', 'watcher', 'all'],
        help='要启动的服务'
    )

    args = parser.parse_args()

    if args.service == 'web':
        from src.web.dashboard import app, logger, Config
        logger.info("启动 Web 管理界面...")
        logger.info(f"访问地址: http://{Config.WEB_HOST}:{Config.WEB_PORT}")
        app.run(debug=Config.WEB_DEBUG, host=Config.WEB_HOST, port=Config.WEB_PORT)

    elif args.service == 'bot':
        from src.services.bot_listener import main as bot_main
        bot_main()

    elif args.service == 'notifier':
        from src.services.result_notifier import main as notifier_main
        notifier_main()

    elif args.service == 'auto':
        from src.services.auto_executor import main as auto_main
        auto_main()

    elif args.service == 'watcher':
        from src.services.file_watcher import main as watcher_main
        watcher_main()

    elif args.service == 'all':
        from scripts.start_services import main as start_all
        start_all()


if __name__ == '__main__':
    main()
