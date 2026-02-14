# Document Converter MCP - Project Summary

## 项目概述

DocumentReviewerMCP 是一个 MCP 服务，专注于将 Word/PDF 文档转换为干净的 Markdown 格式。

**设计原则**: MCP 只负责纯粹的数据提取和转换，所有分析逻辑都在 Skill 层实现。

## 核心功能

### 文档转换（纯数据提取）
- **PDF 转 Markdown**: 使用 PyPDF2 提取 PDF 文本内容
- **Word 转 Markdown**: 使用 pypandoc 转换 DOCX 文件
- **无分析逻辑**: 只返回干净的 Markdown 文本

## 技术栈

- **Python 3.x**
- **MCP SDK**: 用于 MCP 服务器实现
- **PyPDF2**: PDF 文本提取
- **pypandoc**: Word 文档转换
- **asyncio**: 异步处理

## 文件结构

```
DocumentReviewerMCP/
├── reviewer_server.py      # MCP 服务器主文件
├── test_reviewer.py        # 测试脚本
├── requirements.txt        # Python 依赖
├── README.md              # 使用文档
├── PROJECT_SUMMARY.md     # 项目总结
├── .gitignore            # Git 忽略配置
└── test_output/          # 测试输出目录
```

## MCP 工具

### convert_document_to_markdown
将 Word 或 PDF 文档转换为 Markdown 格式（纯数据提取）。

**参数:**
- `file_path` (string): 文档的绝对路径

**返回:**
- 干净的 Markdown 文本内容

## 配套 Skill

### document-review
完整的文档审稿工作流程：
1. 使用 MCP 转换文档为 Markdown（数据提取）
2. Claude 在 Skill 中执行内容分析（分析逻辑）
3. Claude 生成 LaTeX 审稿报告（报告生成）
4. 转换为 PDF
5. 发送到 Telegram

**使用方法:**
```
/document-review <file_path>
```

**架构设计:**
- **MCP 层**: 纯数据提取和转换
- **Skill 层**: 所有分析、审稿逻辑和报告生成

## 安装与配置

### 依赖安装
```bash
pip install -r requirements.txt
```

### 额外要求
- **Pandoc**: Word 文档转换需要
  - Windows: 从 https://pandoc.org/installing.html 下载
  - macOS: `brew install pandoc`
  - Linux: `sudo apt-get install pandoc`

### MCP 配置
在 `.mcp.json` 中添加：
```json
{
  "document-reviewer": {
    "command": "python",
    "args": ["C:/workspace/claudecodelabspace/mcps/DocumentReviewerMCP/reviewer_server.py"]
  }
}
```

## 使用示例

### 转换文档
```json
{
  "tool": "convert_document_to_markdown",
  "arguments": {
    "file_path": "/path/to/document.pdf"
  }
}
```

### 分析文档
```json
{
  "tool": "analyze_document_content",
  "arguments": {
    "markdown_content": "# Document Title\n\nContent...",
    "output_path": "/path/to/review_report.tex"
  }
}
```

## 审稿标准

### 客观性
- 保持中立、专业的语气
- 基于文档证据进行评价
- 避免个人偏见
- 建设性而非破坏性

### 简洁性
- 每个审稿点聚焦明确
- 使用具体例子支持观点
- 避免冗余
- 优先关注最重要的问题

## 开发状态

- ✅ 文档转换功能（PDF/Word）
- ✅ LaTeX 报告生成
- ✅ MCP 服务器实现
- ✅ 配套 Skill 定义
- ✅ 配置文件更新

## 未来改进

- [ ] 支持更多文档格式（PPT, HTML 等）
- [ ] 增强 PDF 文本提取质量
- [ ] 添加图表识别功能
- [ ] 支持批量文档审稿
- [ ] 集成 AI 自动分析功能

## 相关文件

- **Skill 定义**: `skills/document-review.md`
- **MCP 配置**: `.mcp.json`
- **工作空间配置**: `CLAUDE_WORKSPACE.md`

## 创建日期

2026-02-03

## 作者

Claude Sonnet 4.5 & davidyuan666
