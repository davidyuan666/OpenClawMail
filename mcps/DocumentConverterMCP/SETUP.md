# Document Converter MCP Setup Guide

## Step 1: Install Python Dependencies

```bash
cd mcps/DocumentConverterMCP
pip install -r requirements.txt
```

## Step 2: Install Pandoc

### Windows
Download and install from: https://pandoc.org/installing.html

Or use Chocolatey:
```bash
choco install pandoc
```

### Linux
```bash
sudo apt-get install pandoc
```

### macOS
```bash
brew install pandoc
```

## Step 3: Install TeXLive

### Windows
1. Download TeXLive installer from: https://www.tug.org/texlive/
2. Run the installer (this may take a while)
3. Add TeXLive to PATH:
   - Default path: `C:\texlive\2023\bin\win32`
   - Add to System Environment Variables

### Linux
```bash
sudo apt-get install texlive-full
```

### macOS
```bash
brew install --cask mactex
```

## Step 4: Verify Installation

```bash
# Check Pandoc
pandoc --version

# Check pdflatex
pdflatex --version
```

## Step 5: Configure MCP

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "document-converter": {
      "command": "python",
      "args": [
        "C:/workspace/claudecodelabspace/mcps/DocumentConverterMCP/converter_server.py"
      ]
    }
  }
}
```

## Step 6: Test the Server

```bash
python test_converter.py
```

This will create test files in the `test_output` directory.

## Troubleshooting

### Issue: "Pandoc not found"
- Restart your terminal after installing Pandoc
- Check if Pandoc is in PATH: `where pandoc` (Windows) or `which pandoc` (Linux/macOS)

### Issue: "pdflatex not found"
- Restart your terminal after installing TeXLive
- Check if pdflatex is in PATH: `where pdflatex` (Windows) or `which pdflatex` (Linux/macOS)
- On Windows, manually add TeXLive bin directory to PATH

### Issue: Chinese characters not displaying
- Ensure you have Chinese fonts installed
- For Windows: Microsoft YaHei is used by default
- For Linux: Install `fonts-wqy-microhei` or similar

