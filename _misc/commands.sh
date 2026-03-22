# Start Web UI
./scripts/start.sh --web-ui
# Open http://localhost:5002

# Stop Web UI  
./scripts/stop.sh --web-ui

# Start MCP Server
./scripts/start.sh

# Stop MCP Server
./scripts/stop.sh

lsof -i :5002
kill -9 1234
# or
kill -9 $(lsof -t -i:5002)

# windows
netstat -ano | findstr :5002
taskkill /PID 1234 /F