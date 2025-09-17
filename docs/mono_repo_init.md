# Monorepo Initialization Guide

> *"The journey of a thousand miles begins with one step."* - Lao Tzu

## Quick Start (Clone and Go)

```bash
# 1. Clone the repository
git clone git@github.com:brl053/Unhinged.git
cd Unhinged

# 2. Initialize secrets (git-ignored)
./tools/secrets/setup-env.sh --env=development

# 3. Start the stack
docker-compose up --build

# 4. Start frontend (in new terminal)
cd frontend && npm install && npm start

# 5. Access at localhost:8081
```

## The Legend/Key/Map Philosophy

This monorepo follows a **Legend/Key/Map** philosophy:

- **Legend** = Documentation that explains the territory
- **Key** = Tools that unlock capabilities  
- **Map** = Structure that shows relationships

### Directory Structure (The Map)
```
Unhinged/
├── .augment/           # Agent configuration and wisdom
├── tools/              # The Keys (utilities and scripts)
├── docs/               # The Legend (documentation)
├── secrets/            # Environment files (git-ignored)
├── backend/            # Kotlin/Spring Boot service
├── frontend/           # TypeScript/React application
├── database/           # PostgreSQL configuration
└── llm/                # Ollama service
```

## Initial Setup Steps

### 1. Repository Setup
```bash
# Initialize git configuration
./tools/github/setup-repo.sh --remote-url=git@github.com:brl053/Unhinged.git

# This creates:
# - .gitignore with proper exclusions
# - Git commit message template
# - Remote configuration
```

### 2. Secrets Management
```bash
# Create environment files
./tools/secrets/setup-env.sh --env=development

# Edit secrets (REQUIRED)
nano secrets/.env.development

# Key variables to update:
# - JWT_SECRET (for production)
# - GITHUB_TOKEN (if using GitHub integration)
# - Database passwords (for production)
```

### 3. Development Environment
```bash
# Install dependencies
cd frontend && npm install
cd ../backend && ./gradlew build

# Start services
docker-compose up --build  # Backend, DB, LLM
npm start                  # Frontend (from /frontend)
```

## Architecture Overview

### Services
- **Backend** (port 8080): Kotlin/Spring Boot API
- **Frontend** (port 3000): TypeScript/React SPA  
- **Database** (port 5432): PostgreSQL 15
- **LLM** (port 11434): Ollama service

### Data Flow
```
Frontend (3000) → Backend (8080) → Database (5432)
                      ↓
                  LLM (11434)
```

## Development Workflow

### Daily Development
1. `docker-compose up` - Start backend services
2. `cd frontend && npm start` - Start frontend
3. Make changes, test, commit
4. Use tools in `tools/` directory for common tasks

### Testing
```bash
# Backend tests
cd backend && ./gradlew test

# Frontend tests  
cd frontend && npm test
```

### Deployment
```bash
# Build all components
./tools/deploy/build-all.sh

# Deploy to staging
./tools/deploy/deploy-staging.sh
```

## File Organization Patterns

### Documentation (TSDoc/JavaDoc Style)
```typescript
/**
 * LEGEND: Brief description of the function/class
 * KEY: The specific problem this solves
 * MAP: How this fits in the overall architecture
 * 
 * @param param1 Description of parameter
 * @returns Description of return value
 * @example
 * ```typescript
 * const result = myFunction('example');
 * ```
 */
```

### Tool Scripts
```bash
#!/bin/bash
# LEGEND: What this tool does
# KEY: Problem it solves
# MAP: Where it fits in workflow
#
# Usage: ./script.sh [options]
# Dependencies: List required tools
# Output: What this produces
```

## Troubleshooting

### Common Issues
1. **Port conflicts**: Check if services are already running
2. **Permission errors**: Ensure scripts are executable (`chmod +x`)
3. **Missing secrets**: Run `./tools/secrets/setup-env.sh`
4. **Docker issues**: Try `docker-compose down && docker-compose up --build`

### Getting Help
1. Check `tools/README.md` for available utilities
2. Review `.augment/agent-instructions.md` for patterns
3. Consult `docs/` directory for specific guides

---

*"The best time to plant a tree was 20 years ago. The second best time is now."*

This initialization guide gets you started quickly while establishing the cultural foundations for long-term success.
