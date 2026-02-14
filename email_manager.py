# -*- coding: utf-8 -*-
"""
Email 管理模块
"""
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
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
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS email_config (
                    id INTEGER PRIMARY KEY,
                    enabled INTEGER DEFAULT 0,
                    smtp_server TEXT,
                    smtp_port INTEGER,
                    imap_server TEXT,
                    imap_port INTEGER,
                    email_address TEXT,
                    email_password TEXT,
                    updated_at TEXT
                )
            ''')

            # 插入默认配置
            cursor.execute('SELECT COUNT(*) FROM email_config')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO email_config (enabled, smtp_server, smtp_port, imap_server, imap_port, email_address, updated_at)
                    VALUES (0, 'smtp.163.com', 465, 'imap.163.com', 993, 'wu.xiguanghua@163.com', ?)
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
                        'imap_server': row['imap_server'],
                        'imap_port': row['imap_port'],
                        'email_address': row['email_address'],
                        'has_password': bool(row['email_password'])
                    }
                return None
        except Exception as e:
            logger.error(f"获取 Email 配置失败: {e}")
            return None

    def update_config(self, enabled=None, smtp_server=None, smtp_port=None,
                     imap_server=None, imap_port=None, email_address=None, email_password=None):
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
                if imap_server:
                    updates.append('imap_server = ?')
                    params.append(imap_server)
                if imap_port:
                    updates.append('imap_port = ?')
                    params.append(imap_port)
                if email_address:
                    updates.append('email_address = ?')
                    params.append(email_address)
                if email_password:
                    updates.append('email_password = ?')
                    params.append(email_password)

                sql = f"UPDATE email_config SET {', '.join(updates)} WHERE id = 1"
                cursor.execute(sql, params)
                logger.info("Email 配置更新成功")
                return True
        except Exception as e:
            logger.error(f"更新 Email 配置失败: {e}")
            raise

    def send_email(self, subject, body):
        """发送邮件"""
        config = self.get_config()
        if not config or not config['enabled']:
            logger.warning("Email 功能未启用")
            return False

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT email_password FROM email_config WHERE id = 1')
                row = cursor.fetchone()
                password = row['email_password'] if row else None

            if not password:
                logger.error("Email 密码未配置")
                return False

            msg = MIMEMultipart()
            msg['From'] = config['email_address']
            msg['To'] = config['email_address']
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            with smtplib.SMTP_SSL(config['smtp_server'], config['smtp_port']) as server:
                server.login(config['email_address'], password)
                server.send_message(msg)

            logger.info(f"邮件发送成功: {subject}")
            return True
        except Exception as e:
            logger.error(f"发送邮件失败: {e}")
            return False

    def check_new_emails(self):
        """检查新邮件"""
        config = self.get_config()
        if not config or not config['enabled']:
            return []

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT email_password FROM email_config WHERE id = 1')
                row = cursor.fetchone()
                password = row['email_password'] if row else None

            if not password:
                return []

            mail = imaplib.IMAP4_SSL(config['imap_server'], config['imap_port'])
            mail.login(config['email_address'], password)
            mail.select('INBOX')

            _, messages = mail.search(None, 'UNSEEN')
            email_ids = messages[0].split()

            emails = []
            for email_id in email_ids[-5:]:  # 只获取最近5封
                _, msg_data = mail.fetch(email_id, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)

                subject = decode_header(email_message['Subject'])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()

                body = ""
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = email_message.get_payload(decode=True).decode()

                emails.append({'subject': subject, 'body': body})

            mail.close()
            mail.logout()
            return emails
        except Exception as e:
            logger.error(f"检查邮件失败: {e}")
            return []
