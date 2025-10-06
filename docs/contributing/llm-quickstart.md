# 🤖 LLM Quickstart Guide - Unhinged Platform

> **Target Audience**: AI Assistants (Claude, GPT, etc.) contributing to the Unhinged platform
> **Purpose**: Provide structured, machine-readable instructions for understanding and contributing to this monorepo
> **Philosophy**: Follow the project's "Legend/Key/Map" approach - provide clear navigation and context

## 🗺️ Project Map (Essential Context)

### Architecture Overview
```
Unhinged Platform (Monorepo)
├── 🏗️ Backend (Kotlin + Clean Architecture)
│   ├── Domain Layer (Business Logic)
│   ├── Application Layer (Use Cases)
│   ├── Infrastructure Layer (External Services)
│   └── Presentation Layer (HTTP/gRPC APIs)
├── 🎨 Frontend (TypeScript + React)
├── 🐍 Services (Python Microservices)
│   ├── whisper-tts (Audio Processing)
│   ├── vision-ai (Image Processing)
│   └── research-orchestrator (AI Research)
├── 📡 Proto (gRPC Definitions)
├── 🐳 Docker (Containerization)
└── 📚 Docs (Documentation)
```

### Key Technologies
- **Backend**: Kotlin, Ktor, Clean Architecture, gRPC
- **Frontend**: TypeScript, React, Webpack
- **Services**: Python, Flask, PyTorch, Transformers
- **Infrastructure**: Docker, PostgreSQL, Kafka
- **Build**: Gradle, Make, Protobuf

## 🚀 Quick Start Protocol

### 1. Understanding the Codebase
```bash
# Get project overview
make help

# Check current status
make status

# View project structure
tree -L 2 -I 'node_modules|build|.git'
```

### 2. Essential Files to Read First
1. **`Makefile`** - All available commands and workflows
2. **`README.md`** - Project overview and setup
3. **`docs/architecture/COMPLETE-PROJECT-SUMMARY.md`** - Comprehensive architecture
4. **`backend/PROJECT_STRUCTURE.md`** - Backend organization
5. **`docker-compose.yml`** - Service definitions

### 3. Development Environment Setup
```bash
# Initial setup (run once)
make setup

# Start development environment
make dev

# Or start full stack
make dev-full
```

## 📋 Command Reference (Make Targets)

### Essential Commands
| Command | Purpose | When to Use |
|---------|---------|-------------|
| `make help` | Show all available commands | Always start here |
| `make status` | Check service health | Before making changes |
| `make setup` | Initial project setup | First time setup |
| `make dev` | Start development environment | Daily development |

### Service Management
| Command | Purpose | Use Case |
|---------|---------|----------|
| `make up` | Start all services | Full system testing |
| `make down` | Stop all services | Clean shutdown |
| `make restart` | Restart all services | After config changes |
| `make logs` | View all service logs | Debugging |

### Backend Development
| Command | Purpose | Use Case |
|---------|---------|----------|
| `make backend-build` | Build backend | After code changes |
| `make backend-run` | Run backend locally | Development |
| `make backend-test` | Run tests | Before commits |
| `make backend-clean` | Clean build artifacts | Build issues |

### Database Operations
| Command | Purpose | Use Case |
|---------|---------|----------|
| `make db-up` | Start database only | Backend development |
| `make db-shell` | Connect to database | Data inspection |
| `make db-migrate` | Run migrations | Schema updates |
| `make db-reset` | Reset database | Clean slate |

### Protobuf Operations
| Command | Purpose | Use Case |
|---------|---------|----------|
| `make proto-gen` | Generate protobuf code | After .proto changes |
| `make proto-clean` | Clean generated code | Build issues |
| `make proto-count` | Show proto statistics | Code review |

## 🎯 Common Workflows

### Adding New Features
1. **Understand the domain**: Read relevant docs in `docs/architecture/`
2. **Check current status**: `make status`
3. **Start development**: `make dev`
4. **Make changes**: Follow clean architecture patterns
5. **Test changes**: `make backend-test`
6. **Update docs**: Update relevant documentation

### Debugging Issues
1. **Check service health**: `make status`
2. **View logs**: `make logs` or `make logs-backend`
3. **Test individual components**: `make test-db`, `make test-tts`
4. **Check ports**: `make ports`
5. **Clean and rebuild**: `make clean && make setup`

### Working with Services
1. **Vision AI**: See `VISION_SETUP.md` for image processing
2. **Audio Processing**: Check `voice-test.html` for TTS testing
3. **Database**: Use `make db-shell` for direct access
4. **gRPC**: Use `make test-grpc` for endpoint testing

## 🧠 LLM-Specific Guidelines

### Code Analysis Approach
1. **Start with architecture docs** - Understand the big picture
2. **Use codebase-retrieval tool** - Get specific code context
3. **Follow clean architecture** - Respect domain boundaries
4. **Check existing patterns** - Look for similar implementations

### Making Changes
1. **Always check status first**: `make status`
2. **Use appropriate Make targets**: Don't run raw commands
3. **Follow naming conventions**: Check existing code patterns
4. **Update documentation**: Keep docs in sync with code
5. **Test thoroughly**: Use provided test commands

### Understanding Dependencies
- **Gradle**: Backend dependency management
- **Docker**: Service orchestration
- **Protobuf**: API contract definitions
- **Make**: Development workflow automation

## 📚 Documentation Structure

### Architecture Documentation
- `docs/architecture/` - System design and patterns
- `docs/backend/` - Backend-specific documentation
- `docs/frontend/` - Frontend-specific documentation

### Development Documentation
- `docs/development/` - Development workflows and guides
- `docs/testing/` - Testing strategies and guides
- `docs/deployment/` - Deployment and infrastructure

### API Documentation
- `docs/api/` - API specifications and examples
- `proto/` - gRPC service definitions

## 🔧 Troubleshooting Guide

### Common Issues
1. **Services not starting**: Check `make status`, restart with `make restart`
2. **Build failures**: Clean with `make clean`, then `make setup`
3. **Port conflicts**: Check `make ports`, stop conflicting services
4. **Database issues**: Try `make db-reset` (WARNING: destroys data)
5. **Proto generation fails**: Run `make proto-clean && make proto-gen`

### Health Checks
```bash
# Complete health check
make health

# Individual service checks
make test-db
make test-tts
curl http://localhost:8080/health
```

## 🎨 Project Philosophy

### Clean Architecture Principles
- **Domain-driven design**: Business logic in domain layer
- **Dependency inversion**: Infrastructure depends on domain
- **Separation of concerns**: Each layer has specific responsibilities
- **Testability**: Easy to test each layer independently

### Development Principles
- **Make-driven workflow**: All operations through Makefile
- **Docker-first**: Services run in containers
- **Proto-driven APIs**: gRPC contracts define interfaces
- **Documentation-driven**: Keep docs current with code

## 🚦 Next Steps

1. **Run the quickstart**: `make help && make status && make dev`
2. **Explore the codebase**: Use the codebase-retrieval tool
3. **Read architecture docs**: Start with `COMPLETE-PROJECT-SUMMARY.md`
4. **Try making changes**: Follow the workflows above
5. **Update documentation**: Keep this guide current

---

**Remember**: This is a living document. Update it when you discover new patterns or workflows!
