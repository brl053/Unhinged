# 📖 Makefile Reference - Unhinged Platform

> **Purpose**: Comprehensive documentation of all Make targets and development workflows
> **Audience**: Developers and AI assistants working on the Unhinged platform
> **Last Updated**: Auto-generated on 2025-10-20 19:14:38

## 🎯 Quick Reference

### Most Used Commands
```bash
make help            # Show this help message
make status          # Show build system status and performance metrics
make setup           # Initial project setup
make dev             # Start development environment
make clean           # Clean build artifacts (smart cleanup)
```

## 🔧 Setup and Installation

#### `make setup`
**Purpose**: Initial project setup
**Usage**: `make setup`
**Actions**:
- $(call require,docker)
- $(call require,curl)

#### `make generate`
**Purpose**: Generate all build artifacts (polyglot proto clients, registry) [use FORCE=1 to bypass cache]
**Usage**: `make generate`
**Actions**:
- $(call log_info,🔧 Generating all build artifacts...)
- $(if $(FORCE),@echo "$(YELLOW)🔥 Force rebuild enabled - bypassing cache$(RESET)",@echo "$(YELLOW)💾 Using cache for faster builds$(RESET)")

#### `make generate-clients`
**Purpose**: Generate client libraries from protos [use FORCE=1 to bypass cache]
**Usage**: `make generate-clients`
**Actions**:
- $(call log_info,🔧 Generating client libraries...)
- $(if $(FORCE),@echo "$(YELLOW)🔥 Force rebuild enabled - bypassing cache$(RESET)",@echo "$(YELLOW)💾 Using cache for faster builds$(RESET)")

#### `make setup-python`
**Purpose**: Setup Python virtual environment and install dependencies
**Usage**: `make setup-python`
**Actions**:
- $(call log_info,🐍 Setting up Python virtual environment...)

#### `make python-deps`
**Purpose**: Install/update Python dependencies
**Usage**: `make python-deps`
**Actions**:
- $(call log_info,📦 Installing Python dependencies...)

#### `make gateway-gen`
**Purpose**: Generate presentation gateway from proto annotations
**Usage**: `make gateway-gen`
**Actions**:
- $(call log_info,🌐 Generating presentation gateway...)

#### `make gateway-dev`
**Purpose**: Start presentation gateway in development mode
**Usage**: `make gateway-dev`
**Actions**:
- $(call log_info,🚀 Starting presentation gateway...)

#### `make gateway-build`
**Purpose**: Build presentation gateway
**Usage**: `make gateway-build`
**Actions**:
- $(call log_info,🔨 Building presentation gateway...)
- $(call log_success,Presentation gateway built)

#### `make build-full`
**Purpose**: Build complete environment with all services
**Usage**: `make build-full`
**Actions**:
- $(call log_info,🚀 Building complete environment...)
- $(call log_success,Full build completed)

#### `make explain`
**Purpose**: Explain a build target (usage: make explain TARGET=dev-fast)
**Usage**: `make explain`
**Actions**:
- $(call log_info,📋 Explaining build target: $(or $(TARGET),dev-fast))

#### `make list`
**Purpose**: List all available build targets
**Usage**: `make list`
**Actions**:
- $(call log_info,📋 Available build targets...)

#### `make profile`
**Purpose**: Profile build performance (usage: make profile TARGET=dev-fast)
**Usage**: `make profile`
**Actions**:
- $(call log_info,⚡ Profiling build target: $(or $(TARGET),dev-fast))

#### `make watch`
**Purpose**: Watch mode for continuous building (usage: make watch TARGET=backend-compile)
**Usage**: `make watch`
**Actions**:
- $(call log_info,👁️ Starting watch mode for: $(or $(TARGET),backend-compile))

#### `make context`
**Purpose**: Generate AI context for development assistance
**Usage**: `make context`
**Actions**:
- $(call log_info,🤖 Generating development context...)

#### `make onboard`
**Purpose**: Generate developer onboarding guide
**Usage**: `make onboard`
**Actions**:
- $(call log_info,📚 Generating developer onboarding guide...)

#### `make explain-error`
**Purpose**: Explain build error (usage: make explain-error TARGET=dev-fast ERROR="error message")
**Usage**: `make explain-error`
**Actions**:
- $(call log_info,🔍 Explaining build error for: $(or $(TARGET),unknown))

#### `make performance`
**Purpose**: Generate build performance report
**Usage**: `make performance`
**Actions**:
- $(call log_info,📊 Generating performance report...)

#### `make metrics`
**Purpose**: Show current performance metrics
**Usage**: `make metrics`
**Actions**:
- $(call log_info,📊 Showing performance metrics...)

#### `make validate`
**Purpose**: Validate build system installation
**Usage**: `make validate`
**Actions**:
- $(call log_info,✅ Validating build system...)

#### `make start`
**Purpose**: Generate service registry and open system health dashboard
**Usage**: `make start`
**Actions**:
- $(call log_info,🏥 Starting System Health Command Center...)

#### `make watch-html`
**Purpose**: Watch for changes and auto-rebuild HTML files
**Usage**: `make watch-html`
**Actions**:
- $(call log_info,👀 Starting HTML build watcher...)

#### `make watch-html-verbose`
**Purpose**: Watch HTML files with verbose output
**Usage**: `make watch-html-verbose`
**Actions**:
- $(call log_info,👀 Starting HTML build watcher (verbose)...)

#### `make standardize-html`
**Purpose**: Standardize all HTML files to use consistent design system
**Usage**: `make standardize-html`
**Actions**:
- $(call log_info,🔧 Standardizing HTML files...)
- $(call log_success,HTML standardization complete)

#### `make start-services`
**Purpose**: Start Docker services only (database, kafka, etc.)
**Usage**: `make start-services`
**Actions**:
- $(call log_info,🐳 Starting Docker services...)

#### `make check-docker`
**Purpose**: Check Docker availability (with installation help)
**Usage**: `make check-docker`
**Actions**:
- echo "$(RED)❌ Docker not found$(RESET)"; \
- echo "$(YELLOW)🐳 Docker is required for Unhinged services$(RESET)"; \

#### `make help-docker-install`
**Purpose**: Guided Docker installation with verification
**Usage**: `make help-docker-install`
**Actions**:

#### `make verify-docker`
**Purpose**: Verify Docker installation
**Usage**: `make verify-docker`
**Actions**:
- echo "$(GREEN)✅ Docker binary found$(RESET)"; \

#### `make install-docker-interactive`
**Purpose**: Install Docker with interactive sudo prompts
**Usage**: `make install-docker-interactive`
**Actions**:
- echo "$(YELLOW)📦 Detected Ubuntu/Debian$(RESET)"; \

#### `make install-docker-automated`
**Purpose**: Auto-install Docker based on detected OS
**Usage**: `make install-docker-automated`
**Actions**:
- echo "$(YELLOW)📦 Detected Ubuntu/Debian$(RESET)"; \

#### `make check-dependencies`
**Purpose**: Check and install required dependencies interactively
**Usage**: `make check-dependencies`
**Actions**:

#### `make check-docker-interactive`
**Purpose**: Check Docker installation with interactive prompts
**Usage**: `make check-docker-interactive`
**Actions**:
- echo "$(RED)❌ Docker not found$(RESET)"; \
- echo "$(YELLOW)🐳 Docker is required for Unhinged services$(RESET)"; \

#### `make check-python-deps`
**Purpose**: Check Python dependencies
**Usage**: `make check-python-deps`
**Actions**:
- echo "$(YELLOW)📦 Installing Python dependencies...$(RESET)"; \

#### `make install-docker`
**Purpose**: Install Docker interactively
**Usage**: `make install-docker`
**Actions**:
- echo "$(YELLOW)📦 Detected Ubuntu/Debian - installing via apt$(RESET)"; \

#### `make install-docker-compose`
**Purpose**: Install Docker Compose
**Usage**: `make install-docker-compose`
**Actions**:

#### `make docs-makefile`
**Purpose**: Generate Makefile reference documentation
**Usage**: `make docs-makefile`
**Actions**:
- $(call log_info,📖 Generating Makefile documentation...)
- $(call log_success,Makefile documentation generated)

#### `make docs-structure`
**Purpose**: Generate project structure documentation
**Usage**: `make docs-structure`
**Actions**:
- $(call log_info,🏗️ Generating project structure documentation...)
- $(call log_success,Project structure documentation generated)

#### `make docs-validate`
**Purpose**: Validate documentation for consistency
**Usage**: `make docs-validate`
**Actions**:
- $(call log_info,🔍 Validating documentation...)
- $(call log_success,Documentation validation complete)

#### `make docs-serve`
**Purpose**: Serve documentation locally (if supported)
**Usage**: `make docs-serve`
**Actions**:
- $(call log_info,🌐 Starting documentation server...)
- (command -v python3 > /dev/null && cd docs && python3 -m http.server 8888) || \

#### `make docs-watch`
**Purpose**: Watch for changes and auto-update documentation
**Usage**: `make docs-watch`
**Actions**:
- $(call log_info,🔍 Starting documentation watcher...)

#### `make docs-ci-setup`
**Purpose**: Set up CI/CD integration for documentation
**Usage**: `make docs-ci-setup`
**Actions**:
- $(call log_info,🔧 Setting up CI integration...)
- $(call log_success,CI integration setup complete)

#### `make docs-comments`
**Purpose**: Extract and generate documentation from LLM comments
**Usage**: `make docs-comments`
**Actions**:
- $(call log_info,🤖 Extracting LLM comments from codebase...)
- $(call log_success,LLM comment documentation generated)

#### `make docs-validate-comments`
**Purpose**: Validate LLM comment consistency and quality
**Usage**: `make docs-validate-comments`
**Actions**:
- $(call log_info,🔍 Validating LLM comments...)
- $(call log_success,LLM comment validation complete)

#### `make docs-context-overview`
**Purpose**: Generate comprehensive project overview for LLM context warming
**Usage**: `make docs-context-overview`
**Actions**:
- $(call log_info,🤖 Generating LLM context overview...)
- $(call log_success,LLM context overview generated)

#### `make docs-context-paginate`
**Purpose**: Paginate through all comments (usage: make docs-context-paginate PAGE=1)
**Usage**: `make docs-context-paginate`
**Actions**:
- $(call log_info,📄 Showing comments page $(or $(PAGE),1)...)

#### `make docs-context-json`
**Purpose**: Generate project overview in JSON format
**Usage**: `make docs-context-json`
**Actions**:
- $(call log_info,🤖 Generating LLM context overview (JSON)...)

#### `make deps-build`
**Purpose**: Build the C dependency tracker
**Usage**: `make deps-build`
**Actions**:
- $(call log_info,🔨 Building dependency tracker...)
- cmake .. && make

#### `make deps-analyze`
**Purpose**: Analyze all dependencies in monorepo
**Usage**: `make deps-analyze`
**Actions**:
- $(call log_info,🔍 Analyzing dependencies...)

#### `make deps-graph`
**Purpose**: Generate dependency visualization
**Usage**: `make deps-graph`
**Actions**:
- $(call log_info,📊 Generating dependency graph...)

#### `make deps-validate`
**Purpose**: Validate dependency consistency
**Usage**: `make deps-validate`
**Actions**:
- $(call log_info,🔍 Validating dependencies...)
- $(call log_success,Dependency validation complete)

#### `make deps-feature-dag`
**Purpose**: Generate feature dependency DAG
**Usage**: `make deps-feature-dag`
**Actions**:
- $(call log_info,🗺️ Generating feature DAG...)

#### `make lint`
**Purpose**: Run polyglot linter on codebase
**Usage**: `make lint`
**Actions**:
- $(call log_info,🔍 Running polyglot linter...)
- $(call log_success,Linting complete)

#### `make lint-llm`
**Purpose**: Run polyglot linter with LLM-specific rationale
**Usage**: `make lint-llm`
**Actions**:
- $(call log_info,🤖 Running LLM-biased polyglot linter...)
- $(call log_success,LLM-biased linting complete)

#### `make lint-json`
**Purpose**: Run polyglot linter with JSON output
**Usage**: `make lint-json`
**Actions**:
- $(call log_info,📊 Running polyglot linter (JSON output)...)

#### `make check-lint`
**Purpose**: Pure function: Run linting analysis
**Usage**: `make check-lint`
**Actions**:

#### `make check-format-python`
**Purpose**: Pure function: Check Python code formatting
**Usage**: `make check-format-python`
**Actions**:

#### `make check-format-typescript`
**Purpose**: Pure function: Check TypeScript/JavaScript formatting
**Usage**: `make check-format-typescript`
**Actions**:

#### `make check-format-json`
**Purpose**: Pure function: Validate JSON files
**Usage**: `make check-format-json`
**Actions**:

#### `make check-deps-available`
**Purpose**: Pure function: Verify dependency consistency
**Usage**: `make check-deps-available`
**Actions**:

#### `make check-generated-files`
**Purpose**: Pure function: Verify generated files are up-to-date
**Usage**: `make check-generated-files`
**Actions**:

#### `make check-build-system`
**Purpose**: Pure function: Validate build system integrity
**Usage**: `make check-build-system`
**Actions**:

#### `make format-python`
**Purpose**: Pure function: Format Python code (if black available)
**Usage**: `make format-python`
**Actions**:

#### `make format-typescript`
**Purpose**: Pure function: Format TypeScript/JavaScript (if prettier available)
**Usage**: `make format-typescript`
**Actions**:

#### `make format-json`
**Purpose**: Pure function: Format JSON files (if jq available)
**Usage**: `make format-json`
**Actions**:

#### `make check-syntax`
**Purpose**: Compose: All syntax checks
**Usage**: `make check-syntax`
**Dependencies**: check-format-python, check-format-typescript, check-format-json
**Actions**:
- $(call log_success,All syntax checks passed)

#### `make check-quality`
**Purpose**: Compose: All quality checks
**Usage**: `make check-quality`
**Dependencies**: check-lint, check-deps-available, check-generated-files
**Actions**:
- $(call log_success,All quality checks passed)

#### `make check-system`
**Purpose**: Compose: All system checks
**Usage**: `make check-system`
**Dependencies**: check-build-system
**Actions**:
- $(call log_success,All system checks passed)

#### `make check`
**Purpose**: Comprehensive code quality pipeline (functional paradigm)
**Usage**: `make check`
**Actions**:
- $(call log_info,🚀 Starting comprehensive code quality pipeline...)

#### `make check-install-formatters`
**Purpose**: Install missing formatters (side effect function)
**Usage**: `make check-install-formatters`
**Actions**:
- $(call log_info,📦 Installing code formatters...)

#### `make check-fix`
**Purpose**: Apply all available formatters (impure: modifies files)
**Usage**: `make check-fix`
**Actions**:
- $(call log_warning,🔧 Applying code formatters (this will modify files)...)

#### `make analyze-deps`
**Purpose**: Run static analysis on dependency tracker
**Usage**: `make analyze-deps`
**Actions**:
- $(call log_info,🔍 Running static analysis on dependency tracker...)
- $(call log_success,Static analysis complete)

#### `make html-setup`
**Purpose**: Setup HTML interface symlinks and launcher
**Usage**: `make html-setup`
**Actions**:
- $(call log_info,🔗 Setting up HTML interface access...)

#### `make html-dashboard`
**Purpose**: Open health monitoring dashboard
**Usage**: `make html-dashboard`
**Actions**:
- $(call log_info,📊 Opening health dashboard...)

#### `make html-vision`
**Purpose**: Open Vision AI testing interface
**Usage**: `make html-vision`
**Actions**:
- $(call log_info,👁️ Opening Vision AI testing...)

#### `make html-audio`
**Purpose**: Open Whisper TTS testing interface
**Usage**: `make html-audio`
**Actions**:
- $(call log_info,🎤 Opening Audio processing testing...)

#### `make html-context`
**Purpose**: Open Context LLM testing interface
**Usage**: `make html-context`
**Actions**:
- $(call log_info,🧠 Opening Context LLM testing...)

#### `make html-list`
**Purpose**: List all available HTML interfaces
**Usage**: `make html-list`
**Actions**:
- $(call log_info,📋 Available HTML interfaces:)

#### `make html-server`
**Purpose**: Start local HTTP server for HTML interfaces
**Usage**: `make html-server`
**Actions**:
- $(call log_info,🌐 Starting HTTP server for HTML interfaces...)

#### `make html-sanity`
**Purpose**: Run complete HTML interface sanity check
**Usage**: `make html-sanity`
**Actions**:
- $(call log_info,🔍 Running HTML interface sanity check...)

#### `make validate-system`
**Purpose**: Complete system validation using walking skeletons
**Usage**: `make validate-system`
**Actions**:
- $(call log_info,🔍 Running complete system validation...)

## 🐳 Docker Services Management

#### `make up`
**Purpose**: Start all services
**Usage**: `make up`
**Actions**:
- $(call log_info,🚀 Starting all services...)
- $(call log_success,Services started)

#### `make down`
**Purpose**: Stop all services
**Usage**: `make down`
**Actions**:
- $(call log_warning,🛑 Stopping all services...)
- $(call log_success,Services stopped)

#### `make restart`
**Purpose**: Restart all services (atomic: down then up)
**Usage**: `make restart`
**Actions**:
- $(call log_info,🔄 Restarting all services...)

#### `make logs`
**Purpose**: Show logs from all services
**Usage**: `make logs`
**Actions**:

#### `make logs-backend`
**Purpose**: Show backend logs only
**Usage**: `make logs-backend`
**Actions**:

#### `make logs-db`
**Purpose**: Show database logs only
**Usage**: `make logs-db`
**Actions**:

#### `make db-up`
**Purpose**: Start database only
**Usage**: `make db-up`
**Actions**:
- $(call log_info,🗄️ Starting database...)
- $(call log_success,Database started)

#### `make db-backup`
**Purpose**: Backup database
**Usage**: `make db-backup`
**Actions**:
- $(call log_info,💾 Backing up database...)

#### `make docs-update`
**Purpose**: Update all documentation automatically
**Usage**: `make docs-update`
**Actions**:
- $(call log_info,📚 Updating all documentation...)
- $(call log_success,Documentation updated)

## 🗄️ Database Operations

#### `make db-shell`
**Purpose**: Connect to database shell
**Usage**: `make db-shell`
**Actions**:
- $(call log_info,🗄️ Connecting to database...)

#### `make db-migrate`
**Purpose**: Run database migrations
**Usage**: `make db-migrate`
**Actions**:
- $(call log_info,🗄️ Running database migrations...)
- $(call run_gradle,flywayMigrate)

#### `make db-reset`
**Purpose**: Reset database (WARNING: destroys all data)
**Usage**: `make db-reset`
**Actions**:
- $(call log_error,⚠️  WARNING: This will destroy all database data!)

## 🔧 Protobuf Operations

#### `make proto-gen`
**Purpose**: Generate protobuf code
**Usage**: `make proto-gen`
**Actions**:
- $(call log_info,🔧 Generating protobuf code...)
- $(call log_success,Protobuf code generated)

#### `make proto-clean`
**Purpose**: Clean generated protobuf code
**Usage**: `make proto-clean`
**Actions**:
- $(call log_warning,🧹 Cleaning protobuf generated code...)
- $(call run_gradle,clean)
- $(call log_success,Protobuf code cleaned)

#### `make proto-count`
**Purpose**: Count generated protobuf files
**Usage**: `make proto-count`
**Actions**:
- $(call log_info,📊 Protobuf Statistics)

## 🏗️ Backend Development

#### `make backend-build`
**Purpose**: Build backend
**Usage**: `make backend-build`
**Actions**:
- $(call log_info,🔨 Building backend...)
- $(call run_gradle,build)
- $(call log_success,Backend built)

#### `make backend-compile`
**Purpose**: Compile backend (faster than full build)
**Usage**: `make backend-compile`
**Actions**:
- $(call log_info,⚡ Compiling backend...)
- $(call run_gradle,compileKotlin)
- $(call log_success,Backend compiled)

#### `make backend-run`
**Purpose**: Run backend locally
**Usage**: `make backend-run`
**Actions**:
- $(call log_info,🚀 Starting backend...)
- $(call run_gradle,run)

#### `make backend-demo`
**Purpose**: Run the working demo
**Usage**: `make backend-demo`
**Actions**:
- $(call log_info,🎯 Starting working demo...)
- $(call run_gradle,run --args="com.unhinged.demo.WorkingDemoKt")

#### `make backend-test`
**Purpose**: Run backend tests
**Usage**: `make backend-test`
**Actions**:
- $(call log_info,🧪 Running backend tests...)
- $(call run_gradle,test)
- $(call log_success,Tests completed)

#### `make backend-clean`
**Purpose**: Clean backend build
**Usage**: `make backend-clean`
**Actions**:
- $(call log_warning,🧹 Cleaning backend...)
- $(call run_gradle,clean)
- $(call log_success,Backend cleaned)

## 🚀 Development Workflows

#### `make dev`
**Purpose**: Start development environment
**Usage**: `make dev`
**Actions**:
- $(call log_info,🚀 Starting development environment...)
- $(call wait_for_db)

#### `make dev-demo`
**Purpose**: Start development with demo
**Usage**: `make dev-demo`
**Actions**:
- $(call log_info,🎯 Starting development with demo...)
- $(call wait_for_db)

#### `make dev-full`
**Purpose**: Start full development environment
**Usage**: `make dev-full`
**Actions**:
- $(call log_info,🚀 Starting full development environment...)

## 🧪 Testing and Debugging

#### `make gateway-test`
**Purpose**: Test presentation gateway
**Usage**: `make gateway-test`
**Actions**:
- $(call log_info,🧪 Testing presentation gateway...)
- $(call log_success,Presentation gateway tests completed)

#### `make test-grpc`
**Purpose**: Test gRPC endpoints with grpcurl
**Usage**: `make test-grpc`
**Actions**:
- $(call log_info,🧪 Testing gRPC endpoints...)
- $(call log_warning,Available services:)

#### `make test-tts`
**Purpose**: Test TTS service
**Usage**: `make test-tts`
**Actions**:
- $(call log_info,🎵 Testing TTS service...)
- -H "Content-Type: application/json" \

#### `make test-vision`
**Purpose**: Test Vision AI service
**Usage**: `make test-vision`
**Actions**:
- $(call log_info,🖼️ Testing Vision AI service...)
- $(call log_success,Vision AI service healthy) || \

#### `make test-multimodal`
**Purpose**: Run comprehensive multimodal AI architecture tests
**Usage**: `make test-multimodal`
**Actions**:
- $(call log_info,🤖 Running multimodal AI integration tests...)
- $(call log_info,📋 Testing complete gRPC pipeline: Kotlin ↔ Python services)

#### `make test-multimodal-backend`
**Purpose**: Run multimodal backend integration tests
**Usage**: `make test-multimodal-backend`
**Actions**:
- $(call log_info,🧪 Running multimodal backend integration tests...)
- $(call run_gradle,test --tests "*MultimodalIntegrationTest*")
- $(call run_gradle,test --tests "*MultimodalControllerTest*")

#### `make test-multimodal-full`
**Purpose**: Full multimodal test suite with service startup
**Usage**: `make test-multimodal-full`
**Actions**:
- $(call log_info,🚀 Running full multimodal architecture test suite...)

#### `make test-multimodal-performance`
**Purpose**: Run multimodal performance benchmarks
**Usage**: `make test-multimodal-performance`
**Actions**:
- $(call log_info,⚡ Running multimodal performance benchmarks...)
- $(call log_success,Performance benchmarks completed)

#### `make test-db`
**Purpose**: Test database connection
**Usage**: `make test-db`
**Actions**:
- $(call log_info,🗄️ Testing database connection...)
- $(call log_success,Database test successful) || \

#### `make debug-memory`
**Purpose**: Show memory usage for compilation
**Usage**: `make debug-memory`
**Actions**:
- $(call log_info,🧠 Memory Usage Information)
- $(call log_warning,JVM Memory Settings:)

#### `make test`
**Purpose**: Test the build system
**Usage**: `make test`
**Actions**:
- $(call log_info,🧪 Testing build system...)

#### `make deps-test`
**Purpose**: Run dependency tracker tests
**Usage**: `make deps-test`
**Actions**:
- $(call log_info,🧪 Running dependency tracker tests...)
- $(call log_success,Dependency tracker tests complete)

#### `make html-test`
**Purpose**: Launch HTML testing interface hub
**Usage**: `make html-test`
**Actions**:
- $(call log_info,🧪 Opening HTML testing interfaces...)
- $(call log_success,HTML testing hub opened)

#### `make health`
**Purpose**: Check health of all services
**Usage**: `make health`
**Actions**:
- $(call log_info,🏥 Health Check)

#### `make test-walking-skeleton`
**Purpose**: Complete walking skeleton validation workflow
**Usage**: `make test-walking-skeleton`
**Actions**:
- $(call log_info,🚶‍♂️ Running walking skeleton validation...)

#### `make test-full-ui`
**Purpose**: Complete UI testing workflow with service startup
**Usage**: `make test-full-ui`
**Actions**:
- $(call log_info,🚀 Running full UI testing workflow...)

#### `make test-ui-quick`
**Purpose**: Quick UI test without service startup
**Usage**: `make test-ui-quick`
**Actions**:
- $(call log_info,⚡ Quick UI testing...)

## 🧹 Cleanup Operations

#### `make clean`
**Purpose**: Clean build artifacts (smart cleanup)
**Usage**: `make clean`
**Actions**:
- $(call log_warning,🧹 Cleaning build artifacts...)
- $(call log_success,Cleanup complete)

#### `make clean-all`
**Purpose**: Clean everything including Docker
**Usage**: `make clean-all`
**Actions**:
- $(call log_warning,🧹 Cleaning everything...)

#### `make clean-docker`
**Purpose**: Clean Docker resources
**Usage**: `make clean-docker`
**Actions**:
- $(call log_warning,🧹 Cleaning Docker resources...)

#### `make deps-clean`
**Purpose**: Clean dependency tracker build
**Usage**: `make deps-clean`
**Actions**:
- $(call log_info,🧹 Cleaning dependency tracker...)
- $(call log_success,Dependency tracker cleaned)

#### `make html-clean`
**Purpose**: Clean HTML interface symlinks and generated files
**Usage**: `make html-clean`
**Actions**:
- $(call log_warning,🧹 Cleaning HTML interface symlinks...)

## 📋 Information and Help

#### `make help`
**Purpose**: Show this help message
**Usage**: `make help`
**Actions**:

#### `make status-services`
**Purpose**: Show status of all services
**Usage**: `make status-services`
**Actions**:
- $(call log_info,📊 Service Status)
- $(call log_warning,Docker Services:)

#### `make status`
**Purpose**: Show build system status and performance metrics
**Usage**: `make status`
**Actions**:
- $(call log_info,📊 Build system status...)

#### `make ports`
**Purpose**: Show which ports are in use
**Usage**: `make ports`
**Actions**:
- $(call log_info,🔌 Port Usage)
- $(call log_warning,Expected ports:)

#### `make version`
**Purpose**: Show version information
**Usage**: `make version`
**Actions**:
- $(call log_info,📋 Version Information)

## 🔗 Aliases

#### `make build`
**Purpose**: Build development environment (v1 enhanced system)
**Usage**: `make build`
**Actions**:
- $(call log_info,🚀 Building development environment...)
- $(call log_success,Build completed)

## 🔧 Configuration Variables

- **RED**: \033[0;31m - Colors for output
- **GREEN**: \033[0;32m
- **YELLOW**: \033[0;33m
- **BLUE**: \033[0;34m
- **PURPLE**: \033[0;35m
- **CYAN**: \033[0;36m
- **WHITE**: \033[0;37m
- **RESET**: \033[0m
- **BACKEND_DIR**: backend - Project directories
- **PROTO_DIR**: proto
- **FRONTEND_DIR**: frontend
- **GRADLE_OPTS**: --no-daemon - Common configurations
- **DOCKER_DB**: postgres-db
- **DB_NAME**: unhinged_db
- **DB_USER**: postgres
- **PORT_BACKEND**: 8080 - Service ports
- **PORT_TTS**: 8000
- **PORT_VISION**: 8001
- **PORT_DB**: 5432
- **PORT_KAFKA**: 9092
- **PORT_GRPC_DEMO**: 9090
- **CACHE_OPTION**: $(if $(FORCE),--no-cache,) - Force rebuild option (use FORCE=1 to bypass cache)

---

**Note**: This documentation is automatically generated from the Makefile.
Run `make docs-update` to refresh after Makefile changes.