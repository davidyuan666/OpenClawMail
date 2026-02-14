#!/usr/bin/env python3
"""
Document Converter MCP Server
Converts Word/PDF documents to clean Markdown format
Pure data extraction - no analysis logic
"""

import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio
import pypandoc
import PyPDF2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("document-reviewer-mcp")

# Initialize MCP server
app = Server("document-reviewer")

# Tool definitions
TOOLS = [
    Tool(
        name="convert_document_to_markdown",
        description="Convert Word (.docx) or PDF (.pdf) document to clean Markdown format. Pure data extraction only.",
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute path to the Word or PDF file"
                }
            },
            "required": ["file_path"]
        }
    )
]

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return TOOLS


def convert_pdf_to_markdown(pdf_path: str) -> str:
    """Convert PDF to Markdown using PyPDF2"""
    try:
        markdown_content = []
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                markdown_content.append(f"## Page {page_num}\n\n{text}\n\n")
        return "\n".join(markdown_content)
    except Exception as e:
        logger.error(f"Error converting PDF: {e}")
        raise


def convert_docx_to_markdown(docx_path: str) -> str:
    """Convert DOCX to Markdown using pypandoc"""
    try:
        markdown_content = pypandoc.convert_file(docx_path, 'markdown')
        return markdown_content
    except Exception as e:
        logger.error(f"Error converting DOCX: {e}")
        raise


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    try:
        if name == "convert_document_to_markdown":
            file_path = arguments.get("file_path")
            if not file_path or not os.path.exists(file_path):
                return [TextContent(type="text", text=f"Error: File not found: {file_path}")]

            file_ext = Path(file_path).suffix.lower()

            if file_ext == ".pdf":
                markdown_content = convert_pdf_to_markdown(file_path)
            elif file_ext == ".docx":
                markdown_content = convert_docx_to_markdown(file_path)
            else:
                return [TextContent(type="text", text=f"Error: Unsupported file format: {file_ext}")]

            return [TextContent(
                type="text",
                text=markdown_content
            )]

        else:
            return [TextContent(type="text", text=f"Error: Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Error in call_tool: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
