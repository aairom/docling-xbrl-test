#!/bin/bash

# XBRL Web UI Startup Script
# This script ensures the web UI runs with the correct virtual environment

cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run: python -m venv venv"
    exit 1
fi

# Use the venv Python directly
VENV_PYTHON="$(pwd)/venv/bin/python"

# Check if docling is installed
if ! "$VENV_PYTHON" -c "import docling" 2>/dev/null; then
    echo "Error: Docling not installed. Installing..."
    "$VENV_PYTHON" -m pip install docling[xbrl]
fi

# Kill any existing web UI processes
pkill -f "python.*web_ui.py" 2>/dev/null || true

# Start the web UI
echo "Starting XBRL Web UI..."
"$VENV_PYTHON" examples/web_ui.py

# Made with Bob
