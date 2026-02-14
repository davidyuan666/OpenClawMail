#!/usr/bin/env python3
"""
ArXiv Search MCP Server
提供 arXiv 论文检索能力的 MCP 服务器
"""
import asyncio
import logging
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
import arxiv

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 MCP 服务器
app = Server("arxiv-search")


async def search_papers(arguments: dict) -> list[TextContent]:
    """搜索 arXiv 论文"""
    query = arguments.get("query", "")
    max_results = arguments.get("max_results", 10)
    sort_by = arguments.get("sort_by", "relevance")

    if not query:
        return [TextContent(type="text", text="Error: Query parameter is required")]

    try:
        # 设置排序方式
        sort_order = arxiv.SortCriterion.Relevance
        if sort_by == "lastUpdatedDate":
            sort_order = arxiv.SortCriterion.LastUpdatedDate
        elif sort_by == "submittedDate":
            sort_order = arxiv.SortCriterion.SubmittedDate

        # 搜索论文
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_order
        )

        results = list(search.results())

        if not results:
            return [TextContent(type="text", text=f"No papers found for query: {query}")]

        # 格式化结果
        output = f"Found {len(results)} papers for query: '{query}'\n\n"

        for i, paper in enumerate(results, 1):
            output += f"--- Paper {i} ---\n"
            output += f"Title: {paper.title}\n"
            output += f"Authors: {', '.join([author.name for author in paper.authors])}\n"
            output += f"Published: {paper.published.strftime('%Y-%m-%d')}\n"
            output += f"Updated: {paper.updated.strftime('%Y-%m-%d')}\n"
            output += f"Categories: {', '.join(paper.categories)}\n"
            output += f"Abstract: {paper.summary[:300]}...\n"
            output += f"PDF URL: {paper.pdf_url}\n"
            output += f"arXiv URL: {paper.entry_id}\n\n"

        return [TextContent(type="text", text=output)]

    except Exception as e:
        logger.error(f"Error searching papers: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def get_paper_by_id(arguments: dict) -> list[TextContent]:
    """通过 arXiv ID 获取论文详情"""
    paper_id = arguments.get("paper_id", "")

    if not paper_id:
        return [TextContent(type="text", text="Error: paper_id parameter is required")]

    try:
        # 搜索特定论文
        search = arxiv.Search(id_list=[paper_id])
        paper = next(search.results())

        # 格式化详细信息
        output = f"=== Paper Details ===\n\n"
        output += f"Title: {paper.title}\n\n"
        output += f"Authors: {', '.join([author.name for author in paper.authors])}\n\n"
        output += f"Published: {paper.published.strftime('%Y-%m-%d')}\n"
        output += f"Updated: {paper.updated.strftime('%Y-%m-%d')}\n\n"
        output += f"Categories: {', '.join(paper.categories)}\n"
        output += f"Primary Category: {paper.primary_category}\n\n"
        output += f"Abstract:\n{paper.summary}\n\n"
        output += f"PDF URL: {paper.pdf_url}\n"
        output += f"arXiv URL: {paper.entry_id}\n"

        if paper.comment:
            output += f"\nComment: {paper.comment}\n"

        if paper.journal_ref:
            output += f"Journal Reference: {paper.journal_ref}\n"

        if paper.doi:
            output += f"DOI: {paper.doi}\n"

        return [TextContent(type="text", text=output)]

    except StopIteration:
        return [TextContent(type="text", text=f"Paper not found: {paper_id}")]
    except Exception as e:
        logger.error(f"Error getting paper: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def search_by_author(arguments: dict) -> list[TextContent]:
    """按作者搜索论文"""
    author = arguments.get("author", "")
    max_results = arguments.get("max_results", 10)

    if not author:
        return [TextContent(type="text", text="Error: author parameter is required")]

    try:
        # 构建作者搜索查询
        query = f"au:{author}"
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )

        results = list(search.results())

        if not results:
            return [TextContent(type="text", text=f"No papers found for author: {author}")]

        output = f"Found {len(results)} papers by author: '{author}'\n\n"

        for i, paper in enumerate(results, 1):
            output += f"--- Paper {i} ---\n"
            output += f"Title: {paper.title}\n"
            output += f"Published: {paper.published.strftime('%Y-%m-%d')}\n"
            output += f"Categories: {', '.join(paper.categories)}\n"
            output += f"arXiv ID: {paper.get_short_id()}\n"
            output += f"URL: {paper.entry_id}\n\n"

        return [TextContent(type="text", text=output)]

    except Exception as e:
        logger.error(f"Error searching by author: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用的 arXiv 工具"""
    return [
        Tool(
            name="search_arxiv_papers",
            description="Search for papers on arXiv by keywords, topics, or queries",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'machine learning', 'quantum computing')"
                    },
                    "max_results": {
                        "type": "number",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10
                    },
                    "sort_by": {
                        "type": "string",
                        "description": "Sort order: 'relevance', 'lastUpdatedDate', or 'submittedDate'",
                        "enum": ["relevance", "lastUpdatedDate", "submittedDate"],
                        "default": "relevance"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_arxiv_paper_by_id",
            description="Get detailed information about a specific arXiv paper by its ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "paper_id": {
                        "type": "string",
                        "description": "arXiv paper ID (e.g., '2301.07041' or 'arxiv:2301.07041')"
                    }
                },
                "required": ["paper_id"]
            }
        ),
        Tool(
            name="search_arxiv_by_author",
            description="Search for papers by a specific author on arXiv",
            inputSchema={
                "type": "object",
                "properties": {
                    "author": {
                        "type": "string",
                        "description": "Author name (e.g., 'Geoffrey Hinton')"
                    },
                    "max_results": {
                        "type": "number",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10
                    }
                },
                "required": ["author"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """处理工具调用"""
    try:
        if name == "search_arxiv_papers":
            return await search_papers(arguments)
        elif name == "get_arxiv_paper_by_id":
            return await get_paper_by_id(arguments)
        elif name == "search_arxiv_by_author":
            return await search_by_author(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """运行 MCP 服务器"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())

