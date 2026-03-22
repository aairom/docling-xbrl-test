#!/bin/bash

# XBRL MCP Server - GitHub Push Script
# This script initializes a git repository and pushes to GitHub

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}XBRL MCP Server - GitHub Push Script${NC}"
echo "====================================="
echo ""

# Check arguments
if [ $# -lt 2 ]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    echo ""
    echo "Usage: $0 <github-repo-url> <commit-message>"
    echo ""
    echo "Examples:"
    echo "  $0 https://github.com/username/repo.git \"Initial commit\""
    echo "  $0 git@github.com:username/repo.git \"Add XBRL conversion agent\""
    echo ""
    exit 1
fi

REPO_URL="$1"
COMMIT_MESSAGE="$2"

# Validate repository URL
if [[ ! "$REPO_URL" =~ ^(https://github\.com/|git@github\.com:) ]]; then
    echo -e "${RED}Error: Invalid GitHub repository URL${NC}"
    echo "URL must start with 'https://github.com/' or 'git@github.com:'"
    exit 1
fi

# Change to project directory
cd "$PROJECT_DIR"

echo -e "${BLUE}Project directory: $PROJECT_DIR${NC}"
echo -e "${BLUE}Repository URL: $REPO_URL${NC}"
echo -e "${BLUE}Commit message: $COMMIT_MESSAGE${NC}"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: git is not installed${NC}"
    echo "Please install git first: https://git-scm.com/downloads"
    exit 1
fi

# Check if already a git repository
if [ -d ".git" ]; then
    echo -e "${YELLOW}Git repository already exists${NC}"
    read -p "Do you want to continue and push to the remote? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
else
    echo "Initializing git repository..."
    git init
    echo -e "${GREEN}✓ Git repository initialized${NC}"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
xbrl-env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Project specific
output/
*.log
.xbrl_server.pid
xbrl_server.log

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.bak
EOF
    echo -e "${GREEN}✓ .gitignore created${NC}"
fi

# Add all files
echo "Adding files to git..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo -e "${YELLOW}No changes to commit${NC}"
else
    # Commit changes
    echo "Committing changes..."
    git commit -m "$COMMIT_MESSAGE"
    echo -e "${GREEN}✓ Changes committed${NC}"
fi

# Check if remote already exists
if git remote | grep -q "^origin$"; then
    echo -e "${YELLOW}Remote 'origin' already exists${NC}"
    CURRENT_REMOTE=$(git remote get-url origin)
    echo "Current remote: $CURRENT_REMOTE"
    
    if [ "$CURRENT_REMOTE" != "$REPO_URL" ]; then
        read -p "Do you want to update the remote URL? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git remote set-url origin "$REPO_URL"
            echo -e "${GREEN}✓ Remote URL updated${NC}"
        fi
    fi
else
    echo "Adding remote repository..."
    git remote add origin "$REPO_URL"
    echo -e "${GREEN}✓ Remote repository added${NC}"
fi

# Get current branch name
BRANCH=$(git branch --show-current)
if [ -z "$BRANCH" ]; then
    BRANCH="main"
    git branch -M main
    echo -e "${GREEN}✓ Renamed branch to 'main'${NC}"
fi

# Push to GitHub
echo ""
echo "Pushing to GitHub..."
echo -e "${YELLOW}Branch: $BRANCH${NC}"

# Try to push
if git push -u origin "$BRANCH" 2>&1; then
    echo ""
    echo -e "${GREEN}✓ Successfully pushed to GitHub!${NC}"
    echo ""
    echo "Repository URL: $REPO_URL"
    echo "Branch: $BRANCH"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Visit your repository on GitHub"
    echo "2. Add a description and topics"
    echo "3. Configure branch protection rules (optional)"
    echo "4. Set up GitHub Actions (optional)"
else
    echo ""
    echo -e "${RED}✗ Failed to push to GitHub${NC}"
    echo ""
    echo -e "${YELLOW}Common issues:${NC}"
    echo "1. Repository doesn't exist - Create it on GitHub first"
    echo "2. Authentication failed - Set up SSH keys or use HTTPS with token"
    echo "3. No permission - Check repository access rights"
    echo ""
    echo "For SSH setup: https://docs.github.com/en/authentication/connecting-to-github-with-ssh"
    echo "For HTTPS token: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token"
    exit 1
fi

# Made with Bob
