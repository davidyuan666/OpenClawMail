#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Document Converter MCP服务器
"""
import asyncio
import json
from pathlib import Path

async def test_converter():
    """测试转换功能"""
    print("=" * 60)
    print("Document Converter MCP 测试")
    print("=" * 60)

    # 测试Markdown内容
    markdown_content = """# 测试文档

## 介绍

这是一个**测试文档**，用于验证Markdown转PDF功能。

### 功能列表

- 支持中文
- 支持**粗体**和*斜体*
- 支持列表

### 代码示例

```python
def hello():
    print("Hello World")
```

## 结论

测试完成。
"""

    # 测试LaTeX内容
    latex_content = r"""\documentclass{article}
\usepackage[UTF8]{ctex}
\usepackage{amsmath}

\title{测试文档}
\author{测试作者}
\date{\today}

\begin{document}

\maketitle

\section{介绍}
这是一个LaTeX测试文档。

\section{数学公式}
爱因斯坦质能方程：
\begin{equation}
E = mc^2
\end{equation}

\section{列表}
\begin{itemize}
    \item 第一项
    \item 第二项
    \item 第三项
\end{itemize}

\end{document}
"""

    # 输出路径
    output_dir = Path(__file__).parent / "test_output"
    output_dir.mkdir(exist_ok=True)

    md_output = output_dir / "test_markdown.pdf"
    latex_output = output_dir / "test_latex.pdf"

    print("\n1. 测试Markdown转PDF...")
    print(f"   输出路径: {md_output}")

    print("\n2. 测试LaTeX转PDF...")
    print(f"   输出路径: {latex_output}")

    print("\n" + "=" * 60)
    print("提示: 请使用MCP客户端调用工具进行实际测试")
    print("=" * 60)

    # 保存测试内容到文件
    with open(output_dir / "test_markdown.md", "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"\nMarkdown内容已保存到: {output_dir / 'test_markdown.md'}")

    with open(output_dir / "test_latex.tex", "w", encoding="utf-8") as f:
        f.write(latex_content)
    print(f"LaTeX内容已保存到: {output_dir / 'test_latex.tex'}")


if __name__ == "__main__":
    asyncio.run(test_converter())
