# -*- coding: utf-8 -*-
"""
启动 OpenClawMail 服务
确保每个服务只启动一个实例
"""
import subprocess
import sys
import os
import time
import psutil

def kill_existing_services():
    """停止所有现有的服务进程"""
    print("正在停止现有服务...")
    killed = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] in ['pythonw.exe', 'python.exe']:
                cmdline = proc.info['cmdline']
                if cmdline and any(script in ' '.join(cmdline) for script in
                                  ['bot_listener_db.py', 'web_dashboard_db.py', 'result_notifier_db.py',
                                   'auto_executor.py', 'telegram_file_watcher.py']):
                    print(f"  停止进程 PID {proc.info['pid']}: {' '.join(cmdline)}")
                    proc.kill()
                    killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if killed > 0:
        print(f"已停止 {killed} 个进程")
        time.sleep(2)
    else:
        print("没有发现运行中的服务")

def start_service(script_name):
    """启动单个服务"""
    pythonw = os.path.join('venv', 'Scripts', 'pythonw.exe')
    if not os.path.exists(pythonw):
        print(f"错误: 找不到 {pythonw}")
        return False

    try:
        subprocess.Popen(
            [pythonw, script_name],
            cwd=os.getcwd(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"[OK] 已启动: {script_name}")
        return True
    except Exception as e:
        print(f"[ERROR] 启动失败 {script_name}: {e}")
        return False

def main():
    print("=" * 50)
    print("  OpenClawMail 服务启动器")
    print("=" * 50)
    print()

    # 停止现有服务
    kill_existing_services()
    print()

    # 启动服务
    print("正在启动服务...")
    services = [
        'bot_listener_db.py',
        'web_dashboard_db.py',
        'result_notifier_db.py',
        'auto_executor.py',
        'telegram_file_watcher.py'
    ]

    success = 0
    for service in services:
        if start_service(service):
            success += 1
        time.sleep(1)

    print()
    print("=" * 50)
    print(f"  启动完成: {success}/{len(services)} 个服务")
    print("=" * 50)
    print()
    print("服务状态:")
    print("  - Bot Listener: 监听 Telegram 消息")
    print("  - Web Dashboard: http://localhost:5000")
    print("  - Result Notifier: 自动通知任务结果")
    print("  - Auto Executor: 自动巡航执行器")
    print("  - Telegram File Watcher: 监控文件发送请求")
    print()
    print("日志位置: data/logs/")
    print()

if __name__ == "__main__":
    main()
