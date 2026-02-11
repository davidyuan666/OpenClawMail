# -*- coding: utf-8 -*-
"""
Claude Code 执行器模块
"""
import subprocess
import sys
import os
from pathlib import Path
from logger import setup_logger
from database import Database
from telegram_client import TelegramClient

logger = setup_logger('claude_executor', 'data/logs/claude_executor.log')

class ClaudeExecutor:
    """Claude CLI 执行器"""

    def __init__(self, db: Database, claude_cli_path='claude', workspace_dir=None, timeout=180):
        """
        初始化 Claude 执行器

        Args:
            db: 数据库实例
            claude_cli_path: Claude CLI 路径
            workspace_dir: 工作目录
            timeout: 超时时间（秒）
        """
        self.db = db
        self.claude_cli_path = claude_cli_path
        self.workspace_dir = workspace_dir or os.getcwd()
        self.timeout = timeout
        self.telegram = TelegramClient()

    def execute_task(self, task_id, workspace_dir=None):
        """
        执行任务

        Args:
            task_id: 任务 ID
            workspace_dir: 工作目录（可选，覆盖默认值）

        Returns:
            dict: 执行结果 {"success": bool, "output": str, "error": str}
        """
        try:
            # 获取任务
            task = self.db.get_task(task_id)
            if not task:
                return {"success": False, "error": "任务不存在"}

            # 更新任务状态为 processing
            self.db.update_status(task_id, 'processing')
            logger.info(f"开始执行任务: {task_id}")

            # 执行 Claude CLI
            result = self._execute_claude_cli(
                task['message'],
                workspace_dir or self.workspace_dir
            )

            # 更新任务状态
            if result['success']:
                self.db.update_status(
                    task_id,
                    'completed',
                    result=result['output']
                )
                logger.info(f"任务执行成功: {task_id}")

                # 发送成功通知到 Telegram
                self._send_telegram_notification(task_id, task, result, success=True)
            else:
                self.db.update_status(
                    task_id,
                    'failed',
                    error=result['error']
                )
                logger.error(f"任务执行失败: {task_id}, 错误: {result['error']}")

                # 发送失败通知到 Telegram
                self._send_telegram_notification(task_id, task, result, success=False)

            return result

        except Exception as e:
            error_msg = f"执行任务异常: {str(e)}"
            logger.error(error_msg)
            try:
                self.db.update_status(task_id, 'failed', error=error_msg)
            except:
                pass
            return {"success": False, "error": error_msg}

    def _execute_claude_cli(self, message, workspace_dir):
        """
        执行 Claude CLI 命令

        Args:
            message: 任务消息
            workspace_dir: 工作目录

        Returns:
            dict: {"success": bool, "output": str, "error": str}
        """
        try:
            # 构建命令
            cmd = [
                self.claude_cli_path,
                '--print',
                '--dangerously-skip-permissions'
            ]

            logger.info(f"执行命令: {' '.join(cmd)}")
            logger.info(f"工作目录: {workspace_dir}")
            logger.info(f"任务内容: {message[:100]}...")

            # 执行命令
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=workspace_dir,
                text=True,
                encoding='utf-8',
                errors='replace',
                shell=(sys.platform == 'win32')
            )

            # 发送任务内容并获取结果
            try:
                stdout, _ = process.communicate(
                    input=message,
                    timeout=self.timeout
                )
                return {
                    "success": True,
                    "output": stdout,
                    "error": None
                }
            except subprocess.TimeoutExpired:
                process.kill()
                error_msg = f"执行超时（{self.timeout}秒）"
                logger.error(error_msg)
                return {
                    "success": False,
                    "output": None,
                    "error": error_msg
                }

        except Exception as e:
            error_msg = f"执行 Claude CLI 失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "output": None,
                "error": error_msg
            }

    def _send_telegram_notification(self, task_id, task, result, success=True):
        """
        发送任务执行结果到 Telegram

        Args:
            task_id: 任务 ID
            task: 任务对象
            result: 执行结果
            success: 是否成功
        """
        try:
            if success:
                # 成功通知
                message = f"✅ *任务执行成功*\n\n"
                message += f"*任务 ID:* `{task_id}`\n"
                message += f"*任务内容:* {self._truncate(task['message'], 100)}\n\n"
                message += f"*执行结果:*\n```\n{self._truncate(result['output'], 500)}\n```"
            else:
                # 失败通知
                message = f"❌ *任务执行失败*\n\n"
                message += f"*任务 ID:* `{task_id}`\n"
                message += f"*任务内容:* {self._truncate(task['message'], 100)}\n\n"
                message += f"*错误信息:*\n```\n{self._truncate(result['error'], 500)}\n```"

            self.telegram.send_message(message)
            logger.info(f"Telegram 通知发送成功: {task_id}")
        except Exception as e:
            logger.error(f"发送 Telegram 通知失败: {e}")

    def _truncate(self, text, max_length):
        """截断文本"""
        if not text:
            return ""
        return text[:max_length] + "..." if len(text) > max_length else text
