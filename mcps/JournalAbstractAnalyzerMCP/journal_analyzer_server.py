#!/usr/bin/env python3
"""
Journal Abstract Analyzer MCP Server
提供OA期刊文章摘要分析和PDF生成能力的 MCP 服务器
支持从Nature、Science等OA期刊提取摘要信息并生成PDF总结
"""
import asyncio
import logging
import re
from typing import Any, List
from mcp.server import Server
from mcp.types import Tool, TextContent
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 MCP 服务器
app = Server("journal-abstract-analyzer")


class JournalArticle:
    """期刊文章数据类"""
    def __init__(self):
        self.title = ""
        self.authors = []
        self.abstract = ""
        self.doi = ""
        self.journal = ""
        self.publication_date = ""
        self.url = ""
        self.keywords = []


def detect_journal(url: str) -> str:
    """检测期刊类型"""
    if "nature.com" in url:
        return "nature"
    elif "science.org" in url or "sciencemag.org" in url:
        return "science"
    elif "plos.org" in url:
        return "plos"
    elif "frontiersin.org" in url:
        return "frontiers"
    elif "mdpi.com" in url:
        return "mdpi"
    elif "springer.com" in url or "springeropen.com" in url:
        return "springer"
    elif "wiley.com" in url:
        return "wiley"
    elif "cell.com" in url:
        return "cell"
    return "unknown"


def extract_nature_article(soup: BeautifulSoup, url: str) -> JournalArticle:
    """提取Nature文章信息"""
    article = JournalArticle()
    article.url = url
    article.journal = "Nature"

    try:
        # 提取标题
        title_tag = soup.find('h1', class_='c-article-title')
        if title_tag:
            article.title = title_tag.get_text(strip=True)

        # 提取作者
        authors_section = soup.find('ul', class_='c-article-author-list')
        if authors_section:
            author_tags = authors_section.find_all('li')
            article.authors = [author.get_text(strip=True) for author in author_tags]

        # 提取摘要
        abstract_section = soup.find('div', id='Abs1-content')
        if not abstract_section:
            abstract_section = soup.find('section', {'data-title': 'Abstract'})
        if abstract_section:
            article.abstract = abstract_section.get_text(strip=True)

        # 提取DOI
        doi_tag = soup.find('span', class_='c-bibliographic-information__value')
        if doi_tag:
            article.doi = doi_tag.get_text(strip=True)

        # 提取发布日期
        date_tag = soup.find('time')
        if date_tag:
            article.publication_date = date_tag.get('datetime', date_tag.get_text(strip=True))

    except Exception as e:
        logger.error(f"Error extracting Nature article: {e}")

    return article


def extract_generic_article(soup: BeautifulSoup, url: str) -> JournalArticle:
    """通用文章信息提取（使用meta标签）"""
    article = JournalArticle()
    article.url = url

    try:
        # 提取标题
        title_meta = soup.find('meta', property='og:title')
        if title_meta:
            article.title = title_meta.get('content', '')
        else:
            title_tag = soup.find('h1')
            if title_tag:
                article.title = title_tag.get_text(strip=True)

        # 提取摘要
        abstract_meta = soup.find('meta', attrs={'name': 'description'})
        if abstract_meta:
            article.abstract = abstract_meta.get('content', '')

        # 尝试从页面中提取更完整的摘要
        abstract_keywords = ['abstract', 'summary', 'Abstract', 'Summary']
        for keyword in abstract_keywords:
            abstract_section = soup.find(['div', 'section', 'p'], class_=re.compile(keyword, re.I))
            if abstract_section:
                text = abstract_section.get_text(strip=True)
                if len(text) > len(article.abstract):
                    article.abstract = text
                break

        # 提取DOI
        doi_meta = soup.find('meta', attrs={'name': 'citation_doi'})
        if doi_meta:
            article.doi = doi_meta.get('content', '')

        # 提取作者
        author_metas = soup.find_all('meta', attrs={'name': 'citation_author'})
        article.authors = [meta.get('content', '') for meta in author_metas]

        # 提取发布日期
        date_meta = soup.find('meta', attrs={'name': 'citation_publication_date'})
        if date_meta:
            article.publication_date = date_meta.get('content', '')

        # 提取期刊名
        journal_meta = soup.find('meta', attrs={'name': 'citation_journal_title'})
        if journal_meta:
            article.journal = journal_meta.get('content', '')

    except Exception as e:
        logger.error(f"Error extracting generic article: {e}")

    return article


def fetch_article_info(url: str) -> JournalArticle:
    """从URL获取文章信息"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        journal_type = detect_journal(url)

        if journal_type == "nature":
            return extract_nature_article(soup, url)
        else:
            return extract_generic_article(soup, url)

    except Exception as e:
        logger.error(f"Error fetching article from {url}: {e}")
        article = JournalArticle()
        article.url = url
        return article


def generate_markdown_summary(articles: List[JournalArticle]) -> str:
    """生成Markdown格式的摘要总结"""
    md_content = f"# Journal Articles Abstract Summary\n\n"
    md_content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md_content += f"Total Articles: {len(articles)}\n\n"
    md_content += "---\n\n"

    for i, article in enumerate(articles, 1):
        md_content += f"## Article {i}: {article.title or 'Untitled'}\n\n"

        if article.authors:
            md_content += f"**Authors:** {', '.join(article.authors[:5])}"
            if len(article.authors) > 5:
                md_content += f" et al. ({len(article.authors)} authors total)"
            md_content += "\n\n"

        if article.journal:
            md_content += f"**Journal:** {article.journal}\n\n"

        if article.publication_date:
            md_content += f"**Publication Date:** {article.publication_date}\n\n"

        if article.doi:
            md_content += f"**DOI:** {article.doi}\n\n"

        md_content += f"**URL:** {article.url}\n\n"

        if article.abstract:
            md_content += f"### Abstract\n\n{article.abstract}\n\n"
        else:
            md_content += f"### Abstract\n\n*Abstract not available*\n\n"

        md_content += "---\n\n"

    return md_content


async def analyze_single_article(arguments: dict) -> list[TextContent]:
    """分析单篇文章并生成markdown摘要"""
    url = arguments.get("url", "")
    output_path = arguments.get("output_path", "")

    if not url:
        return [TextContent(type="text", text="Error: URL parameter is required")]

    if not output_path:
        output_path = f"journal_abstract_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    elif not output_path.endswith('.md'):
        output_path = output_path.replace('.pdf', '.md')

    try:
        article = fetch_article_info(url)

        if not article.title and not article.abstract:
            return [TextContent(type="text", text=f"Error: Could not extract article information from {url}")]

        markdown_content = generate_markdown_summary([article])

        # 保存markdown文件
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        output = f"=== Article Analysis Complete ===\n\n"
        output += f"Title: {article.title}\n"
        output += f"Journal: {article.journal or 'Unknown'}\n"
        output += f"Authors: {', '.join(article.authors[:3]) if article.authors else 'Unknown'}"
        if len(article.authors) > 3:
            output += f" et al."
        output += f"\n\nAbstract extracted successfully ({len(article.abstract)} characters).\n"
        output += f"\nMarkdown saved to: {output_path}\n"
        output += f"\nTo convert to PDF, use: document-converter tool with this markdown file.\n"

        return [TextContent(type="text", text=output)]

    except Exception as e:
        logger.error(f"Error analyzing article: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def analyze_multiple_articles(arguments: dict) -> list[TextContent]:
    """分析多篇文章并生成markdown摘要"""
    urls = arguments.get("urls", [])
    output_path = arguments.get("output_path", "")

    if not urls:
        return [TextContent(type="text", text="Error: URLs parameter is required")]

    if isinstance(urls, str):
        urls = [u.strip() for u in urls.split(',')]

    if not output_path:
        output_path = f"journal_abstracts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    elif not output_path.endswith('.md'):
        output_path = output_path.replace('.pdf', '.md')

    try:
        articles = []
        failed_urls = []

        for url in urls:
            article = fetch_article_info(url.strip())
            if article.title or article.abstract:
                articles.append(article)
            else:
                failed_urls.append(url)

        if not articles:
            return [TextContent(type="text", text="Error: Could not extract information from any of the provided URLs")]

        markdown_content = generate_markdown_summary(articles)

        # 保存markdown文件
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        output = f"=== Multiple Articles Analysis Complete ===\n\n"
        output += f"Successfully analyzed: {len(articles)} articles\n"
        if failed_urls:
            output += f"Failed to analyze: {len(failed_urls)} URLs\n"
            output += f"Failed URLs: {', '.join(failed_urls[:3])}\n"

        output += f"\nArticles:\n"
        for i, article in enumerate(articles, 1):
            title = article.title[:80] if len(article.title) > 80 else article.title
            output += f"{i}. {title}\n"

        output += f"\nMarkdown saved to: {output_path}\n"
        output += f"To convert to PDF, use: document-converter tool with this markdown file.\n"

        return [TextContent(type="text", text=output)]

    except Exception as e:
        logger.error(f"Error analyzing multiple articles: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用的期刊摘要分析工具"""
    return [
        Tool(
            name="analyze_article",
            description="Analyze a single OA journal article, extract abstract and metadata, generate markdown summary",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Article URL (supports Nature, Science, PLOS, Frontiers, MDPI, Springer, etc.)"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Output file path (optional, default: journal_abstract_YYYYMMDD_HHMMSS.pdf)",
                        "default": ""
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="analyze_multiple_articles",
            description="Analyze multiple OA journal articles, extract abstracts and metadata, generate combined markdown summary",
            inputSchema={
                "type": "object",
                "properties": {
                    "urls": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of article URLs or comma-separated string"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Output file path (optional, default: journal_abstracts_YYYYMMDD_HHMMSS.pdf)",
                        "default": ""
                    }
                },
                "required": ["urls"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """处理工具调用"""
    try:
        if name == "analyze_article":
            return await analyze_single_article(arguments)
        elif name == "analyze_multiple_articles":
            return await analyze_multiple_articles(arguments)
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


