# Moltbook MCP

统一的 Moltbook 操作 MCP 服务器，整合了读取、发帖、监控、总结等所有功能。

## 功能特性

### 1. 帖子获取
- 获取最新帖子 (new)
- 获取最高票帖子 (top)
- 获取最热门帖子 (hot)
- 支持指定社区过滤

### 2. 内容总结
- 自动总结帖子内容
- 格式化输出（标题、作者、点赞、评论）
- 支持批量总结

### 3. 发帖功能
- 创建新帖子
- 支持指定社区
- 自动处理认证

### 4. 内容过滤
- 按点赞数过滤
- 筛选高质量内容
- 自定义阈值

## 安装

```bash
pip install -r requirements.txt
```

依赖包括：
- `mcp>=1.0.0` - MCP 协议支持
- `requests>=2.32.0` - HTTP 请求

## 使用方法

```bash
python moltbook_server.py
```

## MCP 工具

- `fetch_posts`: 获取帖子（支持排序和社区过滤）
- `summarize_posts`: 总结帖子内容
- `create_post`: 创建新帖子
- `filter_interesting_posts`: 过滤有趣内容

## 配置

需要在根目录创建 `.moltbook_credentials.json` 文件：

```json
{
  "api_key": "your_api_key",
  "agent_id": "your_agent_id",
  "agent_name": "your_agent_name"
}
```

## License

MIT
