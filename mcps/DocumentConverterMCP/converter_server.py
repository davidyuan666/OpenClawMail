#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Document Converter MCP Server
支持Markdown转PDF和LaTeX转PDF
"""
import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Sequence

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    import mcp.server.stdio
except ImportError:
    print("Error: mcp package not found. Please install it with: pip install mcp")
    sys.exit(1)

# 创建MCP服务器实例
app = Server("document-converter")


def check_latex_installation():
    """检查LaTeX是否已安装"""
    try:
        result = subprocess.run(
            ["pdflatex", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def markdown_to_pdf_pandoc(md_content: str, output_path: str) -> tuple[bool, str]:
    """使用Pandoc将Markdown转换为PDF"""
    try:
        # 创建临时Markdown文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp_md:
            tmp_md.write(md_content)
            tmp_md_path = tmp_md.name

        # 使用pandoc转换
        result = subprocess.run(
            [
                "pandoc",
                tmp_md_path,
                "-o", output_path,
                "--pdf-engine=xelatex",
                "-V", "CJKmainfont=Microsoft YaHei",
                "-V", "geometry:margin=2cm"
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        # 清理临时文件
        os.unlink(tmp_md_path)

        if result.returncode == 0:
            return True, f"PDF generated successfully: {output_path}"
        else:
            return False, f"Pandoc error: {result.stderr}"

    except FileNotFoundError:
        return False, "Pandoc not found. Please install pandoc."
    except Exception as e:
        return False, f"Error: {str(e)}"


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的工具"""
    return [
        Tool(
            name="convert_markdown_to_pdf",
            description="Convert Markdown content to PDF file",
            inputSchema={
                "type": "object",
                "properties": {
                    "markdown_content": {
                        "type": "string",
                        "description": "Markdown content to convert"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Output PDF file path"
                    }
                },
                "required": ["markdown_content", "output_path"]
            }
        ),
        Tool(
            name="convert_latex_to_pdf",
            description="Convert LaTeX content to PDF file using local TeXLive",
            inputSchema={
                "type": "object",
                "properties": {
                    "latex_content": {
                        "type": "string",
                        "description": "LaTeX content to convert"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Output PDF file path"
                    }
                },
                "required": ["latex_content", "output_path"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """处理工具调用"""
    try:
        if name == "convert_markdown_to_pdf":
            markdown_content = arguments.get("markdown_content", "")
            output_path = arguments.get("output_path", "")

            if not markdown_content:
                return [TextContent(type="text", text="Error: markdown_content is required")]

            if not output_path:
                return [TextContent(type="text", text="Error: output_path is required")]

            # 转换Markdown到PDF
            success, message = markdown_to_pdf_pandoc(markdown_content, output_path)

            return [TextContent(type="text", text=message)]

        elif name == "convert_latex_to_pdf":
            latex_content = arguments.get("latex_content", "")
            output_path = arguments.get("output_path", "")

            if not latex_content:
                return [TextContent(type="text", text="Error: latex_content is required")]

            if not output_path:
                return [TextContent(type="text", text="Error: output_path is required")]

            # 转换LaTeX到PDF
            success, message = latex_to_pdf(latex_content, output_path)

            return [TextContent(type="text", text=message)]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """主函数"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
def latex_to_pdf(latex_content: str, output_path: str) -> tuple[bool, str]:
    """使用本地TeXLive将LaTeX转换为PDF"""
    try:
        # 检查LaTeX是否安装
        if not check_latex_installation():
            return False, "LaTeX (pdflatex) not found. Please install TeXLive."

        # 创建临时LaTeX文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False, encoding='utf-8') as tmp_tex:
            tmp_tex.write(latex_content)
            tmp_tex_path = tmp_tex.name

        # 获取临时目录
        tmp_dir = os.path.dirname(tmp_tex_path)
        tmp_basename = os.path.splitext(os.path.basename(tmp_tex_path))[0]

        # 运行pdflatex（可能需要运行两次以生成目录和引用）
        for i in range(2):
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", f"-output-directory={tmp_dir}", tmp_tex_path],
                capture_output=True,
                text=True,
                timeout=60
            )

        # 检查PDF是否生成
        tmp_pdf = os.path.join(tmp_dir, f"{tmp_basename}.pdf")
        if os.path.exists(tmp_pdf):
            # 移动PDF到目标位置
            import shutil
            shutil.move(tmp_pdf, output_path)

            # 清理临时文件
            for ext in ['.tex', '.aux', '.log', '.out']:
                tmp_file = os.path.join(tmp_dir, f"{tmp_basename}{ext}")
                if os.path.exists(tmp_file):
                    os.unlink(tmp_file)

            return True, f"PDF generated successfully: {output_path}"
        else:
            return False, f"PDF generation failed. LaTeX error: {result.stderr}"

    except Exception as e:
        return False, f"Error: {str(e)}"

