# XBRL Document Conversion - Troubleshooting Guide

## Issue: "Docling library is required" Error in Web UI

### Problem Description
The Web UI was showing "Error: Docling library is required. Install with: pip install docling[xbrl]" even though the dependencies were correctly installed in the virtual environment.

### Root Causes Identified

#### 1. Incorrect Import Paths (Primary Issue)
The code was using outdated import paths that don't exist in the current version of docling:
- **Wrong**: `from docling.backend.xbrl_backend import XbrlBackend, XbrlBackendOptions`
- **Correct**: `from docling.backend.xml.xbrl_backend import XBRLDocumentBackend, XBRLBackendOptions`

#### 2. Incorrect Class Names
The class names had changed in the docling library:
- **Wrong**: `XbrlBackend`, `XbrlBackendOptions`
- **Correct**: `XBRLDocumentBackend`, `XBRLBackendOptions`

#### 3. Incorrect InputFormat
The XBRL format enum value was incorrect:
- **Wrong**: `InputFormat.XBRL`
- **Correct**: `InputFormat.XML_XBRL`

#### 4. Incorrect Backend Options Fields
The `XBRLBackendOptions` class has different field names than expected:
- **Wrong**: `taxonomy_dir`, `taxonomy_package`
- **Correct**: `taxonomy` (single field that accepts a Path to either directory or package)

#### 5. Old Process Still Running
The bash script was not properly stopping old web UI processes, causing the old version with incorrect imports to keep running.

### Solution

#### 1. Fixed Import Paths in `xbrl_agent.py`
```python
# Line 26: Corrected import path
from docling.backend.xml.xbrl_backend import XBRLDocumentBackend, XBRLBackendOptions

# Line 146: Corrected format enum
converter = DocumentConverter(
    allowed_formats=[InputFormat.XML_XBRL],
    pipeline_options=pipeline_options
)
```

#### 2. Fixed Backend Options Configuration in `xbrl_agent.py` (lines 126-138)
```python
# Use taxonomy_package if available, otherwise use taxonomy_dir
taxonomy_path = None
if self.config.taxonomy_package and self.config.taxonomy_package.exists():
    taxonomy_path = self.config.taxonomy_package
elif self.config.taxonomy_dir and self.config.taxonomy_dir.exists():
    taxonomy_path = self.config.taxonomy_dir

xbrl_options = XBRLBackendOptions(
    enable_local_fetch=self.config.enable_local_fetch,
    enable_remote_fetch=self.config.enable_remote_fetch,
    taxonomy=taxonomy_path
)
```

#### 3. Created Proper Startup Script (`scripts/start_webui.sh`)
```bash
#!/bin/bash
cd "$(dirname "$0")/.."

# Use the venv Python directly (no subshell issues)
VENV_PYTHON="$(pwd)/venv/bin/python"

# Kill any existing web UI processes
pkill -f "python.*web_ui.py" 2>/dev/null || true

# Start the web UI with venv Python
"$VENV_PYTHON" examples/web_ui.py
```

#### 4. Created Proper Stop Script (`scripts/stop_webui.sh`)
```bash
#!/bin/bash
pids=$(ps aux | grep -i "python.*web_ui.py" | grep -v grep | awk '{print $2}')
for pid in $pids; do
    kill -9 $pid
done
```

### Verification
After applying these fixes:
1. The Web UI starts successfully without import errors
2. The Flask application runs on http://localhost:5002
3. The docling library and XBRL backend are properly imported
4. XBRL documents can be converted successfully

### Testing
To verify the fix is working:
```bash
# Start the Web UI
./scripts/start_webui.sh

# Check that it's running
ps aux | grep web_ui.py

# Open in browser
open http://localhost:5002

# Stop the Web UI
./scripts/stop_webui.sh
```

### Key Learnings

1. **Always check actual module structure**: Use `python -c "import module; print(dir(module))"` to verify available classes and functions
2. **Check class signatures**: Use `inspect.signature()` to verify parameter names and types
3. **Kill old processes**: Always ensure old processes are stopped before starting new ones
4. **Use direct Python paths**: Avoid shell activation in scripts; use full path to venv Python instead

### Related Files
- `xbrl_agent.py` - Fixed import paths and backend options
- `scripts/start_webui.sh` - New startup script with proper venv handling
- `scripts/stop_webui.sh` - New stop script that kills all web UI processes
- `examples/web_ui.py` - Flask application (unchanged)

### Prevention
To avoid similar issues in the future:
1. Always verify import paths match the installed library version
2. Check class names and signatures when upgrading dependencies
3. Use proper process management scripts
4. Test with a fresh virtual environment to catch import issues early