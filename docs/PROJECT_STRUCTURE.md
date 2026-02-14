# OpenClawMail 项目结构

## 目录结构

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
│   ├── ArxivSearchMCP/        # arXiv 论文搜索服务
│   ├── BilibiliAnalyzerMCP/   # B站视频分析服务
│   ├── DocumentConverterMCP/  # 文档格式转换服务
│   ├── DocumentReviewerMCP/   # 文档审阅服务
│   ├── JournalAbstractAnalyzerMCP/  # 期刊摘要分析服务
│   ├── MedicalSearchMCP/      # 医学文献搜索服务
│   ├── MoltbookMCP/           # Moltbook 分子数据库服务
│   └── README.md              # MCP 服务器说明文档
│
├── src/                       # 源代码目录
│   ├── __init__.py
│   │
│   ├── core/                  # 核心模块
│   │   ├── __init__.py
│   │   ├── config.py         # 配置管理
│   │   ├── database.py       # 数据库模型
│   │   └── logger.py         # 日志系统
│   │
│   ├── claude/                # Claude 相关模块
│   │   ├── __init__.py
│   │   ├── executor.py       # Claude 任务执行器
│   │   └── cc_switch.py      # Claude CLI 配置切换
│   │
│   ├── services/              # 服务层
│   │   ├── __init__.py
│   │   ├── bot_listener.py   # Telegram Bot 监听器
│   │   ├── task_processor.py # 任务处理器
│   │   ├── result_notifier.py # 结果通知器
│   │   ├── auto_executor.py  # 自动执行器
│   │   └── file_watcher.py   # 文件监控器
│   │
│   ├── telegram/              # Telegram 相关模块
│   │   ├── __init__.py
│   │   ├── client.py         # Telegram API 客户端
│   │   └── config_manager.py # Telegram 配置管理
│   │
│   ├── managers/              # 管理器模块
│   │   ├── __init__.py
│   │   ├── history_manager.py # 历史记录管理
│   │   └── mcp_manager.py    # MCP 管理器
│   │
│   └── web/                   # Web 界面模块
│       ├── __init__.py
│       ├── dashboard.py      # Flask Web 应用
│       ├── static/           # 静态资源
│       │   └── favicon.svg   # 网站图标
│       └── templates/        # HTML 模板
│           └── index.html    # 主页面
│
├── scripts/                   # 脚本目录
│   ├── start_services.py     # 启动所有服务
│   ├── send_completion_message.py # 发送完成消息
│   ├── start.sh              # Linux/Mac 启动脚本
│   ├── start.bat             # Windows 启动脚本
│   ├── stop.sh               # Linux/Mac 停止脚本
│   ├── stop.bat              # Windows 停止脚本
│   ├── restart.sh            # Linux/Mac 重启脚本
│   └── restart.bat           # Windows 重启脚本
│
├── tests/                     # 测试目录
│   └── test_claude_stdin.py # 测试文件
│
├── docs/                      # 文档目录
│   └── HISTORY_CONTEXT_FEATURE.md # 历史上下文功能文档
│
├── data/                      # 数据目录（运行时生成）
│   ├── tasks.db              # SQLite 数据库
│   └── logs/                 # 日志文件
│       ├── web_dashboard.log
│       ├── bot_listener.log
│       └── ...
│
└── venv/                      # Python 虚拟环境（需自行创建）
```

## 模块说明

### MCP 服务器集合 (mcps/)
包含 7 个专业的 MCP (Model Context Protocol) 服务器：
- **ArxivSearchMCP**: arXiv 论文数据库搜索服务
- **BilibiliAnalyzerMCP**: B站视频内容和数据分析服务
- **DocumentConverterMCP**: 文档格式转换服务（PDF、Word、Markdown 等）
- **DocumentReviewerMCP**: 自动文档审阅和评估服务
- **JournalAbstractAnalyzerMCP**: 学术期刊摘要分析服务
- **MedicalSearchMCP**: 医学文献数据库搜索服务
- **MoltbookMCP**: Moltbook 分子数据库查询服务

每个 MCP 服务器都是独立的 Python 应用，通过 `config/mcp.json` 配置文件进行管理。详细说明请查看 `mcps/README.md`。

### 核心模块 (src/core/)
- **config.py**: 统一的配置管理，从环境变量和配置文件读取配置
- **database.py**: SQLite 数据库操作封装，提供任务的 CRUD 接口
- **logger.py**: 日志系统配置，统一的日志格式和输出

### Claude 模块 (src/claude/)
- **executor.py**: Claude CLI 任务执行器，负责调用 Claude 处理任务
- **cc_switch.py**: Claude CLI 配置切换管理器，支持多配置切换

### 服务层 (src/services/)
- **bot_listener.py**: 监听 Telegram Bot 消息，自动创建任务
- **task_processor.py**: 任务处理器基类
- **result_notifier.py**: 监控已完成任务，自动通知用户
- **auto_executor.py**: 自动巡航执行器，定时处理待办任务
- **file_watcher.py**: 文件监控器，监控文件发送请求

### Telegram 模块 (src/telegram/)
- **client.py**: Telegram API 客户端封装
- **config_manager.py**: Telegram 配置管理

### 管理器模块 (src/managers/)
- **history_manager.py**: 历史记录管理，支持上下文注入
- **mcp_manager.py**: MCP 服务器管理

### Web 模块 (src/web/)
- **dashboard.py**: Flask Web 应用，提供 RESTful API 和管理界面
- **static/**: 静态资源文件（CSS、JS、图片等）
- **templates/**: HTML 模板文件

## 设计原则

1. **模块化**: 按功能划分模块，每个模块职责单一
2. **分层架构**: 核心层 → 服务层 → 应用层，依赖关系清晰
3. **配置分离**: 配置文件独立于代码，支持环境变量
4. **日志规范**: 统一的日志格式和输出位置
5. **可测试性**: 模块间低耦合，便于单元测试

## 启动方式

### 方式一：使用统一入口（推荐）

```bash
# 启动 Web 管理界面
python main.py web

# 启动 Telegram Bot 监听器
python main.py bot

# 启动所有服务
python main.py all
```

### 方式二：使用脚本

```bash
# Linux/Mac
./scripts/start.sh

# Windows
scripts\start.bat
```

### 方式三：直接运行模块

```bash
# 启动 Web 管理界面
python -m src.web.dashboard

# 启动 Bot 监听器
python -m src.services.bot_listener
```
