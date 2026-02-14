# ArXiv Search MCP 配置指南

## 在 Claude Code 中配置

在项目根目录的 `.mcp.json` 文件中添加以下配置：

```json
{
  "mcpServers": {
    "arxiv-search": {
      "command": "python",
      "args": [
        "C:/workspace/claudecodelabspace/mcps/ArxivSearchMCP/arxiv_server.py"
      ]
    }
  }
}
```

## 配置说明

- **command**: 使用 Python 解释器运行服务器
- **args**: 指向 arxiv_server.py 的完整路径
- **无需环境变量**: 此 MCP 不需要 API 密钥或其他环境变量

## 验证配置

配置完成后，重启 Claude Code，然后可以使用以下命令测试：

```
搜索关于 "deep learning" 的论文
```

如果配置正确，将返回相关论文列表。
