# XBRL Document Conversion - Architecture Documentation

This document provides a comprehensive overview of the XBRL Document Conversion system architecture, including component diagrams, data flows, and interaction patterns.

## Table of Contents
1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Component Architecture](#component-architecture)
4. [Conversion Flow](#conversion-flow)
5. [Web UI Flow](#web-ui-flow)
6. [MCP Server Architecture](#mcp-server-architecture)
7. [Data Models](#data-models)

---

## System Overview

The XBRL Document Conversion system is built on top of the Docling library and provides multiple interfaces for converting XBRL (eXtensible Business Reporting Language) documents into various formats (Markdown, JSON, HTML).

### Key Features
- XBRL instance document parsing
- Taxonomy validation (local and remote)
- Multiple export formats
- Web UI for easy interaction
- MCP server for programmatic access
- Offline processing support

---

## High-Level Architecture

```mermaid
graph TB
    subgraph "User Interfaces"
        WebUI[Web UI<br/>Flask Application]
        CLI[CLI Scripts<br/>Python]
        MCP[MCP Server<br/>Model Context Protocol]
    end
    
    subgraph "Core Components"
        Agent[XBRL Conversion Agent<br/>xbrl_agent.py]
        Config[Configuration<br/>XBRLConversionConfig]
    end
    
    subgraph "Docling Library"
        Converter[Document Converter]
        Backend[XBRL Backend]
        FormatOpt[XBRL Format Option]
    end
    
    subgraph "Data Storage"
        Uploads[(Uploads<br/>XBRL Files)]
        Output[(Output<br/>Converted Files)]
        Taxonomy[(Taxonomy<br/>Schema & Linkbase)]
    end
    
    WebUI --> Agent
    CLI --> Agent
    MCP --> Agent
    
    Agent --> Config
    Agent --> Converter
    
    Converter --> Backend
    Converter --> FormatOpt
    FormatOpt --> Backend
    
    Agent --> Uploads
    Agent --> Output
    Backend --> Taxonomy
    
    style Agent fill:#667eea,color:#fff
    style Converter fill:#764ba2,color:#fff
    style Backend fill:#764ba2,color:#fff
```

---

## Component Architecture

```mermaid
classDiagram
    class XBRLConversionAgent {
        -config: XBRLConversionConfig
        -converter: DocumentConverter
        +__init__(config)
        +convert_document(xbrl_path)
        +export_to_markdown(document, path)
        +export_to_json(document, path)
        +export_to_html(document, path)
        +process_xbrl_file(xbrl_path)
    }
    
    class XBRLConversionConfig {
        +enable_local_fetch: bool
        +enable_remote_fetch: bool
        +taxonomy_dir: Path
        +taxonomy_package: Path
        +output_dir: Path
        +export_formats: List[str]
    }
    
    class DocumentConverter {
        +allowed_formats: List[InputFormat]
        +format_options: Dict
        +convert(source)
    }
    
    class XBRLFormatOption {
        +backend_options: XBRLBackendOptions
    }
    
    class XBRLBackendOptions {
        +enable_local_fetch: bool
        +enable_remote_fetch: bool
        +taxonomy: Path
    }
    
    class ConversionResult {
        +document: DoclingDocument
        +status: ConversionStatus
    }
    
    class DoclingDocument {
        +name: str
        +texts: List
        +tables: List
        +key_value_items: List
        +export_to_markdown()
        +model_dump()
    }
    
    XBRLConversionAgent --> XBRLConversionConfig
    XBRLConversionAgent --> DocumentConverter
    DocumentConverter --> XBRLFormatOption
    XBRLFormatOption --> XBRLBackendOptions
    DocumentConverter --> ConversionResult
    ConversionResult --> DoclingDocument
```

---

## Conversion Flow

```mermaid
sequenceDiagram
    participant User
    participant Agent as XBRL Agent
    participant Config as Configuration
    participant Converter as Document Converter
    participant Backend as XBRL Backend
    participant FS as File System
    
    User->>Agent: process_xbrl_file(path)
    
    Agent->>Config: Get taxonomy settings
    Config-->>Agent: Taxonomy path, options
    
    Agent->>Converter: Setup with XBRLFormatOption
    Note over Converter: XBRLFormatOption wraps<br/>XBRLBackendOptions
    
    Agent->>FS: Read XBRL file
    FS-->>Agent: XBRL content
    
    Agent->>Converter: convert(xbrl_path)
    
    Converter->>Backend: Parse XBRL
    Backend->>FS: Load taxonomy files
    FS-->>Backend: Schema & linkbase
    
    Backend->>Backend: Validate against taxonomy
    Backend->>Backend: Extract facts & metadata
    Backend-->>Converter: Parsed document
    
    Converter-->>Agent: ConversionResult
    
    Agent->>Agent: Analyze structure
    Agent->>Agent: Extract key-value pairs
    Agent->>Agent: Extract text content
    
    loop For each export format
        Agent->>Agent: Export to format
        Agent->>FS: Write output file
    end
    
    Agent-->>User: Processing results
```

---

## Web UI Flow

```mermaid
sequenceDiagram
    participant Browser
    participant Flask as Flask Server
    participant Agent as XBRL Agent
    participant FS as File System
    
    Browser->>Flask: GET /
    Flask-->>Browser: HTML form
    
    Browser->>Browser: User selects file & options
    Browser->>Flask: POST /convert (multipart/form-data)
    
    Flask->>FS: Save uploaded file
    FS-->>Flask: Upload path
    
    Flask->>Agent: Create/reuse agent
    Note over Agent: Configured with taxonomy
    
    Flask->>Agent: process_xbrl_file()
    
    Agent->>Agent: Convert document
    Agent->>FS: Export to formats
    FS-->>Agent: Output paths
    
    Agent-->>Flask: Conversion results
    
    Flask->>FS: Delete uploaded file
    Flask->>Flask: Convert absolute paths to relative
    
    Flask-->>Browser: JSON response with results
    
    Browser->>Browser: Display results
    Browser->>Browser: Show download buttons
    
    Browser->>Flask: GET /download/{path}
    Flask->>FS: Read output file
    FS-->>Flask: File content
    Flask-->>Browser: File download
```

### Web UI Component Interaction

```mermaid
graph LR
    subgraph "Frontend (Browser)"
        Form[Upload Form]
        Results[Results Display]
        Download[Download Links]
    end
    
    subgraph "Backend (Flask)"
        Index["/ Route"]
        Convert["/convert Route"]
        DL["/download Route"]
    end
    
    subgraph "Processing"
        Agent[XBRL Agent]
        Docling[Docling Library]
    end
    
    subgraph "Storage"
        Uploads[(Uploads)]
        Output[(Output)]
    end
    
    Form -->|POST| Convert
    Convert --> Uploads
    Convert --> Agent
    Agent --> Docling
    Agent --> Output
    Convert -->|JSON| Results
    Results --> Download
    Download -->|GET| DL
    DL --> Output
    DL -->|File| Download
    
    Index -->|HTML| Form
    
    style Agent fill:#667eea,color:#fff
    style Docling fill:#764ba2,color:#fff
```

---

## MCP Server Architecture

```mermaid
graph TB
    subgraph "MCP Client"
        IDE[IDE/Editor<br/>VS Code, etc.]
        Client[MCP Client]
    end
    
    subgraph "MCP Server"
        Server[MCP Server<br/>xbrl_mcp_server.py]
        Tools[Tool Handlers]
    end
    
    subgraph "Core Logic"
        Agent[XBRL Agent]
        Converter[Document Converter]
    end
    
    subgraph "Resources"
        Taxonomy[(Taxonomy)]
        Files[(XBRL Files)]
    end
    
    IDE --> Client
    Client <-->|JSON-RPC| Server
    Server --> Tools
    
    Tools -->|convert_xbrl| Agent
    Tools -->|list_formats| Agent
    Tools -->|validate_taxonomy| Agent
    
    Agent --> Converter
    Converter --> Taxonomy
    Agent --> Files
    
    style Server fill:#667eea,color:#fff
    style Agent fill:#764ba2,color:#fff
```

### MCP Tool Flow

```mermaid
sequenceDiagram
    participant Client as MCP Client
    participant Server as MCP Server
    participant Tool as Tool Handler
    participant Agent as XBRL Agent
    
    Client->>Server: tools/list
    Server-->>Client: Available tools
    
    Client->>Server: tools/call: convert_xbrl
    Note over Client,Server: Parameters: file_path,<br/>taxonomy_dir, formats
    
    Server->>Tool: Route to handler
    Tool->>Agent: Create agent instance
    Tool->>Agent: process_xbrl_file()
    
    Agent->>Agent: Convert & export
    Agent-->>Tool: Results
    
    Tool-->>Server: Tool response
    Server-->>Client: Conversion results
```

---

## Data Models

### XBRL Document Structure

```mermaid
graph TB
    subgraph "XBRL Instance Document"
        Instance[XBRL Instance<br/>.xml file]
        Context[Contexts<br/>Time periods, entities]
        Facts[Facts<br/>Numeric & text data]
        Units[Units<br/>Currency, shares, etc.]
    end
    
    subgraph "Taxonomy"
        Schema[Schema<br/>.xsd files]
        Calc[Calculation Linkbase<br/>_cal.xml]
        Def[Definition Linkbase<br/>_def.xml]
        Lab[Label Linkbase<br/>_lab.xml]
        Pres[Presentation Linkbase<br/>_pre.xml]
    end
    
    subgraph "Converted Output"
        Doc[DoclingDocument]
        Texts[Text Items]
        Tables[Tables]
        KV[Key-Value Pairs]
    end
    
    Instance --> Context
    Instance --> Facts
    Instance --> Units
    
    Facts -.->|References| Schema
    Facts -.->|Uses| Calc
    Facts -.->|Uses| Def
    Facts -.->|Uses| Lab
    Facts -.->|Uses| Pres
    
    Instance -->|Converts to| Doc
    Facts -->|Extracted as| Texts
    Facts -->|Structured as| Tables
    Facts -->|Mapped to| KV
    
    style Instance fill:#667eea,color:#fff
    style Doc fill:#764ba2,color:#fff
```

### Configuration Flow

```mermaid
graph LR
    subgraph "Input Configuration"
        TaxDir[Taxonomy Directory]
        TaxPkg[Taxonomy Package<br/>.zip]
        LocalFetch[Enable Local Fetch]
        RemoteFetch[Enable Remote Fetch]
        Formats[Export Formats]
    end
    
    subgraph "XBRLConversionConfig"
        Config[Configuration Object]
    end
    
    subgraph "Backend Configuration"
        BackendOpt[XBRLBackendOptions]
        FormatOpt[XBRLFormatOption]
    end
    
    subgraph "Document Converter"
        Converter[DocumentConverter]
    end
    
    TaxDir --> Config
    TaxPkg --> Config
    LocalFetch --> Config
    RemoteFetch --> Config
    Formats --> Config
    
    Config --> BackendOpt
    BackendOpt --> FormatOpt
    FormatOpt --> Converter
    
    style Config fill:#667eea,color:#fff
    style Converter fill:#764ba2,color:#fff
```

---

## File Organization

```
docling-xbrl-test/
├── xbrl_agent.py              # Core conversion agent
├── xbrl_mcp_server.py         # MCP server implementation
├── requirements.txt           # Python dependencies
├── examples/
│   ├── web_ui.py             # Flask web interface
│   └── basic_usage.py        # CLI examples
├── scripts/
│   ├── start.sh              # Start services
│   └── stop.sh               # Stop services
├── uploads/                   # Uploaded XBRL files
├── output/                    # Converted output files
├── Docs/
│   ├── ARCHITECTURE.md       # This document
│   ├── API_REFERENCE.md      # API documentation
│   ├── SETUP_GUIDE.md        # Setup instructions
│   └── MCP_SERVER.md         # MCP server guide
└── _data/
    └── xbrl/
        └── mlac-taxonomy/    # Taxonomy files
```

---

## Technology Stack

```mermaid
graph TB
    subgraph "Frontend"
        HTML[HTML5]
        CSS[CSS3]
        JS[JavaScript]
    end
    
    subgraph "Backend"
        Python[Python 3.12+]
        Flask[Flask Web Framework]
        MCP[MCP Protocol]
    end
    
    subgraph "Core Libraries"
        Docling[Docling Library]
        Arelle[Arelle XBRL Engine]
        Pydantic[Pydantic Models]
    end
    
    subgraph "Data Formats"
        XBRL[XBRL/XML]
        MD[Markdown]
        JSON[JSON]
        HTMLOut[HTML]
    end
    
    HTML --> Flask
    CSS --> Flask
    JS --> Flask
    
    Flask --> Python
    MCP --> Python
    
    Python --> Docling
    Docling --> Arelle
    Docling --> Pydantic
    
    Docling --> XBRL
    Docling --> MD
    Docling --> JSON
    Docling --> HTMLOut
    
    style Docling fill:#667eea,color:#fff
    style Python fill:#764ba2,color:#fff
```

---

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        Dev[Local Development]
        VEnv[Python Virtual Env]
        DevServer[Flask Dev Server]
    end
    
    subgraph "Production Environment"
        Prod[Production Server]
        WSGI[WSGI Server<br/>Gunicorn/uWSGI]
        Nginx[Nginx Reverse Proxy]
    end
    
    subgraph "Services"
        WebUI[Web UI Service<br/>Port 5002]
        MCPServ[MCP Server<br/>stdio/SSE]
    end
    
    subgraph "Data"
        UploadVol[Upload Volume]
        OutputVol[Output Volume]
        TaxVol[Taxonomy Volume]
    end
    
    Dev --> VEnv
    VEnv --> DevServer
    DevServer --> WebUI
    
    Prod --> WSGI
    WSGI --> Nginx
    Nginx --> WebUI
    
    WebUI --> UploadVol
    WebUI --> OutputVol
    WebUI --> TaxVol
    
    MCPServ --> TaxVol
    
    style WebUI fill:#667eea,color:#fff
    style MCPServ fill:#764ba2,color:#fff
```

---

## Error Handling Flow

```mermaid
graph TB
    Start[Start Conversion]
    
    Start --> CheckFile{File Exists?}
    CheckFile -->|No| FileError[FileNotFoundError]
    CheckFile -->|Yes| CheckFormat{Valid XBRL?}
    
    CheckFormat -->|No| FormatError[ValueError:<br/>Invalid Format]
    CheckFormat -->|Yes| CheckTax{Taxonomy<br/>Available?}
    
    CheckTax -->|No| TaxError[Warning:<br/>No Taxonomy]
    CheckTax -->|Yes| Convert[Convert Document]
    TaxError --> Convert
    
    Convert --> CheckStatus{Conversion<br/>Success?}
    CheckStatus -->|No| ConvError[ValueError:<br/>Conversion Failed]
    CheckStatus -->|Yes| Export[Export to Formats]
    
    Export --> CheckExport{Export<br/>Success?}
    CheckExport -->|No| ExportError[IOError:<br/>Export Failed]
    CheckExport -->|Yes| Success[Return Results]
    
    FileError --> LogError[Log Error]
    FormatError --> LogError
    ConvError --> LogError
    ExportError --> LogError
    
    LogError --> ReturnError[Return Error Response]
    
    style Success fill:#28a745,color:#fff
    style ReturnError fill:#dc3545,color:#fff
```

---

## Performance Considerations

### Caching Strategy

```mermaid
graph LR
    subgraph "Request Flow"
        Req[Request]
        Cache{Cache Hit?}
        Process[Process XBRL]
        Store[Store Result]
        Return[Return Result]
    end
    
    Req --> Cache
    Cache -->|Yes| Return
    Cache -->|No| Process
    Process --> Store
    Store --> Return
    
    style Cache fill:#ffc107,color:#000
    style Return fill:#28a745,color:#fff
```

### Optimization Points

1. **Taxonomy Caching**: Load taxonomy once, reuse for multiple conversions
2. **Agent Reuse**: Keep agent instance alive in web UI
3. **Streaming**: Process large files in chunks
4. **Parallel Processing**: Convert to multiple formats concurrently
5. **File Cleanup**: Remove temporary files after processing

---

## Security Considerations

```mermaid
graph TB
    subgraph "Input Validation"
        FileType[File Type Check]
        FileSize[File Size Limit]
        PathValid[Path Validation]
    end
    
    subgraph "Processing"
        Sandbox[Sandboxed Execution]
        TempFiles[Temporary File Handling]
        Cleanup[Automatic Cleanup]
    end
    
    subgraph "Output"
        PathSafe[Safe Path Construction]
        PermCheck[Permission Checks]
        Sanitize[Output Sanitization]
    end
    
    FileType --> Sandbox
    FileSize --> Sandbox
    PathValid --> Sandbox
    
    Sandbox --> TempFiles
    TempFiles --> Cleanup
    
    Cleanup --> PathSafe
    PathSafe --> PermCheck
    PermCheck --> Sanitize
    
    style Sandbox fill:#dc3545,color:#fff
    style Cleanup fill:#28a745,color:#fff
```

---

## Future Enhancements

1. **Batch Processing**: Convert multiple XBRL files in parallel
2. **API Authentication**: Add OAuth2/JWT authentication for MCP server
3. **Cloud Storage**: Support S3/Azure Blob for taxonomy and outputs
4. **Real-time Updates**: WebSocket support for conversion progress
5. **Advanced Analytics**: Extract financial ratios and trends
6. **Visualization**: Generate charts from financial data
7. **Comparison Tools**: Compare multiple XBRL filings
8. **Validation Reports**: Detailed taxonomy validation results

---

## Conclusion

This architecture provides a flexible, extensible system for XBRL document conversion with multiple interfaces (Web UI, CLI, MCP) and robust error handling. The modular design allows for easy maintenance and future enhancements.

For more details, see:
- [API Reference](API_REFERENCE.md)
- [Setup Guide](SETUP_GUIDE.md)
- [MCP Server Documentation](MCP_SERVER.md)