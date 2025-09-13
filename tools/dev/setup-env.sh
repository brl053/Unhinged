#!/bin/bash
# LEGEND: Initialize complete development environment for Unhinged monorepo
# KEY: Solves the problem of complex multi-step environment setup
# MAP: Orchestrates all setup tools to create ready-to-code environment
#
# Usage: ./setup-env.sh [--skip-docker] [--skip-npm]
# Example: ./setup-env.sh --skip-docker
#
# Dependencies: docker, docker-compose, node, npm, java
# Output: Fully configured development environment

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKIP_DOCKER=false
SKIP_NPM=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-docker)
            SKIP_DOCKER=true
            shift
            ;;
        --skip-npm)
            SKIP_NPM=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--skip-docker] [--skip-npm]"
            echo "Initialize complete development environment"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

cd "$REPO_ROOT"

echo "🚀 Initializing Unhinged development environment..."

# 1. Setup repository
echo "📦 Setting up repository..."
./tools/github/setup-repo.sh

# 2. Create secrets
echo "🔐 Setting up secrets..."
./tools/secrets/setup-env.sh --env=development

# 3. Install frontend dependencies
if [ "$SKIP_NPM" = false ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# 4. Build backend
echo "🔨 Building backend..."
cd backend
./gradlew build -x test  # Skip tests for faster setup
cd ..

# 5. Start Docker services
if [ "$SKIP_DOCKER" = false ]; then
    echo "🐳 Starting Docker services..."
    docker-compose up -d database llm
    
    # Wait for services to be ready
    echo "⏳ Waiting for services to start..."
    sleep 10
fi

echo "✅ Development environment ready!"
echo ""
echo "🎯 Next steps:"
echo "1. Edit secrets/.env.development with your actual values"
echo "2. Start backend: docker-compose up backend"
echo "3. Start frontend: cd frontend && npm start"
echo "4. Access application at localhost:8081"
echo ""
echo "🛠️  Available tools:"
echo "- tools/README.md - Tool documentation"
echo "- docs/mono_repo_init.md - Detailed setup guide"
