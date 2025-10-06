# 📚 Unhinged Platform Documentation

> **Welcome to the comprehensive documentation system for the Unhinged platform**
> **Philosophy**: "Legend/Key/Map" approach - Clear navigation, structured information, AI-assistant friendly

## 🗺️ Documentation Map

### 🚀 Quick Start
- **[LLM Quickstart Guide](contributing/llm-quickstart.md)** - Essential guide for AI assistants
- **[Development Workflow](development/workflow.md)** - Complete development lifecycle
- **[Makefile Reference](development/makefile-reference.md)** - All available commands

### 🏗️ Architecture & Design
- **[Complete Project Summary](architecture/COMPLETE-PROJECT-SUMMARY.md)** - System overview
- **[Domain-Driven Design](architecture/domain-driven-design.md)** - Architecture principles
- **[Proto-Driven Implementation](architecture/proto-driven-implementation.md)** - API-first approach

### 🛠️ Development
- **[Project Structure](development/project-structure.md)** - Codebase organization
- **[Walking Skeleton Approach](development/walking-skeleton-approach.md)** - Development methodology
- **[Testing Strategy](testing/strategy.md)** - Testing approaches

### 🚀 Services
- **[Services Overview](services/overview.md)** - All microservices
- **[Vision AI Setup](../VISION_SETUP.md)** - Image processing service
- **[Audio Processing](../voice-test.html)** - TTS and speech services

### 📡 APIs
- **[API Endpoints](api/endpoints.md)** - REST API documentation
- **[Generated API Reference](api/generated-api-reference.md)** - Auto-generated from proto files

### 🎨 Frontend
- **[Component Architecture](frontend/component-architecture.md)** - React component structure
- **[Design System](design-system/DESIGN_SYSTEM_SPECIFICATIONS.md)** - UI/UX guidelines

## 🤖 For AI Assistants

### Essential Reading Order
1. **[LLM Quickstart Guide](contributing/llm-quickstart.md)** - Start here!
2. **[Makefile Reference](development/makefile-reference.md)** - All commands
3. **[Development Workflow](development/workflow.md)** - How to contribute
4. **[Project Structure](development/project-structure.md)** - Codebase layout

### Key Commands
```bash
# Get help and status
make help
make status

# Development workflow
make setup
make dev
make test

# Documentation
make docs-update    # Update all documentation
make docs-watch     # Watch for changes
make docs-validate  # Validate documentation
```

## 📋 Documentation System

### Automated Documentation
This documentation system automatically updates when code changes:

- **Makefile Reference** - Generated from Makefile analysis
- **Project Structure** - Generated from codebase analysis  
- **API Reference** - Generated from proto files
- **Service Overview** - Generated from services directory

### Update Commands
```bash
make docs-update      # Update all documentation
make docs-makefile    # Update Makefile reference only
make docs-structure   # Update project structure only
make docs-validate    # Validate documentation
make docs-watch       # Watch for changes and auto-update
make docs-ci-setup    # Set up CI/CD integration
```

### Documentation Loop
The system includes:
- **File watching** - Monitors key files for changes
- **Auto-generation** - Updates docs when changes detected
- **Validation** - Ensures documentation consistency
- **CI integration** - GitHub Actions workflow
- **Pre-commit hooks** - Validates docs before commits

## 🎯 Documentation Philosophy

### Legend/Key/Map Approach
Every document follows this structure:
1. **Legend** - What this document covers
2. **Key** - Essential information and quick reference
3. **Map** - Detailed navigation and relationships

### AI-Assistant Friendly
- **Structured information** - Clear hierarchies and sections
- **Machine-readable** - Consistent formatting and patterns
- **Context-rich** - Comprehensive background information
- **Action-oriented** - Clear next steps and workflows

### Living Documentation
- **Auto-generated** - Stays current with code changes
- **Validated** - Consistency checks and link validation
- **Versioned** - Tracked with code changes
- **Collaborative** - Easy to contribute and maintain

## 📊 Documentation Status

**Last Update**: Auto-generated on every `make docs-update`

### Coverage
- ✅ **Architecture** - Complete system documentation
- ✅ **Development** - Comprehensive workflow guides
- ✅ **APIs** - Auto-generated from proto files
- ✅ **Services** - Auto-generated service overview
- ✅ **Frontend** - Component and design documentation
- ✅ **Testing** - Strategy and implementation guides

### Quality Metrics
- **Consistency** - Automated validation
- **Completeness** - Coverage tracking
- **Currency** - Auto-update system
- **Accessibility** - AI-assistant optimized

## 🚀 Getting Started

### For Developers
1. Read the [Development Workflow](development/workflow.md)
2. Run `make setup` to initialize the project
3. Use `make help` to see all available commands
4. Follow the workflow in [Makefile Reference](development/makefile-reference.md)

### For AI Assistants
1. **Start with**: [LLM Quickstart Guide](contributing/llm-quickstart.md)
2. **Understand commands**: [Makefile Reference](development/makefile-reference.md)
3. **Learn structure**: [Project Structure](development/project-structure.md)
4. **Follow workflows**: [Development Workflow](development/workflow.md)

### For Contributors
1. Read the [Contributing Guidelines](contributing/llm-quickstart.md)
2. Set up the development environment with `make setup`
3. Use `make docs-update` to keep documentation current
4. Follow the established patterns and conventions

## 🔧 Maintenance

### Keeping Documentation Current
```bash
# Manual update
make docs-update

# Automatic watching
make docs-watch

# Validation
make docs-validate

# CI setup
make docs-ci-setup
```

### Adding New Documentation
1. Create new `.md` files in appropriate directories
2. Follow the Legend/Key/Map structure
3. Update this README with links
4. Run `make docs-update` to refresh auto-generated content

### Troubleshooting
- **Broken links**: Run `make docs-validate`
- **Outdated content**: Run `make docs-update`
- **Missing documentation**: Check the services overview
- **CI issues**: Verify GitHub Actions workflow

---

**Remember**: This documentation system is designed to be both human and AI-assistant friendly. It automatically stays current with code changes and provides comprehensive guidance for all contributors.
