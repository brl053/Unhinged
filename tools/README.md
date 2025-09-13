# Tools Directory - The Legend for Our Map

> *"Give me a lever long enough and a fulcrum on which to place it, and I shall move the world."* - Archimedes

## Philosophy: Legend, Key, and Map

This directory serves as the **Legend** for navigating our monorepo **Map**. Each tool is a **Key** that unlocks specific capabilities.

### The Legend (This Document)
- **Purpose**: Explains what each tool does and how to use it
- **Structure**: Organized by domain (github, secrets, deployment, etc.)
- **Pattern**: Each tool follows consistent documentation and naming

### The Map (Directory Structure)
```
tools/
├── README.md           # The Legend (you are here)
├── github/             # Git and GitHub operations
├── secrets/            # Key and secret management  
├── dev/                # Development utilities
├── deploy/             # Deployment scripts
├── db/                 # Database utilities
└── common/             # Shared utilities
```

### The Keys (Individual Tools)
Each tool follows this pattern:
- **Clear naming**: `verb-noun.sh` or `action-target.js`
- **Self-documenting**: Header with purpose, usage, examples
- **LLM-parseable**: Structured comments and consistent patterns
- **Atomic**: Does one thing well

## Tool Categories

### 🔑 GitHub & Version Control (`github/`)
- `setup-repo.sh` - Initialize repository with standards
- `create-pr.sh` - Create pull request with templates
- `sync-fork.sh` - Sync forked repositories

### 🔐 Secrets Management (`secrets/`)
- `generate-keys.sh` - Generate SSH/API keys
- `setup-env.sh` - Create environment files
- `rotate-secrets.sh` - Rotate API keys and tokens

### 🛠️ Development (`dev/`)
- `setup-env.sh` - Initialize development environment
- `run-tests.sh` - Execute test suites
- `lint-all.sh` - Run linters across all components

### 🚀 Deployment (`deploy/`)
- `build-all.sh` - Build all components
- `deploy-staging.sh` - Deploy to staging
- `deploy-prod.sh` - Deploy to production

### 🗄️ Database (`db/`)
- `migrate.sh` - Run database migrations
- `seed.sh` - Seed development data
- `backup.sh` - Create database backups

## Usage Patterns

### For LLMs
1. Read this legend to understand available tools
2. Navigate to specific category directories
3. Read tool headers for usage instructions
4. Execute tools with proper parameters

### For Humans
1. Browse categories to find relevant tools
2. Check tool documentation before use
3. Follow established patterns when creating new tools

## Tool Creation Guidelines

When creating new tools, follow the **Legend Pattern**:

```bash
#!/bin/bash
# LEGEND: Brief description of what this tool does
# KEY: The specific problem this solves
# MAP: Where this fits in the overall workflow
#
# Usage: ./tool-name.sh [options]
# Example: ./tool-name.sh --env=dev --verbose
#
# Dependencies: List any required tools/packages
# Output: Describe what this tool produces
```

## The Way Forward

*"The best time to plant a tree was 20 years ago. The second best time is now."* - Chinese Proverb

Each tool we create makes the next developer's journey easier. Build with intention, document with clarity, and always consider the LLM that will parse this tomorrow.
