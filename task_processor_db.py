# -*- coding: utf-8 -*-
"""
任务处理器 - 使用数据库版本
"""
from database import Database
from logger import setup_logger

logger = setup_logger('task_processor', 'data/logs/task_processor.log')

def show_task(task_id):
    """显示任务详情"""
    db = Database()
    task = db.get_task(task_id)

    if not task:
        logger.warning(f"任务 {task_id} 不存在")
        return None

    logger.info(f"\n{'='*50}")
    logger.info(f"任务ID: {task['id']}")
    logger.info(f"状态: {task['status']}")
    logger.info(f"优先级: {task['priority']}")
    logger.info(f"创建时间: {task['created_at']}")
    logger.info(f"{'='*50}")
    logger.info(f"\n任务内容:\n{task['message']}")
    logger.info(f"\n{'='*50}\n")

    return task

def process_task(task_id, result_text):
    """处理任务并保存结果"""
    db = Database()

    # 更新为处理中
    db.update_status(task_id, 'processing')
    logger.info(f"任务 {task_id} 标记为处理中")

    # 保存结果
    db.update_status(task_id, 'completed', result=result_text)
    logger.info(f"任务 {task_id} 已完成")

    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        show_task(sys.argv[1])
