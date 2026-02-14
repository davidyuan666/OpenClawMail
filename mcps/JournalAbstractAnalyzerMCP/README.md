# Journal Abstract Analyzer MCP

OA期刊文章摘要分析和总结工具的MCP服务器。

## 功能特性

- 从多个OA期刊网站提取文章摘要信息
- 支持的期刊：Nature, Science, PLOS, Frontiers, MDPI, Springer, Wiley, Cell等
- 提取文章标题、作者、摘要、DOI、发布日期等元数据
- 生成Markdown格式的摘要总结
- 支持单篇或多篇文章批量分析

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### 分析单篇文章

```python
analyze_article(
    url="https://www.nature.com/articles/s41598-026-38079-5",
    output_path="article_summary.pdf"  # 可选
)
```

### 分析多篇文章

```python
analyze_multiple_articles(
    urls=[
        "https://www.nature.com/articles/s41598-026-38079-5",
        "https://www.nature.com/articles/s41467-024-12345-6"
    ],
    output_path="articles_summary.pdf"  # 可选
)
```

## 输出格式

工具会生成Markdown文件，包含：
- 文章标题
- 作者列表
- 期刊名称
- 发布日期
- DOI
- 完整摘要

使用document-converter MCP工具可将Markdown转换为PDF。

## 支持的期刊

- Nature系列
- Science系列
- PLOS系列
- Frontiers系列
- MDPI期刊
- Springer Open Access
- Wiley Open Access
- Cell系列
- 其他支持标准meta标签的OA期刊
