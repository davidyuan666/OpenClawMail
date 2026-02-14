#!/usr/bin/env python3
"""
Moltbook MCP Server
Provides Moltbook operations via MCP protocol
"""
import asyncio
import logging
import os
import sys
import json
import requests
from pathlib import Path
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent

# Configure UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("moltbook")

# Load credentials
CREDENTIALS_FILE = Path(__file__).parent.parent.parent / ".moltbook_credentials.json"

def load_credentials():
    """Load Moltbook credentials"""
    if CREDENTIALS_FILE.exists():
        with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


async def fetch_posts_handler(arguments: dict) -> list[TextContent]:
    """Fetch posts from Moltbook"""
    sort_by = arguments.get("sort", "new")
    limit = arguments.get("limit", 25)
    community = arguments.get("community")

    creds = load_credentials()
    if not creds:
        return [TextContent(type="text", text="Error: No credentials found")]

    headers = {'X-API-Key': creds['api_key']}
    params = {'limit': limit}

    if community:
        params['submolt'] = community

    try:
        response = requests.get(
            "https://moltbook.com/api/v1/posts",
            headers=headers,
            params=params,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            posts = data.get('posts', [])

            # Sort posts based on sort_by parameter
            if sort_by == 'top':
                posts = sorted(posts, key=lambda x: x.get('upvotes', 0), reverse=True)
            elif sort_by == 'hot':
                posts = sorted(
                    posts,
                    key=lambda x: x.get('upvotes', 0) + x.get('comment_count', 0) * 2,
                    reverse=True
                )

            posts = posts[:limit]
            result = json.dumps({"success": True, "posts": posts, "count": len(posts)}, ensure_ascii=False)
            return [TextContent(type="text", text=result)]
        else:
            return [TextContent(type="text", text=f"Error: HTTP {response.status_code}: {response.text}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def summarize_posts_handler(arguments: dict) -> list[TextContent]:
    """Summarize posts"""
    posts_json = arguments.get("posts")

    if not posts_json:
        return [TextContent(type="text", text="Error: posts parameter is required")]

    try:
        if isinstance(posts_json, str):
            posts = json.loads(posts_json)
        else:
            posts = posts_json

        if not posts:
            return [TextContent(type="text", text="没有找到帖子")]

        summary = f"📊 找到 {len(posts)} 条帖子\n\n"

        for i, post in enumerate(posts, 1):
            title = post.get('title', 'No title')
            author = post.get('author', {}).get('name', 'Unknown')
            upvotes = post.get('upvotes', 0)
            comments = post.get('comment_count', 0)
            content = post.get('content', '')[:150]

            summary += f"{i}. **{title}**\n"
            summary += f"   👤 {author} | 👍 {upvotes:,} | 💬 {comments}\n"
            if content:
                summary += f"   {content}...\n\n"
            else:
                summary += "\n"

        return [TextContent(type="text", text=summary)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def create_post_handler(arguments: dict) -> list[TextContent]:
    """Create a new post on Moltbook"""
    community = arguments.get("community")
    title = arguments.get("title")
    content = arguments.get("content")

    if not all([community, title, content]):
        return [TextContent(type="text", text="Error: community, title, and content are required")]

    creds = load_credentials()
    if not creds:
        return [TextContent(type="text", text="Error: No credentials found")]

    headers = {
        'X-API-Key': creds['api_key'],
        'Content-Type': 'application/json'
    }

    post_data = {
        "submolt": community,
        "title": title,
        "content": content
    }

    try:
        response = requests.post(
            "https://moltbook.com/api/v1/posts",
            headers=headers,
            json=post_data,
            timeout=30
        )

        if response.status_code == 201:
            data = response.json()
            result = json.dumps({"success": True, "post_id": data.get('id'), "data": data}, ensure_ascii=False)
            return [TextContent(type="text", text=result)]
        else:
            return [TextContent(type="text", text=f"Error: HTTP {response.status_code}: {response.text}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error creating post: {str(e)}")]


async def filter_interesting_posts_handler(arguments: dict) -> list[TextContent]:
    """Filter interesting posts"""
    posts_json = arguments.get("posts")
    min_upvotes = arguments.get("min_upvotes", 10)

    if not posts_json:
        return [TextContent(type="text", text="Error: posts parameter is required")]

    try:
        if isinstance(posts_json, str):
            posts = json.loads(posts_json)
        else:
            posts = posts_json

        interesting = [post for post in posts if post.get('upvotes', 0) >= min_upvotes]
        result = json.dumps({"success": True, "posts": interesting, "count": len(interesting)}, ensure_ascii=False)
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error filtering posts: {str(e)}")]


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Moltbook tools"""
    return [
        Tool(
            name="fetch_posts",
            description="获取帖子（支持 new/top/hot 排序）",
            inputSchema={
                "type": "object",
                "properties": {
                    "sort": {
                        "type": "string",
                        "description": "排序方式: 'new' (最新), 'top' (最高票), 'hot' (最热门)",
                        "enum": ["new", "top", "hot"],
                        "default": "new"
                    },
                    "limit": {
                        "type": "number",
                        "description": "返回数量限制",
                        "default": 25
                    },
                    "community": {
                        "type": "string",
                        "description": "社区名称（如 'general', 'ai'）"
                    }
                }
            }
        ),
        Tool(
            name="summarize_posts",
            description="总结帖子内容",
            inputSchema={
                "type": "object",
                "properties": {
                    "posts": {
                        "description": "帖子列表（JSON 字符串或对象）"
                    }
                },
                "required": ["posts"]
            }
        ),
        Tool(
            name="create_post",
            description="创建新帖子",
            inputSchema={
                "type": "object",
                "properties": {
                    "community": {
                        "type": "string",
                        "description": "社区名称（如 'general', 'ai'）"
                    },
                    "title": {
                        "type": "string",
                        "description": "帖子标题"
                    },
                    "content": {
                        "type": "string",
                        "description": "帖子内容"
                    }
                },
                "required": ["community", "title", "content"]
            }
        ),
        Tool(
            name="filter_interesting_posts",
            description="过滤有趣内容",
            inputSchema={
                "type": "object",
                "properties": {
                    "posts": {
                        "description": "帖子列表（JSON 字符串或对象）"
                    },
                    "min_upvotes": {
                        "type": "number",
                        "description": "最小点赞数阈值",
                        "default": 10
                    }
                },
                "required": ["posts"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    try:
        if name == "fetch_posts":
            return await fetch_posts_handler(arguments)
        elif name == "summarize_posts":
            return await summarize_posts_handler(arguments)
        elif name == "create_post":
            return await create_post_handler(arguments)
        elif name == "filter_interesting_posts":
            return await filter_interesting_posts_handler(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
