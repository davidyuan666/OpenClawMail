# -*- coding: utf-8 -*-
"""
Telegram 配置管理模块
"""
import sqlite3
from datetime import datetime
from contextlib import contextmanager
from logger import setup_logger

logger = setup_logger('telegram_config_manager', 'data/logs/telegram_config_manager.log')

class TelegramConfigManager:
    """Telegram 配置管理器"""

    def __init__(self, db_path="data/tasks.db"):
        self.db_path = db_path
        self.init_tables()

    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            conn.close()

    def init_tables(self):
        """初始化 Telegram 配置表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS telegram_config (
                    id INTEGER PRIMARY KEY,
                    enabled INTEGER DEFAULT 0,
                    bot_token TEXT,
                    chat_id TEXT,
                    updated_at TEXT
                )
            ''')

            # 插入默认配置
            cursor.execute('SELECT COUNT(*) FROM telegram_config')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO telegram_config (enabled, updated_at)
                    VALUES (0, ?)
                ''', (datetime.now().isoformat(),))

            logger.info("Telegram 配置表初始化完成")

    def get_config(self):
        """获取 Telegram 配置"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM telegram_config WHERE id = 1')
                row = cursor.fetchone()
                if row:
                    return {
                        'enabled': bool(row['enabled']),
                        'bot_token': row['bot_token'] or '',
                        'chat_id': row['chat_id'] or '',
                        'has_token': bool(row['bot_token'])
                    }
                return {'enabled': False, 'bot_token': '', 'chat_id': '', 'has_token': False}
        except Exception as e:
            logger.error(f"获取 Telegram 配置失败: {e}")
            return {'enabled': False, 'bot_token': '', 'chat_id': '', 'has_token': False}

    def update_config(self, enabled=None, bot_token=None, chat_id=None):
        """更新 Telegram 配置"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                updates = ['updated_at = ?']
                params = [datetime.now().isoformat()]

                if enabled is not None:
                    updates.append('enabled = ?')
                    params.append(1 if enabled else 0)
                if bot_token is not None:
                    updates.append('bot_token = ?')
                    params.append(bot_token)
                if chat_id is not None:
                    updates.append('chat_id = ?')
                    params.append(chat_id)

                sql = f"UPDATE telegram_config SET {', '.join(updates)} WHERE id = 1"
                cursor.execute(sql, params)
                logger.info("Telegram 配置更新成功")
                return True
        except Exception as e:
            logger.error(f"更新 Telegram 配置失败: {e}")
            raise
