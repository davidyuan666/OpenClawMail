#!/usr/bin/env python3
"""
测试医学检索 MCP 服务器
"""
import asyncio
import sys
sys.path.append('.')

from medical_server import search_pubmed, get_paper_details, search_clinical_trials


async def test_search_pubmed():
    """测试 PubMed 搜索"""
    print("=== Testing PubMed Search ===")
    result = await search_pubmed({
        "query": "COVID-19 vaccine",
        "max_results": 5
    })
    print(result[0].text)
    print("\n")


async def test_get_paper_details():
    """测试获取论文详情"""
    print("=== Testing Get Paper Details ===")
    result = await get_paper_details({
        "pmid": "33301246"  # 一个关于 COVID-19 疫苗的论文
    })
    print(result[0].text)
    print("\n")


async def test_search_clinical_trials():
    """测试临床试验搜索"""
    print("=== Testing Clinical Trials Search ===")
    result = await search_clinical_trials({
        "query": "diabetes",
        "max_results": 3
    })
    print(result[0].text)
    print("\n")


async def main():
    """运行所有测试"""
    await test_search_pubmed()
    await test_get_paper_details()
    await test_search_clinical_trials()


if __name__ == "__main__":
    asyncio.run(main())
