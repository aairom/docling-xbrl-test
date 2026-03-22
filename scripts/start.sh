#!/bin/bash

# XBRL MCP Server - Start Script
# This script starts the XBRL MCP server in the background

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SERVER_SCRIPT="$PROJECT_DIR/xbrl_mcp_server.py"
PID_FILE="$PROJECT_DIR/.xbrl_server.pid"
LOG_FILE="$PROJECT_DIR/xbrl_server.log"

echo -e "${GREEN}XBRL MCP Server - Start Script${NC}"
echo "================================"

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
python3 -c "import mcp; import docling" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Required dependencies not installed${NC}"
    echo "Please run: pip install -r requirements.txt"
    exit 1
fi

# Start the server in background
echo "Starting XBRL MCP Server..."
cd "$PROJECT_DIR"

nohup python3 "$SERVER_SCRIPT" > "$LOG_FILE" 2>&1 &
SERVER_PID=$!

# Save PID
echo "$SERVER_PID" > "$PID_FILE"

# Wait a moment and check if server started successfully
sleep 2

if ps -p "$SERVER_PID" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Server started successfully${NC}"
    echo "  PID: $SERVER_PID"
    echo "  Log file: $LOG_FILE"
    echo "  PID file: $PID_FILE"
    echo ""
    echo "To stop the server, run: ./scripts/stop.sh"
    echo "To view logs, run: tail -f $LOG_FILE"
else
    echo -e "${RED}✗ Server failed to start${NC}"
    echo "Check the log file for details: $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi

# Made with Bob
