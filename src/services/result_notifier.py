# -*- coding: utf-8 -*-
"""
结果通知器 - 使用数据库版本
"""
import time
from src.core.database import Database
from src.telegram.client import TelegramClient
from src.core.logger import setup_logger

logger = setup_logger('result_notifier', 'data/logs/result_notifier.log')

def notify_completed_tasks():
    """通知已完成的任务"""
    db = Database()
    telegram = TelegramClient()
    tasks = db.list_tasks(status='已完成', limit=50)

    for task in tasks:
        result = task.get('result', '无结果')
        message = (
            f"✅ **任务完成**\n\n"
            f"**任务ID**: `{task['id']}`\n"
            f"**原始请求**: {task['message']}\n\n"
            f"**处理结果**:\n{result}"
        )

        if telegram.send_message(message):
            db.update_status(task['id'], '已归档')
            logger.info(f"已通知并归档: {task['id']}")

        time.sleep(1)

if __name__ == "__main__":
    logger.info("检查已完成任务...")
    notify_completed_tasks()
    logger.info("完成")
