# -*- coding: utf-8 -*-
"""
配置管理模块
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """配置类"""

    # Telegram 配置
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    TELEGRAM_BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

    # 数据库配置
    DATABASE_PATH = "data/tasks.db"

    # Web 配置
    WEB_HOST = "0.0.0.0"
    WEB_PORT = 5000
    WEB_DEBUG = True

    # 超时配置
    REQUEST_TIMEOUT = 10
    LONG_POLL_TIMEOUT = 30

    # Claude CLI 配置
    CLAUDE_CLI_PATH = os.getenv('CLAUDE_CLI_PATH', 'claude')
    CLAUDE_WORKSPACE_DIR = os.getenv('CLAUDE_WORKSPACE_DIR', os.getcwd())
    CLAUDE_TIMEOUT = int(os.getenv('CLAUDE_TIMEOUT', '180'))

    @classmethod
    def validate(cls):
        """验证配置"""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN 未设置")
        if not cls.TELEGRAM_CHAT_ID:
            raise ValueError("TELEGRAM_CHAT_ID 未设置")
        return True

# 验证配置
Config.validate()
