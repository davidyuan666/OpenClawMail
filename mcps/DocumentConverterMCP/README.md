# Document Converter MCP

A Model Context Protocol (MCP) server that provides document conversion capabilities.

## Features

- **Markdown to PDF**: Convert Markdown content to PDF using Pandoc
- **LaTeX to PDF**: Convert LaTeX content to PDF using local TeXLive installation

## Prerequisites

### Required Software

1. **Python 3.8+**
2. **Pandoc** (for Markdown to PDF conversion)
   - Download from: https://pandoc.org/installing.html
   - Windows: `choco install pandoc` or download installer

3. **TeXLive** (for LaTeX to PDF conversion)
   - Download from: https://www.tug.org/texlive/
   - Windows: Install TeXLive with XeLaTeX support
   - Ensure `pdflatex` is in your PATH

## Installation

1. Clone or download this repository
2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Verify Pandoc installation:

```bash
pandoc --version
```

4. Verify TeXLive installation:

```bash
pdflatex --version
```

## Configuration

Add this to your `.mcp.json` file:

```json
{
  "mcpServers": {
    "document-converter": {
      "command": "python",
      "args": [
        "C:/workspace/claudecodelabspace/mcps/DocumentConverterMCP/converter_server.py"
      ]
    }
  }
}
```

## Available Tools

### 1. convert_markdown_to_pdf

Convert Markdown content to PDF file.

**Parameters:**
- `markdown_content` (string, required): Markdown content to convert
- `output_path` (string, required): Output PDF file path

**Example:**
```python
{
  "markdown_content": "# Hello World\n\nThis is a test.",
  "output_path": "output.pdf"
}
```

### 2. convert_latex_to_pdf

Convert LaTeX content to PDF file using local TeXLive.

**Parameters:**
- `latex_content` (string, required): LaTeX content to convert
- `output_path` (string, required): Output PDF file path

**Example:**
```python
{
  "latex_content": "\\documentclass{article}\n\\begin{document}\nHello World\n\\end{document}",
  "output_path": "output.pdf"
}
```

## Usage Examples

### Markdown to PDF

```markdown
# My Document

This is a **bold** text and this is *italic*.

- Item 1
- Item 2
- Item 3
```

### LaTeX to PDF

```latex
\documentclass{article}
\usepackage[UTF8]{ctex}
\begin{document}
\title{我的文档}
\author{作者}
\maketitle

\section{介绍}
这是一个LaTeX文档示例。

\end{document}
```

## Troubleshooting

### Pandoc not found
- Make sure Pandoc is installed and in your PATH
- Restart your terminal/IDE after installation

### pdflatex not found
- Make sure TeXLive is installed
- Add TeXLive bin directory to your PATH
- Windows: Usually `C:\texlive\2023\bin\win32`

### Chinese characters not displaying
- For Markdown: Pandoc uses XeLaTeX with Microsoft YaHei font
- For LaTeX: Use `\usepackage[UTF8]{ctex}` in your document

## License

MIT License
