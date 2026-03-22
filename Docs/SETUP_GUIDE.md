# Setup Guide

Complete setup guide for the XBRL Document Conversion Agent.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Steps](#installation-steps)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 2GB RAM minimum (4GB recommended)
- **Disk Space**: 500MB for dependencies and data

### Recommended Setup

- **Python**: 3.10 or higher
- **Memory**: 8GB RAM
- **Disk Space**: 2GB for larger XBRL files

## Installation Steps

### Step 1: Install Python

Verify Python installation:

```bash
python --version
# or
python3 --version
```

If Python is not installed, download from [python.org](https://www.python.org/downloads/).

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv xbrl-env

# Activate on macOS/Linux
source xbrl-env/bin/activate

# Activate on Windows
xbrl-env\Scripts\activate
```

### Step 3: Install Dependencies

#### Option A: Install from requirements.txt

```bash
pip install -r requirements.txt
```

#### Option B: Install individually

```bash
# Core XBRL conversion
pip install docling[xbrl]

# MCP server support (optional)
pip install mcp
```

### Step 4: Verify Installation

```bash
python -c "import docling; print('Docling installed successfully')"
python -c "import mcp; print('MCP installed successfully')"
```

## Configuration

### Directory Structure

Create the following directory structure:

```
xbrl-conversion-agent/
├── xbrl_agent.py           # Main agent code
├── xbrl_mcp_server.py      # MCP server
├── requirements.txt        # Dependencies
├── examples/
│   └── basic_usage.py      # Example scripts
├── Docs/
│   ├── README.md           # Main documentation
│   ├── API_REFERENCE.md    # API docs
│   ├── MCP_SERVER.md       # MCP docs
│   └── SETUP_GUIDE.md      # This file
├── _data/
│   └── xbrl/               # Sample XBRL files
│       ├── mlac-20251231.xml
│       ├── mlac-taxonomy/
│       │   ├── mlac-20251231.xsd
│       │   ├── mlac-20251231_cal.xml
│       │   ├── mlac-20251231_def.xml
│       │   ├── mlac-20251231_lab.xml
│       │   ├── mlac-20251231_pre.xml
│       │   └── taxonomy_package.zip
│       └── grve-taxonomy/
└── output/                 # Output directory (auto-created)
```

### Taxonomy Setup

1. **Obtain Taxonomy Files**:
   - Download from SEC EDGAR or other sources
   - Ensure you have: .xsd, _cal.xml, _def.xml, _lab.xml, _pre.xml files

2. **Create Taxonomy Package** (for offline use):
   - Zip all taxonomy files
   - Name it `taxonomy_package.zip`
   - Place in taxonomy directory

### Environment Variables (Optional)

```bash
# Set default output directory
export XBRL_OUTPUT_DIR="./output"

# Set default taxonomy directory
export XBRL_TAXONOMY_DIR="./_data/xbrl/mlac-taxonomy"
```

## Verification

### Test 1: Basic Agent Creation

```python
from pathlib import Path
from xbrl_agent import create_agent_from_taxonomy

agent = create_agent_from_taxonomy(
    taxonomy_dir=Path("./_data/xbrl/mlac-taxonomy"),
    taxonomy_package=Path("./_data/xbrl/mlac-taxonomy/taxonomy_package.zip")
)
print("✓ Agent created successfully")
```

### Test 2: Document Conversion

```python
result = agent.process_xbrl_file("./_data/xbrl/mlac-20251231.xml")
print(f"✓ Conversion status: {result['conversion_status']}")
print(f"✓ Document name: {result['document_name']}")
```

### Test 3: MCP Server

```bash
# Start server
python xbrl_mcp_server.py

# Should see: "XBRL MCP Server running on stdio"
# Press Ctrl+C to stop
```

### Test 4: Run Examples

```bash
cd examples
python basic_usage.py
```

Expected output:
```
====================================================
XBRL Document Conversion - Usage Examples
====================================================

Example 1: Basic XBRL Conversion
====================================================
✓ Conversion Status: SUCCESS
✓ Document Name: mlac-20251231
...
```

## Troubleshooting

### Issue: Import Error for docling

**Error**:
```
ImportError: No module named 'docling'
```

**Solution**:
```bash
pip install docling[xbrl]
```

### Issue: Import Error for mcp

**Error**:
```
ImportError: No module named 'mcp'
```

**Solution**:
```bash
pip install mcp
```

### Issue: Taxonomy Files Not Found

**Error**:
```
FileNotFoundError: Taxonomy files not found
```

**Solution**:
1. Verify taxonomy directory path
2. Check that all required files exist:
   - .xsd file
   - _cal.xml, _def.xml, _lab.xml, _pre.xml files
3. Use absolute paths if relative paths fail

### Issue: Conversion Fails

**Error**:
```
ValueError: Conversion failed with status: FAILURE
```

**Solutions**:
1. **Check XBRL file validity**:
   ```bash
   # Verify XML is well-formed
   xmllint --noout your-file.xml
   ```

2. **Verify taxonomy matches**:
   - Ensure taxonomy version matches XBRL instance
   - Check schemaRef in XBRL file

3. **Enable remote fetch** (if taxonomy incomplete):
   ```python
   agent = create_agent_from_taxonomy(
       taxonomy_dir=Path("./taxonomy"),
       enable_remote_fetch=True  # Allow remote fetching
   )
   ```

### Issue: Permission Denied

**Error**:
```
PermissionError: [Errno 13] Permission denied: 'output/file.md'
```

**Solution**:
```bash
# Create output directory with proper permissions
mkdir -p output
chmod 755 output
```

### Issue: Memory Error

**Error**:
```
MemoryError: Unable to allocate memory
```

**Solutions**:
1. Process smaller XBRL files
2. Increase system memory
3. Use analyze=False to reduce memory usage:
   ```python
   result = agent.process_xbrl_file(
       "large-file.xml",
       analyze=False  # Skip analysis
   )
   ```

### Issue: MCP Server Not Responding

**Symptoms**:
- Server starts but tools don't appear
- Client can't connect

**Solutions**:
1. **Check server logs**:
   ```bash
   python xbrl_mcp_server.py 2>&1 | tee server.log
   ```

2. **Verify MCP client configuration**:
   - Use absolute paths
   - Check JSON syntax
   - Restart MCP client

3. **Test server directly**:
   ```python
   import asyncio
   from xbrl_mcp_server import XBRLMCPServer
   
   async def test():
       server = XBRLMCPServer()
       print("Server created successfully")
   
   asyncio.run(test())
   ```

## Advanced Configuration

### Custom Output Directory

```python
from xbrl_agent import XBRLConversionConfig, XBRLConversionAgent

config = XBRLConversionConfig(
    taxonomy_dir=Path("./taxonomy"),
    output_dir=Path("/custom/output/path"),
    export_formats=["markdown", "json", "html"]
)

agent = XBRLConversionAgent(config)
```

### Enable Remote Taxonomy Fetching

```python
config = XBRLConversionConfig(
    enable_local_fetch=True,
    enable_remote_fetch=True,  # Enable remote fetching
    taxonomy_dir=Path("./taxonomy")
)
```

### Logging Configuration

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('xbrl_agent.log'),
        logging.StreamHandler()
    ]
)
```

## Next Steps

After successful setup:

1. **Read Documentation**:
   - [README.md](./README.md) - Overview and quick start
   - [API_REFERENCE.md](./API_REFERENCE.md) - Complete API docs
   - [MCP_SERVER.md](./MCP_SERVER.md) - MCP server guide

2. **Try Examples**:
   - Run `examples/basic_usage.py`
   - Modify examples for your use case

3. **Process Your Data**:
   - Prepare your XBRL files
   - Configure taxonomy
   - Run conversions

4. **Integrate with Tools**:
   - Set up MCP server
   - Configure AI assistant
   - Automate workflows

## Support

For issues and questions:

1. Check [Troubleshooting](#troubleshooting) section
2. Review [API Reference](./API_REFERENCE.md)
3. Check Docling documentation
4. Review XBRL specifications

## Updates

To update dependencies:

```bash
pip install --upgrade docling[xbrl] mcp
```

To verify versions:

```bash
pip show docling mcp