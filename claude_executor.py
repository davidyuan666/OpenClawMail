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

    # 任务执行进度缓存（内存）
    _task_progress = {}

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

            # 更新任务状态为处理中
            self.db.update_status(task_id, '处理中')
            logger.info(f"开始执行任务: {task_id}")

            # 初始化进度缓存
            ClaudeExecutor._task_progress[task_id] = {
                'status': '处理中',
                'lines': [],
                'completed': False
            }

            # 执行 Claude CLI
            result = self._execute_claude_cli(
                task['message'],
                workspace_dir or self.workspace_dir,
                task_id=task_id
            )

            # 更新任务状态
            if result['success']:
                self.db.update_status(
                    task_id,
                    '已完成',
                    result=result['output']
                )
                logger.info(f"任务执行成功: {task_id}")

                # 更新进度缓存
                if task_id in ClaudeExecutor._task_progress:
                    ClaudeExecutor._task_progress[task_id]['status'] = '已完成'
                    ClaudeExecutor._task_progress[task_id]['completed'] = True

                # 发送成功通知到 Telegram
                self._send_telegram_notification(task_id, task, result, success=True)
            else:
                self.db.update_status(
                    task_id,
                    '失败',
                    error=result['error']
                )
                logger.error(f"任务执行失败: {task_id}, 错误: {result['error']}")

                # 更新进度缓存
                if task_id in ClaudeExecutor._task_progress:
                    ClaudeExecutor._task_progress[task_id]['status'] = '失败'
                    ClaudeExecutor._task_progress[task_id]['completed'] = True

                # 发送失败通知到 Telegram
                self._send_telegram_notification(task_id, task, result, success=False)

            return result

        except Exception as e:
            error_msg = f"执行任务异常: {str(e)}"
            logger.error(error_msg)
            try:
                self.db.update_status(task_id, '失败', error=error_msg)
            except:
                pass
            return {"success": False, "error": error_msg}

    def _build_context_prompt(self, user_message):
        """
        构建包含上下文信息的完整提示

        Args:
            user_message: 用户的任务消息

        Returns:
            str: 包含上下文的完整提示
        """
        context = """# 工作空间上下文信息

## 可用的 MCP 工具

你可以使用以下 MCP 工具来完成任务（按需使用）：

### 学术研究类
- **ArxivSearchMCP**: 搜索 arXiv 论文
- **MedicalSearchMCP**: 搜索医学文献 (PubMed)
- **JournalAbstractAnalyzerMCP**: 分析期刊摘要

### 文档处理类
- **DocumentConverterMCP**: 文档格式转换 (PDF/DOCX/Markdown)
- **DocumentReviewerMCP**: 文档审阅和评审

### 社交媒体类
- **BilibiliAnalyzerMCP**: B站视频分析
- **MoltbookMCP**: Moltbook 社区数据获取

### Telegram 通信类
- **telegram-mcp**: 发送 Telegram 消息、图片、文档、语音等
  - 使用 `mcp__telegram-mcp__telegram_send_message` 发送文本消息
  - 使用 `mcp__telegram-mcp__telegram_send_photo` 发送图片
  - 使用 `mcp__telegram-mcp__telegram_send_document` 发送文档
  - 使用 `mcp__telegram-mcp__telegram_send_video` 发送视频
  - Chat ID: 751182377

## 重要说明

1. **MCP 工具按需使用**: 只在任务需要时才调用相应的 MCP 工具
2. **Telegram 通知**: 如果任务完成后需要发送文件或特殊格式的通知，可以使用 telegram-mcp 工具
3. **工作目录**: 当前工作目录为 OpenClawMail 项目目录
4. **文件操作**: 可以读写文件、执行命令等操作

---

# 用户任务

"""
        return context + user_message

    def _execute_claude_cli(self, message, workspace_dir, task_id=None):
        """
        执行 Claude CLI 命令

        Args:
            message: 任务消息
            workspace_dir: 工作目录
            task_id: 任务 ID（用于进度缓存）

        Returns:
            dict: {"success": bool, "output": str, "error": str}
        """
        try:
            # 构建包含上下文的完整提示
            full_prompt = self._build_context_prompt(message)

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
            # 统一使用 UTF-8 编码
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=workspace_dir,
                text=True,
                encoding='utf-8',
                errors='replace',
                shell=(sys.platform == 'win32'),
                bufsize=1  # 行缓冲，支持实时输出
            )

            # 发送任务内容（包含上下文）
            if process.stdin:
                process.stdin.write(full_prompt)
                process.stdin.close()

            # 实时读取输出
            output_lines = []
            try:
                import time
                start_time = time.time()

                while True:
                    # 检查超时
                    if time.time() - start_time > self.timeout:
                        process.kill()
                        error_msg = f"执行超时（{self.timeout}秒）"
                        logger.error(error_msg)
                        return {
                            "success": False,
                            "output": None,
                            "error": error_msg
                        }

                    # 读取一行输出
                    line = process.stdout.readline()
                    if not line:
                        # 检查进程是否结束
                        if process.poll() is not None:
                            break
                        continue

                    output_lines.append(line)
                    # 缓存输出行（用于轮询获取）
                    if task_id and task_id in ClaudeExecutor._task_progress:
                        ClaudeExecutor._task_progress[task_id]['lines'].append(line.rstrip())

                # 获取返回码
                return_code = process.wait()
                full_output = ''.join(output_lines)

                return {
                    "success": return_code == 0,
                    "output": full_output if return_code == 0 else None,
                    "error": full_output if return_code != 0 else None
                }

            except Exception as e:
                process.kill()
                error_msg = f"读取输出失败: {str(e)}"
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

    @classmethod
    def get_task_progress(cls, task_id):
        """
        获取任务执行进度

        Args:
            task_id: 任务 ID

        Returns:
            dict: 进度信息 {"status": str, "lines": list, "completed": bool}
        """
        return cls._task_progress.get(task_id, None)

    @classmethod
    def clear_task_progress(cls, task_id):
        """
        清除任务进度缓存

        Args:
            task_id: 任务 ID
        """
        if task_id in cls._task_progress:
            del cls._task_progress[task_id]
