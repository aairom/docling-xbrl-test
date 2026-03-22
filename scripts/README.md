# Utility Scripts

This folder contains utility scripts for managing the XBRL MCP Server.

## Available Scripts

### 1. start.sh

Starts the XBRL MCP server or Web UI in the background.

**Usage**:
```bash
# Start MCP Server (default)
./scripts/start.sh

# Start Web UI
./scripts/start.sh --web-ui
# or
./scripts/start.sh -w
```
**Features**:
- **Automatic virtual environment creation**: Creates `venv/` if it doesn't exist
- **Automatic dependency installation**: Installs requirements.txt if needed
- Activates virtual environment before starting server
- Checks if server is already running
- Starts server in background with nohup
- Creates PID file for process management
- Logs output to `xbrl_server.log`

**First Run**:
On first run, the script will:
1. Create a virtual environment in `venv/`
2. Install all dependencies from `requirements.txt`
3. Start the server

**Subsequent Runs**:
The script will use the existing virtual environment and only install missing dependencies.


**Features**:
- Checks if server is already running
- Validates dependencies
- Starts server in background with nohup
- Creates PID file for process management
- Logs output to `xbrl_server.log`

**Output (MCP Server)**:
```
XBRL MCP Server - Start Script
================================
Creating virtual environment...
✓ Virtual environment created
Activating virtual environment...
Checking dependencies...
Starting XBRL MCP Server...
✓ Server started successfully
  PID: 12345
  Log file: /path/to/xbrl_server.log
  PID file: /path/to/.xbrl_server.pid

To stop the server, run: ./scripts/stop.sh
To view logs, run: tail -f /path/to/xbrl_server.log
```

**Output (Web UI)**:
```
XBRL Web UI - Start Script
===========================
Activating virtual environment...
Checking dependencies...
Starting XBRL Web UI...
✓ Web UI started successfully
  PID: 12346
  URL: http://localhost:5000
  Log file: /path/to/xbrl_webui.log
  PID file: /path/to/.xbrl_webui.pid

To stop the Web UI, run: ./scripts/stop.sh --web-ui
To view logs, run: tail -f /path/to/xbrl_webui.log

Open http://localhost:5000 in your browser
```

### 2. stop.sh

Stops the XBRL MCP server or Web UI running in the background.

**Usage**:
```bash
# Stop MCP Server (default)
./scripts/stop.sh

# Stop Web UI
./scripts/stop.sh --web-ui
# or
./scripts/stop.sh -w
```

**Features**:
- Graceful shutdown with SIGTERM
- Force kill if graceful shutdown fails
- Cleans up PID file
- Preserves log file

**Output (MCP Server)**:
```
XBRL MCP Server - Stop Script
================================
Stopping XBRL MCP Server (PID: 12345)...
.
✓ Server stopped successfully

Log file preserved at: /path/to/xbrl_server.log
To view logs, run: cat /path/to/xbrl_server.log
```

**Output (Web UI)**:
```
XBRL Web UI - Stop Script
==========================
Stopping XBRL Web UI (PID: 12346)...
.
✓ Web UI stopped successfully

Log file preserved at: /path/to/xbrl_webui.log
To view logs, run: cat /path/to/xbrl_webui.log
```

### 3. github-push.sh

Initializes a git repository and pushes to GitHub.

**Usage**:
```bash
./scripts/github-push.sh <github-repo-url> <commit-message>
```

**Parameters**:
- `github-repo-url`: GitHub repository URL (HTTPS or SSH)
- `commit-message`: Commit message for the changes

**Examples**:
```bash
# Using HTTPS
./scripts/github-push.sh https://github.com/username/xbrl-agent.git "Initial commit"

# Using SSH
./scripts/github-push.sh git@github.com:username/xbrl-agent.git "Add XBRL conversion agent"

# With detailed message
./scripts/github-push.sh https://github.com/username/xbrl-agent.git "feat: Add MCP server implementation"
```

**Features**:
- Initializes git repository if needed
- Creates comprehensive .gitignore
- Adds and commits all changes
- Configures remote repository
- Pushes to GitHub
- Handles existing repositories
- Validates GitHub URLs
- Provides helpful error messages

**Output**:
```
XBRL MCP Server - GitHub Push Script
=====================================

Project directory: /path/to/project
Repository URL: https://github.com/username/xbrl-agent.git
Commit message: Initial commit

Initializing git repository...
✓ Git repository initialized
Creating .gitignore...
✓ .gitignore created
Adding files to git...
Committing changes...
✓ Changes committed
Adding remote repository...
✓ Remote repository added

Pushing to GitHub...
Branch: main

✓ Successfully pushed to GitHub!

Repository URL: https://github.com/username/xbrl-agent.git
Branch: main

Next steps:
1. Visit your repository on GitHub
2. Add a description and topics
3. Configure branch protection rules (optional)
4. Set up GitHub Actions (optional)

### 4. remove-underscore-folders.sh

Removes folders starting with underscore (_sources/, _data/, _images/) from GitHub while keeping them locally.

**Usage**:
```bash
./scripts/remove-underscore-folders.sh
```

**What it does**:
1. Removes `_sources/`, `_data/`, and `_images/` from git tracking
2. Keeps the folders on your local machine
3. Updates .gitignore to prevent future commits
4. Commits and pushes the changes to GitHub

**Interactive prompts**:
```
Remove Underscore Folders from GitHub
========================================

WARNING: This will remove _sources/, _data/, and _images/ from GitHub
The folders will remain on your local machine

Do you want to continue? (yes/no): yes

Step 1: Removing folders from git tracking...
✓ Folders removed from git tracking

Step 2: Verifying .gitignore...
✓ .gitignore verified

Step 3: Committing changes...
✓ Changes committed

Step 4: Pushing to GitHub...
Note: This will push to the current branch
Push to GitHub now? (yes/no): yes
✓ Changes pushed to GitHub

Done!

Summary:
  • Folders removed from GitHub: _sources/, _data/, _images/
  • Folders still available locally
  • .gitignore updated to prevent future commits
```

**Important Notes**:
- The folders will be removed from GitHub but remain on your local machine
- This is useful for keeping source materials and test data locally without exposing them publicly
- The .gitignore is automatically updated to prevent accidental future commits
- You can safely run this script multiple times

```

## Common Workflows

### Starting the Server

```bash
# Start the server
./scripts/start.sh

# View logs in real-time
tail -f xbrl_server.log

# Check if server is running
ps aux | grep xbrl_mcp_server
```

### Stopping the Server

```bash
# Stop the server
./scripts/stop.sh

# View final logs
cat xbrl_server.log
```

### Pushing to GitHub

```bash
# First time setup
./scripts/github-push.sh https://github.com/username/xbrl-agent.git "Initial commit"

# Subsequent updates
./scripts/github-push.sh https://github.com/username/xbrl-agent.git "Update documentation"
```

## Files Created

### By start.sh
- `.xbrl_server.pid` - Process ID file
- `xbrl_server.log` - Server log file

### By github-push.sh
- `.git/` - Git repository directory
- `.gitignore` - Git ignore file

## Troubleshooting

### start.sh Issues

**Server won't start**:
```bash
# Check dependencies
pip install -r requirements.txt

# Check for port conflicts
lsof -i :8080

# View error logs
cat xbrl_server.log
```

**Already running error**:
```bash
# Stop existing server first
./scripts/stop.sh

# Then start again
./scripts/start.sh
```

### stop.sh Issues

**Process won't stop**:
```bash
# Find the process
ps aux | grep xbrl_mcp_server

# Force kill manually
kill -9 <PID>

# Clean up PID file
rm -f .xbrl_server.pid
```

### github-push.sh Issues

**Authentication failed**:
```bash
# For HTTPS, use personal access token
# For SSH, set up SSH keys
ssh-keygen -t ed25519 -C "your_email@example.com"
ssh-add ~/.ssh/id_ed25519
```

**Repository doesn't exist**:
1. Create repository on GitHub first
2. Then run the script

**Permission denied**:
```bash
# Make script executable
chmod +x scripts/github-push.sh
```

## Best Practices

1. **Always stop the server before updates**:
   ```bash
   ./scripts/stop.sh
   # Make changes
   ./scripts/start.sh
   ```

2. **Check logs regularly**:
   ```bash
   tail -f xbrl_server.log
   ```

3. **Commit frequently**:
   ```bash
   ./scripts/github-push.sh <repo-url> "Descriptive commit message"
   ```

4. **Use meaningful commit messages**:
   - ✅ "Add XBRL extraction feature"
   - ✅ "Fix taxonomy loading bug"
   - ❌ "Update"
   - ❌ "Changes"

## Script Permissions

All scripts are executable. If you need to reset permissions:

```bash
chmod +x scripts/*.sh
```

## Environment Variables

Optional environment variables for customization:

```bash
# Set custom log file location
export XBRL_LOG_FILE="/custom/path/xbrl_server.log"

# Set custom PID file location
export XBRL_PID_FILE="/custom/path/.xbrl_server.pid"
```

## Integration with CI/CD

These scripts can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Deploy XBRL Server

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Start server
        run: ./scripts/start.sh
      - name: Run tests
        run: python -m pytest
      - name: Stop server
        run: ./scripts/stop.sh
```

## Support

For issues with these scripts:
1. Check the troubleshooting section above
2. Review the main documentation in `Docs/`
3. Check script output and log files