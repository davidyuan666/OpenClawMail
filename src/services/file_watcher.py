# -*- coding: utf-8 -*-
"""
Telegram 文件发送监控服务
监控 telegram_send_request.json 文件，自动发送文件到 Telegram
"""
import os
import json
import time
from pathlib import Path
from src.telegram.client import TelegramClient
from src.core.logger import setup_logger

logger = setup_logger('telegram_file_watcher', 'data/logs/telegram_file_watcher.log')

class TelegramFileWatcher:
    """Telegram 文件发送监控器"""

    REQUEST_FILE = "telegram_send_request.json"
    CHECK_INTERVAL = 2  # 检查间隔（秒）

    def __init__(self):
        self.telegram = TelegramClient()
        self.last_mtime = None

    def check_and_process(self):
        """检查并处理发送请求"""
        try:
            if not os.path.exists(self.REQUEST_FILE):
                return

            # 检查文件是否被修改
            current_mtime = os.path.getmtime(self.REQUEST_FILE)
            if self.last_mtime is not None and current_mtime == self.last_mtime:
                return

            self.last_mtime = current_mtime

            # 读取请求
            with open(self.REQUEST_FILE, 'r', encoding='utf-8') as f:
                request = json.load(f)

            logger.info(f"检测到发送请求: {request}")

            # 处理请求
            request_type = request.get('type')
            if request_type == 'document':
                self._send_document(request)
            elif request_type == 'message':
                self._send_message(request)
            else:
                logger.error(f"未知的请求类型: {request_type}")
                return

            # 删除请求文件
            os.remove(self.REQUEST_FILE)
            logger.info(f"请求处理完成，已删除请求文件")

        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}")
        except Exception as e:
            logger.error(f"处理请求失败: {e}")

    def _send_document(self, request):
        """发送文档"""
        file_path = request.get('file_path')
        caption = request.get('caption')

        if not file_path:
            logger.error("缺少 file_path 参数")
            return

        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return

        logger.info(f"发送文档: {file_path}")
        result = self.telegram.send_document(file_path, caption)

        if result:
            logger.info(f"文档发送成功: {file_path}")
        else:
            logger.error(f"文档发送失败: {file_path}")

    def _send_message(self, request):
        """发送消息"""
        text = request.get('text')

        if not text:
            logger.error("缺少 text 参数")
            return

        logger.info(f"发送消息: {text[:50]}...")
        result = self.telegram.send_message(text)

        if result:
            logger.info("消息发送成功")
        else:
            logger.error("消息发送失败")

    def run(self):
        """主循环"""
        logger.info("Telegram 文件监控服务启动")
        logger.info(f"监控文件: {self.REQUEST_FILE}")
        logger.info(f"检查间隔: {self.CHECK_INTERVAL} 秒")

        try:
            while True:
                self.check_and_process()
                time.sleep(self.CHECK_INTERVAL)
        except KeyboardInterrupt:
            logger.info("收到停止信号，退出")
        except Exception as e:
            logger.error(f"主循环异常: {e}")


def main():
    """主函数"""
    watcher = TelegramFileWatcher()
    watcher.run()


if __name__ == "__main__":
    main()
