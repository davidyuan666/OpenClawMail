# -*- coding: utf-8 -*-
"""
OpenClaw-Lite Web 管理界面 - 使用数据库版本
"""
from flask import Flask, render_template, jsonify, request
from database import Database
from config import Config
from logger import setup_logger
from claude_executor import ClaudeExecutor
from auto_executor import AutoExecutor
import threading

logger = setup_logger('web_dashboard', 'data/logs/web_dashboard.log')

app = Flask(__name__)
db = Database()
claude_executor = ClaudeExecutor(
    db=db,
    claude_cli_path=Config.CLAUDE_CLI_PATH,
    workspace_dir=Config.CLAUDE_WORKSPACE_DIR,
    timeout=Config.CLAUDE_TIMEOUT
)
auto_executor = AutoExecutor()

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

if __name__ == '__main__':
    logger.info("Web 管理界面启动中...")
    logger.info(f"访问地址: http://{Config.WEB_HOST}:{Config.WEB_PORT}")
    app.run(debug=Config.WEB_DEBUG, host=Config.WEB_HOST, port=Config.WEB_PORT)
