# -*- coding: utf-8 -*-
"""
Email 管理模块 - 仅发送通知
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
from datetime import datetime
from contextlib import contextmanager
from logger import setup_logger

logger = setup_logger('email_manager', 'data/logs/email_manager.log')

class EmailManager:
    """Email 管理器"""

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
        """初始化 Email 配置表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 删除旧表（如果存在）并重建
            cursor.execute('DROP TABLE IF EXISTS email_config')

            cursor.execute('''
                CREATE TABLE email_config (
                    id INTEGER PRIMARY KEY,
                    enabled INTEGER DEFAULT 0,
                    smtp_server TEXT,
                    smtp_port INTEGER,
                    sender_email TEXT,
                    sender_password TEXT,
                    recipient_email TEXT,
                    updated_at TEXT
                )
            ''')

            # 插入默认配置
            cursor.execute('''
                INSERT INTO email_config (enabled, smtp_server, smtp_port, recipient_email, updated_at)
                VALUES (0, 'smtp.163.com', 465, 'wu.xiguanghua@163.com', ?)
            ''', (datetime.now().isoformat(),))

            logger.info("Email 配置表初始化完成")

    def get_config(self):
        """获取 Email 配置"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM email_config WHERE id = 1')
                row = cursor.fetchone()
                if row:
                    return {
                        'enabled': bool(row['enabled']),
                        'smtp_server': row['smtp_server'],
                        'smtp_port': row['smtp_port'],
                        'sender_email': row['sender_email'],
                        'recipient_email': row['recipient_email'],
                        'has_password': bool(row['sender_password'])
                    }
                return None
        except Exception as e:
            logger.error(f"获取 Email 配置失败: {e}")
            return None

    def update_config(self, enabled=None, smtp_server=None, smtp_port=None,
                     sender_email=None, sender_password=None, recipient_email=None):
        """更新 Email 配置"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                updates = ['updated_at = ?']
                params = [datetime.now().isoformat()]

                if enabled is not None:
                    updates.append('enabled = ?')
                    params.append(1 if enabled else 0)
                if smtp_server:
                    updates.append('smtp_server = ?')
                    params.append(smtp_server)
                if smtp_port:
                    updates.append('smtp_port = ?')
                    params.append(smtp_port)
                if sender_email:
                    updates.append('sender_email = ?')
                    params.append(sender_email)
                if sender_password:
                    updates.append('sender_password = ?')
                    params.append(sender_password)
                if recipient_email:
                    updates.append('recipient_email = ?')
                    params.append(recipient_email)

                sql = f"UPDATE email_config SET {', '.join(updates)} WHERE id = 1"
                cursor.execute(sql, params)
                logger.info("Email 配置更新成功")
                return True
        except Exception as e:
            logger.error(f"更新 Email 配置失败: {e}")
            raise

    def send_email(self, subject, body):
        """发送邮件到接收邮箱"""
        config = self.get_config()
        if not config or not config['enabled']:
            logger.warning("Email 功能未启用")
            return False

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT sender_password FROM email_config WHERE id = 1')
                row = cursor.fetchone()
                password = row['sender_password'] if row else None

            if not password or not config['sender_email']:
                logger.error("发送邮箱或密码未配置")
                return False

            msg = MIMEMultipart()
            msg['From'] = config['sender_email']
            msg['To'] = config['recipient_email']
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            with smtplib.SMTP_SSL(config['smtp_server'], config['smtp_port']) as server:
                server.login(config['sender_email'], password)
                server.send_message(msg)

            logger.info(f"邮件发送成功: {subject} -> {config['recipient_email']}")
            return True
        except Exception as e:
            logger.error(f"发送邮件失败: {e}")
            return False
