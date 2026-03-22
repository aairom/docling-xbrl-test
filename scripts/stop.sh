#!/bin/bash

# XBRL MCP Server - Stop Script
# This script stops the XBRL MCP server or Web UI running in the background
# Usage: ./scripts/stop.sh [--web-ui]

set -e

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

if [ "$WEB_UI_MODE" = true ]; then
    PID_FILE="$PROJECT_DIR/.xbrl_webui.pid"
    LOG_FILE="$PROJECT_DIR/xbrl_webui.log"
    echo -e "${GREEN}XBRL Web UI - Stop Script${NC}"
    echo "=========================="
else
    PID_FILE="$PROJECT_DIR/.xbrl_server.pid"
    LOG_FILE="$PROJECT_DIR/xbrl_server.log"
    echo -e "${GREEN}XBRL MCP Server - Stop Script${NC}"
    echo "================================"
fi

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    if [ "$WEB_UI_MODE" = true ]; then
        echo -e "${YELLOW}Web UI is not running (no PID file found)${NC}"
    else
        echo -e "${YELLOW}Server is not running (no PID file found)${NC}"
    fi
    exit 0
fi

# Read PID
PID=$(cat "$PID_FILE")

# Check if process is running
if ! ps -p "$PID" > /dev/null 2>&1; then
    if [ "$WEB_UI_MODE" = true ]; then
        echo -e "${YELLOW}Web UI is not running (process $PID not found)${NC}"
    else
        echo -e "${YELLOW}Server is not running (process $PID not found)${NC}"
    fi
    echo "Cleaning up PID file..."
    rm -f "$PID_FILE"
    exit 0
fi

# Stop the server
if [ "$WEB_UI_MODE" = true ]; then
    echo "Stopping XBRL Web UI (PID: $PID)..."
else
    echo "Stopping XBRL MCP Server (PID: $PID)..."
fi

# Try graceful shutdown first
kill "$PID" 2>/dev/null

# Wait for process to stop (max 10 seconds)
COUNTER=0
while ps -p "$PID" > /dev/null 2>&1 && [ $COUNTER -lt 10 ]; do
    sleep 1
    COUNTER=$((COUNTER + 1))
    echo -n "."
done
echo ""

# Check if process stopped
if ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${YELLOW}Process did not stop gracefully, forcing shutdown...${NC}"
    kill -9 "$PID" 2>/dev/null
    sleep 1
fi

# Verify process is stopped
if ps -p "$PID" > /dev/null 2>&1; then
    if [ "$WEB_UI_MODE" = true ]; then
        echo -e "${RED}✗ Failed to stop Web UI${NC}"
    else
        echo -e "${RED}✗ Failed to stop server${NC}"
    fi
    exit 1
else
    if [ "$WEB_UI_MODE" = true ]; then
        echo -e "${GREEN}✓ Web UI stopped successfully${NC}"
    else
        echo -e "${GREEN}✓ Server stopped successfully${NC}"
    fi
    rm -f "$PID_FILE"
    
    # Show log file location
    if [ -f "$LOG_FILE" ]; then
        echo ""
        echo "Log file preserved at: $LOG_FILE"
        echo "To view logs, run: cat $LOG_FILE"
    fi
fi

# Made with Bob
