#!/bin/bash

# XBRL MCP Server - Start Script
# This script starts the XBRL MCP server or Web UI in the background
# Usage: ./scripts/start.sh [--web-ui]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse command line arguments
WEB_UI_MODE=false
if [ "$1" = "--web-ui" ] || [ "$1" = "-w" ]; then
    WEB_UI_MODE=true
fi

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/venv"

if [ "$WEB_UI_MODE" = true ]; then
    SERVER_SCRIPT="$PROJECT_DIR/examples/web_ui.py"
    PID_FILE="$PROJECT_DIR/.xbrl_webui.pid"
    LOG_FILE="$PROJECT_DIR/xbrl_webui.log"
    echo -e "${GREEN}XBRL Web UI - Start Script${NC}"
    echo "==========================="
else
    SERVER_SCRIPT="$PROJECT_DIR/xbrl_mcp_server.py"
    PID_FILE="$PROJECT_DIR/.xbrl_server.pid"
    LOG_FILE="$PROJECT_DIR/xbrl_server.log"
    echo -e "${GREEN}XBRL MCP Server - Start Script${NC}"
    echo "================================"
fi

# Check if virtual environment exists, create if not
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to create virtual environment${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to activate virtual environment${NC}"
    exit 1
fi

# Check if server script exists
if [ ! -f "$SERVER_SCRIPT" ]; then
    echo -e "${RED}Error: Server script not found at $SERVER_SCRIPT${NC}"
    exit 1
fi

# Check if server is already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}Server is already running with PID $PID${NC}"
        echo "Use './scripts/stop.sh' to stop it first"
        exit 1
    else
        echo -e "${YELLOW}Removing stale PID file${NC}"
        rm -f "$PID_FILE"
    fi
fi

# Check Python dependencies
echo "Checking dependencies..."
if [ "$WEB_UI_MODE" = true ]; then
    if ! python -c "import flask; from docling.backend.xbrl_backend import XbrlBackend" 2>/dev/null; then
        echo -e "${YELLOW}Installing dependencies...${NC}"
        if ! pip install -r "$PROJECT_DIR/requirements.txt"; then
            echo -e "${RED}Error: Failed to install dependencies${NC}"
            exit 1
        fi
        echo -e "${GREEN}✓ Dependencies installed${NC}"
    else
        echo -e "${GREEN}✓ Dependencies already installed${NC}"
    fi
else
    if ! python -c "import mcp; from docling.backend.xbrl_backend import XbrlBackend" 2>/dev/null; then
        echo -e "${YELLOW}Installing dependencies...${NC}"
        if ! pip install -r "$PROJECT_DIR/requirements.txt"; then
            echo -e "${RED}Error: Failed to install dependencies${NC}"
            exit 1
        fi
        echo -e "${GREEN}✓ Dependencies installed${NC}"
    else
        echo -e "${GREEN}✓ Dependencies already installed${NC}"
    fi
fi

# Start the server in background
if [ "$WEB_UI_MODE" = true ]; then
    echo "Starting XBRL Web UI..."
else
    echo "Starting XBRL MCP Server..."
fi
cd "$PROJECT_DIR"

# Set PYTHONPATH to include venv site-packages and run with venv Python
SITE_PACKAGES="$VENV_DIR/lib/python3.12/site-packages"
nohup bash -c "export PYTHONPATH='$SITE_PACKAGES:$PYTHONPATH' && '$VENV_DIR/bin/python' '$SERVER_SCRIPT'" > "$LOG_FILE" 2>&1 &
SERVER_PID=$!

# Save PID
echo "$SERVER_PID" > "$PID_FILE"

# Wait a moment and check if server started successfully
sleep 2

if ps -p "$SERVER_PID" > /dev/null 2>&1; then
    if [ "$WEB_UI_MODE" = true ]; then
        # Extract port from web_ui.py (macOS compatible)
        WEB_PORT=$(grep -o "port=[0-9]*" "$SERVER_SCRIPT" | grep -o "[0-9]*" | head -1)
        if [ -z "$WEB_PORT" ]; then
            WEB_PORT="5000"
        fi
        echo -e "${GREEN}✓ Web UI started successfully${NC}"
        echo "  PID: $SERVER_PID"
        echo "  URL: http://localhost:$WEB_PORT"
        echo "  Log file: $LOG_FILE"
        echo "  PID file: $PID_FILE"
        echo ""
        echo "To stop the Web UI, run: ./scripts/stop.sh --web-ui"
        echo "To view logs, run: tail -f $LOG_FILE"
        echo ""
        echo -e "${YELLOW}Open http://localhost:$WEB_PORT in your browser${NC}"
    else
        echo -e "${GREEN}✓ Server started successfully${NC}"
        echo "  PID: $SERVER_PID"
        echo "  Log file: $LOG_FILE"
        echo "  PID file: $PID_FILE"
        echo ""
        echo "To stop the server, run: ./scripts/stop.sh"
        echo "To view logs, run: tail -f $LOG_FILE"
    fi
else
    if [ "$WEB_UI_MODE" = true ]; then
        echo -e "${RED}✗ Web UI failed to start${NC}"
    else
        echo -e "${RED}✗ Server failed to start${NC}"
    fi
    echo "Check the log file for details: $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi

# Made with Bob
