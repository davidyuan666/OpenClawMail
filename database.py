# -*- coding: utf-8 -*-
"""
数据库模型 - 使用 SQLite
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
from logger import setup_logger

logger = setup_logger('database', 'data/logs/database.log')

class Database:
    def __init__(self, db_path="data/tasks.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    @contextmanager
    def get_connection(self):
        """获取数据库连接（上下文管理器）"""
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

    def init_db(self):
        """初始化数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority TEXT DEFAULT 'normal',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    result TEXT,
                    error TEXT
                )
            ''')

            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_status
                ON tasks(status)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_created_at
                ON tasks(created_at DESC)
            ''')

            logger.info("数据库初始化完成")

    def create_task(self, user_id, message, priority='normal'):
        """创建任务"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        task_id = f"task_{timestamp}"
        now = datetime.now().isoformat()

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO tasks (id, user_id, message, status, priority, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (task_id, user_id, message, '待处理', priority, now, now))
                logger.info(f"任务创建成功: {task_id}")
                return task_id
        except Exception as e:
            logger.error(f"创建任务失败: {e}")
            raise

    def get_task(self, task_id):
        """获取单个任务"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"获取任务失败: {e}")
            return None

    def list_tasks(self, status=None, limit=100, offset=0):
        """列出任务"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if status:
                    cursor.execute(
                        'SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC LIMIT ? OFFSET ?',
                        (status, limit, offset)
                    )
                else:
                    cursor.execute(
                        'SELECT * FROM tasks ORDER BY created_at DESC LIMIT ? OFFSET ?',
                        (limit, offset)
                    )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"列出任务失败: {e}")
            return []

    def update_status(self, task_id, status, result=None, error=None):
        """更新任务状态"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()

                updates = ['status = ?', 'updated_at = ?']
                params = [status, now]

                if status == '处理中':
                    updates.append('started_at = ?')
                    params.append(now)
                elif status in ['已完成', '失败', '已归档']:
                    updates.append('completed_at = ?')
                    params.append(now)

                if result:
                    updates.append('result = ?')
                    params.append(result)
                if error:
                    updates.append('error = ?')
                    params.append(error)

                params.append(task_id)
                sql = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(sql, params)
                logger.info(f"任务状态更新: {task_id} -> {status}")
        except Exception as e:
            logger.error(f"更新任务状态失败: {e}")
            raise

    def get_stats(self):
        """获取统计信息"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                stats = {}
                for status in ['待处理', '处理中', '已完成', '失败', '已归档']:
                    cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = ?', (status,))
                    stats[status] = cursor.fetchone()[0]
                return stats
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}

    def can_edit_task(self, task_id):
        """检查任务是否可编辑（只有待处理状态的任务可编辑）"""
        task = self.get_task(task_id)
        if not task:
            return False
        return task['status'] == '待处理'

    def can_delete_task(self, task_id):
        """检查任务是否可删除（只有待处理状态的任务可删除）"""
        task = self.get_task(task_id)
        if not task:
            return False
        return task['status'] == '待处理'

    def update_task(self, task_id, message=None, priority=None):
        """更新任务内容和优先级（仅允许在待处理状态下编辑）"""
        try:
            # 检查是否可编辑
            if not self.can_edit_task(task_id):
                raise ValueError("任务状态不允许编辑")

            with self.get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()

                updates = ['updated_at = ?']
                params = [now]

                if message is not None:
                    updates.append('message = ?')
                    params.append(message)
                if priority is not None:
                    updates.append('priority = ?')
                    params.append(priority)

                params.append(task_id)
                sql = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(sql, params)
                logger.info(f"任务更新成功: {task_id}")
                return True
        except Exception as e:
            logger.error(f"更新任务失败: {e}")
            raise

    def delete_task(self, task_id):
        """删除任务（仅允许删除待处理状态的任务）"""
        try:
            # 检查是否可删除
            if not self.can_delete_task(task_id):
                raise ValueError("任务状态不允许删除")

            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
                logger.info(f"任务删除成功: {task_id}")
                return True
        except Exception as e:
            logger.error(f"删除任务失败: {e}")
            raise

    def can_archive_task(self, task_id):
        """检查任务是否可归档（只有已完成或失败的任务可归档）"""
        task = self.get_task(task_id)
        if not task:
            return False
        return task['status'] in ['已完成', '失败']

    def archive_task(self, task_id):
        """归档任务（仅允许归档已完成或失败的任务）"""
        try:
            # 检查是否可归档
            if not self.can_archive_task(task_id):
                raise ValueError("任务状态不允许归档")

            self.update_status(task_id, '已归档')
            logger.info(f"任务归档成功: {task_id}")
            return True
        except Exception as e:
            logger.error(f"归档任务失败: {e}")
            raise
