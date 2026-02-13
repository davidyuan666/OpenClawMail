# -*- coding: utf-8 -*-
"""
Telegram 客户端封装
"""
import requests
from config import Config
from logger import setup_logger

logger = setup_logger('telegram_client', 'data/logs/telegram.log')

class TelegramClient:
    """Telegram API 客户端"""

    def __init__(self):
        self.base_url = Config.TELEGRAM_BASE_URL
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.timeout = Config.REQUEST_TIMEOUT

    def send_message(self, text, parse_mode="Markdown"):
        """发送消息"""
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": text
        }

        if parse_mode:
            data["parse_mode"] = parse_mode

        try:
            response = requests.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            logger.info(f"消息发送成功: {text[:50]}...")
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"发送消息失败: {e}, Response: {response.text}")
            return None
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return None

    def get_updates(self, offset=None):
        """获取更新"""
        url = f"{self.base_url}/getUpdates"
        params = {
            "timeout": Config.LONG_POLL_TIMEOUT,
            "offset": offset
        }

        try:
            response = requests.get(
                url,
                params=params,
                timeout=Config.LONG_POLL_TIMEOUT + 5
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取更新失败: {e}")
            return None

    def send_document(self, file_path, caption=None):
        """发送文档"""
        url = f"{self.base_url}/sendDocument"

        try:
            with open(file_path, 'rb') as f:
                files = {'document': f}
                data = {'chat_id': self.chat_id}
                if caption:
                    data['caption'] = caption

                response = requests.post(url, data=data, files=files, timeout=30)
                response.raise_for_status()
                logger.info(f"文档发送成功: {file_path}")
                return response.json()
        except Exception as e:
            logger.error(f"发送文档失败: {e}")
            return None
