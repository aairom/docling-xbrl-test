"""
XBRL Document Conversion Agent

This module provides a comprehensive agent for converting XBRL (eXtensible Business 
Reporting Language) documents using Docling, with support for offline processing,
taxonomy validation, and multiple export formats.

XBRL is a standard XML-based format used globally by companies, regulators, and 
financial institutions for exchanging business and financial information in a 
structured, machine-readable format.

Author: Generated for XBRL Document Conversion
License: MIT
"""

import logging
from pathlib import Path
from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass, field
import json

try:
    from docling.document_converter import DocumentConverter, PdfFormatOption, XBRLFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PipelineOptions
    from docling.datamodel.backend_options import XBRLBackendOptions
    from docling.datamodel.document import ConversionResult, DoclingDocument
    DOCLING_AVAILABLE = True
except ImportError as e:
    DOCLING_AVAILABLE = False
    # Define placeholder types when docling is not available
    ConversionResult = Any
    DoclingDocument = Any
    logging.warning(f"Docling library not available. Install with: pip install docling[xbrl]. Error: {e}")


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class XBRLConversionConfig:
    """
    Configuration for XBRL document conversion.
    
    Attributes:
        enable_local_fetch: Enable fetching taxonomy files from local directory
        enable_remote_fetch: Enable fetching taxonomy files from remote URLs
        taxonomy_dir: Path to local taxonomy directory containing schema and linkbase files
        taxonomy_package: Path to taxonomy package ZIP file for offline operation
        output_dir: Directory for saving converted documents
        export_formats: List of export formats (markdown, json, html, text)
    """
    enable_local_fetch: bool = True
    enable_remote_fetch: bool = False
    taxonomy_dir: Optional[Path] = None
    taxonomy_package: Optional[Path] = None
    output_dir: Path = Path("./output")
    export_formats: List[str] = field(default_factory=lambda: ["markdown", "json"])
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.enable_local_fetch and not self.taxonomy_dir:
            logger.warning("Local fetch enabled but no taxonomy_dir specified")
        
        if not self.enable_local_fetch and not self.enable_remote_fetch:
            raise ValueError("At least one of enable_local_fetch or enable_remote_fetch must be True")
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)


class XBRLConversionAgent:
    """
    Agent for converting XBRL documents to various formats.
    
    This agent handles:
    - XBRL instance document parsing
    - Taxonomy validation (local or remote)
    - Metadata extraction
    - Text block extraction
    - Numeric fact extraction
    - Export to multiple formats (Markdown, JSON, HTML, etc.)
    
    Example:
        >>> config = XBRLConversionConfig(
        ...     taxonomy_dir=Path("./taxonomy"),
        ...     taxonomy_package=Path("./taxonomy/package.zip")
        ... )
        >>> agent = XBRLConversionAgent(config)
        >>> result = agent.convert_document("report.xml")
        >>> agent.export_document(result.document, "output")
    """
    
    def __init__(self, config: XBRLConversionConfig):
        """
        Initialize the XBRL conversion agent.
        
        Args:
            config: Configuration object for XBRL conversion
            
        Raises:
            ImportError: If Docling library is not available
            ValueError: If configuration is invalid
        """
        if not DOCLING_AVAILABLE:
            raise ImportError(
                "Docling library is required. Install with: pip install docling[xbrl]"
            )
        
        self.config = config
        self.converter = self._setup_converter()
        logger.info("XBRL Conversion Agent initialized successfully")
    
    def _setup_converter(self) -> DocumentConverter:
        """
        Set up the DocumentConverter with XBRL backend configuration.
        
        Returns:
            Configured DocumentConverter instance
        """
        # Configure XBRL backend options
        # Use taxonomy_package if available, otherwise use taxonomy_dir
        taxonomy_path = None
        if self.config.taxonomy_package and self.config.taxonomy_package.exists():
            taxonomy_path = self.config.taxonomy_package
        elif self.config.taxonomy_dir and self.config.taxonomy_dir.exists():
            taxonomy_path = self.config.taxonomy_dir
        
        # Create backend options
        backend_options = XBRLBackendOptions(
            enable_local_fetch=self.config.enable_local_fetch,
            enable_remote_fetch=self.config.enable_remote_fetch,
            taxonomy=taxonomy_path
        )
        
        # Create format options with XBRLFormatOption wrapper
        # This is the correct way according to Docling's test suite
        format_options = {
            InputFormat.XML_XBRL: XBRLFormatOption(backend_options=backend_options)
        }
        
        # Create and return converter
        converter = DocumentConverter(
            allowed_formats=[InputFormat.XML_XBRL],
            format_options=format_options
        )
        
        logger.info("XBRL converter configured successfully")
        return converter
    
    def convert_document(
        self, 
        xbrl_path: Union[str, Path]
    ) -> ConversionResult:
        """
        Convert an XBRL instance document to DoclingDocument format.
        
        This method:
        1. Parses the XBRL instance file
        2. Validates against the taxonomy
        3. Extracts metadata, text blocks, and numeric facts
        4. Returns a unified DoclingDocument representation
        
        Args:
            xbrl_path: Path to XBRL instance document (.xml file)
            
        Returns:
            ConversionResult containing the converted document and metadata
            
        Raises:
            FileNotFoundError: If XBRL file doesn't exist
            ValueError: If conversion fails
        """
        xbrl_path = Path(xbrl_path)
        
        if not xbrl_path.exists():
            raise FileNotFoundError(f"XBRL file not found: {xbrl_path}")
        
        logger.info(f"Converting XBRL document: {xbrl_path}")
        
        try:
            result = self.converter.convert(xbrl_path)
            
            if result.status.name != "SUCCESS":
                raise ValueError(f"Conversion failed with status: {result.status}")
            
            logger.info(f"Conversion successful! Document: {result.document.name}")
            logger.info(f"Number of items: {len(list(result.document.iterate_items()))}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error converting XBRL document: {e}")
            raise
    
    def get_document_structure(self, document: DoclingDocument) -> Dict[str, int]:
        """
        Analyze and return the structure of a converted document.
        
        Args:
            document: Converted DoclingDocument
            
        Returns:
            Dictionary mapping item types to their counts
        """
        structure = {}
        
        for item, _ in document.iterate_items():
            item_type = type(item).__name__
            structure[item_type] = structure.get(item_type, 0) + 1
        
        logger.info(f"Document structure: {structure}")
        return structure
    
    def extract_key_value_pairs(self, document: DoclingDocument) -> List[Dict[str, Any]]:
        """
        Extract numeric facts as key-value pairs from XBRL document.
        
        XBRL numeric facts are represented as key-value pairs in the document.
        This method extracts all such pairs for analysis.
        
        Args:
            document: Converted DoclingDocument
            
        Returns:
            List of dictionaries containing key-value pairs with metadata
        """
        key_value_pairs = []
        
        # Extract from key-value regions
        for kv_item in document.key_value_items:
            key_value_pairs.append({
                "key": kv_item.label if hasattr(kv_item, 'label') else str(kv_item),
                "value": kv_item.text if hasattr(kv_item, 'text') else None,
                "type": "key_value_region"
            })
        
        logger.info(f"Extracted {len(key_value_pairs)} key-value pairs")
        return key_value_pairs
    
    def extract_text_content(
        self, 
        document: DoclingDocument, 
        max_items: int = 10
    ) -> List[str]:
        """
        Extract sample text content from the document.
        
        Args:
            document: Converted DoclingDocument
            max_items: Maximum number of text items to extract
            
        Returns:
            List of text strings
        """
        text_items = []
        
        for item in document.texts[:max_items]:
            if hasattr(item, 'text') and item.text:
                # Truncate long text for readability
                text = item.text[:200] + "..." if len(item.text) > 200 else item.text
                text_items.append(text)
        
        logger.info(f"Extracted {len(text_items)} text items")
        return text_items
    
    def export_to_markdown(
        self, 
        document: DoclingDocument, 
        output_path: Optional[Path] = None
    ) -> str:
        """
        Export document to Markdown format.
        
        Args:
            document: Converted DoclingDocument
            output_path: Optional path to save the markdown file
            
        Returns:
            Markdown string
        """
        markdown = document.export_to_markdown()
        
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(markdown, encoding='utf-8')
            logger.info(f"Markdown exported to: {output_path}")
        
        return markdown
    
    def export_to_json(
        self,
        document: DoclingDocument,
        output_path: Optional[Path] = None
    ) -> str:
        """
        Export document to JSON format.
        
        Args:
            document: Converted DoclingDocument
            output_path: Optional path to save the JSON file
            
        Returns:
            JSON string
        """
        # Use the document's dict representation and convert to JSON
        json_str = json.dumps(document.model_dump(), indent=2, ensure_ascii=False)
        
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json_str, encoding='utf-8')
            
            # Calculate file size
            size_kb = len(json_str.encode('utf-8')) / 1024
            logger.info(f"JSON exported to: {output_path} ({size_kb:.2f} KB)")
        
        return json_str
    
    def export_to_html(
        self, 
        document: DoclingDocument, 
        output_path: Optional[Path] = None
    ) -> str:
        """
        Export document to HTML format.
        
        Args:
            document: Converted DoclingDocument
            output_path: Optional path to save the HTML file
            
        Returns:
            HTML string
        """
        html = document.export_to_html()
        
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html, encoding='utf-8')
            logger.info(f"HTML exported to: {output_path}")
        
        return html
    
    def export_document(
        self, 
        document: DoclingDocument, 
        base_name: str,
        formats: Optional[List[str]] = None
    ) -> Dict[str, Path]:
        """
        Export document to multiple formats.
        
        Args:
            document: Converted DoclingDocument
            base_name: Base name for output files (without extension)
            formats: List of formats to export (default: from config)
            
        Returns:
            Dictionary mapping format names to output file paths
        """
        formats = formats or self.config.export_formats
        output_files = {}
        
        for fmt in formats:
            output_path = self.config.output_dir / f"{base_name}.{fmt}"
            
            if fmt == "markdown" or fmt == "md":
                self.export_to_markdown(document, output_path)
                output_files["markdown"] = output_path
                
            elif fmt == "json":
                self.export_to_json(document, output_path)
                output_files["json"] = output_path
                
            elif fmt == "html":
                self.export_to_html(document, output_path)
                output_files["html"] = output_path
                
            else:
                logger.warning(f"Unsupported export format: {fmt}")
        
        return output_files
    
    def process_xbrl_file(
        self, 
        xbrl_path: Union[str, Path],
        output_base_name: Optional[str] = None,
        analyze: bool = True
    ) -> Dict[str, Any]:
        """
        Complete processing pipeline for an XBRL file.
        
        This is a convenience method that:
        1. Converts the XBRL document
        2. Analyzes the structure (optional)
        3. Exports to configured formats
        
        Args:
            xbrl_path: Path to XBRL instance document
            output_base_name: Base name for output files (default: input filename)
            analyze: Whether to perform structure analysis
            
        Returns:
            Dictionary containing conversion results and analysis
        """
        xbrl_path = Path(xbrl_path)
        
        if not output_base_name:
            output_base_name = xbrl_path.stem
        
        # Convert document
        result = self.convert_document(xbrl_path)
        document = result.document
        
        # Prepare results
        results = {
            "input_file": str(xbrl_path),
            "document_name": document.name,
            "conversion_status": result.status.name,
        }
        
        # Analyze structure if requested
        if analyze:
            results["structure"] = self.get_document_structure(document)
            results["key_value_pairs"] = self.extract_key_value_pairs(document)
            results["sample_text"] = self.extract_text_content(document, max_items=5)
        
        # Export to configured formats
        output_files = self.export_document(document, output_base_name)
        results["output_files"] = {k: str(v) for k, v in output_files.items()}
        
        logger.info(f"Processing complete for {xbrl_path}")
        return results


def create_agent_from_taxonomy(
    taxonomy_dir: Union[str, Path],
    taxonomy_package: Optional[Union[str, Path]] = None,
    output_dir: Union[str, Path] = "./output",
    enable_remote_fetch: bool = False
) -> XBRLConversionAgent:
    """
    Factory function to create an XBRL agent with taxonomy configuration.
    
    Args:
        taxonomy_dir: Path to directory containing taxonomy files
        taxonomy_package: Optional path to taxonomy package ZIP
        output_dir: Directory for output files
        enable_remote_fetch: Whether to allow remote taxonomy fetching
        
    Returns:
        Configured XBRLConversionAgent instance
        
    Example:
        >>> agent = create_agent_from_taxonomy(
        ...     taxonomy_dir="./data/xbrl/mlac-taxonomy",
        ...     taxonomy_package="./data/xbrl/mlac-taxonomy/taxonomy_package.zip"
        ... )
        >>> result = agent.process_xbrl_file("./data/xbrl/mlac-20251231.xml")
    """
    config = XBRLConversionConfig(
        enable_local_fetch=True,
        enable_remote_fetch=enable_remote_fetch,
        taxonomy_dir=Path(taxonomy_dir),
        taxonomy_package=Path(taxonomy_package) if taxonomy_package else None,
        output_dir=Path(output_dir)
    )
    
    return XBRLConversionAgent(config)


if __name__ == "__main__":
    # Example usage
    print("XBRL Document Conversion Agent")
    print("=" * 50)
    print("\nThis module provides tools for converting XBRL documents.")
    print("Import and use the XBRLConversionAgent class in your code.")
    print("\nExample:")
    print("  from xbrl_agent import create_agent_from_taxonomy")
    print("  agent = create_agent_from_taxonomy('./taxonomy')")
    print("  result = agent.process_xbrl_file('report.xml')")

# Made with Bob
