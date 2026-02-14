# MCP 服务器集合

本目录包含 OpenClawMail 项目使用的所有 MCP (Model Context Protocol) 服务器。

## 目录结构

```
mcps/
├── ArxivSearchMCP/              # arXiv 论文搜索服务
├── BilibiliAnalyzerMCP/         # B站视频分析服务
├── DocumentConverterMCP/        # 文档格式转换服务
├── DocumentReviewerMCP/         # 文档审阅服务
├── JournalAbstractAnalyzerMCP/  # 期刊摘要分析服务
├── MedicalSearchMCP/            # 医学文献搜索服务
└── MoltbookMCP/                 # Moltbook 分子数据库服务
```

## MCP 服务器列表

### 1. ArxivSearchMCP
- **功能**: 搜索 arXiv 论文数据库
- **入口**: `arxiv_server.py`
- **依赖**: 见 `requirements.txt`

### 2. BilibiliAnalyzerMCP
- **功能**: 分析 B站视频内容和数据
- **入口**: `bilibili_analyzer_server.py`
- **依赖**: 见 `requirements.txt`

### 3. DocumentConverterMCP
- **功能**: 转换文档格式（PDF、Word、Markdown 等）
- **入口**: `converter_server.py`
- **依赖**: 见 `requirements.txt`

### 4. DocumentReviewerMCP
- **功能**: 自动审阅和评估文档
- **入口**: `reviewer_server.py`
- **依赖**: 见 `requirements.txt`

### 5. JournalAbstractAnalyzerMCP
- **功能**: 分析学术期刊摘要
- **入口**: `journal_analyzer_server.py`
- **依赖**: 见 `requirements.txt`

### 6. MedicalSearchMCP
- **功能**: 搜索医学文献数据库
- **入口**: `medical_server.py`
- **依赖**: 见 `requirements.txt`

### 7. MoltbookMCP
- **功能**: 查询 Moltbook 分子数据库
- **入口**: `moltbook_server.py`
- **依赖**: 见 `requirements.txt`

## 配置

所有 MCP 服务器的配置在 `config/mcp.json` 文件中定义。

```json
{
  "mcpServers": {
    "arxiv-search": {
      "command": "python",
      "args": ["mcps/ArxivSearchMCP/arxiv_server.py"]
    },
    ...
  }
}
```

## 安装依赖

每个 MCP 服务器都有自己的 `requirements.txt` 文件。可以使用以下命令安装所有依赖：

```bash
# 安装所有 MCP 服务器的依赖
for dir in mcps/*/; do
    if [ -f "$dir/requirements.txt" ]; then
        pip install -r "$dir/requirements.txt"
    fi
done
```

或者单独安装某个服务器的依赖：

```bash
pip install -r mcps/ArxivSearchMCP/requirements.txt
```

## 测试

大多数 MCP 服务器都包含测试文件，可以独立测试：

```bash
# 测试 ArxivSearchMCP
python mcps/ArxivSearchMCP/test_arxiv.py

# 测试 MedicalSearchMCP
python mcps/MedicalSearchMCP/test_medical.py
```

## 开发指南

### 添加新的 MCP 服务器

1. 在 `mcps/` 目录下创建新的服务器目录
2. 实现服务器逻辑（参考现有服务器）
3. 添加 `requirements.txt` 文件
4. 在 `config/mcp.json` 中注册服务器
5. 添加 README 和测试文件

### MCP 服务器结构

标准的 MCP 服务器目录应包含：

```
YourMCP/
├── server.py           # 主服务器文件
├── requirements.txt    # Python 依赖
├── README.md          # 服务器说明
├── test_*.py          # 测试文件（可选）
└── .gitignore         # Git 忽略配置（可选）
```

## 注意事项

- 所有 MCP 服务器使用 Python 实现
- 确保安装了所需的依赖包
- 某些服务器可能需要额外的配置（API 密钥等）
- 详细使用说明请查看各服务器目录下的 README.md

## 许可证

各 MCP 服务器的许可证请查看对应目录下的文档。
