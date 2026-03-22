# XBRL Document Conversion Agent

A comprehensive Python agent for converting XBRL (eXtensible Business Reporting Language) documents using Docling, with support for offline processing, taxonomy validation, and multiple export formats.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Usage Examples](#usage-examples)
- [MCP Server](#mcp-server)
- [Troubleshooting](#troubleshooting)

## Overview

XBRL is a standard XML-based format used globally by companies, regulators, and financial institutions for exchanging business and financial information in a structured, machine-readable format. It's widely adopted for regulatory filings (e.g., SEC filings in the US).

This project provides:

1. **XBRL Conversion Agent** - A Python library for converting XBRL documents
2. **MCP Server** - Model Context Protocol server for AI assistant integration
3. **Example Scripts** - Ready-to-use examples for common use cases

## Features

### Core Capabilities

- ✅ **Offline XBRL Processing** - Parse XBRL documents completely offline
- ✅ **Taxonomy Support** - Local and remote taxonomy validation
- ✅ **Structured Extraction** - Extract metadata, text blocks, and numeric facts
- ✅ **Multiple Export Formats** - Markdown, JSON, HTML, and plain text
- ✅ **Batch Processing** - Process multiple XBRL files efficiently
- ✅ **MCP Integration** - Use as an MCP server for AI assistants

### Technical Features

- **Type-safe** - Full type hints for better IDE support
- **Configurable** - Flexible configuration system
- **Well-documented** - Comprehensive documentation and examples
- **Error handling** - Robust error handling and logging
- **Extensible** - Easy to extend with custom functionality

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Basic Installation

```bash
# Install the XBRL conversion agent
pip install docling[xbrl]
```

### MCP Server Installation

```bash
# Install MCP dependencies
pip install mcp docling[xbrl]
```

### Development Installation

```bash
# Clone the repository
git clone <repository-url>
cd xbrl-conversion-agent

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from pathlib import Path
from xbrl_agent import create_agent_from_taxonomy

# Create an agent with taxonomy configuration
agent = create_agent_from_taxonomy(
    taxonomy_dir=Path("./_data/xbrl/mlac-taxonomy"),
    taxonomy_package=Path("./_data/xbrl/mlac-taxonomy/taxonomy_package.zip"),
    output_dir=Path("./output")
)

# Convert an XBRL document
result = agent.process_xbrl_file("./_data/xbrl/mlac-20251231.xml")

# Access the results
print(f"Document: {result['document_name']}")
print(f"Status: {result['conversion_status']}")
print(f"Output files: {result['output_files']}")
```

### Using the MCP Server

1. **Configure MCP Client** (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "xbrl": {
      "command": "python",
      "args": ["/path/to/xbrl_mcp_server.py"]
    }
  }
}
```

2. **Use in AI Assistant**:

```
Create an XBRL agent and convert the document mlac-20251231.xml
```


### Using the Web UI

For a graphical interface:

```bash
# Install Flask
pip install flask

# Start the web UI
python examples/web_ui.py

# Open http://localhost:5000 in your browser
```

The web UI provides an intuitive interface for:
- Uploading XBRL files
- Configuring taxonomy settings
- Viewing conversion results
- Downloading exported files

The MCP server will handle the conversion and return structured results.

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    XBRL Conversion System                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐      ┌──────────────────┐             │
│  │  XBRL Agent     │◄─────┤  Configuration   │             │
│  │  (xbrl_agent.py)│      │  (Config class)  │             │
│  └────────┬────────┘      └──────────────────┘             │
│           │                                                  │
│           │ uses                                             │
│           ▼                                                  │
│  ┌─────────────────┐      ┌──────────────────┐             │
│  │ Docling Library │◄─────┤ XBRL Backend     │             │
│  │ (DocumentConv.) │      │ (XbrlBackend)    │             │
│  └─────────────────┘      └──────────────────┘             │
│           │                                                  │
│           │ produces                                         │
│           ▼                                                  │
│  ┌─────────────────┐                                        │
│  │ DoclingDocument │                                        │
│  │ (Structured)    │                                        │
│  └────────┬────────┘                                        │
│           │                                                  │
│           │ exports to                                       │
│           ▼                                                  │
│  ┌─────────────────────────────────────┐                   │
│  │  Output Formats                     │                   │
│  │  • Markdown  • JSON  • HTML         │                   │
│  └─────────────────────────────────────┘                   │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│                      MCP Server Layer                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  xbrl_mcp_server.py                                 │   │
│  │  • Tool Registration                                │   │
│  │  • Request Handling                                 │   │
│  │  • Response Formatting                              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Input**: XBRL instance document (.xml) + Taxonomy files
2. **Processing**: 
   - Parse XBRL structure
   - Validate against taxonomy
   - Extract facts, contexts, and text blocks
3. **Transformation**: Convert to DoclingDocument format
4. **Output**: Export to desired formats (Markdown, JSON, HTML)

## Usage Examples

See the `examples/basic_usage.py` file for comprehensive examples including:

- Basic XBRL document conversion
- Custom configuration
- Step-by-step conversion with detailed analysis
- Batch processing multiple files

For detailed API documentation, see [API_REFERENCE.md](./API_REFERENCE.md).

## MCP Server

The MCP server provides 6 tools for XBRL conversion:

1. **xbrl_create_agent** - Create conversion agent with taxonomy
2. **xbrl_convert_document** - Convert XBRL document
3. **xbrl_analyze_structure** - Analyze document structure
4. **xbrl_extract_key_values** - Extract numeric facts
5. **xbrl_extract_text** - Extract text content
6. **xbrl_export_document** - Export to formats

For detailed MCP documentation, see [MCP_SERVER.md](./MCP_SERVER.md).

## Troubleshooting

### Common Issues

**Issue**: `ImportError: No module named 'docling'`
- **Solution**: Install Docling with `pip install docling[xbrl]`

**Issue**: `FileNotFoundError: Taxonomy files not found`
- **Solution**: Ensure taxonomy_dir points to correct directory with .xsd and linkbase files

**Issue**: Conversion fails with validation errors
- **Solution**: Check that taxonomy package matches the XBRL instance document version

**Issue**: MCP server not responding
- **Solution**: Check server logs and ensure MCP library is installed

For more help, see [TROUBLESHOOTING.md](./TROUBLESHOOTING.md).

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.