#!/usr/bin/env python3
"""
测试 ArXiv Search MCP Server
"""
import asyncio
from arxiv_server import search_papers, get_paper_by_id, search_by_author


async def test_search_papers():
    """测试搜索论文功能"""
    print("=== Testing search_papers ===")
    result = await search_papers({
        "query": "large language model",
        "max_results": 3,
        "sort_by": "relevance"
    })
    print(result[0].text)
    print("\n")


async def test_get_paper_by_id():
    """测试获取论文详情功能"""
    print("=== Testing get_paper_by_id ===")
    result = await get_paper_by_id({
        "paper_id": "2301.07041"
    })
    print(result[0].text)
    print("\n")


async def test_search_by_author():
    """测试按作者搜索功能"""
    print("=== Testing search_by_author ===")
    result = await search_by_author({
        "author": "Yann LeCun",
        "max_results": 3
    })
    print(result[0].text)
    print("\n")


async def main():
    """运行所有测试"""
    await test_search_papers()
    await test_get_paper_by_id()
    await test_search_by_author()


if __name__ == "__main__":
    asyncio.run(main())
