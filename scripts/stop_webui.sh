#!/bin/bash

# XBRL Web UI Stop Script
# This script properly stops all web UI processes

echo "Stopping XBRL Web UI..."

# Find and kill all web_ui.py processes
pids=$(ps aux | grep -i "python.*web_ui.py" | grep -v grep | awk '{print $2}')

if [ -z "$pids" ]; then
    echo "No web UI processes found running."
    exit 0
fi

echo "Found processes: $pids"
for pid in $pids; do
    echo "Killing process $pid..."
    kill -9 $pid
done

echo "Web UI stopped successfully."

# Made with Bob
