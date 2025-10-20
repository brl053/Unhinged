#!/bin/bash
# LEGEND: Initialize GitHub repository with Unhinged monorepo standards
# KEY: Solves the problem of consistent repo setup across environments
# MAP: Foundation tool for GitHub workflow in tools/github/
#
# Usage: ./setup-repo.sh [--remote-url=<url>] [--branch=<name>]
# Example: ./setup-repo.sh --remote-url=git@github.com:brl053/Unhinged.git --branch=main
#
# Dependencies: git, gh (GitHub CLI optional)
# Output: Configured repository with proper remotes and branches

set -e  # Exit on any error

# Default values
REMOTE_URL=""
BRANCH="main"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --remote-url=*)
            REMOTE_URL="${1#*=}"
            shift
            ;;
        --branch=*)
            BRANCH="${1#*=}"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--remote-url=<url>] [--branch=<name>]"
            echo "Initialize GitHub repository with Unhinged standards"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "🔧 Setting up Unhinged repository..."

# Navigate to repo root
cd "$REPO_ROOT"

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git branch -M "$BRANCH"
fi

# Add remote if provided
if [ -n "$REMOTE_URL" ]; then
    echo "🔗 Adding remote origin: $REMOTE_URL"
    git remote add origin "$REMOTE_URL" 2>/dev/null || git remote set-url origin "$REMOTE_URL"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Secrets and Environment
secrets/
.env
.env.local
.env.*.local

# Dependencies
node_modules/
*/node_modules/

# Build outputs
build/
dist/
target/
*/build/
*/dist/
*/target/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Gradle
.gradle/
gradle/wrapper/gradle-wrapper.jar

# Docker
.docker/
EOF
fi

# Set up git hooks directory
mkdir -p .githooks

# Create commit message template
cat > .gitmessage << 'EOF'
# LEGEND: Brief description of what this commit accomplishes
# KEY: The specific problem this solves or feature this adds
# MAP: How this fits into the overall project architecture
#
# Type: feat|fix|docs|style|refactor|test|chore
# Scope: backend|frontend|database|llm|tools|docs|config
#
# Example:
# feat(backend): add user authentication service
# 
# LEGEND: Implements JWT-based authentication for API endpoints
# KEY: Solves security requirement for protected routes
# MAP: Foundation for user management system in backend architecture

EOF

git config commit.template .gitmessage

echo "✅ Repository setup complete!"
echo "📍 Remote: $(git remote get-url origin 2>/dev/null || echo 'Not set')"
echo "🌿 Branch: $(git branch --show-current)"
echo ""
echo "Next steps:"
echo "1. Review .gitignore and adjust if needed"
echo "2. Create secrets/ directory for local development"
echo "3. Run: git add . && git commit -m 'Initial commit'"
