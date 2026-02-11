# -*- coding: utf-8 -*-
"""
Bot 监听器 - 使用数据库版本
"""
import time
from database import Database
from telegram_client import TelegramClient
from logger import setup_logger

logger = setup_logger('bot_listener', 'data/logs/bot_listener.log')

def main():
    """主循环"""
    db = Database()
    telegram = TelegramClient()
    offset = None

    logger.info("Bot 监听器启动中...")
    logger.info(f"监听 Chat ID: {telegram.chat_id}")

    while True:
        try:
            result = telegram.get_updates(offset)
            if not result or not result.get("ok"):
                time.sleep(1)
                continue

            for update in result.get("result", []):
                offset = update["update_id"] + 1

                message = update.get("message", {})
                if not message:
                    continue

                chat_id = str(message.get("chat", {}).get("id", ""))
                if chat_id != telegram.chat_id:
                    continue

                text = message.get("text", "").strip()
                if not text or text.startswith("/"):
                    continue

                user_id = str(message.get("from", {}).get("id", ""))

                # 创建任务
                task_id = db.create_task(user_id, text)
                logger.info(f"新任务: {task_id}")

                # 发送确认
                telegram.send_message(
                    f"✅ 任务已创建\n\n"
                    f"**任务ID**: `{task_id}`\n"
                    f"**内容**: {text}\n\n"
                    f"请在 Web 界面查看并处理任务"
                )

        except KeyboardInterrupt:
            logger.info("停止监听")
            break
        except Exception as e:
            logger.error(f"错误: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
