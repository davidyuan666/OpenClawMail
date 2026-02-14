#!/usr/bin/env python3
"""
Medical Search MCP Server
提供医学论文检索能力的 MCP 服务器
支持 PubMed、临床试验、药品信息等检索
"""
import asyncio
import logging
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
import requests
from xml.etree import ElementTree as ET
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 MCP 服务器
app = Server("medical-search")

# PubMed API 基础 URL
PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
PUBMED_SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"


async def search_pubmed(arguments: dict) -> list[TextContent]:
    """搜索 PubMed 医学文献"""
    query = arguments.get("query", "")
    max_results = arguments.get("max_results", 10)
    sort_by = arguments.get("sort_by", "relevance")

    if not query:
        return [TextContent(type="text", text="Error: Query parameter is required")]

    try:
        # 第一步：搜索获取 PMID 列表
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance" if sort_by == "relevance" else "pub_date"
        }

        response = requests.get(PUBMED_SEARCH_URL, params=search_params, timeout=30)
        response.raise_for_status()
        search_data = response.json()

        id_list = search_data.get("esearchresult", {}).get("idlist", [])

        if not id_list:
            return [TextContent(type="text", text=f"No papers found for query: {query}")]

        # 第二步：获取文献摘要信息
        summary_params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "json"
        }

        summary_response = requests.get(PUBMED_SUMMARY_URL, params=summary_params, timeout=30)
        summary_response.raise_for_status()
        summary_data = summary_response.json()

        results = summary_data.get("result", {})

        # 格式化结果
        output = f"Found {len(id_list)} medical papers for query: '{query}'\n\n"

        for i, pmid in enumerate(id_list, 1):
            paper = results.get(pmid, {})
            if not paper:
                continue

            output += f"--- Paper {i} ---\n"
            output += f"PMID: {pmid}\n"
            output += f"Title: {paper.get('title', 'N/A')}\n"

            authors = paper.get('authors', [])
            if authors:
                author_names = [author.get('name', '') for author in authors[:3]]
                output += f"Authors: {', '.join(author_names)}"
                if len(authors) > 3:
                    output += f" et al. ({len(authors)} total)"
                output += "\n"

            pub_date = paper.get('pubdate', 'N/A')
            output += f"Published: {pub_date}\n"

            source = paper.get('source', 'N/A')
            output += f"Journal: {source}\n"

            output += f"PubMed URL: https://pubmed.ncbi.nlm.nih.gov/{pmid}/\n\n"

        return [TextContent(type="text", text=output)]

    except Exception as e:
        logger.error(f"Error searching PubMed: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def get_paper_details(arguments: dict) -> list[TextContent]:
    """通过 PMID 获取论文详细信息"""
    pmid = arguments.get("pmid", "")

    if not pmid:
        return [TextContent(type="text", text="Error: pmid parameter is required")]

    try:
        # 获取详细的 XML 格式数据
        fetch_params = {
            "db": "pubmed",
            "id": pmid,
            "retmode": "xml"
        }

        response = requests.get(PUBMED_FETCH_URL, params=fetch_params, timeout=30)
        response.raise_for_status()

        # 解析 XML
        root = ET.fromstring(response.content)
        article = root.find(".//PubmedArticle")

        if article is None:
            return [TextContent(type="text", text=f"Paper not found: PMID {pmid}")]

        # 提取信息
        output = f"=== Medical Paper Details ===\n\n"
        output += f"PMID: {pmid}\n\n"

        # 标题
        title_elem = article.find(".//ArticleTitle")
        if title_elem is not None:
            output += f"Title: {title_elem.text}\n\n"

        # 作者
        authors = article.findall(".//Author")
        if authors:
            author_list = []
            for author in authors[:10]:
                last_name = author.find("LastName")
                fore_name = author.find("ForeName")
                if last_name is not None and fore_name is not None:
                    author_list.append(f"{fore_name.text} {last_name.text}")
            if author_list:
                output += f"Authors: {', '.join(author_list)}"
                if len(authors) > 10:
                    output += f" et al. ({len(authors)} total)"
                output += "\n\n"

        # 期刊信息
        journal = article.find(".//Journal/Title")
        if journal is not None:
            output += f"Journal: {journal.text}\n"

        # 发表日期
        pub_date = article.find(".//PubDate")
        if pub_date is not None:
            year = pub_date.find("Year")
            month = pub_date.find("Month")
            if year is not None:
                date_str = year.text
                if month is not None:
                    date_str = f"{month.text} {date_str}"
                output += f"Published: {date_str}\n\n"

        # 摘要
        abstract = article.find(".//Abstract/AbstractText")
        if abstract is not None and abstract.text:
            output += f"Abstract:\n{abstract.text}\n\n"

        # DOI
        doi = article.find(".//ArticleId[@IdType='doi']")
        if doi is not None:
            output += f"DOI: {doi.text}\n"

        # PMC ID
        pmc = article.find(".//ArticleId[@IdType='pmc']")
        if pmc is not None:
            output += f"PMC: {pmc.text}\n"

        output += f"\nPubMed URL: https://pubmed.ncbi.nlm.nih.gov/{pmid}/\n"

        return [TextContent(type="text", text=output)]

    except Exception as e:
        logger.error(f"Error getting paper details: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def search_clinical_trials(arguments: dict) -> list[TextContent]:
    """搜索临床试验信息"""
    query = arguments.get("query", "")
    max_results = arguments.get("max_results", 10)

    if not query:
        return [TextContent(type="text", text="Error: Query parameter is required")]

    try:
        # ClinicalTrials.gov API v2
        api_url = "https://clinicaltrials.gov/api/v2/studies"
        params = {
            "query.term": query,
            "pageSize": min(max_results, 100),
            "format": "json"
        }

        response = requests.get(api_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        studies = data.get("studies", [])

        if not studies:
            return [TextContent(type="text", text=f"No clinical trials found for query: {query}")]

        output = f"Found {len(studies)} clinical trials for query: '{query}'\n\n"

        for i, study in enumerate(studies, 1):
            protocol = study.get("protocolSection", {})
            identification = protocol.get("identificationModule", {})
            status = protocol.get("statusModule", {})
            description = protocol.get("descriptionModule", {})

            output += f"--- Trial {i} ---\n"
            output += f"NCT ID: {identification.get('nctId', 'N/A')}\n"
            output += f"Title: {identification.get('briefTitle', 'N/A')}\n"
            output += f"Status: {status.get('overallStatus', 'N/A')}\n"

            brief_summary = description.get("briefSummary", "")
            if brief_summary:
                summary_text = brief_summary[:200] + "..." if len(brief_summary) > 200 else brief_summary
                output += f"Summary: {summary_text}\n"

            nct_id = identification.get('nctId', '')
            if nct_id:
                output += f"URL: https://clinicaltrials.gov/study/{nct_id}\n"

            output += "\n"

        return [TextContent(type="text", text=output)]

    except Exception as e:
        logger.error(f"Error searching clinical trials: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用的医学检索工具"""
    return [
        Tool(
            name="search_pubmed_papers",
            description="Search for medical papers on PubMed by keywords, diseases, treatments, or medical topics",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'diabetes treatment', 'COVID-19 vaccine', 'cancer immunotherapy')"
                    },
                    "max_results": {
                        "type": "number",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10
                    },
                    "sort_by": {
                        "type": "string",
                        "description": "Sort order: 'relevance' or 'date'",
                        "enum": ["relevance", "date"],
                        "default": "relevance"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_pubmed_paper_details",
            description="Get detailed information about a specific PubMed paper by its PMID",
            inputSchema={
                "type": "object",
                "properties": {
                    "pmid": {
                        "type": "string",
                        "description": "PubMed ID (PMID) of the paper (e.g., '12345678')"
                    }
                },
                "required": ["pmid"]
            }
        ),
        Tool(
            name="search_clinical_trials",
            description="Search for clinical trials on ClinicalTrials.gov by disease, treatment, or condition",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'breast cancer', 'Alzheimer disease', 'diabetes type 2')"
                    },
                    "max_results": {
                        "type": "number",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """处理工具调用"""
    try:
        if name == "search_pubmed_papers":
            return await search_pubmed(arguments)
        elif name == "get_pubmed_paper_details":
            return await get_paper_details(arguments)
        elif name == "search_clinical_trials":
            return await search_clinical_trials(arguments)
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
