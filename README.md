# OpenClaw Email

基于 Telegram 的智能任务管理系统，采用现代化邮箱风格界面，支持通过 Telegram 接收任务、Web 界面管理、自动通知结果。

## 功能特性

- **现代化 UI**: Gmail 风格的三栏布局，简洁美观
- **Telegram Bot 监听**: 自动接收用户通过 Telegram 发送的任务
- **数据库存储**: 使用 SQLite 持久化存储任务数据
- **Web 管理界面**: 提供友好的 Web 界面查看和管理任务
- **实时搜索**: 支持按任务内容或 ID 快速搜索
- **自动通知**: 任务完成后自动通知用户
- **自动巡航**: 自动执行待办任务队列
- **文件监控**: 监控文件发送请求
- **MCP 服务器集成**: 内置 7 个专业 MCP 服务器，支持论文搜索、文档转换、数据分析等
- **状态管理**: 支持任务状态流转（inbox → processing → completed/failed → archive）

## 项目结构

```
OpenClawMail/
├── main.py                    # 统一入口文件
├── README.md                  # 项目说明文档
├── requirements.txt           # Python 依赖
├── .env                       # 环境变量配置（需自行创建）
├── .gitignore                # Git 忽略配置
│
├── config/                    # 配置文件目录
│   └── mcp.json              # MCP 服务器配置
│
├── mcps/                      # MCP 服务器集合
│   ├── ArxivSearchMCP/        # arXiv 论文搜索
│   ├── BilibiliAnalyzerMCP/   # B站视频分析
│   ├── DocumentConverterMCP/  # 文档格式转换
│   ├── DocumentReviewerMCP/   # 文档审阅
│   ├── JournalAbstractAnalyzerMCP/ # 期刊摘要分析
│   ├── MedicalSearchMCP/      # 医学文献搜索
│   ├── MoltbookMCP/           # Moltbook 分子数据库
│   └── README.md              # MCP 服务器说明
│
├── src/                       # 源代码目录
│   ├── core/                  # 核心功能模块
│   │   ├── config.py         # 配置管理
│   │   ├── database.py       # 数据库模型
│   │   └── logger.py         # 日志系统
│   ├── services/             # 服务层
│   │   ├── bot_listener.py   # Telegram Bot 监听器
│   │   ├── task_processor.py # 任务处理器
│   │   ├── result_notifier.py # 结果通知器
│   │   ├── auto_executor.py  # 自动执行器
│   │   └── file_watcher.py   # 文件监控器
│   ├── telegram/             # Telegram 相关
│   │   ├── client.py         # Telegram API 封装
│   │   └── config_manager.py # Telegram 配置管理
│   ├── claude/               # Claude 相关
│   │   ├── executor.py       # Claude 执行器
│   │   └── cc_switch.py      # CC 切换管理
│   ├── managers/             # 管理器模块
│   │   ├── history_manager.py # 历史管理
│   │   └── mcp_manager.py    # MCP 管理
│   └── web/                  # Web 界面
│       ├── dashboard.py      # Web 管理界面
│       ├── static/           # 静态资源
│       │   └── favicon.svg   # 网站图标
│       └── templates/        # HTML 模板
│           └── index.html    # 主页面
│
├── scripts/                  # 脚本目录
│   ├── start_services.py     # 启动所有服务
│   ├── send_completion_message.py
│   ├── start.sh              # Linux/Mac 启动脚本
│   ├── start.bat             # Windows 启动脚本
│   ├── stop.sh               # Linux/Mac 停止脚本
│   ├── stop.bat              # Windows 停止脚本
│   ├── restart.sh            # Linux/Mac 重启脚本
│   └── restart.bat           # Windows 重启脚本
│
├── tests/                    # 测试目录
│   └── test_claude_stdin.py
│
├── docs/                     # 文档目录
│   ├── HISTORY_CONTEXT_FEATURE.md
│   └── PROJECT_STRUCTURE.md  # 项目结构文档
│
├── data/                     # 数据目录（运行时生成）
│   ├── tasks.db             # SQLite 数据库
│   └── logs/                # 日志文件
│
└── venv/                     # Python 虚拟环境（需自行创建）
```

详细的项目结构说明请查看 [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)

## 安装步骤

### 1. 克隆项目

```bash
git clone git@github.com:davidyuan666/OpenClawMail.git
cd OpenClawMail
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

#### 方式一：使用统一入口（推荐）

```bash
# 启动 Web 管理界面
python main.py web

# 启动 Telegram Bot 监听器
python main.py bot

# 启动结果通知器
python main.py notifier

# 启动自动执行器
python main.py auto

# 启动文件监控器
python main.py watcher

# 启动所有服务
python main.py all
```

#### 方式二：使用启动脚本

```bash
# Linux/Mac
./scripts/start.sh

# Windows
scripts\start.bat
```

这将自动启动所有服务：
- Bot Listener: 监听 Telegram 消息
- Web Dashboard: http://localhost:5000
- Result Notifier: 自动通知任务结果
- Auto Executor: 自动巡航执行器
- File Watcher: 监控文件发送请求

#### 方式三：手动启动单个服务

```bash
# 启动 Bot 监听器
python -m src.services.bot_listener

# 启动 Web 管理界面
python -m src.web.dashboard

# 启动结果通知器
python -m src.services.result_notifier

# 启动自动执行器
python -m src.services.auto_executor

# 启动文件监控器
python -m src.services.file_watcher
```

### 停止服务

```bash
# Linux/Mac
./scripts/stop.sh

# Windows
scripts\stop.bat
```

### 重启服务

```bash
# Linux/Mac
./scripts/restart.sh

# Windows
scripts\restart.bat
```

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

### 模块说明

- **core**: 核心模块，包含配置、数据库、日志等基础功能
- **services**: 服务层，包含各种后台服务
- **telegram**: Telegram 相关功能封装
- **claude**: Claude CLI 相关功能
- **managers**: 各种管理器（历史、MCP 等）
- **web**: Web 界面和 API

## 许可证

MIT License
