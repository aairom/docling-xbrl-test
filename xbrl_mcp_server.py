#!/usr/bin/env python3
"""
XBRL MCP Server

Model Context Protocol (MCP) server for XBRL document conversion.
This server exposes XBRL conversion capabilities as MCP tools that can be
used by AI assistants and other MCP clients.

Usage:
    python xbrl_mcp_server.py

Or as an MCP server in your MCP configuration:
    {
      "mcpServers": {
        "xbrl": {
          "command": "python",
          "args": ["/path/to/xbrl_mcp_server.py"]
        }
      }
    }
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP library not available. Install with: pip install mcp")

from xbrl_agent import (
    XBRLConversionAgent,
    XBRLConversionConfig,
    create_agent_from_taxonomy,
    DOCLING_AVAILABLE
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class XBRLMCPServer:
    """
    MCP Server for XBRL document conversion.
    
    Provides tools for:
    - Converting XBRL documents
    - Analyzing XBRL structure
    - Extracting data from XBRL
    - Exporting to various formats
    """
    
    def __init__(self):
        """Initialize the XBRL MCP server."""
        if not MCP_AVAILABLE:
            raise ImportError("MCP library required. Install with: pip install mcp")
        
        if not DOCLING_AVAILABLE:
            raise ImportError("Docling library required. Install with: pip install docling[xbrl]")
        
        self.server = Server("xbrl-converter")
        self.agents: Dict[str, XBRLConversionAgent] = {}
        self._setup_tools()
        logger.info("XBRL MCP Server initialized")
    
    def _setup_tools(self):
        """Register all MCP tools."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available XBRL conversion tools."""
            return [
                Tool(
                    name="xbrl_create_agent",
                    description=(
                        "Create an XBRL conversion agent with taxonomy configuration. "
                        "This must be called before using other XBRL tools. "
                        "Returns an agent_id to use in subsequent calls."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {
                                "type": "string",
                                "description": "Unique identifier for this agent"
                            },
                            "taxonomy_dir": {
                                "type": "string",
                                "description": "Path to directory containing taxonomy files"
                            },
                            "taxonomy_package": {
                                "type": "string",
                                "description": "Optional path to taxonomy package ZIP file"
                            },
                            "output_dir": {
                                "type": "string",
                                "description": "Directory for output files (default: ./output)",
                                "default": "./output"
                            },
                            "enable_remote_fetch": {
                                "type": "boolean",
                                "description": "Allow fetching taxonomy from remote URLs",
                                "default": False
                            }
                        },
                        "required": ["agent_id", "taxonomy_dir"]
                    }
                ),
                Tool(
                    name="xbrl_convert_document",
                    description=(
                        "Convert an XBRL instance document to DoclingDocument format. "
                        "Parses the XBRL file, validates against taxonomy, and extracts "
                        "metadata, text blocks, and numeric facts."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {
                                "type": "string",
                                "description": "Agent ID from xbrl_create_agent"
                            },
                            "xbrl_path": {
                                "type": "string",
                                "description": "Path to XBRL instance document (.xml file)"
                            },
                            "output_base_name": {
                                "type": "string",
                                "description": "Base name for output files (optional)"
                            },
                            "analyze": {
                                "type": "boolean",
                                "description": "Perform structure analysis",
                                "default": True
                            }
                        },
                        "required": ["agent_id", "xbrl_path"]
                    }
                ),
                Tool(
                    name="xbrl_analyze_structure",
                    description=(
                        "Analyze the structure of a converted XBRL document. "
                        "Returns counts of different item types (text, tables, etc.)."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {
                                "type": "string",
                                "description": "Agent ID from xbrl_create_agent"
                            },
                            "xbrl_path": {
                                "type": "string",
                                "description": "Path to XBRL instance document"
                            }
                        },
                        "required": ["agent_id", "xbrl_path"]
                    }
                ),
                Tool(
                    name="xbrl_extract_key_values",
                    description=(
                        "Extract numeric facts as key-value pairs from XBRL document. "
                        "Returns all XBRL facts with their values and metadata."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {
                                "type": "string",
                                "description": "Agent ID from xbrl_create_agent"
                            },
                            "xbrl_path": {
                                "type": "string",
                                "description": "Path to XBRL instance document"
                            },
                            "max_items": {
                                "type": "integer",
                                "description": "Maximum number of items to return",
                                "default": 100
                            }
                        },
                        "required": ["agent_id", "xbrl_path"]
                    }
                ),
                Tool(
                    name="xbrl_extract_text",
                    description=(
                        "Extract text content from XBRL document. "
                        "Returns text blocks and narrative content."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {
                                "type": "string",
                                "description": "Agent ID from xbrl_create_agent"
                            },
                            "xbrl_path": {
                                "type": "string",
                                "description": "Path to XBRL instance document"
                            },
                            "max_items": {
                                "type": "integer",
                                "description": "Maximum number of text items to return",
                                "default": 10
                            }
                        },
                        "required": ["agent_id", "xbrl_path"]
                    }
                ),
                Tool(
                    name="xbrl_export_document",
                    description=(
                        "Export XBRL document to specified formats. "
                        "Supports markdown, json, and html formats."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {
                                "type": "string",
                                "description": "Agent ID from xbrl_create_agent"
                            },
                            "xbrl_path": {
                                "type": "string",
                                "description": "Path to XBRL instance document"
                            },
                            "output_base_name": {
                                "type": "string",
                                "description": "Base name for output files"
                            },
                            "formats": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Export formats (markdown, json, html)",
                                "default": ["markdown", "json"]
                            }
                        },
                        "required": ["agent_id", "xbrl_path", "output_base_name"]
                    }
                ),
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> List[TextContent]:
            """Handle tool calls."""
            try:
                if name == "xbrl_create_agent":
                    return await self._create_agent(arguments)
                elif name == "xbrl_convert_document":
                    return await self._convert_document(arguments)
                elif name == "xbrl_analyze_structure":
                    return await self._analyze_structure(arguments)
                elif name == "xbrl_extract_key_values":
                    return await self._extract_key_values(arguments)
                elif name == "xbrl_extract_text":
                    return await self._extract_text(arguments)
                elif name == "xbrl_export_document":
                    return await self._export_document(arguments)
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    async def _create_agent(self, args: Dict[str, Any]) -> List[TextContent]:
        """Create an XBRL conversion agent."""
        agent_id = args["agent_id"]
        
        if agent_id in self.agents:
            return [TextContent(
                type="text",
                text=f"Agent '{agent_id}' already exists. Use a different agent_id."
            )]
        
        try:
            agent = create_agent_from_taxonomy(
                taxonomy_dir=args["taxonomy_dir"],
                taxonomy_package=args.get("taxonomy_package"),
                output_dir=args.get("output_dir", "./output"),
                enable_remote_fetch=args.get("enable_remote_fetch", False)
            )
            
            self.agents[agent_id] = agent
            
            result = {
                "status": "success",
                "agent_id": agent_id,
                "message": f"XBRL agent '{agent_id}' created successfully",
                "config": {
                    "taxonomy_dir": args["taxonomy_dir"],
                    "output_dir": args.get("output_dir", "./output"),
                    "enable_remote_fetch": args.get("enable_remote_fetch", False)
                }
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": str(e)
                }, indent=2)
            )]
    
    async def _convert_document(self, args: Dict[str, Any]) -> List[TextContent]:
        """Convert an XBRL document."""
        agent_id = args["agent_id"]
        
        if agent_id not in self.agents:
            return [TextContent(
                type="text",
                text=f"Agent '{agent_id}' not found. Create it first with xbrl_create_agent."
            )]
        
        agent = self.agents[agent_id]
        
        try:
            result = agent.process_xbrl_file(
                xbrl_path=args["xbrl_path"],
                output_base_name=args.get("output_base_name"),
                analyze=args.get("analyze", True)
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": str(e)
                }, indent=2)
            )]
    
    async def _analyze_structure(self, args: Dict[str, Any]) -> List[TextContent]:
        """Analyze XBRL document structure."""
        agent_id = args["agent_id"]
        
        if agent_id not in self.agents:
            return [TextContent(
                type="text",
                text=f"Agent '{agent_id}' not found."
            )]
        
        agent = self.agents[agent_id]
        
        try:
            conv_result = agent.convert_document(args["xbrl_path"])
            structure = agent.get_document_structure(conv_result.document)
            
            result = {
                "status": "success",
                "document_name": conv_result.document.name,
                "structure": structure,
                "total_items": sum(structure.values())
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": str(e)
                }, indent=2)
            )]
    
    async def _extract_key_values(self, args: Dict[str, Any]) -> List[TextContent]:
        """Extract key-value pairs from XBRL document."""
        agent_id = args["agent_id"]
        
        if agent_id not in self.agents:
            return [TextContent(
                type="text",
                text=f"Agent '{agent_id}' not found."
            )]
        
        agent = self.agents[agent_id]
        
        try:
            conv_result = agent.convert_document(args["xbrl_path"])
            kv_pairs = agent.extract_key_value_pairs(conv_result.document)
            
            max_items = args.get("max_items", 100)
            kv_pairs = kv_pairs[:max_items]
            
            result = {
                "status": "success",
                "document_name": conv_result.document.name,
                "key_value_pairs": kv_pairs,
                "count": len(kv_pairs)
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": str(e)
                }, indent=2)
            )]
    
    async def _extract_text(self, args: Dict[str, Any]) -> List[TextContent]:
        """Extract text content from XBRL document."""
        agent_id = args["agent_id"]
        
        if agent_id not in self.agents:
            return [TextContent(
                type="text",
                text=f"Agent '{agent_id}' not found."
            )]
        
        agent = self.agents[agent_id]
        
        try:
            conv_result = agent.convert_document(args["xbrl_path"])
            max_items = args.get("max_items", 10)
            texts = agent.extract_text_content(conv_result.document, max_items)
            
            result = {
                "status": "success",
                "document_name": conv_result.document.name,
                "text_items": texts,
                "count": len(texts)
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": str(e)
                }, indent=2)
            )]
    
    async def _export_document(self, args: Dict[str, Any]) -> List[TextContent]:
        """Export XBRL document to specified formats."""
        agent_id = args["agent_id"]
        
        if agent_id not in self.agents:
            return [TextContent(
                type="text",
                text=f"Agent '{agent_id}' not found."
            )]
        
        agent = self.agents[agent_id]
        
        try:
            conv_result = agent.convert_document(args["xbrl_path"])
            output_files = agent.export_document(
                document=conv_result.document,
                base_name=args["output_base_name"],
                formats=args.get("formats", ["markdown", "json"])
            )
            
            result = {
                "status": "success",
                "document_name": conv_result.document.name,
                "output_files": {k: str(v) for k, v in output_files.items()}
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": str(e)
                }, indent=2)
            )]
    
    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            logger.info("XBRL MCP Server running on stdio")
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point for the MCP server."""
    try:
        server = XBRLMCPServer()
        await server.run()
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.error("Install with: pip install mcp docling[xbrl]")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
