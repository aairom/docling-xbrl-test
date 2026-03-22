# API Reference

Complete API documentation for the XBRL Conversion Agent.

## Table of Contents

- [Configuration](#configuration)
- [Agent Creation](#agent-creation)
- [Document Conversion](#document-conversion)
- [Data Extraction](#data-extraction)
- [Export Functions](#export-functions)

## Configuration

### `XBRLConversionConfig`

Configuration dataclass for XBRL conversion settings.

```python
@dataclass
class XBRLConversionConfig:
    enable_local_fetch: bool = True
    enable_remote_fetch: bool = False
    taxonomy_dir: Optional[Path] = None
    taxonomy_package: Optional[Path] = None
    output_dir: Path = Path("./output")
    export_formats: List[str] = field(default_factory=lambda: ["markdown", "json"])
```

**Attributes**:

- `enable_local_fetch` (bool): Enable fetching taxonomy files from local directory. Default: True
- `enable_remote_fetch` (bool): Enable fetching taxonomy files from remote URLs. Default: False
- `taxonomy_dir` (Optional[Path]): Path to local taxonomy directory containing schema and linkbase files
- `taxonomy_package` (Optional[Path]): Path to taxonomy package ZIP file for offline operation
- `output_dir` (Path): Directory for saving converted documents. Default: "./output"
- `export_formats` (List[str]): List of export formats. Default: ["markdown", "json"]

**Example**:
```python
config = XBRLConversionConfig(
    enable_local_fetch=True,
    enable_remote_fetch=False,
    taxonomy_dir=Path("./taxonomy"),
    taxonomy_package=Path("./taxonomy/package.zip"),
    output_dir=Path("./output"),
    export_formats=["markdown", "json", "html"]
)
```

## Agent Creation

### `create_agent_from_taxonomy()`

Factory function to create an XBRL agent with taxonomy configuration.

```python
def create_agent_from_taxonomy(
    taxonomy_dir: Union[str, Path],
    taxonomy_package: Optional[Union[str, Path]] = None,
    output_dir: Union[str, Path] = "./output",
    enable_remote_fetch: bool = False
) -> XBRLConversionAgent
```

**Parameters**:
- `taxonomy_dir`: Path to directory containing taxonomy files
- `taxonomy_package`: Optional path to taxonomy package ZIP
- `output_dir`: Directory for output files (default: "./output")
- `enable_remote_fetch`: Whether to allow remote taxonomy fetching (default: False)

**Returns**: Configured `XBRLConversionAgent` instance

**Example**:
```python
agent = create_agent_from_taxonomy(
    taxonomy_dir="./data/xbrl/mlac-taxonomy",
    taxonomy_package="./data/xbrl/mlac-taxonomy/taxonomy_package.zip"
)
```

### `XBRLConversionAgent.__init__()`

Initialize the XBRL conversion agent.

```python
def __init__(self, config: XBRLConversionConfig)
```

**Parameters**:
- `config`: Configuration object for XBRL conversion

**Raises**:
- `ImportError`: If Docling library is not available
- `ValueError`: If configuration is invalid

**Example**:
```python
config = XBRLConversionConfig(taxonomy_dir=Path("./taxonomy"))
agent = XBRLConversionAgent(config)
```

## Document Conversion

### `convert_document()`

Convert an XBRL instance document to DoclingDocument format.

```python
def convert_document(
    self, 
    xbrl_path: Union[str, Path]
) -> ConversionResult
```

**Parameters**:
- `xbrl_path`: Path to XBRL instance document (.xml file)

**Returns**: `ConversionResult` containing:
- `document`: The converted DoclingDocument
- `status`: Conversion status
- `errors`: List of any errors encountered

**Raises**:
- `FileNotFoundError`: If XBRL file doesn't exist
- `ValueError`: If conversion fails

**Example**:
```python
result = agent.convert_document("./data/xbrl/mlac-20251231.xml")
document = result.document
print(f"Status: {result.status.name}")
print(f"Document: {document.name}")
```

### `process_xbrl_file()`

Complete processing pipeline for an XBRL file.

```python
def process_xbrl_file(
    self, 
    xbrl_path: Union[str, Path],
    output_base_name: Optional[str] = None,
    analyze: bool = True
) -> Dict[str, Any]
```

**Parameters**:
- `xbrl_path`: Path to XBRL instance document
- `output_base_name`: Base name for output files (default: input filename)
- `analyze`: Whether to perform structure analysis (default: True)

**Returns**: Dictionary containing:
```python
{
    "input_file": str,              # Input file path
    "document_name": str,           # Document name
    "conversion_status": str,       # Conversion status
    "structure": Dict[str, int],    # Document structure (if analyze=True)
    "key_value_pairs": List[Dict],  # Extracted facts (if analyze=True)
    "sample_text": List[str],       # Sample text (if analyze=True)
    "output_files": Dict[str, str]  # Exported files
}
```

**Example**:
```python
result = agent.process_xbrl_file(
    "./data/xbrl/mlac-20251231.xml",
    output_base_name="mlac_report",
    analyze=True
)

print(f"Document: {result['document_name']}")
print(f"Structure: {result['structure']}")
print(f"Output files: {result['output_files']}")
```

## Data Extraction

### `get_document_structure()`

Analyze and return the structure of a converted document.

```python
def get_document_structure(
    self, 
    document: DoclingDocument
) -> Dict[str, int]
```

**Parameters**:
- `document`: Converted DoclingDocument

**Returns**: Dictionary mapping item types to their counts

**Example**:
```python
structure = agent.get_document_structure(document)
# Output: {'TextItem': 267, 'TableItem': 23, 'TitleItem': 1, ...}

for item_type, count in structure.items():
    print(f"{item_type}: {count}")
```

### `extract_key_value_pairs()`

Extract numeric facts as key-value pairs from XBRL document.

```python
def extract_key_value_pairs(
    self, 
    document: DoclingDocument
) -> List[Dict[str, Any]]
```

**Parameters**:
- `document`: Converted DoclingDocument

**Returns**: List of dictionaries with structure:
```python
[
    {
        "key": str,      # Fact name
        "value": Any,    # Fact value
        "type": str      # Item type
    },
    ...
]
```

**Example**:
```python
kv_pairs = agent.extract_key_value_pairs(document)
print(f"Total facts: {len(kv_pairs)}")

for pair in kv_pairs[:5]:
    print(f"{pair['key']}: {pair['value']}")
```

### `extract_text_content()`

Extract sample text content from the document.

```python
def extract_text_content(
    self, 
    document: DoclingDocument, 
    max_items: int = 10
) -> List[str]
```

**Parameters**:
- `document`: Converted DoclingDocument
- `max_items`: Maximum number of text items to extract (default: 10)

**Returns**: List of text strings (truncated to 200 chars each)

**Example**:
```python
texts = agent.extract_text_content(document, max_items=5)

for i, text in enumerate(texts, 1):
    print(f"{i}. {text}")
```

## Export Functions

### `export_to_markdown()`

Export document to Markdown format.

```python
def export_to_markdown(
    self, 
    document: DoclingDocument, 
    output_path: Optional[Path] = None
) -> str
```

**Parameters**:
- `document`: Converted DoclingDocument
- `output_path`: Optional path to save the markdown file

**Returns**: Markdown string

**Example**:
```python
# Export to string
markdown = agent.export_to_markdown(document)
print(markdown[:500])

# Export to file
agent.export_to_markdown(document, Path("output/report.md"))
```

### `export_to_json()`

Export document to JSON format.

```python
def export_to_json(
    self, 
    document: DoclingDocument, 
    output_path: Optional[Path] = None
) -> str
```

**Parameters**:
- `document`: Converted DoclingDocument
- `output_path`: Optional path to save the JSON file

**Returns**: JSON string

**Example**:
```python
# Export to string
json_str = agent.export_to_json(document)
data = json.loads(json_str)

# Export to file
agent.export_to_json(document, Path("output/report.json"))
```

### `export_to_html()`

Export document to HTML format.

```python
def export_to_html(
    self, 
    document: DoclingDocument, 
    output_path: Optional[Path] = None
) -> str
```

**Parameters**:
- `document`: Converted DoclingDocument
- `output_path`: Optional path to save the HTML file

**Returns**: HTML string

**Example**:
```python
# Export to string
html = agent.export_to_html(document)

# Export to file
agent.export_to_html(document, Path("output/report.html"))
```

### `export_document()`

Export document to multiple formats at once.

```python
def export_document(
    self, 
    document: DoclingDocument, 
    base_name: str,
    formats: Optional[List[str]] = None
) -> Dict[str, Path]
```

**Parameters**:
- `document`: Converted DoclingDocument
- `base_name`: Base name for output files (without extension)
- `formats`: List of formats to export (default: from config)
  - Supported: "markdown", "md", "json", "html"

**Returns**: Dictionary mapping format names to output file paths

**Example**:
```python
output_files = agent.export_document(
    document, 
    "mlac_report",
    formats=["markdown", "json", "html"]
)

for fmt, path in output_files.items():
    print(f"{fmt}: {path}")
# Output:
# markdown: output/mlac_report.md
# json: output/mlac_report.json
# html: output/mlac_report.html
```

## Complete Example

```python
from pathlib import Path
from xbrl_agent import create_agent_from_taxonomy

# 1. Create agent
agent = create_agent_from_taxonomy(
    taxonomy_dir=Path("./data/xbrl/mlac-taxonomy"),
    taxonomy_package=Path("./data/xbrl/mlac-taxonomy/taxonomy_package.zip"),
    output_dir=Path("./output")
)

# 2. Convert document
result = agent.convert_document("./data/xbrl/mlac-20251231.xml")
document = result.document

# 3. Analyze structure
structure = agent.get_document_structure(document)
print(f"Document structure: {structure}")

# 4. Extract data
kv_pairs = agent.extract_key_value_pairs(document)
texts = agent.extract_text_content(document, max_items=5)

print(f"Key-value pairs: {len(kv_pairs)}")
print(f"Text items: {len(texts)}")

# 5. Export to multiple formats
output_files = agent.export_document(
    document,
    "mlac_report",
    formats=["markdown", "json", "html"]
)

print(f"Exported files: {output_files}")