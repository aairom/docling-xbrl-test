#!/bin/bash

# Script to remove folders starting with underscore from GitHub
# This removes them from git history while keeping them locally

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Remove Underscore Folders from GitHub${NC}"
echo "========================================"
echo ""
echo -e "${YELLOW}WARNING: This will remove _sources/, _data/, and _images/ from GitHub${NC}"
echo -e "${YELLOW}The folders will remain on your local machine${NC}"
echo ""
read -p "Do you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Operation cancelled"
    exit 0
fi

# Get project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}Error: Not a git repository${NC}"
    echo "Please initialize git first or run this from the project root"
    exit 1
fi

echo ""
echo "Step 1: Removing folders from git tracking..."

# Remove folders from git but keep them locally
git rm -r --cached _sources/ 2>/dev/null || echo "  _sources/ not in git"
git rm -r --cached _data/ 2>/dev/null || echo "  _data/ not in git"
git rm -r --cached _images/ 2>/dev/null || echo "  _images/ not in git"

echo -e "${GREEN}✓ Folders removed from git tracking${NC}"

echo ""
echo "Step 2: Verifying .gitignore..."

# Check if .gitignore has the entries
if ! grep -q "^_sources/" .gitignore; then
    echo "_sources/" >> .gitignore
    echo "  Added _sources/ to .gitignore"
fi

if ! grep -q "^_images/" .gitignore; then
    echo "_images/" >> .gitignore
    echo "  Added _images/ to .gitignore"
fi

if ! grep -q "^_data" .gitignore; then
    echo "_data/" >> .gitignore
    echo "  Added _data/ to .gitignore"
fi

echo -e "${GREEN}✓ .gitignore verified${NC}"

echo ""
echo "Step 3: Committing changes..."

git add .gitignore
git commit -m "Remove underscore folders from git tracking

- Removed _sources/, _data/, and _images/ from repository
- Updated .gitignore to exclude these folders
- Folders remain available locally for development"

echo -e "${GREEN}✓ Changes committed${NC}"

echo ""
echo "Step 4: Pushing to GitHub..."
echo -e "${YELLOW}Note: This will push to the current branch${NC}"
read -p "Push to GitHub now? (yes/no): " push_confirm

if [ "$push_confirm" = "yes" ]; then
    CURRENT_BRANCH=$(git branch --show-current)
    git push origin "$CURRENT_BRANCH"
    echo -e "${GREEN}✓ Changes pushed to GitHub${NC}"
else
    echo -e "${YELLOW}Skipped push. Run 'git push' manually when ready${NC}"
fi

echo ""
echo -e "${GREEN}Done!${NC}"
echo ""
echo "Summary:"
echo "  • Folders removed from GitHub: _sources/, _data/, _images/"
echo "  • Folders still available locally"
echo "  • .gitignore updated to prevent future commits"
echo ""
echo "To verify, check your GitHub repository - the folders should be gone"
echo "but they will still exist in your local project directory."

# Made with Bob