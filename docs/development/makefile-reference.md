# 📖 Makefile Reference - Unhinged Platform

> **Purpose**: Comprehensive documentation of all Make targets and development workflows
> **Audience**: Developers and AI assistants working on the Unhinged platform
> **Last Updated**: Auto-generated on 2025-10-18 19:46:46

## 🎯 Quick Reference

### Most Used Commands
```bash
make help            # Show this help message
make status          # Show status of all services
make setup           # Initial project setup
make dev             # Start development environment
make clean           # Clean all build artifacts
```

## 🔧 Setup and Installation

#### `make setup`
**Purpose**: Initial project setup
**Usage**: `make setup`
**Actions**:
- $(call require,docker)
- $(call require,curl)

#### `make install`
**Purpose**: Alias for setup
**Usage**: `make install`
**Dependencies**: setup

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

#### `make build-enhanced`
**Purpose**: Use enhanced build system for development
**Usage**: `make build-enhanced`
**Actions**:
- $(call log_info,🚀 Using enhanced build system...)
- $(call log_success,Enhanced build completed)

#### `make build-enhanced-full`
**Purpose**: Full enhanced build with all services
**Usage**: `make build-enhanced-full`
**Actions**:
- $(call log_info,🚀 Running full enhanced build...)
- $(call log_success,Enhanced full build completed)

#### `make build-explain`
**Purpose**: Explain a build target (usage: make build-explain TARGET=dev-fast)
**Usage**: `make build-explain`
**Actions**:
- $(call log_info,📋 Explaining build target: $(or $(TARGET),dev-fast))

#### `make build-list`
**Purpose**: List all available enhanced build targets
**Usage**: `make build-list`
**Actions**:
- $(call log_info,📋 Available enhanced build targets...)

#### `make build-profile`
**Purpose**: Profile build performance (usage: make build-profile TARGET=dev-fast)
**Usage**: `make build-profile`
**Actions**:
- $(call log_info,⚡ Profiling build target: $(or $(TARGET),dev-fast))

#### `make build-watch`
**Purpose**: Watch mode for continuous building (usage: make build-watch TARGET=backend-compile)
**Usage**: `make build-watch`
**Actions**:
- $(call log_info,👁️ Starting watch mode for: $(or $(TARGET),backend-compile))

#### `make build-context`
**Purpose**: Generate LLM context for build assistance
**Usage**: `make build-context`
**Actions**:
- $(call log_info,🤖 Generating LLM build context...)

#### `make build-context-json`
**Purpose**: Generate LLM context in JSON format
**Usage**: `make build-context-json`
**Actions**:
- $(call log_info,🤖 Generating LLM build context (JSON)...)

#### `make build-onboard`
**Purpose**: Generate developer onboarding guide
**Usage**: `make build-onboard`
**Actions**:
- $(call log_info,📚 Generating developer onboarding guide...)

#### `make build-explain-error`
**Purpose**: Explain build error (usage: make build-explain-error TARGET=dev-fast ERROR="error message")
**Usage**: `make build-explain-error`
**Actions**:
- $(call log_info,🔍 Explaining build error for: $(or $(TARGET),unknown))

#### `make build-performance-report`
**Purpose**: Generate build performance report
**Usage**: `make build-performance-report`
**Actions**:
- $(call log_info,📊 Generating performance report...)

#### `make build-performance-metrics`
**Purpose**: Show current performance metrics
**Usage**: `make build-performance-metrics`
**Actions**:
- $(call log_info,📊 Showing performance metrics...)

#### `make build-performance-json`
**Purpose**: Get performance data in JSON format
**Usage**: `make build-performance-json`
**Actions**:
- $(call log_info,📊 Generating performance data (JSON)...)

#### `make build-validate`
**Purpose**: Validate enhanced build system installation
**Usage**: `make build-validate`
**Actions**:
- $(call log_info,✅ Validating enhanced build system...)

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
**Purpose**: Generate project overview for LLM context warming (YAML)
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

#### `make docs-context-enhanced`
**Purpose**: Generate enhanced project overview with getting started and dependencies
**Usage**: `make docs-context-enhanced`
**Actions**:
- $(call log_info,🚀 Generating enhanced LLM context overview...)
- $(call log_success,Enhanced LLM context overview generated)

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
- $(call log_success,Dependency analysis complete)

#### `make deps-graph`
**Purpose**: Generate dependency visualization
**Usage**: `make deps-graph`
**Actions**:
- $(call log_info,📊 Generating dependency graph...)
- $(call log_success,Dependency graph generated)

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
- $(call log_success,Feature DAG generated)

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

#### `make ui-setup`
**Purpose**: Alias for html-setup
**Usage**: `make ui-setup`
**Dependencies**: html-setup

#### `make ui-dashboard`
**Purpose**: Alias for html-dashboard
**Usage**: `make ui-dashboard`
**Dependencies**: html-dashboard

#### `make ui-vision`
**Purpose**: Alias for html-vision
**Usage**: `make ui-vision`
**Dependencies**: html-vision

#### `make ui-audio`
**Purpose**: Alias for html-audio
**Usage**: `make ui-audio`
**Dependencies**: html-audio

#### `make ui-context`
**Purpose**: Alias for html-context
**Usage**: `make ui-context`
**Dependencies**: html-context

#### `make ui-sanity`
**Purpose**: Alias for html-sanity
**Usage**: `make ui-sanity`
**Dependencies**: html-sanity

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
**Purpose**: Restart all services
**Usage**: `make restart`
**Dependencies**: down, up

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
- $(call run_gradle,generateProto)
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

#### `make dev-enhanced`
**Purpose**: Alias for enhanced development build
**Usage**: `make dev-enhanced`
**Dependencies**: build-enhanced

#### `make dev-fast-enhanced`
**Purpose**: Alias for fast enhanced development build
**Usage**: `make dev-fast-enhanced`
**Dependencies**: build-enhanced

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

#### `make build-test`
**Purpose**: Test the enhanced build system
**Usage**: `make build-test`
**Actions**:
- $(call log_info,🧪 Testing enhanced build system...)

#### `make docs-test-context`
**Purpose**: Run TDD tests for LLM context warming improvements
**Usage**: `make docs-test-context`
**Actions**:
- $(call log_info,🧪 Running LLM context warmer tests...)
- $(call log_success,LLM context warmer tests completed)

#### `make docs-test-enhancements`
**Purpose**: Run TDD tests for final LLM context warmer enhancements
**Usage**: `make docs-test-enhancements`
**Actions**:
- $(call log_info,🧪 Running enhanced context warmer tests...)
- $(call log_success,Enhanced context warmer tests completed)

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

#### `make test-ui`
**Purpose**: Alias for html-test
**Usage**: `make test-ui`
**Dependencies**: html-test

#### `make ui-test`
**Purpose**: Alias for html-test
**Usage**: `make ui-test`
**Dependencies**: html-test

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

#### `make test`
**Purpose**: Alias for backend-test
**Usage**: `make test`
**Dependencies**: backend-test

## 🧹 Cleanup Operations

#### `make clean`
**Purpose**: Clean all build artifacts
**Usage**: `make clean`
**Actions**:
- $(call log_warning,🧹 Cleaning all build artifacts...)

#### `make clean-enhanced`
**Purpose**: Clean using enhanced build system
**Usage**: `make clean-enhanced`
**Actions**:
- $(call log_warning,🧹 Enhanced cleanup...)
- $(call log_success,Enhanced cleanup complete)

#### `make clean-docker`
**Purpose**: Clean Docker resources
**Usage**: `make clean-docker`
**Actions**:
- $(call log_warning,🧹 Cleaning Docker resources...)

#### `make clean-all`
**Purpose**: Clean everything
**Usage**: `make clean-all`
**Dependencies**: clean, clean-docker

#### `make clean-all-enhanced`
**Purpose**: Enhanced clean everything
**Usage**: `make clean-all-enhanced`
**Dependencies**: clean-enhanced, clean-docker

#### `make deps-clean`
**Purpose**: Clean dependency tracker build
**Usage**: `make deps-clean`
**Actions**:
- $(call log_info,🧹 Cleaning dependency tracker...)
- $(call log_success,Dependency tracker cleaned)

#### `make clean-deps`
**Purpose**: Alias for deps-clean (disk space management)
**Usage**: `make clean-deps`
**Actions**:
- $(MAKE) deps-clean

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

#### `make status`
**Purpose**: Show status of all services
**Usage**: `make status`
**Actions**:
- $(call log_info,📊 Service Status)
- $(call log_warning,Docker Services:)

#### `make build-status`
**Purpose**: Show enhanced build system status
**Usage**: `make build-status`
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
**Purpose**: Alias for backend-build
**Usage**: `make build`
**Dependencies**: backend-build

#### `make run`
**Purpose**: Alias for backend-run
**Usage**: `make run`
**Dependencies**: backend-run

#### `make demo`
**Purpose**: Alias for backend-demo
**Usage**: `make demo`
**Dependencies**: backend-demo

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

---

**Note**: This documentation is automatically generated from the Makefile.
Run `make docs-update` to refresh after Makefile changes.