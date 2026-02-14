# -*- coding: utf-8 -*-
"""
OpenClaw-Lite Web 管理界面 - 使用数据库版本
"""
from flask import Flask, render_template, jsonify, request
from src.core.database import Database
from src.core.config import Config
from src.core.logger import setup_logger
from src.claude.executor import ClaudeExecutor
from src.services.auto_executor import AutoExecutor
from src.managers.mcp_manager import MCPManager
from src.claude.cc_switch import CCSwitchManager
from src.managers.history_manager import HistoryManager
from src.telegram.config_manager import TelegramConfigManager
import threading
import sys

logger = setup_logger('web_dashboard', 'data/logs/web_dashboard.log')

# 获取当前文件所在目录
import os
current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
            template_folder=os.path.join(current_dir, 'templates'),
            static_folder=os.path.join(current_dir, 'static'))
db = Database()
claude_executor = ClaudeExecutor(
    db=db,
    claude_cli_path=Config.CLAUDE_CLI_PATH,
    workspace_dir=Config.CLAUDE_WORKSPACE_DIR,
    timeout=Config.CLAUDE_TIMEOUT
)
auto_executor = AutoExecutor()
mcp_manager = MCPManager()
cc_switch_manager = CCSwitchManager()
history_manager = HistoryManager()
telegram_config_manager = TelegramConfigManager()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/tasks')
def get_tasks():
    """获取任务列表"""
    status = request.args.get('status')
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    tasks = db.list_tasks(status, limit, offset)
    return jsonify(tasks)

@app.route('/api/tasks/<task_id>')
def get_task(task_id):
    """获取任务详情"""
    task = db.get_task(task_id)
    if task:
        return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

@app.route('/api/stats')
def get_stats():
    """获取统计信息"""
    stats = db.get_stats()
    return jsonify(stats)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """创建新任务"""
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "缺少必需参数: message"}), 400

        user_id = data.get('user_id', 'web_user')
        message = data.get('message')
        priority = data.get('priority', 'normal')

        task_id = db.create_task(user_id, message, priority)
        logger.info(f"创建任务成功: {task_id}")
        return jsonify({"success": True, "task_id": task_id}), 201
    except Exception as e:
        logger.error(f"创建任务失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """更新任务"""
    try:
        # 检查任务是否存在
        task = db.get_task(task_id)
        if not task:
            return jsonify({"error": "任务不存在"}), 404

        # 检查是否可编辑
        if not db.can_edit_task(task_id):
            return jsonify({"error": "任务状态不允许编辑"}), 403

        # 更新任务
        data = request.json
        message = data.get('message')
        priority = data.get('priority')

        db.update_task(task_id, message, priority)
        logger.info(f"更新任务成功: {task_id}")
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"更新任务失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除任务"""
    try:
        # 检查任务是否存在
        task = db.get_task(task_id)
        if not task:
            return jsonify({"error": "任务不存在"}), 404

        # 检查是否可删除
        if not db.can_delete_task(task_id):
            return jsonify({"error": "任务状态不允许删除"}), 403

        # 删除任务
        db.delete_task(task_id)
        logger.info(f"删除任务成功: {task_id}")
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"删除任务失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<task_id>/execute', methods=['POST'])
def execute_task(task_id):
    """执行任务（异步）"""
    try:
        # 检查任务是否存在
        task = db.get_task(task_id)
        if not task:
            return jsonify({"error": "任务不存在"}), 404

        # 检查任务状态
        if task['status'] == '处理中':
            return jsonify({"error": "任务正在执行中"}), 400

        # 获取工作目录（可选）
        data = request.json or {}
        workspace_dir = data.get('workspace_dir')

        # 在后台线程中异步执行任务
        def execute_in_background():
            try:
                result = claude_executor.execute_task(task_id, workspace_dir)
                logger.info(f"任务执行完成: {task_id}, 成功: {result['success']}")
            except Exception as e:
                logger.error(f"后台执行任务失败: {task_id}, 错误: {e}")

        thread = threading.Thread(target=execute_in_background, daemon=True)
        thread.start()

        logger.info(f"任务已提交后台执行: {task_id}")
        return jsonify({
            "success": True,
            "message": "任务已提交后台执行，请稍后查看结果"
        })
    except Exception as e:
        logger.error(f"提交任务失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<task_id>/archive', methods=['POST'])
def archive_task(task_id):
    """归档任务"""
    try:
        # 检查任务是否存在
        task = db.get_task(task_id)
        if not task:
            return jsonify({"error": "任务不存在"}), 404

        # 检查是否可归档
        if not db.can_archive_task(task_id):
            return jsonify({"error": "只有已完成或失败的任务才能归档"}), 403

        # 归档任务
        db.archive_task(task_id)
        logger.info(f"归档任务成功: {task_id}")
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"归档任务失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<task_id>/progress')
def get_task_progress(task_id):
    """获取任务执行进度（用于轮询）"""
    try:
        progress = ClaudeExecutor.get_task_progress(task_id)
        if progress is None:
            return jsonify({"error": "任务进度不存在"}), 404
        return jsonify(progress)
    except Exception as e:
        logger.error(f"获取任务进度失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<task_id>/progress', methods=['DELETE'])
def clear_task_progress(task_id):
    """清除任务进度缓存"""
    try:
        ClaudeExecutor.clear_task_progress(task_id)
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"清除任务进度失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/auto-executor/config')
def get_auto_executor_config():
    """获取自动巡航配置"""
    try:
        config = auto_executor.get_config()
        return jsonify(config)
    except Exception as e:
        logger.error(f"获取自动巡航配置失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/auto-executor/config', methods=['POST'])
def update_auto_executor_config():
    """更新自动巡航配置"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "缺少配置数据"}), 400

        # 更新配置
        current_config = auto_executor.get_config()

        if 'enabled' in data:
            current_config['enabled'] = bool(data['enabled'])
        if 'interval' in data:
            current_config['interval'] = int(data['interval'])
        if 'max_concurrent' in data:
            current_config['max_concurrent'] = int(data['max_concurrent'])
        if 'priority_order' in data:
            current_config['priority_order'] = data['priority_order']

        auto_executor.save_config(current_config)
        logger.info(f"自动巡航配置已更新: {current_config}")

        return jsonify({"success": True, "config": current_config})
    except Exception as e:
        logger.error(f"更新自动巡航配置失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/auto-executor/toggle', methods=['POST'])
def toggle_auto_executor():
    """切换自动巡航开关"""
    try:
        data = request.json
        enabled = data.get('enabled', False)

        auto_executor.set_enabled(enabled)
        logger.info(f"自动巡航已{'启用' if enabled else '禁用'}")

        return jsonify({
            "success": True,
            "enabled": enabled,
            "message": f"自动巡航已{'启用' if enabled else '禁用'}"
        })
    except Exception as e:
        logger.error(f"切换自动巡航失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/auto-executor/status')
def get_auto_executor_status():
    """获取自动巡航状态"""
    try:
        config = auto_executor.get_config()
        pending_tasks = auto_executor.get_pending_tasks()
        processing_count = auto_executor.get_processing_count()
        queue_size = auto_executor.get_queue_size()
        next_check_time = auto_executor.get_next_check_time()

        # 计算倒计时（秒）
        countdown = 0
        if next_check_time:
            import datetime
            now = datetime.datetime.now()
            countdown = max(0, int((next_check_time - now).total_seconds()))

        return jsonify({
            "enabled": config.get('enabled', False),
            "interval": config.get('interval', 60),
            "max_concurrent": config.get('max_concurrent', 1),
            "pending_count": len(pending_tasks),
            "processing_count": processing_count,
            "queue_size": queue_size,
            "worker_count": len(auto_executor.workers),
            "countdown": countdown,
            "next_check_time": next_check_time.isoformat() if next_check_time else None
        })
    except Exception as e:
        logger.error(f"获取自动巡航状态失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/mcp/list')
def get_mcp_list():
    """获取 MCP 列表"""
    try:
        mcps = mcp_manager.get_all_mcps()
        return jsonify(mcps)
    except Exception as e:
        logger.error(f"获取 MCP 列表失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/mcp/scan')
def scan_local_mcps():
    """扫描本地 MCPs"""
    try:
        discovered = mcp_manager.scan_local_mcps()
        return jsonify(discovered)
    except Exception as e:
        logger.error(f"扫描本地 MCPs 失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/mcp/<name>')
def get_mcp_info(name):
    """获取 MCP 详细信息"""
    try:
        info = mcp_manager.get_mcp_info(name)
        if info:
            return jsonify(info)
        return jsonify({"error": "MCP 不存在"}), 404
    except Exception as e:
        logger.error(f"获取 MCP 信息失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/mcp', methods=['POST'])
def add_mcp():
    """添加 MCP"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "缺少请求数据"}), 400

        name = data.get('name')
        command = data.get('command')
        args = data.get('args')
        env = data.get('env')

        if not name or not command or not args:
            return jsonify({"error": "缺少必需参数"}), 400

        result = mcp_manager.add_mcp(name, command, args, env)
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"添加 MCP 失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/mcp/<name>', methods=['PUT'])
def update_mcp(name):
    """更新 MCP"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "缺少请求数据"}), 400

        command = data.get('command')
        args = data.get('args')
        env = data.get('env')

        if not command or not args:
            return jsonify({"error": "缺少必需参数"}), 400

        result = mcp_manager.update_mcp(name, command, args, env)
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"更新 MCP 失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/mcp/<name>', methods=['DELETE'])
def delete_mcp(name):
    """删除 MCP"""
    try:
        result = mcp_manager.delete_mcp(name)
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"删除 MCP 失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/cc-switch/list')
def get_cc_switch_list():
    """获取 CC Switch 配置列表"""
    try:
        profiles = cc_switch_manager.get_all_profiles()
        return jsonify(profiles)
    except Exception as e:
        logger.error(f"获取 CC Switch 列表失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/cc-switch/current')
def get_cc_switch_current():
    """获取当前 CC Switch 配置"""
    try:
        current = cc_switch_manager.get_current_profile()
        if current:
            return jsonify(current)
        return jsonify({"message": "未设置当前配置"}), 200
    except Exception as e:
        logger.error(f"获取当前 CC Switch 配置失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/cc-switch', methods=['POST'])
def add_cc_switch():
    """添加 CC Switch 配置"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "缺少请求数据"}), 400

        name = data.get('name')
        base_url = data.get('base_url')
        auth_token = data.get('auth_token')

        if not name or not base_url or not auth_token:
            return jsonify({"error": "缺少必需参数"}), 400

        result = cc_switch_manager.add_profile(name, base_url, auth_token)
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"添加 CC Switch 配置失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/cc-switch/<name>', methods=['PUT'])
def update_cc_switch(name):
    """更新 CC Switch 配置"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "缺少请求数据"}), 400

        base_url = data.get('base_url')
        auth_token = data.get('auth_token')

        if not base_url or not auth_token:
            return jsonify({"error": "缺少必需参数"}), 400

        result = cc_switch_manager.update_profile(name, base_url, auth_token)
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"更新 CC Switch 配置失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/cc-switch/<name>', methods=['DELETE'])
def delete_cc_switch(name):
    """删除 CC Switch 配置"""
    try:
        result = cc_switch_manager.delete_profile(name)
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"删除 CC Switch 配置失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/cc-switch/<name>/switch', methods=['POST'])
def switch_cc_switch(name):
    """切换 CC Switch 配置"""
    try:
        result = cc_switch_manager.switch_profile(name)
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"切换 CC Switch 配置失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/history/config')
def get_history_config():
    """获取历史上下文配置"""
    try:
        config = history_manager.get_config()
        return jsonify(config)
    except Exception as e:
        logger.error(f"获取历史配置失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/history/config', methods=['POST'])
def update_history_config():
    """更新历史上下文配置"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "缺少配置数据"}), 400

        enabled = data.get('enabled')
        max_history_count = data.get('max_history_count')

        history_manager.update_config(enabled, max_history_count)
        config = history_manager.get_config()
        logger.info(f"历史配置已更新: {config}")

        return jsonify({"success": True, "config": config})
    except Exception as e:
        logger.error(f"更新历史配置失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/history/stats')
def get_history_stats():
    """获取历史记录统计"""
    try:
        stats = history_manager.get_history_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"获取历史统计失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/history/records')
def get_history_records():
    """获取历史记录列表"""
    try:
        limit = int(request.args.get('limit', 10))
        records = history_manager.get_recent_history(limit)
        return jsonify(records)
    except Exception as e:
        logger.error(f"获取历史记录失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    """清除历史记录"""
    try:
        affected = history_manager.clear_history()
        logger.info(f"历史记录已清除，共 {affected} 条")
        return jsonify({"success": True, "affected": affected})
    except Exception as e:
        logger.error(f"清除历史记录失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/telegram-config/config')
def get_telegram_config():
    """获取 Telegram 配置"""
    try:
        config = telegram_config_manager.get_config()
        return jsonify(config)
    except Exception as e:
        logger.error(f"获取 Telegram 配置失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/telegram-config/config', methods=['POST'])
def update_telegram_config():
    """更新 Telegram 配置"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "缺少配置数据"}), 400

        telegram_config_manager.update_config(
            enabled=data.get('enabled'),
            bot_token=data.get('bot_token'),
            chat_id=data.get('chat_id')
        )
        config = telegram_config_manager.get_config()
        logger.info(f"Telegram 配置已更新")
        return jsonify({"success": True, "config": config})
    except Exception as e:
        logger.error(f"更新 Telegram 配置失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/cc/health')
def check_cc_health():
    """检查 Claude CLI 健康状态（真实链路检测）"""
    try:
        import subprocess
        import time

        start_time = time.time()

        # 使用一个真实的任务来测试 API 链路
        # 让 Claude 列举当前目录的文件
        result = subprocess.run(
            ['claude', '--print', '--dangerously-skip-permissions'],
            input='请使用 ls 命令列举当前目录的文件，只返回命令执行结果，不要有其他解释',
            capture_output=True,
            text=True,
            timeout=15,  # 15秒超时
            shell=(sys.platform == 'win32')
        )

        response_time = int((time.time() - start_time) * 1000)  # 毫秒

        if result.returncode == 0 and result.stdout.strip():
            # 根据响应时间判断链路质量
            if response_time < 3000:
                quality = "优秀"
            elif response_time < 6000:
                quality = "良好"
            else:
                quality = "较慢"

            return jsonify({
                "status": "online",
                "message": f"CC 链路{quality}",
                "response_time": response_time
            })
        else:
            return jsonify({
                "status": "offline",
                "message": "CC API 不可用",
                "response_time": response_time
            })
    except subprocess.TimeoutExpired:
        return jsonify({
            "status": "offline",
            "message": "连接超时 (>15s)",
            "response_time": 15000
        })
    except Exception as e:
        return jsonify({
            "status": "offline",
            "message": f"检测失败: {str(e)}",
            "response_time": 0
        })

if __name__ == '__main__':
    logger.info("Web 管理界面启动中...")
    logger.info(f"访问地址: http://{Config.WEB_HOST}:{Config.WEB_PORT}")
    app.run(debug=Config.WEB_DEBUG, host=Config.WEB_HOST, port=Config.WEB_PORT)
