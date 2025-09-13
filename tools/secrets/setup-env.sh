#!/bin/bash
# LEGEND: Create and manage environment files for Unhinged monorepo
# KEY: Solves the problem of consistent environment setup across components
# MAP: Foundation for secrets management in tools/secrets/
#
# Usage: ./setup-env.sh [--env=<environment>] [--component=<name>]
# Example: ./setup-env.sh --env=development --component=backend
#
# Dependencies: None (pure bash)
# Output: Environment files in secrets/ directory (git-ignored)

set -e

# Default values
ENVIRONMENT="development"
COMPONENT=""
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SECRETS_DIR="$REPO_ROOT/secrets"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --env=*)
            ENVIRONMENT="${1#*=}"
            shift
            ;;
        --component=*)
            COMPONENT="${1#*=}"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--env=<environment>] [--component=<name>]"
            echo "Create environment files for Unhinged components"
            echo "Environments: development, staging, production"
            echo "Components: backend, frontend, database, llm"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "🔐 Setting up environment for: $ENVIRONMENT"

# Create secrets directory
mkdir -p "$SECRETS_DIR"

# Create main environment file
ENV_FILE="$SECRETS_DIR/.env.$ENVIRONMENT"

if [ ! -f "$ENV_FILE" ]; then
    echo "📝 Creating $ENV_FILE..."
    cat > "$ENV_FILE" << EOF
# Unhinged Environment Configuration - $ENVIRONMENT
# LEGEND: Environment variables for the Unhinged monorepo
# KEY: Centralizes configuration management
# MAP: Used by all components in the stack

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=unhinged_db
DB_USER=postgres
DB_PASSWORD=postgres
DATABASE_URL=postgresql://\${DB_USER}:\${DB_PASSWORD}@\${DB_HOST}:\${DB_PORT}/\${DB_NAME}

# Backend Configuration
BACKEND_PORT=8080
BACKEND_HOST=localhost
JWT_SECRET=your-jwt-secret-here-change-in-production
API_BASE_URL=http://\${BACKEND_HOST}:\${BACKEND_PORT}

# Frontend Configuration
FRONTEND_PORT=3000
FRONTEND_HOST=localhost
REACT_APP_API_URL=\${API_BASE_URL}

# LLM Configuration
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
OLLAMA_BASE_URL=http://\${OLLAMA_HOST}:\${OLLAMA_PORT}

# GitHub Configuration (optional)
GITHUB_TOKEN=your-github-token-here
GITHUB_REPO=brl053/Unhinged

# Development Tools
LOG_LEVEL=debug
DEBUG_MODE=true
EOF
fi

# Create component-specific files if requested
if [ -n "$COMPONENT" ]; then
    COMPONENT_FILE="$SECRETS_DIR/.env.$COMPONENT.$ENVIRONMENT"
    
    case "$COMPONENT" in
        backend)
            if [ ! -f "$COMPONENT_FILE" ]; then
                echo "📝 Creating backend-specific environment..."
                cat > "$COMPONENT_FILE" << EOF
# Backend-specific environment variables
SPRING_PROFILES_ACTIVE=$ENVIRONMENT
SERVER_PORT=\${BACKEND_PORT}
SPRING_DATASOURCE_URL=\${DATABASE_URL}
SPRING_DATASOURCE_USERNAME=\${DB_USER}
SPRING_DATASOURCE_PASSWORD=\${DB_PASSWORD}
OLLAMA_API_URL=\${OLLAMA_BASE_URL}
EOF
            fi
            ;;
        frontend)
            if [ ! -f "$COMPONENT_FILE" ]; then
                echo "📝 Creating frontend-specific environment..."
                cat > "$COMPONENT_FILE" << EOF
# Frontend-specific environment variables
PORT=\${FRONTEND_PORT}
REACT_APP_API_BASE_URL=\${API_BASE_URL}
REACT_APP_ENVIRONMENT=$ENVIRONMENT
GENERATE_SOURCEMAP=true
EOF
            fi
            ;;
        *)
            echo "⚠️  Unknown component: $COMPONENT"
            echo "Available components: backend, frontend"
            ;;
    esac
fi

# Create secrets README
README_FILE="$SECRETS_DIR/README.md"
if [ ! -f "$README_FILE" ]; then
    cat > "$README_FILE" << 'EOF'
# Secrets Directory

This directory contains environment files and secrets for the Unhinged monorepo.

## Files
- `.env.development` - Development environment variables
- `.env.staging` - Staging environment variables  
- `.env.production` - Production environment variables
- `.env.<component>.<env>` - Component-specific overrides

## Usage
1. Copy the appropriate .env file for your environment
2. Update values as needed for your local setup
3. Source the file: `source .env.development`
4. Or use with docker-compose: `docker-compose --env-file secrets/.env.development up`

## Security
- This directory is git-ignored
- Never commit actual secrets to version control
- Use placeholder values in templates
- Rotate secrets regularly

## Generation
Use `tools/secrets/setup-env.sh` to generate new environment files.
EOF
fi

echo "✅ Environment setup complete!"
echo "📁 Files created in: $SECRETS_DIR"
echo "🔧 Edit the files to add your actual secrets"
echo ""
echo "Next steps:"
echo "1. Update placeholder values in $ENV_FILE"
echo "2. Source the file: source $ENV_FILE"
echo "3. Test with: echo \$DATABASE_URL"
