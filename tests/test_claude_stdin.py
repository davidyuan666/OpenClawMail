# -*- coding: utf-8 -*-
"""
测试 Claude CLI stdin 传递
"""
import subprocess
import sys

def test_claude_stdin():
    """测试通过 stdin 传递任务给 Claude CLI"""

    # 任务内容（使用英文避免编码问题）
    task_message = "Please reply: Task received. What is the current time?"

    print("=" * 60)
    print("Test Claude CLI stdin passing")
    print("=" * 60)
    print(f"\nTask message: {task_message}\n")

    # 构建命令
    cmd = [
        'claude',
        '--print',
        '--dangerously-skip-permissions'
    ]

    print(f"执行命令: {' '.join(cmd)}")
    print(f"工作目录: {sys.path[0]}")
    print("\n开始执行...\n")

    try:
        # 启动进程
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=sys.path[0],
            text=True,
            encoding='utf-8',
            errors='replace',
            shell=(sys.platform == 'win32')
        )

        # 通过 stdin 发送任务内容
        stdout, _ = process.communicate(
            input=task_message,
            timeout=60
        )

        print("=" * 60)
        print("Claude CLI 输出:")
        print("=" * 60)
        print(stdout)
        print("=" * 60)
        print("\n测试完成！")

    except subprocess.TimeoutExpired:
        process.kill()
        print("执行超时！")
    except Exception as e:
        print(f"执行失败: {e}")

if __name__ == '__main__':
    test_claude_stdin()
