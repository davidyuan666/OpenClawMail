# Document Converter MCP

An MCP server that converts Word/PDF documents to clean Markdown format.

**Design Philosophy**: This MCP focuses purely on data extraction and conversion. All analysis logic is handled in the Skill layer.

## Features

- **Document Conversion**: Convert Word (.docx) and PDF (.pdf) files to clean Markdown format
- **Pure Data Extraction**: No analysis or processing logic - just clean data

## Installation

```bash
pip install -r requirements.txt
```

### Additional Requirements

- **Pandoc**: Required for Word document conversion
  - Windows: Download from https://pandoc.org/installing.html
  - macOS: `brew install pandoc`
  - Linux: `sudo apt-get install pandoc`

## Tools

### convert_document_to_markdown

Convert Word or PDF documents to clean Markdown format.

**Parameters:**
- `file_path` (string, required): Absolute path to the Word or PDF file

**Returns:**
- Clean Markdown text content

**Example:**
```json
{
  "file_path": "/path/to/document.pdf"
}
```

## Usage with Claude Code

Add to your `.clauderc` configuration:

```json
{
  "mcpServers": {
    "document-reviewer": {
      "command": "python",
      "args": ["C:/workspace/claudecodelabspace/mcps/DocumentReviewerMCP/reviewer_server.py"]
    }
  }
}
```

## Architecture

This MCP follows the principle of separation of concerns:
- **MCP Layer**: Pure data extraction and conversion
- **Skill Layer**: All analysis, review logic, and report generation

This design keeps the MCP simple, maintainable, and reusable.

## License

MIT
