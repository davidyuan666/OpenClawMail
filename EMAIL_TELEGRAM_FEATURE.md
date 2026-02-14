# Email 和 Telegram 配置功能说明

## 功能概述

OpenClawMail 现在支持通过 Email 和 Telegram 进行任务通知和管理。用户可以在左侧边栏配置这两个通知渠道，实现多渠道的任务管理。

## Email 功能

### 主要特性

1. **邮件接收任务**: 通过检查邮箱收件箱自动创建任务
2. **邮件发送结果**: 任务完成后自动发送结果到邮箱
3. **163 邮箱支持**: 默认配置为 163 邮箱（wu.xiguanghua@163.com）
4. **开关控制**: 可随时启用/禁用 Email 功能

### 配置步骤

1. **获取 163 邮箱授权码**:
   - 登录 163 邮箱
   - 进入"设置" → "POP3/SMTP/IMAP"
   - 开启 IMAP/SMTP 服务
   - 获取授权码（不是登录密码）

2. **在 OpenClawMail 中配置**:
   - 打开 Web 界面
   - 在左侧边栏找到"EMAIL 通知"面板
   - 点击"⚙️ 配置"按钮
   - 填写以下信息：
     - 邮箱地址: wu.xiguanghua@163.com
     - 邮箱密码/授权码: [你的授权码]
     - SMTP 服务器: smtp.163.com
     - SMTP 端口: 465
     - IMAP 服务器: imap.163.com
     - IMAP 端口: 993
   - 点击"保存"

3. **启用 Email 功能**:
   - 在"EMAIL 通知"面板中打开开关
   - 启用后系统会自动检查新邮件并发送结果

### 使用方法

#### 通过邮件创建任务
1. 发送邮件到 wu.xiguanghua@163.com
2. 邮件主题作为任务标题
3. 邮件正文作为任务内容
4. 系统会自动检测未读邮件并创建任务

#### 接收任务结果
- 任务完成后，系统会自动发送邮件到配置的邮箱
- 邮件包含任务 ID、内容和执行结果

## Telegram 功能

### 主要特性

1. **Telegram 通知**: 任务完成后发送通知到 Telegram
2. **Bot 集成**: 使用 Telegram Bot API
3. **开关控制**: 可随时启用/禁用 Telegram 功能

### 配置步骤

1. **创建 Telegram Bot**:
   - 在 Telegram 中搜索 @BotFather
   - 发送 `/newbot` 命令
   - 按提示设置 Bot 名称
   - 获取 Bot Token（格式: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11）

2. **获取 Chat ID**:
   - 在 Telegram 中搜索 @userinfobot
   - 发送任意消息
   - Bot 会返回你的 Chat ID（纯数字）

3. **在 OpenClawMail 中配置**:
   - 打开 Web 界面
   - 在左侧边栏找到"TELEGRAM 通知"面板
   - 点击"⚙️ 配置"按钮
   - 填写以下信息：
     - Bot Token: [你的 Bot Token]
     - Chat ID: [你的 Chat ID]
   - 点击"保存"

4. **启用 Telegram 功能**:
   - 在"TELEGRAM 通知"面板中打开开关
   - 启用后任务完成会自动发送 Telegram 通知

### 使用方法

- 任务完成后，系统会自动发送消息到你的 Telegram
- 消息包含任务状态、ID 和执行结果

## 技术实现

### 后端组件

#### 1. email_manager.py
- **EmailManager 类**: 管理 Email 配置和收发
- **数据库表**: `email_config`
  - `enabled`: 是否启用（0/1）
  - `smtp_server`: SMTP 服务器地址
  - `smtp_port`: SMTP 端口
  - `imap_server`: IMAP 服务器地址
  - `imap_port`: IMAP 端口
  - `email_address`: 邮箱地址
  - `email_password`: 邮箱密码/授权码
  - `updated_at`: 更新时间

- **主要方法**:
  - `get_config()`: 获取配置
  - `update_config()`: 更新配置
  - `send_email()`: 发送邮件
  - `check_new_emails()`: 检查新邮件

#### 2. telegram_config_manager.py
- **TelegramConfigManager 类**: 管理 Telegram 配置
- **数据库表**: `telegram_config`
  - `enabled`: 是否启用（0/1）
  - `bot_token`: Bot Token
  - `chat_id`: Chat ID
  - `updated_at`: 更新时间

- **主要方法**:
  - `get_config()`: 获取配置
  - `update_config()`: 更新配置

### API 端点

#### Email API
- `GET /api/email/config`: 获取 Email 配置
- `POST /api/email/config`: 更新 Email 配置

#### Telegram API
- `GET /api/telegram-config/config`: 获取 Telegram 配置
- `POST /api/telegram-config/config`: 更新 Telegram 配置

### 前端组件

#### UI 面板
在左侧边栏添加了两个配置面板：
1. **EMAIL 通知面板**:
   - 显示邮箱地址
   - 开关控制
   - 配置按钮

2. **TELEGRAM 通知面板**:
   - 显示 Chat ID
   - 开关控制
   - 配置按钮

#### 配置模态框
1. **Email 配置模态框**:
   - 邮箱地址输入
   - 密码/授权码输入
   - SMTP/IMAP 服务器配置
   - 端口配置

2. **Telegram 配置模态框**:
   - Bot Token 输入
   - Chat ID 输入

#### JavaScript 函数
- `loadEmailStatus()`: 加载 Email 状态
- `toggleEmail()`: 切换 Email 开关
- `openEmailSettings()`: 打开 Email 配置
- `saveEmailSettings()`: 保存 Email 配置
- `loadTelegramStatus()`: 加载 Telegram 状态
- `toggleTelegram()`: 切换 Telegram 开关
- `openTelegramSettings()`: 打开 Telegram 配置
- `saveTelegramSettings()`: 保存 Telegram 配置

## 配置示例

### Email 配置（163 邮箱）
```json
{
  "enabled": true,
  "email_address": "wu.xiguanghua@163.com",
  "email_password": "YOUR_AUTH_CODE",
  "smtp_server": "smtp.163.com",
  "smtp_port": 465,
  "imap_server": "imap.163.com",
  "imap_port": 993
}
```

### Telegram 配置
```json
{
  "enabled": true,
  "bot_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
  "chat_id": "123456789"
}
```

## 使用场景

### Email 适用场景
- 需要通过邮件远程提交任务
- 需要邮件形式的任务报告
- 团队协作，多人通过邮件提交任务
- 需要邮件存档任务结果

### Telegram 适用场景
- 需要即时通知
- 移动端快速查看任务状态
- 轻量级通知需求
- 与其他 Telegram Bot 集成

## 注意事项

### Email
1. **授权码不是登录密码**: 163 邮箱需要使用授权码，不是邮箱登录密码
2. **防火墙设置**: 确保服务器可以访问 SMTP/IMAP 端口
3. **邮件检查频率**: 系统会定期检查新邮件，不是实时的
4. **安全性**: 密码存储在数据库中，建议使用专用邮箱

### Telegram
1. **Bot Token 保密**: 不要泄露 Bot Token
2. **Chat ID 唯一性**: 每个用户的 Chat ID 是唯一的
3. **Bot 权限**: 确保 Bot 有发送消息的权限
4. **网络访问**: 确保服务器可以访问 Telegram API

## 故障排查

### Email 无法发送
1. 检查授权码是否正确
2. 检查 SMTP 服务器和端口
3. 检查网络连接
4. 查看日志: `data/logs/email_manager.log`

### Email 无法接收
1. 检查 IMAP 服务是否开启
2. 检查 IMAP 服务器和端口
3. 确认有未读邮件
4. 查看日志: `data/logs/email_manager.log`

### Telegram 无法发送
1. 检查 Bot Token 是否正确
2. 检查 Chat ID 是否正确
3. 确认 Bot 已启动（发送 /start）
4. 检查网络连接
5. 查看日志: `data/logs/telegram_config_manager.log`

## 更新日志

### v1.0.0 (2026-02-14)
- ✨ 新增 Email 配置管理功能
- ✨ 新增 Telegram 配置管理功能
- ✨ 支持通过 Email 接收任务
- ✨ 支持通过 Email 发送结果
- ✨ 支持 Telegram 通知
- ✨ 在左侧边栏添加配置面板
- ✨ 新增配置模态框
- ✨ 支持开关控制
