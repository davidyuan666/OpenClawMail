# OpenClaw-Email

基于 Telegram 的任务管理系统，支持通过 Telegram 接收任务、Web 界面管理、自动通知结果。

## 功能特性

- **Telegram Bot 监听**: 自动接收用户通过 Telegram 发送的任务
- **数据库存储**: 使用 SQLite 持久化存储任务数据
- **Web 管理界面**: 提供友好的 Web 界面查看和管理任务
- **自动通知**: 任务完成后自动通知用户
- **状态管理**: 支持任务状态流转（inbox → processing → completed/failed → archive）

## 项目结构

```
openclaw-email/
├── bot_listener_db.py      # Telegram Bot 监听器
├── result_notifier_db.py   # 结果通知器
├── task_processor_db.py    # 任务处理器
├── web_dashboard_db.py     # Web 管理界面
├── database.py             # 数据库模型
├── telegram_client.py      # Telegram API 封装
├── config.py               # 配置管理
├── logger.py               # 日志系统
├── requirements.txt        # Python 依赖
├── .env                    # 环境变量配置
├── data/                   # 数据目录
│   ├── tasks.db           # SQLite 数据库
│   └── logs/              # 日志文件
└── templates/              # Web 模板
    └── index.html         # 管理界面
```

## 安装步骤

### 1. 克隆项目

```bash
cd openclaw-email
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件并配置以下变量：

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

## 使用说明

### 启动服务

#### 1. 启动 Bot 监听器

```bash
python bot_listener_db.py
```

监听 Telegram 消息，自动创建任务。

#### 2. 启动 Web 管理界面

```bash
python web_dashboard_db.py
```

访问 http://localhost:5000 查看任务列表。

#### 3. 处理任务

查看任务：
```bash
python task_processor_db.py task_20260210_130000
```

#### 4. 通知结果

```bash
python result_notifier_db.py
```

自动将已完成任务通知到 Telegram。

### 任务状态流转

```
inbox → processing → completed/failed → archive
```

- **inbox**: 新创建的任务
- **processing**: 正在处理中
- **completed**: 已完成
- **failed**: 处理失败
- **archive**: 已归档（已通知用户）

## 技术栈

- **Python 3.8+**
- **Flask**: Web 框架
- **SQLite**: 数据库
- **Telegram Bot API**: 消息通信
- **Requests**: HTTP 客户端

## 开发说明

### 数据库模型

任务表结构：
- `id`: 任务唯一标识
- `user_id`: 用户 ID
- `message`: 任务内容
- `status`: 任务状态
- `priority`: 优先级
- `created_at`: 创建时间
- `updated_at`: 更新时间
- `started_at`: 开始处理时间
- `completed_at`: 完成时间
- `result`: 处理结果
- `error`: 错误信息

## 许可证

MIT License

