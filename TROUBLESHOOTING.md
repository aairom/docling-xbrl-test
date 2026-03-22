# XBRL Document Conversion - Troubleshooting Guide

## Issue: "Docling library is required" Error in Web UI

### Problem Description
The Web UI was showing "Error: Docling library is required. Install with: pip install docling[xbrl]" even though the dependencies were correctly installed in the virtual environment.

### Root Cause
The issue was caused by Python symlink resolution in the virtual environment. On macOS, the virtual environment's Python executable (`venv/bin/python3.12`) is a symlink that points to the system Python installation at `/Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12`. When using `nohup` to run the Flask application in the background, the symlink was resolved to the system Python, which didn't have access to the packages installed in the virtual environment's `site-packages` directory.

### Solution
The fix involved explicitly setting the `PYTHONPATH` environment variable to include the virtual environment's `site-packages` directory before running the Flask application. This ensures that even when the system Python is used (due to symlink resolution), it can find and import the packages installed in the virtual environment.

### Changes Made

#### 1. Modified `scripts/start.sh` (lines 108-112)
```bash
cd "$PROJECT_DIR"

# Set PYTHONPATH to include venv site-packages and run with venv Python
SITE_PACKAGES="$VENV_DIR/lib/python3.12/site-packages"
nohup bash -c "export PYTHONPATH='$SITE_PACKAGES:$PYTHONPATH' && '$VENV_DIR/bin/python' '$SERVER_SCRIPT'" > "$LOG_FILE" 2>&1 &
```

This change:
- Explicitly sets `PYTHONPATH` to include the venv's `site-packages` directory
- Runs the command in a bash subshell to ensure the environment variable is properly set
- Uses the venv's Python executable to maintain consistency

#### 2. Removed Shebang from `examples/web_ui.py`
Previously, the file had `#!/usr/bin/env python3` at the top, which could override the Python interpreter specified on the command line. This line was removed to ensure the script uses the Python interpreter specified in the start script.

#### 3. Disabled Flask Debug Mode in `examples/web_ui.py` (line 551)
```python
app.run(host='0.0.0.0', port=5002, debug=False)
```

Changed from `debug=True` to `debug=False` to prevent Flask from creating a reloader process that could use a different Python interpreter.

#### 4. Enhanced Dependency Check in `scripts/start.sh` (line 79)
```bash
if ! python -c "import flask; from docling.backend.xbrl_backend import XbrlBackend" 2>/dev/null; then
```

Updated the dependency check to verify not just the basic docling import, but also the XBRL backend specifically, ensuring all required components are available.

### Verification
After applying these fixes:
1. The Web UI starts successfully without import errors
2. The Flask application runs on http://localhost:5002
3. The docling library and XBRL backend are properly imported
4. The application is fully functional

### Additional Notes

#### Virtual Environment Structure on macOS
```
venv/bin/python -> python3.12
venv/bin/python3 -> python3.12
venv/bin/python3.12 -> /Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12
```

The symlink chain means the actual Python executable is the system Python, but packages are installed in `venv/lib/python3.12/site-packages/`.

#### Alternative Solutions (Not Implemented)
1. **Recreate venv with --copies flag**: This would create actual copies of Python binaries instead of symlinks, but would increase disk usage.
2. **Use a wrapper script**: Create a separate wrapper that sets up the environment before running Python.
3. **Install in system Python**: Not recommended as it pollutes the system Python installation.

### Prevention
To avoid similar issues in the future:
1. Always use explicit PYTHONPATH when running Python scripts in background processes
2. Avoid using shebangs in scripts that should use a specific virtual environment
3. Disable Flask debug mode in production-like deployments
4. Test dependency imports specifically for the features you're using (e.g., XBRL backend)

### Related Files
- `scripts/start.sh` - Startup script with PYTHONPATH fix
- `examples/web_ui.py` - Flask application (shebang removed, debug disabled)
- `xbrl_agent.py` - Agent implementation with proper import error handling

### Testing
To verify the fix is working:
```bash
# Start the Web UI
./scripts/start.sh --web-ui

# Check the logs for any import errors
tail -f xbrl_webui.log

# Open in browser
open http://localhost:5002

# Stop the Web UI
./scripts/stop.sh --web-ui
```

The Web UI should load without any "Docling library required" errors and display the XBRL Document Conversion interface.