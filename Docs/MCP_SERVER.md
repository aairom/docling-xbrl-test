# MCP Server Documentation

Complete documentation for the XBRL MCP (Model Context Protocol) Server.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Configuration](#configuration)
- [Available Tools](#available-tools)
- [Usage Examples](#usage-examples)
- [Integration Guide](#integration-guide)

## Overview

The XBRL MCP Server exposes XBRL conversion capabilities through the Model Context Protocol, allowing AI assistants and other MCP clients to convert and analyze XBRL documents.

### Features

- 6 specialized tools for XBRL processing
- Stateful agent management
- JSON-based request/response format
- Async operation support
- Comprehensive error handling

## Installation

### Prerequisites

```bash
pip install mcp docling[xbrl]
```

### Verify Installation

```bash
python xbrl_mcp_server.py --help
```

## Configuration

### MCP Client Configuration

#### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "xbrl": {
      "command": "python",
      "args": ["/absolute/path/to/xbrl_mcp_server.py"]
    }
  }
}
```

#### Other MCP Clients

Configure according to your client's documentation, using:
- **Command**: `python`
- **Args**: `["/path/to/xbrl_mcp_server.py"]`
- **Transport**: stdio

### Starting the Server

```bash
# Run directly
python xbrl_mcp_server.py

# Or with logging
python xbrl_mcp_server.py 2>&1 | tee server.log
```

## Available Tools

### 1. xbrl_create_agent

Create an XBRL conversion agent with taxonomy configuration.

**Purpose**: Initialize an agent before performing any XBRL operations.

**Input Schema**:
```json
{
  "agent_id": "string (required)",
  "taxonomy_dir": "string (required)",
  "taxonomy_package": "string (optional)",
  "output_dir": "string (optional, default: ./output)",
  "enable_remote_fetch": "boolean (optional, default: false)"
}
```

**Example Request**:
```json
{
  "agent_id": "mlac_agent",
  "taxonomy_dir": "./_data/xbrl/mlac-taxonomy",
  "taxonomy_package": "./_data/xbrl/mlac-taxonomy/taxonomy_package.zip",
  "output_dir": "./output",
  "enable_remote_fetch": false
}
```

**Example Response**:
```json
{
  "status": "success",
  "agent_id": "mlac_agent",
  "message": "XBRL agent 'mlac_agent' created successfully",
  "config": {
    "taxonomy_dir": "./_data/xbrl/mlac-taxonomy",
    "output_dir": "./output",
    "enable_remote_fetch": false
  }
}
```

### 2. xbrl_convert_document

Convert an XBRL instance document to structured format.

**Purpose**: Parse and convert XBRL documents with full analysis.

**Input Schema**:
```json
{
  "agent_id": "string (required)",
  "xbrl_path": "string (required)",
  "output_base_name": "string (optional)",
  "analyze": "boolean (optional, default: true)"
}
```

**Example Request**:
```json
{
  "agent_id": "mlac_agent",
  "xbrl_path": "./_data/xbrl/mlac-20251231.xml",
  "output_base_name": "mlac_report",
  "analyze": true
}
```

**Example Response**:
```json
{
  "input_file": "./_data/xbrl/mlac-20251231.xml",
  "document_name": "mlac-20251231",
  "conversion_status": "SUCCESS",
  "structure": {
    "TextItem": 267,
    "TableItem": 23,
    "TitleItem": 1,
    "KeyValueItem": 1
  },
  "key_value_pairs": [
    {
      "key": "EntityPublicFloat",
      "value": "239160600",
      "type": "key_value_region"
    }
  ],
  "sample_text": [
    "We are a special purpose acquisition company...",
    "We depend on digital technologies..."
  ],
  "output_files": {
    "markdown": "output/mlac_report.md",
    "json": "output/mlac_report.json"
  }
}
```

### 3. xbrl_analyze_structure

Analyze the structure of an XBRL document.

**Purpose**: Get document structure without full conversion.

**Input Schema**:
```json
{
  "agent_id": "string (required)",
  "xbrl_path": "string (required)"
}
```

**Example Request**:
```json
{
  "agent_id": "mlac_agent",
  "xbrl_path": "./_data/xbrl/mlac-20251231.xml"
}
```

**Example Response**:
```json
{
  "status": "success",
  "document_name": "mlac-20251231",
  "structure": {
    "TextItem": 267,
    "TableItem": 23,
    "TitleItem": 1,
    "KeyValueItem": 1
  },
  "total_items": 292
}
```

### 4. xbrl_extract_key_values

Extract numeric facts from XBRL document.

**Purpose**: Get all XBRL facts with their values.

**Input Schema**:
```json
{
  "agent_id": "string (required)",
  "xbrl_path": "string (required)",
  "max_items": "integer (optional, default: 100)"
}
```

**Example Request**:
```json
{
  "agent_id": "mlac_agent",
  "xbrl_path": "./_data/xbrl/mlac-20251231.xml",
  "max_items": 50
}
```

**Example Response**:
```json
{
  "status": "success",
  "document_name": "mlac-20251231",
  "key_value_pairs": [
    {
      "key": "EntityPublicFloat",
      "value": "239160600",
      "type": "key_value_region"
    },
    {
      "key": "Cash",
      "value": "452680",
      "type": "key_value_region"
    }
  ],
  "count": 50
}
```

### 5. xbrl_extract_text

Extract text content from XBRL document.

**Purpose**: Get narrative text blocks from XBRL.

**Input Schema**:
```json
{
  "agent_id": "string (required)",
  "xbrl_path": "string (required)",
  "max_items": "integer (optional, default: 10)"
}
```

**Example Request**:
```json
{
  "agent_id": "mlac_agent",
  "xbrl_path": "./_data/xbrl/mlac-20251231.xml",
  "max_items": 5
}
```

**Example Response**:
```json
{
  "status": "success",
  "document_name": "mlac-20251231",
  "text_items": [
    "We are a special purpose acquisition company with no business operations...",
    "We depend on digital technologies, including information systems..."
  ],
  "count": 5
}
```

### 6. xbrl_export_document

Export XBRL document to specified formats.

**Purpose**: Export converted document to multiple formats.

**Input Schema**:
```json
{
  "agent_id": "string (required)",
  "xbrl_path": "string (required)",
  "output_base_name": "string (required)",
  "formats": "array of strings (optional, default: ['markdown', 'json'])"
}
```

**Example Request**:
```json
{
  "agent_id": "mlac_agent",
  "xbrl_path": "./_data/xbrl/mlac-20251231.xml",
  "output_base_name": "mlac_final",
  "formats": ["markdown", "json", "html"]
}
```

**Example Response**:
```json
{
  "status": "success",
  "document_name": "mlac-20251231",
  "output_files": {
    "markdown": "output/mlac_final.md",
    "json": "output/mlac_final.json",
    "html": "output/mlac_final.html"
  }
}
```

## Usage Examples

### Example 1: Basic Workflow

```
User: Create an XBRL agent for the MLAC taxonomy and convert the document

Assistant uses:
1. xbrl_create_agent with taxonomy configuration
2. xbrl_convert_document to process the file
3. Returns structured results
```

### Example 2: Analysis Only

```
User: Analyze the structure of mlac-20251231.xml

Assistant uses:
1. xbrl_create_agent (if not already created)
2. xbrl_analyze_structure to get document structure
3. Returns item counts
```

### Example 3: Extract Specific Data

```
User: Extract all numeric facts from the XBRL document

Assistant uses:
1. xbrl_create_agent (if not already created)
2. xbrl_extract_key_values with appropriate max_items
3. Returns all facts
```

### Example 4: Multi-Format Export

```
User: Convert the document and export to all formats

Assistant uses:
1. xbrl_create_agent
2. xbrl_export_document with formats=["markdown", "json", "html"]
3. Returns paths to all exported files
```

## Integration Guide

### With Claude Desktop

1. **Install Dependencies**:
```bash
pip install mcp docling[xbrl]
```

2. **Configure Claude**:
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "xbrl": {
      "command": "python",
      "args": ["/Users/username/path/to/xbrl_mcp_server.py"]
    }
  }
}
```

3. **Restart Claude Desktop**

4. **Test Integration**:
```
User: List available MCP tools
Claude: [Shows xbrl tools]

User: Create an XBRL agent and convert mlac-20251231.xml
Claude: [Uses xbrl_create_agent and xbrl_convert_document]
```

### With Custom MCP Clients

```python
import asyncio
from mcp.client import Client

async def use_xbrl_server():
    async with Client() as client:
        # Connect to server
        await client.connect_stdio(
            command="python",
            args=["xbrl_mcp_server.py"]
        )
        
        # List tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")
        
        # Create agent
        result = await client.call_tool(
            "xbrl_create_agent",
            {
                "agent_id": "test_agent",
                "taxonomy_dir": "./taxonomy"
            }
        )
        print(result)

asyncio.run(use_xbrl_server())
```

## Error Handling

### Common Errors

**Agent Not Found**:
```json
{
  "status": "error",
  "message": "Agent 'agent_id' not found. Create it first with xbrl_create_agent."
}
```
**Solution**: Create agent before using other tools.

**File Not Found**:
```json
{
  "status": "error",
  "message": "XBRL file not found: /path/to/file.xml"
}
```
**Solution**: Check file path is correct and accessible.

**Conversion Failed**:
```json
{
  "status": "error",
  "message": "Conversion failed with status: FAILURE"
}
```
**Solution**: Check taxonomy configuration and XBRL file validity.

## Best Practices

1. **Agent Management**:
   - Create one agent per taxonomy
   - Reuse agents for multiple documents with same taxonomy
   - Use descriptive agent_id names

2. **Performance**:
   - Set appropriate max_items for large documents
   - Use analyze=False when structure analysis not needed
   - Export only required formats

3. **Error Handling**:
   - Always check response status
   - Handle agent creation errors gracefully
   - Validate file paths before processing

4. **Security**:
   - Use absolute paths for production
   - Validate input paths
   - Restrict output directories

## Troubleshooting

### Server Won't Start

**Check**:
- Python version (3.8+)
- Dependencies installed
- No port conflicts

**Solution**:
```bash
python -c "import mcp; import docling; print('OK')"
```

### Tools Not Appearing

**Check**:
- MCP client configuration
- Server path is absolute
- Client restarted after config change

### Conversion Errors

**Check**:
- Taxonomy files present
- XBRL file valid
- Sufficient disk space

**Debug**:
```bash
python xbrl_mcp_server.py 2>&1 | tee debug.log
```

## Additional Resources

- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Docling Documentation](https://github.com/docling-project/docling)
- [XBRL Specification](https://www.xbrl.org)