# -*- coding: utf-8 -*-
"""
历史上下文管理模块
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
from src.core.logger import setup_logger

logger = setup_logger('history_manager', 'data/logs/history_manager.log')

class HistoryManager:
    """历史上下文管理器"""

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
        """初始化历史上下文相关表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 历史上下文配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history_config (
                    id INTEGER PRIMARY KEY,
                    enabled INTEGER DEFAULT 0,
                    max_history_count INTEGER DEFAULT 5,
                    updated_at TEXT
                )
            ''')

            # 历史上下文记录表（存储压缩后的上下文）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history_context_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            ''')

            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_history_created_at
                ON history_context_records(created_at DESC)
            ''')

            # 如果配置表为空，插入默认配置
            cursor.execute('SELECT COUNT(*) FROM history_config')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO history_config (enabled, max_history_count, updated_at)
                    VALUES (0, 5, ?)
                ''', (datetime.now().isoformat(),))

            logger.info("历史上下文表初始化完成")

    def get_config(self):
        """获取历史上下文配置"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM history_config WHERE id = 1')
                row = cursor.fetchone()
                if row:
                    return {
                        'enabled': bool(row['enabled']),
                        'max_history_count': row['max_history_count']
                    }
                return {'enabled': False, 'max_history_count': 5}
        except Exception as e:
            logger.error(f"获取历史配置失败: {e}")
            return {'enabled': False, 'max_history_count': 5}

    def update_config(self, enabled=None, max_history_count=None):
        """更新历史上下文配置"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                updates = ['updated_at = ?']
                params = [datetime.now().isoformat()]

                if enabled is not None:
                    updates.append('enabled = ?')
                    params.append(1 if enabled else 0)
                if max_history_count is not None:
                    updates.append('max_history_count = ?')
                    params.append(max_history_count)

                sql = f"UPDATE history_config SET {', '.join(updates)} WHERE id = 1"
                cursor.execute(sql, params)
                logger.info(f"历史配置更新成功: enabled={enabled}, max_count={max_history_count}")
                return True
        except Exception as e:
            logger.error(f"更新历史配置失败: {e}")
            raise

    def get_recent_history(self, limit=5):
        """获取最近的历史上下文记录"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, task_id, summary, created_at
                    FROM history_context_records
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"获取历史记录失败: {e}")
            return []

    def add_context_record(self, task_id, task_message, task_result):
        """添加历史上下文记录（压缩任务信息）"""
        try:
            # 压缩任务信息：只保留关键内容
            summary = f"任务: {task_message[:200]}"
            if task_result:
                summary += f"\n结果: {task_result[:300]}"

            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO history_context_records (task_id, summary, created_at)
                    VALUES (?, ?, ?)
                ''', (task_id, summary, datetime.now().isoformat()))

                # 检查是否超过最大记录数，如果超过则删除最旧的
                config = self.get_config()
                max_count = config['max_history_count']

                cursor.execute('SELECT COUNT(*) FROM history_context_records')
                total = cursor.fetchone()[0]

                if total > max_count:
                    # 删除最旧的记录
                    cursor.execute('''
                        DELETE FROM history_context_records
                        WHERE id IN (
                            SELECT id FROM history_context_records
                            ORDER BY created_at ASC
                            LIMIT ?
                        )
                    ''', (total - max_count,))

                logger.info(f"添加历史上下文记录: {task_id}")
                return True
        except Exception as e:
            logger.error(f"添加历史上下文记录失败: {e}")
            return False

    def build_history_context(self):
        """构建历史上下文字符串"""
        config = self.get_config()
        if not config['enabled']:
            return ""

        history = self.get_recent_history(config['max_history_count'])
        if not history:
            return ""

        context = "\n## 历史任务上下文\n\n"
        context += "以下是最近完成的任务记录，可以帮助你了解之前的工作内容：\n\n"

        for i, record in enumerate(history, 1):
            context += f"### 历史任务 {i}\n"
            context += f"- **任务ID**: {record['task_id']}\n"
            context += f"- **时间**: {record['created_at']}\n"
            context += f"{record['summary']}\n\n"

        context += "---\n\n"
        return context

    def clear_history(self):
        """清除所有历史上下文记录"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM history_context_records')
                affected = cursor.rowcount
                logger.info(f"清除历史上下文记录成功，共删除 {affected} 条记录")
                return affected
        except Exception as e:
            logger.error(f"清除历史记录失败: {e}")
            raise

    def get_history_stats(self):
        """获取历史记录统计"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total FROM history_context_records')
                total = cursor.fetchone()['total']

                return {
                    'total': total,
                    'max_count': self.get_config()['max_history_count']
                }
        except Exception as e:
            logger.error(f"获取历史统计失败: {e}")
            return {'total': 0, 'max_count': 5}
