# Document Converter MCP - Project Summary

## 项目概述

Document Converter MCP 是一个基于 Model Context Protocol (MCP) 的文档转换服务器，提供 Markdown 和 LaTeX 到 PDF 的转换功能。

## 项目结构

```
DocumentConverterMCP/
├── converter_server.py    # MCP服务器主程序
├── test_converter.py      # 测试脚本
├── requirements.txt       # Python依赖
├── README.md             # 项目说明
├── SETUP.md              # 安装指南
├── .gitignore            # Git忽略文件
└── test_output/          # 测试输出目录
    ├── test_markdown.md
    └── test_latex.tex
```

## 核心功能

### 1. Markdown转PDF
- 使用Pandoc进行转换
- 支持中文（使用XeLaTeX + Microsoft YaHei字体）
- 支持Markdown所有标准语法

### 2. LaTeX转PDF
- 使用本地TeXLive的pdflatex
- 自动运行两次以生成目录和引用
- 支持中文（需要ctex宏包）
- 自动清理临时文件（.aux, .log, .out）

## MCP工具接口

### convert_markdown_to_pdf
**输入参数:**
- `markdown_content`: Markdown内容字符串
- `output_path`: 输出PDF文件路径

**返回:** 成功/失败消息

### convert_latex_to_pdf
**输入参数:**
- `latex_content`: LaTeX内容字符串
- `output_path`: 输出PDF文件路径

**返回:** 成功/失败消息

## 依赖要求

### Python依赖
- mcp >= 0.9.0

### 外部工具
- **Pandoc**: Markdown转PDF
- **TeXLive**: LaTeX转PDF（需要pdflatex命令）

## 配置说明

已更新 `.mcp.json` 配置文件，添加了以下配置：

```json
"document-converter": {
    "command": "python",
    "args": [
        "C:/workspace/claudecodelabspace/mcps/DocumentConverterMCP/converter_server.py"
    ]
}
```

## 使用示例

### 通过MCP调用Markdown转PDF

```python
{
    "tool": "convert_markdown_to_pdf",
    "arguments": {
        "markdown_content": "# 标题\n\n这是内容",
        "output_path": "output.pdf"
    }
}
```

### 通过MCP调用LaTeX转PDF

```python
{
    "tool": "convert_latex_to_pdf",
    "arguments": {
        "latex_content": "\\documentclass{article}...",
        "output_path": "output.pdf"
    }
}
```

## 测试状态

✅ 项目结构创建完成
✅ MCP服务器代码实现完成
✅ 测试脚本创建完成
✅ 文档编写完成
✅ .mcp.json配置更新完成
⏳ 等待GitHub仓库地址进行提交

## 下一步

请提供GitHub仓库地址，我将：
1. 初始化Git仓库（如果需要）
2. 添加所有文件
3. 创建提交
4. 推送到远程仓库

