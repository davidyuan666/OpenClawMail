# ArXiv Search MCP

一个用于检索 arXiv 论文的 MCP (Model Context Protocol) 服务器。

## 功能特性

- 🔍 按关键词搜索论文
- 📄 通过 arXiv ID 获取论文详情
- 👤 按作者名搜索论文
- 📊 支持多种排序方式（相关性、更新时间、提交时间）

## 安装

1. 安装依赖：
```bash
pip install -r requirements.txt
```

## 配置

在 `.mcp.json` 中添加以下配置：

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

## 可用工具

### 1. search_arxiv_papers
搜索 arXiv 论文

**参数：**
- `query` (必需): 搜索关键词
- `max_results` (可选): 最大结果数，默认 10
- `sort_by` (可选): 排序方式，可选值：relevance, lastUpdatedDate, submittedDate

**示例：**
```
搜索关于 "transformer neural networks" 的论文
```

### 2. get_arxiv_paper_by_id
通过 arXiv ID 获取论文详细信息

**参数：**
- `paper_id` (必需): arXiv 论文 ID，例如 "2301.07041"

**示例：**
```
获取论文 2301.07041 的详细信息
```

### 3. search_arxiv_by_author
按作者名搜索论文

**参数：**
- `author` (必需): 作者名
- `max_results` (可选): 最大结果数，默认 10

**示例：**
```
搜索 Geoffrey Hinton 的论文
```

## 使用场景

- 📚 文献调研：快速查找相关领域的最新论文
- ✍️ 论文写作：查找引用文献和相关研究
- 🎓 学术研究：跟踪特定作者或主题的研究进展
- 💡 灵感获取：发现新的研究方向和思路

## 许可证

MIT License
