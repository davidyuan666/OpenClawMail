# Medical Search MCP Server

医学论文检索 MCP 服务器，提供 PubMed 医学文献和临床试验信息检索功能。

## 功能特性

### 1. PubMed 医学文献检索
- 搜索 3000 万+ 医学文献
- 支持按相关性或日期排序
- 获取论文标题、作者、期刊、发表日期等信息

### 2. 论文详情获取
- 通过 PMID 获取完整论文信息
- 包含摘要、DOI、PMC ID 等详细数据

### 3. 临床试验检索
- 搜索 ClinicalTrials.gov 数据库
- 获取试验状态、NCT ID、简介等信息

## 安装依赖

```bash
pip install mcp requests
```

## 使用方法

### 作为 MCP 服务器运行

```bash
python medical_server.py
```

### 测试功能

```bash
python test_medical.py
```

## API 工具

### search_pubmed_papers
搜索 PubMed 医学文献

参数:
- `query`: 搜索关键词（必需）
- `max_results`: 最大结果数（默认: 10）
- `sort_by`: 排序方式 - "relevance" 或 "date"（默认: "relevance"）

### get_pubmed_paper_details
获取论文详细信息

参数:
- `pmid`: PubMed ID（必需）

### search_clinical_trials
搜索临床试验

参数:
- `query`: 搜索关键词（必需）
- `max_results`: 最大结果数（默认: 10）

## 数据来源

- **PubMed**: 美国国家医学图书馆的免费医学文献数据库
- **ClinicalTrials.gov**: 美国国立卫生研究院的临床试验注册数据库

## 注意事项

- 完全免费，无需 API Key
- 遵守 NCBI E-utilities 使用政策
- 建议合理控制请求频率
