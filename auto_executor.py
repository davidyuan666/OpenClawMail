# -*- coding: utf-8 -*-
"""
自动任务执行器 - 自动巡航功能
基于队列的异步执行，支持并发控制
"""
import time
import json
import threading
import queue
from pathlib import Path
from database import Database
from claude_executor import ClaudeExecutor
from config import Config
from logger import setup_logger

logger = setup_logger('auto_executor', 'data/logs/auto_executor.log')

class TaskWorker(threading.Thread):
    """任务工作线程"""

    def __init__(self, task_queue, executor, worker_id):
        super().__init__(daemon=False)  # 非守护线程，确保任务完成
        self.task_queue = task_queue
        self.executor = executor
        self.worker_id = worker_id
        self.running = True

    def run(self):
        """工作线程主循环"""
        logger.info(f"工作线程 {self.worker_id} 启动")

        while self.running:
            try:
                # 从队列获取任务（超时 1 秒）
                try:
                    task_id = self.task_queue.get(timeout=1)
                except queue.Empty:
                    continue

                if task_id is None:  # 停止信号
                    break

                logger.info(f"工作线程 {self.worker_id} 开始执行任务: {task_id}")

                # 执行任务（同步执行，确保完成）
                try:
                    result = self.executor.execute_task(task_id)
                    if result['success']:
                        logger.info(f"工作线程 {self.worker_id} 任务执行成功: {task_id}")
                    else:
                        logger.error(f"工作线程 {self.worker_id} 任务执行失败: {task_id}, 错误: {result.get('error')}")
                except Exception as e:
                    logger.error(f"工作线程 {self.worker_id} 执行任务异常: {task_id}, {e}")
                finally:
                    # 标记任务完成
                    self.task_queue.task_done()

            except Exception as e:
                logger.error(f"工作线程 {self.worker_id} 异常: {e}")

        logger.info(f"工作线程 {self.worker_id} 停止")

    def stop(self):
        """停止工作线程"""
        self.running = False


class AutoExecutor:
    """自动任务执行器"""

    CONFIG_FILE = "data/auto_executor_config.json"

    def __init__(self):
        self.db = Database()
        self.executor = ClaudeExecutor(
            db=self.db,
            claude_cli_path=Config.CLAUDE_CLI_PATH,
            workspace_dir=Config.CLAUDE_WORKSPACE_DIR,
            timeout=Config.CLAUDE_TIMEOUT
        )
        self.config = self.load_config()
        self.next_check_time = None  # 下次检查时间

        # 任务队列
        self.task_queue = queue.Queue()

        # 工作线程池
        self.workers = []
        self.workers_lock = threading.Lock()

        # 启动工作线程
        self._start_workers()

    def load_config(self):
        """加载配置"""
        try:
            if Path(self.CONFIG_FILE).exists():
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"加载配置失败: {e}")

        # 默认配置
        return {
            "enabled": False,
            "interval": 60,  # 检查间隔（秒）
            "max_concurrent": 1,  # 最大并发任务数
            "priority_order": ["high", "normal", "low"]  # 优先级顺序
        }

    def save_config(self, config):
        """保存配置"""
        try:
            Path(self.CONFIG_FILE).parent.mkdir(parents=True, exist_ok=True)
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            # 检查是否需要调整工作线程数量
            old_max_concurrent = self.config.get("max_concurrent", 1)
            new_max_concurrent = config.get("max_concurrent", 1)

            self.config = config
            logger.info(f"配置已保存: {config}")

            # 如果并发数改变，重启工作线程
            if old_max_concurrent != new_max_concurrent:
                self._restart_workers()

            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False

    def get_config(self):
        """获取当前配置"""
        return self.config

    def set_enabled(self, enabled):
        """设置启用状态"""
        self.config["enabled"] = enabled
        self.save_config(self.config)
        logger.info(f"自动巡航已{'启用' if enabled else '禁用'}")

    def is_enabled(self):
        """检查是否启用"""
        return self.config.get("enabled", False)

    def get_pending_tasks(self):
        """获取待处理的任务（按优先级排序）"""
        try:
            # 获取所有待处理任务
            pending_tasks = self.db.list_tasks(status='待处理', limit=100)

            # 按优先级排序
            priority_map = {p: i for i, p in enumerate(self.config["priority_order"])}
            pending_tasks.sort(key=lambda t: (
                priority_map.get(t.get('priority', 'normal'), 999),
                t.get('created_at', '')
            ))

            return pending_tasks
        except Exception as e:
            logger.error(f"获取待处理任务失败: {e}")
            return []

    def get_processing_count(self):
        """获取正在处理的任务数量"""
        try:
            processing_tasks = self.db.list_tasks(status='处理中', limit=100)
            return len(processing_tasks)
        except Exception as e:
            logger.error(f"获取处理中任务数量失败: {e}")
            return 0

    def get_queue_size(self):
        """获取队列中等待的任务数量"""
        return self.task_queue.qsize()

    def _start_workers(self):
        """启动工作线程"""
        with self.workers_lock:
            max_concurrent = self.config.get("max_concurrent", 1)
            for i in range(max_concurrent):
                worker = TaskWorker(self.task_queue, self.executor, i + 1)
                worker.start()
                self.workers.append(worker)
            logger.info(f"启动了 {max_concurrent} 个工作线程")

    def _stop_workers(self):
        """停止所有工作线程"""
        with self.workers_lock:
            # 发送停止信号
            for _ in self.workers:
                self.task_queue.put(None)

            # 等待所有线程结束
            for worker in self.workers:
                worker.stop()
                worker.join(timeout=5)

            self.workers.clear()
            logger.info("所有工作线程已停止")

    def _restart_workers(self):
        """重启工作线程（用于调整并发数）"""
        logger.info("重启工作线程...")
        self._stop_workers()
        self._start_workers()

    def add_task_to_queue(self, task_id):
        """添加任务到队列"""
        try:
            self.task_queue.put(task_id)
            logger.info(f"任务 {task_id} 已加入队列，当前队列大小: {self.task_queue.qsize()}")
            return True
        except Exception as e:
            logger.error(f"添加任务到队列失败: {e}")
            return False

    def check_and_queue_tasks(self):
        """检查并将待处理任务加入队列"""
        try:
            # 获取待处理任务
            pending_tasks = self.get_pending_tasks()
            if not pending_tasks:
                logger.debug("没有待处理的任务")
                return 0

            # 获取当前队列大小和处理中的任务数
            queue_size = self.get_queue_size()
            processing_count = self.get_processing_count()
            max_concurrent = self.config.get("max_concurrent", 1)

            # 计算可以加入队列的任务数
            # 队列中的任务 + 正在处理的任务 不应超过最大并发数
            available_slots = max_concurrent - (queue_size + processing_count)

            if available_slots <= 0:
                logger.debug(f"队列已满或达到并发限制 (队列: {queue_size}, 处理中: {processing_count}, 最大: {max_concurrent})")
                return 0

            # 将任务加入队列
            added_count = 0
            for task in pending_tasks[:available_slots]:
                task_id = task['id']
                if self.add_task_to_queue(task_id):
                    added_count += 1
                    logger.info(f"任务 {task_id} (优先级: {task.get('priority', 'normal')}) 已加入执行队列")

            return added_count

        except Exception as e:
            logger.error(f"检查并加入任务失败: {e}")
            return 0

    def run(self):
        """主循环"""
        logger.info("自动任务执行器启动")
        logger.info(f"配置: {self.config}")

        try:
            while True:
                try:
                    # 重新加载配置（支持动态更新）
                    self.config = self.load_config()

                    if self.is_enabled():
                        logger.info("检查待处理任务...")
                        added = self.check_and_queue_tasks()
                        if added > 0:
                            logger.info(f"本次检查加入了 {added} 个任务到队列")
                        else:
                            logger.info("没有待处理的任务")
                    else:
                        logger.info("自动巡航已禁用，等待中...")

                    # 等待指定间隔
                    interval = self.config.get("interval", 60)

                    # 设置下次检查时间
                    import datetime
                    self.next_check_time = datetime.datetime.now() + datetime.timedelta(seconds=interval)
                    logger.info(f"下次检查时间: {self.next_check_time.strftime('%Y-%m-%d %H:%M:%S')}")

                    time.sleep(interval)

                except KeyboardInterrupt:
                    logger.info("收到停止信号，退出")
                    break
                except Exception as e:
                    logger.error(f"主循环异常: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    time.sleep(10)

        finally:
            # 清理资源
            logger.info("正在停止工作线程...")
            self._stop_workers()
            logger.info("自动任务执行器已停止")

    def get_next_check_time(self):
        """获取下次检查时间"""
        return self.next_check_time

    def get_status(self):
        """获取详细状态"""
        return {
            "enabled": self.is_enabled(),
            "queue_size": self.get_queue_size(),
            "processing_count": self.get_processing_count(),
            "worker_count": len(self.workers),
            "next_check_time": self.next_check_time
        }


def main():
    """主函数"""
    executor = AutoExecutor()
    executor.run()


if __name__ == "__main__":
    main()
