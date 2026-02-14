#!/usr/bin/env python3
"""
测试视频分析器功能
"""
import asyncio
from video_analyzer_server import analyze_single_video, analyze_channel

async def test_video():
    """测试单个视频分析"""
    print("=== 测试单个视频分析 ===")

    # 测试YouTube视频
    result = await analyze_single_video({
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    })
    print(result[0].text)
    print("\n" + "="*50 + "\n")

async def test_channel():
    """测试频道分析"""
    print("=== 测试频道分析 ===")

    # 测试YouTube频道
    result = await analyze_channel({
        "url": "https://www.youtube.com/@YouTube",
        "max_videos": 5
    })
    print(result[0].text)

if __name__ == "__main__":
    print("视频分析器测试脚本")
    print("注意：需要网络连接才能正常工作\n")

    # 运行测试
    asyncio.run(test_video())
