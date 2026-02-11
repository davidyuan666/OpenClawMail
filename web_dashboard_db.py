# -*- coding: utf-8 -*-
"""
OpenClaw-Lite Web 管理界面 - 使用数据库版本
"""
from flask import Flask, render_template, jsonify, request
from database import Database
from config import Config
from logger import setup_logger
from claude_executor import ClaudeExecutor
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
        if task['status'] == 'processing':
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

if __name__ == '__main__':
    logger.info("Web 管理界面启动中...")
    logger.info(f"访问地址: http://{Config.WEB_HOST}:{Config.WEB_PORT}")
    app.run(debug=Config.WEB_DEBUG, host=Config.WEB_HOST, port=Config.WEB_PORT)
