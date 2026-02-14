#!/usr/bin/env python3
"""
Bilibili Analyzer MCP Server
提供 Bilibili 视频内容分析能力的 MCP 服务器
"""
import asyncio
import logging
import re
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
import yt_dlp

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 MCP 服务器
app = Server("bilibili-analyzer")


def extract_video_id(url: str) -> str:
    """从URL中提取Bilibili视频ID"""
    patterns = [
        r'bilibili\.com\/video\/(BV\w+)',
        r'bilibili\.com\/video\/(av\d+)',
        r'b23\.tv\/(\w+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ""


def is_bilibili_url(url: str) -> bool:
    """检测是否为Bilibili URL"""
    return "bilibili.com" in url or "b23.tv" in url


async def analyze_single_video(arguments: dict) -> list[TextContent]:
    """分析单个Bilibili视频内容"""
    url = arguments.get("url", "")

    if not url:
        return [TextContent(type="text", text="Error: URL parameter is required")]

    if not is_bilibili_url(url):
        return [TextContent(type="text", text="Error: Only Bilibili URLs are supported.")]

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # 格式化输出
            output = f"=== Bilibili Video Analysis ===\n\n"
            output += f"Title: {info.get('title', 'N/A')}\n"
            output += f"Uploader: {info.get('uploader', 'N/A')}\n"
            output += f"Upload Date: {info.get('upload_date', 'N/A')}\n"
            output += f"Duration: {info.get('duration', 0)} seconds\n"
            output += f"Views: {info.get('view_count', 0):,}\n"
            output += f"Likes: {info.get('like_count', 0):,}\n"

            description = info.get('description', '')
            if description:
                output += f"\nDescription:\n{description[:500]}{'...' if len(description) > 500 else ''}\n"

            tags = info.get('tags', [])
            if tags:
                output += f"\nTags: {', '.join(tags[:10])}\n"

            output += f"\nVideo URL: {url}\n"

            return [TextContent(type="text", text=output)]

    except Exception as e:
        logger.error(f"Error analyzing video: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def analyze_channel(arguments: dict) -> list[TextContent]:
    """分析Bilibili UP主的视频内容"""
    url = arguments.get("url", "")
    max_videos = arguments.get("max_videos", 10)

    if not url:
        return [TextContent(type="text", text="Error: URL parameter is required")]

    if not is_bilibili_url(url):
        return [TextContent(type="text", text="Error: Only Bilibili URLs are supported.")]

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'skip_download': True,
            'playlistend': max_videos,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            output = f"=== Bilibili UP主 Analysis ===\n\n"
            output += f"UP主: {info.get('uploader', info.get('channel', 'N/A'))}\n"
            output += f"Channel URL: {url}\n\n"

            entries = info.get('entries', [])
            if not entries:
                return [TextContent(type="text", text="No videos found for this UP主.")]

            output += f"Analyzing {len(entries)} recent videos:\n\n"

            # 统计信息
            total_views = 0
            topics = {}

            for i, entry in enumerate(entries[:max_videos], 1):
                title = entry.get('title', 'N/A')
                views = entry.get('view_count', 0)
                duration = entry.get('duration', 0)

                output += f"{i}. {title}\n"
                output += f"   Views: {views:,} | Duration: {duration}s\n\n"

                total_views += views

                # 简单的主题提取（基于标题关键词）
                for word in title.split():
                    if len(word) > 2:
                        topics[word] = topics.get(word, 0) + 1

            # 总结
            output += f"\n=== Summary ===\n"
            output += f"Total Videos Analyzed: {len(entries)}\n"
            output += f"Total Views: {total_views:,}\n"
            output += f"Average Views: {total_views // len(entries):,}\n\n"

            # 高频主题
            if topics:
                sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]
                output += f"Common Topics/Keywords:\n"
                for topic, count in sorted_topics:
                    output += f"  - {topic}: {count} times\n"

            return [TextContent(type="text", text=output)]

    except Exception as e:
        logger.error(f"Error analyzing channel: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用的Bilibili视频分析工具"""
    return [
        Tool(
            name="analyze_video",
            description="Analyze a single Bilibili video, extract title, description, views, likes, and other metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Bilibili video URL"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="analyze_channel",
            description="Analyze a Bilibili UP主's videos to summarize content themes and statistics",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Bilibili UP主 URL"
                    },
                    "max_videos": {
                        "type": "number",
                        "description": "Maximum number of videos to analyze (default: 10)",
                        "default": 10
                    }
                },
                "required": ["url"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """处理工具调用"""
    try:
        if name == "analyze_video":
            return await analyze_single_video(arguments)
        elif name == "analyze_channel":
            return await analyze_channel(arguments)
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
