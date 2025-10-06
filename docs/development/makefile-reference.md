# 📖 Makefile Reference - Unhinged Platform

> **Purpose**: Comprehensive documentation of all Make targets and development workflows
> **Audience**: Developers and AI assistants working on the Unhinged platform
> **Last Updated**: Auto-generated on 2025-10-05 21:18:04

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

## 🧪 Testing and Debugging

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

#### `make health`
**Purpose**: Check health of all services
**Usage**: `make health`
**Actions**:
- $(call log_info,🏥 Health Check)

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

#### `make clean-docker`
**Purpose**: Clean Docker resources
**Usage**: `make clean-docker`
**Actions**:
- $(call log_warning,🧹 Cleaning Docker resources...)

#### `make clean-all`
**Purpose**: Clean everything
**Usage**: `make clean-all`
**Dependencies**: clean, clean-docker

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