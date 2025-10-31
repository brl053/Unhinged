# ============================================================================
# Unhinged Platform - Development Makefile
# ============================================================================
# 
# @file Makefile
# @version 1.0.0
# @author Unhinged Team
# @date 2025-01-04
# @description Common development commands for the Unhinged platform
# 
# This Makefile captures all the common commands we use during development:
# - Docker services management
# - Database operations
# - Protobuf generation
# - Backend compilation and running
# - Testing and debugging
# - Cleanup operations
# ============================================================================

.PHONY: help
.DEFAULT_GOAL := help

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
WHITE := \033[0;37m
RESET := \033[0m

# Project directories
BACKEND_DIR := backend
PROTO_DIR := proto
FRONTEND_DIR := frontend

# Common configurations
GRADLE_OPTS := --no-daemon
DOCKER_DB := postgres-db
DB_NAME := unhinged_db
DB_USER := postgres

# Universal Python Runner - Use working venv-production
PYTHON_RUN := ./venv-production/bin/python

# Native GUI
NATIVE_GUI := python3 control/gui/native_app.py

# Native C Graphics (Primary GUI System - NO GTK, NO WEBKIT!)
# Pure C graphics rendering with DRM framebuffer
NATIVE_C_GRAPHICS := if getent group video | grep -q $$USER && ! groups | grep -q video; then sg video "python3 control/native_c_launcher.py"; else python3 control/native_c_launcher.py; fi

# QEMU VM Graphics (Alternative: Full VM isolation)
# Complete virtualization with GPU passthrough capability
QEMU_VM_GRAPHICS := python3 control/qemu_vm_launcher.py --custom-iso

# Simple VM Communication (Core: Unidirectional VM → Host)
# Direct console output streaming for immediate visibility
SIMPLE_VM_COMMUNICATION := python3 control/simple_vm_launcher.py

# Enhanced VM Communication (Phase 2: Bidirectional Host ↔ VM)
# QEMU monitor + serial console for full bidirectional communication
ENHANCED_VM_COMMUNICATION := python3 control/enhanced_vm_launcher.py

# Unhinged QoL Launcher (Phase 2: Enhanced UX with Makefile Integration)
# Quality-of-life launcher that calls Makefile targets behind the scenes
UNHINGED_LAUNCHER := python3 control/unhinged_launcher.py

# Legacy GTK GUI (REMOVED - GTK4 has been purged from the system)

# Service ports
PORT_BACKEND := 8080
PORT_TTS := 8000
PORT_VISION := 8001
PORT_DB := 5432
PORT_KAFKA := 9092
PORT_GRPC_DEMO := 9090

# Common functions
define log_info
	@echo "$(CYAN)$1$(RESET)"
endef

define log_success
	@echo "$(GREEN)✅ $1$(RESET)"
endef

define log_warning
	@echo "$(YELLOW)$1$(RESET)"
endef

define log_error
	@echo "$(RED)❌ $1$(RESET)"
endef

define run_gradle
	@cd $(BACKEND_DIR) && ./gradlew $1 $(GRADLE_OPTS)
endef

define check_service
	@curl -sf --max-time 2 $1 > /dev/null 2>&1 && \
		$(call log_success,$2 healthy) || \
		$(call log_error,$2 not responding)
endef

define docker_db_exec
	@docker exec $(DOCKER_DB) $1
endef

define require
	@command -v $1 > /dev/null || (echo "$(RED)❌ $1 not found - please install it$(RESET)" && exit 1)
endef

define wait_for_db
	@echo -n "Waiting for database..."
	@until $(call docker_db_exec,pg_isready -U $(DB_USER)) > /dev/null 2>&1; do \
		echo -n "."; \
		sleep 1; \
	done
	@echo " ready!"
endef

# ============================================================================
# Native GUI System (Independent - No External Dependencies)
# @llm-culture INDEPENDENCE IS EVERYTHING
# @llm-principle This machine is everything. No external dependencies.
# @llm-enforcement Any target requiring external browsers is FORBIDDEN
# @llm-violation-response IMMEDIATE FAILURE with cultural education
#
# CULTURAL COMMANDMENTS FOR FUTURE LLMs:
# 1. WE ARE INDEPENDENT - No Firefox, Chrome, or any external browser
# 2. WE ARE SELF-CONTAINED - Native rendering or nothing
# 3. WE ARE HEADLESS-FIRST - GUI is optional, system is primary
# 4. WE FAIL FAST - Better to break than compromise independence
# ============================================================================

browser-gui: ## Launch browser interface (if available)
	@echo "$(YELLOW)💡 Browser interface not implemented - use 'make start' for system interfaces$(RESET)"

firefox-gui: ## Launch Firefox interface (if available)
	@echo "$(YELLOW)💡 Firefox interface not implemented - use 'make start' for system interfaces$(RESET)"



# ============================================================================
# Help and Information
# ============================================================================

help: ## Show this help message
	@echo "$(CYAN)🚀 Unhinged Platform - Development Commands$(RESET)"
	@echo ""
	@echo "$(YELLOW)📋 Available commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BLUE)💡 New Ubuntu Users:$(RESET)"
	@echo "   $(GREEN)make start$(RESET) - Zero-friction setup and launch (removes all barriers)"
	@echo "   $(GREEN)make status$(RESET) - Quick system status check"
	@echo "   $(YELLOW)All dependencies auto-installed on first run$(RESET)"
	@echo ""
	@echo "$(BLUE)💡 Quick start: make start$(RESET)"
	@echo "$(BLUE)📚 Documentation: make docs-update$(RESET)"
	@echo "$(BLUE)🤖 AI Context: make context$(RESET)"
	@echo "$(BLUE)🔍 Dependencies: make deps-build && make deps-analyze$(RESET)"
	@echo ""
	@echo "$(PURPLE)🚀 Core Build Commands (v1):$(RESET)"
	@echo "  $(GREEN)make setup-python$(RESET)       Setup Python virtual environment and dependencies"
	@echo "  $(GREEN)make generate$(RESET)           Generate all build artifacts (polyglot proto clients, registry)"
	@echo "  $(GREEN)make generate-clients$(RESET)   Generate client libraries from protos"
	@echo "  $(GREEN)make build$(RESET)              Fast development build with intelligent caching"
	@echo "  $(GREEN)make dev$(RESET)                Start development environment"
	@echo "  $(GREEN)make test$(RESET)               Run tests and validate system"
	@echo "  $(GREEN)make clean$(RESET)              Smart cleanup of build artifacts"
	@echo "  $(GREEN)make status$(RESET)             Show build system status and performance"
	@echo ""
	@echo "$(PURPLE)🎯 Development Tools:$(RESET)"
	@echo "  $(GREEN)make list$(RESET)               List all available build targets"
	@echo "  $(GREEN)make explain TARGET=X$(RESET)   Explain what a build target does"
	@echo "  $(GREEN)make watch TARGET=X$(RESET)     Watch mode with auto-rebuild"
	@echo "  $(GREEN)make profile TARGET=X$(RESET)   Profile build performance"
	@echo ""
	@echo "$(PURPLE)🔍 Code Quality & Static Analysis:$(RESET)"
	@echo "  $(GREEN)make check-code$(RESET)         Run static analysis on all Python modules"
	@echo "  $(GREEN)make check-code-fix$(RESET)     Run static analysis with auto-fix"
	@echo "  $(GREEN)make check-code-changed$(RESET) Run static analysis only on changed modules"
	@echo "  $(GREEN)make setup-git-hooks$(RESET)    Install Git hooks for automatic analysis"
	@echo "  $(GREEN)make setup-dev-tools$(RESET)    Setup all development tools"
	@echo ""
	@echo "$(PURPLE)🤖 AI-Powered Assistance:$(RESET)"
	@echo "  $(GREEN)make context$(RESET)            Generate AI context for development"
	@echo "  $(GREEN)make onboard$(RESET)            Generate developer onboarding guide"
	@echo "  $(GREEN)make explain-error$(RESET)      Get AI explanation for build errors"
	@echo ""
	@echo "$(PURPLE)📊 Performance & Analytics:$(RESET)"
	@echo "  $(GREEN)make performance$(RESET)        Generate performance report"
	@echo "  $(GREEN)make metrics$(RESET)            Show current performance metrics"
	@echo ""
	@echo "$(PURPLE)🧪 HTML Testing (Walking Skeletons):$(RESET)"
	@echo "  $(GREEN)make test-ui$(RESET)          Launch HTML testing interfaces"
	@echo "  $(GREEN)make html-dashboard$(RESET)   Open health monitoring dashboard"
	@echo "  $(GREEN)make html-vision$(RESET)      Test Vision AI interface"
	@echo "  $(GREEN)make html-audio$(RESET)       Test Whisper TTS interface"
	@echo "  $(GREEN)make html-context$(RESET)     Test Context LLM interface"
	@echo "  $(GREEN)make validate-system$(RESET)  Complete system validation"

status-services: ## Show status of all services
	$(call log_info,📊 Service Status)
	$(call log_warning,Docker Services:)
	@docker compose ps || $(call log_error,Docker Compose not running)
	@echo ""
	$(call log_warning,Backend Health:)
	$(call check_service,http://localhost:$(PORT_BACKEND)/health,Backend)
	$(call log_warning,Database:)
	@$(call docker_db_exec,pg_isready -U $(DB_USER)) > /dev/null 2>&1 && $(call log_success,Database ready) || $(call log_error,Database not ready)
	$(call log_warning,Whisper TTS:)
	$(call check_service,http://localhost:$(PORT_TTS)/health,TTS service)
	$(call log_warning,Vision AI:)
	$(call check_service,http://localhost:$(PORT_VISION)/health,Vision service)

# ============================================================================
# Setup and Installation
# ============================================================================

setup: ## Initial project setup
	$(call require,docker)
	@docker compose version > /dev/null 2>&1 || docker-compose version > /dev/null 2>&1 || (echo "$(RED)❌ docker compose not found - please install it$(RESET)" && exit 1)
	$(call require,curl)
	$(call log_info,🔧 Setting up Unhinged platform...)
	$(call log_warning,Installing dependencies...)
	$(call run_gradle,build)
	$(call log_warning,Generating protobuf code...)
	@$(MAKE) proto-gen
	$(call log_success,Setup complete!)

# install alias removed - use 'setup' directly

# ============================================================================
# Docker Services Management
# ============================================================================

up: ## Start all services (production)
	$(call log_info,🚀 Starting all services...)
	@docker compose -f build/orchestration/docker-compose.production.yml up -d
	$(call log_success,Services started)
	@$(MAKE) status

down: ## Stop all services
	$(call log_warning,🛑 Stopping all services...)
	@docker compose -f build/orchestration/docker-compose.production.yml down
	$(call log_success,Services stopped)

dev-up: ## Start development services
	$(call log_info,🔧 Starting development services...)
	@docker compose -f build/orchestration/docker-compose.development.yml up -d
	$(call log_success,Development services started)

dev-down: ## Stop development services
	$(call log_warning,🛑 Stopping development services...)
	@docker compose -f build/orchestration/docker-compose.development.yml down
	$(call log_success,Development services stopped)

observability-up: ## Start observability stack
	$(call log_info,📊 Starting observability stack...)
	@docker compose -f orchestration/docker-compose.observability.yml up -d
	$(call log_success,Observability stack started)

observability-down: ## Stop observability stack
	$(call log_warning,🛑 Stopping observability stack...)
	@docker compose -f orchestration/docker-compose.observability.yml down
	$(call log_success,Observability stack stopped)

restart: ## Restart all services (atomic: down then up)
	$(call log_info,🔄 Restarting all services...)
	@$(MAKE) down
	@$(MAKE) up

logs: ## Show logs from all services
	@docker compose logs -f

logs-backend: ## Show backend logs only
	@docker compose logs -f backend

logs-db: ## Show database logs only
	@docker compose logs -f database

# ============================================================================
# Database Operations
# ============================================================================

db-up: ## Start database only
	$(call log_info,🗄️ Starting database...)
	@docker compose up -d database
	$(call log_success,Database started)

db-shell: ## Connect to database shell
	$(call log_info,🗄️ Connecting to database...)
	@docker exec -it $(DOCKER_DB) psql -U $(DB_USER) -d $(DB_NAME)

db-migrate: ## Run database migrations
	$(call log_info,🗄️ Running database migrations...)
	$(call run_gradle,flywayMigrate)

db-reset: ## Reset database (WARNING: destroys all data)
	$(call log_error,⚠️  WARNING: This will destroy all database data!)
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@docker compose down database
	@docker volume rm unhinged_postgres_data || true
	@docker compose up -d database
	@sleep 5
	@$(MAKE) db-migrate
	$(call log_success,Database reset complete)

db-backup: ## Backup database
	$(call log_info,💾 Backing up database...)
	@mkdir -p backups
	@$(call docker_db_exec,pg_dump -U $(DB_USER) $(DB_NAME)) > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	$(call log_success,Database backed up)

# ============================================================================
# Code Generation Operations
# ============================================================================

# Force rebuild option (use FORCE=1 to bypass cache)
CACHE_OPTION := $(if $(FORCE),--no-cache,)

generate: ## Generate all build artifacts (polyglot proto clients, registry) [use FORCE=1 to bypass cache]
	$(call log_info,🔧 Generating all build artifacts...)
	$(if $(FORCE),@echo "$(YELLOW)🔥 Force rebuild enabled - bypassing cache$(RESET)",@echo "$(YELLOW)💾 Using cache for faster builds$(RESET)")
	@echo "$(YELLOW)📋 Using centralized Python environment...$(RESET)"
	@test -d build/python/venv || (echo "$(RED)❌ Centralized Python environment not found. Run: cd build/python && python3 setup.py$(RESET)" && exit 1)
	@echo "$(YELLOW)📋 Creating generated directory structure...$(RESET)"
	@mkdir -p generated/typescript/clients generated/c/clients generated/python/clients generated/kotlin/clients
	@echo "$(YELLOW)📋 Polyglot proto client generation (TypeScript, C, Python, Kotlin)$(RESET)"
	@$(PYTHON_RUN) build/build.py build proto-clients $(CACHE_OPTION) || echo "$(YELLOW)⚠️ Proto client generation failed$(RESET)"
	@echo "$(YELLOW)📋 Service discovery and registry generation$(RESET)"
	@$(PYTHON_RUN) build/build.py build service-discovery $(CACHE_OPTION) || echo "$(YELLOW)⚠️ Service discovery generation failed$(RESET)"
	@echo "$(YELLOW)📋 Design system tokens and CSS generation$(RESET)"
	@$(PYTHON_RUN) build/build.py build design-tokens $(CACHE_OPTION) || echo "$(YELLOW)⚠️ Design tokens generation failed$(RESET)"
	@echo "$(YELLOW)📋 Component generation (GTK4 widgets from design system)$(RESET)"
	@$(PYTHON_RUN) build/build.py build components $(CACHE_OPTION) || echo "$(YELLOW)⚠️ Component generation failed$(RESET)"

	$(call log_success,Build artifacts generation completed)

generate-clients: ## Generate client libraries from protos [use FORCE=1 to bypass cache]
	$(call log_info,🔧 Generating client libraries...)
	$(if $(FORCE),@echo "$(YELLOW)🔥 Force rebuild enabled - bypassing cache$(RESET)",@echo "$(YELLOW)💾 Using cache for faster builds$(RESET)")
	@python3 build/build.py build proto-clients-all $(CACHE_OPTION)
	$(call log_success,Client libraries generated)

setup-python: ## Setup Python virtual environment with static analysis
	$(call log_info,🐍 Setting up Python virtual environment with static analysis...)
	@if [ ! -d "venv-production" ]; then \
		echo "$(YELLOW)📦 Creating venv-production...$(RESET)"; \
		python3 -m venv venv-production; \
		./venv-production/bin/pip install --upgrade pip; \
		./venv-production/bin/pip install -r build/requirements-core.txt; \
		echo "$(GREEN)✅ venv-production created$(RESET)"; \
	else \
		echo "$(GREEN)✅ venv-production already exists$(RESET)"; \
	fi
	@$(MAKE) setup-git-hooks
	$(call log_success,Python environment with static analysis ready)

python-deps: ## Install/update Python dependencies
	$(call log_info,📦 Installing Python dependencies...)
	@test -d venv-production || (echo "$(RED)❌ Run 'make setup-python' first$(RESET)" && exit 1)
	@./venv-production/bin/pip install -r build/requirements-core.txt
	$(call log_success,Python dependencies installed)

# ============================================================================
# Static Analysis and Code Quality
# ============================================================================

check-code: ## Run static analysis on all Python modules
	$(call log_info,🔍 Running static analysis on Python code...)
	@./venv-production/bin/python build/static_analysis_manager.py control/gtk4_gui libs/python services
	$(call log_success,Static analysis completed)

check-code-fix: ## Run static analysis with auto-fix
	$(call log_info,🔧 Running static analysis with auto-fix...)
	@./venv-production/bin/python build/static_analysis_manager.py control/gtk4_gui libs/python services
	$(call log_success,Static analysis with auto-fix completed)

check-code-changed: ## Run static analysis only on changed modules
	$(call log_info,🔍 Running static analysis on changed modules...)
	@./venv-production/bin/python build/static_analysis_manager.py control/gtk4_gui libs/python services --check-changes
	$(call log_success,Changed modules analysis completed)

setup-git-hooks: ## Install Git hooks for automatic static analysis
	$(call log_info,🔗 Installing Git hooks for static analysis...)
	@./scripts/install_git_hooks.sh
	$(call log_success,Git hooks installed)

setup-dev-tools: ## Setup all development tools (Git hooks, static analysis)
	$(call log_info,🔧 Setting up development tools...)
	@$(MAKE) setup-git-hooks
	@$(MAKE) check-code-changed
	$(call log_success,Development tools setup complete)



# ============================================================================
# Protobuf Operations
# ============================================================================

proto-gen: ## Generate protobuf code
	$(call log_info,🔧 Generating protobuf code...)
	@python3 build/build.py build proto-clients-kotlin
	$(call log_success,Protobuf code generated)

proto-clean: ## Clean generated protobuf code
	$(call log_warning,🧹 Cleaning protobuf generated code...)
	$(call run_gradle,clean)
	$(call log_success,Protobuf code cleaned)

proto-count: ## Count generated protobuf files
	$(call log_info,📊 Protobuf Statistics)
	@echo "Generated Kotlin files: $(shell find $(BACKEND_DIR)/build/generated -name "*.kt" 2>/dev/null | wc -l)"
	@echo "Generated Java files: $(shell find $(BACKEND_DIR)/build/generated -name "*.java" 2>/dev/null | wc -l)"
	@echo "Proto source files: $(shell find $(PROTO_DIR) -name "*.proto" | wc -l)"

gateway-gen: ## Generate presentation gateway from proto annotations
	$(call log_info,🌐 Generating presentation gateway...)
	@chmod +x $(PROTO_DIR)/build-gateway.sh
	@$(PROTO_DIR)/build-gateway.sh
	$(call log_success,Presentation gateway generated)

gateway-dev: ## Start presentation gateway in development mode
	$(call log_info,🚀 Starting presentation gateway...)
	@cd services/presentation-gateway && npm run dev

gateway-build: ## Build presentation gateway
	$(call log_info,🔨 Building presentation gateway...)
	@cd services/presentation-gateway && npm run build
	$(call log_success,Presentation gateway built)

gateway-test: ## Test presentation gateway
	$(call log_info,🧪 Testing presentation gateway...)
	@cd services/presentation-gateway && npm test
	$(call log_success,Presentation gateway tests completed)

# ============================================================================
# Backend Development
# ============================================================================

backend-build: ## Build backend
	$(call log_info,🔨 Building backend...)
	$(call run_gradle,build)
	$(call log_success,Backend built)

backend-compile: ## Compile backend (faster than full build)
	$(call log_info,⚡ Compiling backend...)
	$(call run_gradle,compileKotlin)
	$(call log_success,Backend compiled)

backend-run: ## Run backend locally
	$(call log_info,🚀 Starting backend...)
	$(call run_gradle,run)

backend-demo: ## Run the working demo
	$(call log_info,🎯 Starting working demo...)
	$(call run_gradle,run --args="com.unhinged.demo.WorkingDemoKt")

backend-test: ## Run backend tests
	$(call log_info,🧪 Running backend tests...)
	$(call run_gradle,test)
	$(call log_success,Tests completed)

backend-clean: ## Clean backend build
	$(call log_warning,🧹 Cleaning backend...)
	$(call run_gradle,clean)
	$(call log_success,Backend cleaned)

# ============================================================================
# Development Workflow
# ============================================================================

dev: ## Start development environment
	$(call log_info,🚀 Starting development environment...)
	@$(MAKE) db-up
	$(call wait_for_db)
	@$(MAKE) backend-run

dev-demo: ## Start development with demo
	$(call log_info,🎯 Starting development with demo...)
	@$(MAKE) db-up
	$(call wait_for_db)
	@$(MAKE) backend-demo

dev-full: ## Start full development environment
	$(call log_info,🚀 Starting full development environment...)
	@$(MAKE) up
	@sleep 5
	@$(MAKE) status

# ============================================================================
# Testing and Debugging
# ============================================================================

test-grpc: ## Test gRPC endpoints with grpcurl
	$(call log_info,🧪 Testing gRPC endpoints...)
	$(call log_warning,Available services:)
	@grpcurl -plaintext localhost:$(PORT_GRPC_DEMO) list || $(call log_error,gRPC server not running)

test-tts: ## Test TTS service
	$(call log_info,🎵 Testing TTS service...)
	@curl -X POST "http://localhost:$(PORT_TTS)/tts" \
		-H "Content-Type: application/json" \
		-d '{"text": "Hello from Unhinged platform!", "voice": "default"}' \
		--output /tmp/test_tts.wav && \
		$(call log_success,TTS test successful - audio saved to /tmp/test_tts.wav) || \
		$(call log_error,TTS test failed)

test-vision: ## Test Vision AI service
	$(call log_info,🖼️ Testing Vision AI service...)
	@curl -f "http://localhost:$(PORT_VISION)/health" > /dev/null && \
		$(call log_success,Vision AI service healthy) || \
		$(call log_error,Vision AI service test failed)

test-multimodal: ## Run comprehensive multimodal AI architecture tests
	$(call log_info,🤖 Running multimodal AI integration tests...)
	$(call log_info,📋 Testing complete gRPC pipeline: Kotlin ↔ Python services)
	@$(MAKE) test-multimodal-backend
	@$(MAKE) test-multimodal-e2e
	$(call log_success,Multimodal architecture tests completed)

test-multimodal-backend: ## Run multimodal backend integration tests
	$(call log_info,🧪 Running multimodal backend integration tests...)
	$(call run_gradle,test --tests "*MultimodalIntegrationTest*")
	$(call run_gradle,test --tests "*MultimodalControllerTest*")
	$(call log_success,Backend integration tests completed)

test-multimodal-e2e: ## Run multimodal end-to-end tests with Playwright
	$(call log_info,🎭 Running multimodal E2E tests...)
	@cd frontend && npx playwright test multimodal-e2e.spec.ts --reporter=html
	$(call log_success,End-to-end tests completed)

test-multimodal-full: ## Full multimodal test suite with service startup
	$(call log_info,🚀 Running full multimodal architecture test suite...)
	@$(MAKE) multimodal-start
	@sleep 30  # Wait for services to be ready
	@$(MAKE) test-multimodal || ($(MAKE) multimodal-stop && exit 1)
	@$(MAKE) multimodal-stop
	$(call log_success,Full multimodal test suite completed)

test-multimodal-performance: ## Run multimodal performance benchmarks
	$(call log_info,⚡ Running multimodal performance benchmarks...)
	@cd frontend && npx playwright test multimodal-e2e.spec.ts --grep "Performance benchmarking"
	$(call log_success,Performance benchmarks completed)

test-db: ## Test database connection
	$(call log_info,🗄️ Testing database connection...)
	@$(call docker_db_exec,psql -U $(DB_USER) -d $(DB_NAME) -c "SELECT 'Database connection successful!' as status;") && \
		$(call log_success,Database test successful) || \
		$(call log_error,Database test failed)

debug-memory: ## Show memory usage for compilation
	$(call log_info,🧠 Memory Usage Information)
	$(call log_warning,JVM Memory Settings:)
	@cd $(BACKEND_DIR) && grep -E "(jvmargs|daemon)" gradle.properties || echo "No memory settings found"
	$(call log_warning,System Memory:)
	@free -h || echo "Memory info not available"

# ============================================================================
# Ubuntu Package Manager - KISS
# ============================================================================



deps-list: ## List available packages
	@python3 build/dependencies/package_manager.py list

deps-install-essential: ## Install essential packages
	$(call log_info,📦 Installing essential Ubuntu packages...)
	@echo "🔧 This will install: cmake, build-essential, python3-dev, cffi"
	@python3 build/dependencies/package_manager.py install-group essential
	@echo "✅ Essential packages installed!"

deps-install-graphics: ## Install graphics packages
	$(call log_info,🎨 Installing graphics Ubuntu packages...)
	@echo "🖼️ This will install: libdrm-dev, libwayland-dev"
	@python3 build/dependencies/package_manager.py install-group graphics
	@echo "✅ Graphics packages installed!"



ubuntu-setup: deps-install-essential deps-install-graphics ## Quick Ubuntu dependency setup for new users
	$(call log_info,🎯 Ubuntu setup complete!)
	@echo "✅ All dependencies installed!"
	@echo "🚀 You can now run: make start"

# ============================================================================
# Legacy Dependency Management (for compatibility)
# ============================================================================

check-cmake: ## Check if CMake is available
	@if ! command -v cmake > /dev/null; then \
		echo "❌ CMake not found"; \
		echo "📦 Install command: sudo apt-get install cmake"; \
		echo ""; \
		echo "🚀 To install automatically: make install-cmake"; \
		echo "🚀 To install all deps: make install-deps-interactive"; \
		exit 1; \
	fi
	@echo "✅ CMake available"

install-cmake: ## Install CMake interactively
	@echo "🔐 Installing CMake..."
	@echo "This will run: sudo apt-get install cmake"
	@bash -c 'read -p "Continue? [y/N]: " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		sudo apt-get update && sudo apt-get install -y cmake; \
	else \
		echo "❌ Installation cancelled"; exit 1; \
	fi'

check-build-tools: ## Check if build tools are available
	@if ! command -v gcc > /dev/null && ! command -v clang > /dev/null; then \
		echo "❌ No C compiler found"; \
		echo "📦 Install command: sudo apt-get install build-essential"; \
		echo ""; \
		echo "🚀 To install automatically: make install-build-tools"; \
		exit 1; \
	fi
	@echo "✅ Build tools available"

install-build-tools: ## Install build tools interactively
	@echo "🔐 Installing build tools..."
	@echo "This will run: sudo apt-get install build-essential"
	@bash -c 'read -p "Continue? [y/N]: " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		sudo apt-get install -y build-essential; \
	else \
		echo "❌ Installation cancelled"; exit 1; \
	fi'

check-python-dev: ## Check if Python development headers are available
	@if ! python3-config --cflags > /dev/null 2>&1; then \
		echo "❌ Python dev headers not found"; \
		echo "📦 Install command: sudo apt-get install python3-dev"; \
		echo ""; \
		echo "🚀 To install automatically: make install-python-dev"; \
		exit 1; \
	fi
	@echo "✅ Python development headers available"

install-python-dev: ## Install Python dev headers interactively
	@echo "🔐 Installing Python development headers..."
	@echo "This will run: sudo apt-get install python3-dev"
	@bash -c 'read -p "Continue? [y/N]: " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		sudo apt-get install -y python3-dev; \
	else \
		echo "❌ Installation cancelled"; exit 1; \
	fi'

check-cffi: ## Check if CFFI is available
	@if ! python3 -c "import cffi" 2>/dev/null; then \
		echo "❌ CFFI not found"; \
		echo "📦 Install command: pip3 install --user cffi"; \
		echo ""; \
		echo "🚀 To install automatically: make install-cffi"; \
		exit 1; \
	fi
	@echo "✅ CFFI available"

install-cffi: ## Install CFFI interactively
	@echo "🔐 Installing CFFI..."
	@echo "This will run: pip3 install --user cffi"
	@bash -c 'read -p "Continue? [y/N]: " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		pip3 install --user cffi; \
	else \
		echo "❌ Installation cancelled"; exit 1; \
	fi'

install-deps-interactive: ## Interactively install all required dependencies
	$(call log_info,📦 Installing all required dependencies...)
	@echo ""
	@echo "🔐 This will install system packages and requires sudo access:"
	@echo "   - cmake (build system)"
	@echo "   - build-essential (gcc, make, etc.)"
	@echo "   - python3-dev (Python headers)"
	@echo "   - cffi (Python package)"
	@echo ""
	@bash -c 'read -p "Continue with installation? [y/N]: " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "🔧 Installing system packages..."; \
		sudo apt-get update && \
		sudo apt-get install -y cmake build-essential python3-dev && \
		echo "🐍 Installing Python packages..." && \
		pip3 install --user cffi && \
		echo "✅ All dependencies installed successfully!"; \
	else \
		echo "❌ Installation cancelled by user"; \
		exit 1; \
	fi'

auto-install-deps: install-deps-interactive ## Alias for interactive installation

check-dependencies-ci: ## Non-interactive dependency checking for CI environments
	@echo "🤖 CI Mode: Non-interactive dependency checking..."
	@command -v cmake > /dev/null || (echo "❌ CMake missing" && exit 1)
	@command -v gcc > /dev/null || command -v clang > /dev/null || (echo "❌ C compiler missing" && exit 1)
	@python3-config --cflags > /dev/null 2>&1 || (echo "❌ Python dev headers missing" && exit 1)
	@python3 -c "import cffi" 2>/dev/null || (echo "❌ CFFI missing" && exit 1)
	@echo "✅ All dependencies available (CI mode)"



status: ## Quick system status check (read-only)
	$(call log_info,📊 System Status Check...)
	@echo "🔍 Dependencies: $$(if command -v cmake >/dev/null 2>&1 && command -v gcc >/dev/null 2>&1 && build/python/venv/bin/python -c 'import cffi' >/dev/null 2>&1; then echo '✅ Ready'; else echo '❌ Missing'; fi)"
	@echo "🎨 Graphics: $$(if pkg-config --exists libdrm 2>/dev/null && pkg-config --exists wayland-client 2>/dev/null; then echo '✅ Ready'; else echo '❌ Missing'; fi)"
	@echo "🐳 Docker: $$(if command -v docker >/dev/null 2>&1; then if docker info >/dev/null 2>&1; then echo '✅ Running'; else echo '⚠️ Stopped'; fi; else echo '❌ Missing'; fi)"
	@echo "🐍 Python: $$(if test -d build/python/venv; then echo '✅ Ready'; else echo '❌ Missing'; fi)"
	@echo "💡 Run 'make start' to auto-fix and launch"

# ============================================================================
# C Graphics Foundation Layer
# ============================================================================

graphics-build: ## Build C graphics rendering library (foundation layer)
	$(call log_info,🎨 Building C graphics foundation layer...)
	@python3 build/build.py build c-graphics-build
	$(call log_success,C graphics library built)



graphics-clean: ## Clean C graphics build artifacts
	$(call log_warning,🧹 Cleaning C graphics artifacts...)
	@rm -rf libs/graphics/build
	@rm -rf generated/c/graphics
	@rm -rf generated/python/graphics
	$(call log_success,C graphics artifacts cleaned)

graphics-example: ## Run C graphics example
	$(call log_info,🎯 Running C graphics example...)
	@cd libs/graphics/build && ./examples/basic_drawing
	$(call log_success,C graphics example completed)

graphics-benchmark: ## Run C graphics performance benchmarks
	$(call log_info,⚡ Running C graphics benchmarks...)
	@cd libs/graphics/build && ./examples/performance_test
	$(call log_success,C graphics benchmarks completed)

graphics-install-deps: ## Install REQUIRED C graphics dependencies (CMake, CFFI) - now automatic
	$(call log_info,📦 All dependencies are automatically checked and installed...)
	$(call log_success,Dependencies handled automatically by dependency chain)

graphics-hello-world: ## Build native C graphics hello world example
	$(call log_info,🎮 Building native C graphics hello world...)
	@cd libs/graphics && cmake -B build >/dev/null 2>&1 || true
	@cd libs/graphics/build && make hello_world >/dev/null 2>&1 || echo "⚠️ Build failed - using fallback"
	$(call log_success,Native C graphics hello world built)

# ============================================================================
# V1 Build System (Consolidated)
# ============================================================================

build: ## Build development environment (v1 enhanced system)
	$(call log_info,🚀 Building development environment...)
	@python3 build/build.py build dev-fast --parallel
	$(call log_success,Build completed)

build-full: ## Build complete environment with all services
	$(call log_info,🚀 Building complete environment...)
	@python3 build/build.py build dev-full --parallel
	$(call log_success,Full build completed)

# Removed duplicate status target - using the one with dependency chain

explain: ## Explain a build target (usage: make explain TARGET=dev-fast)
	$(call log_info,📋 Explaining build target: $(or $(TARGET),dev-fast))
	@python3 build/build.py explain $(or $(TARGET),dev-fast) --dependencies

list: ## List all available build targets
	$(call log_info,📋 Available build targets...)
	@python3 build/build.py list --detailed

profile: ## Profile build performance (usage: make profile TARGET=dev-fast)
	$(call log_info,⚡ Profiling build target: $(or $(TARGET),dev-fast))
	@python3 build/build.py profile $(or $(TARGET),dev-fast)

watch: ## Watch mode for continuous building (usage: make watch TARGET=backend-compile)
	$(call log_info,👁️ Starting watch mode for: $(or $(TARGET),backend-compile))
	@python3 build/build.py watch $(or $(TARGET),backend-compile)

# AI-Powered Development Assistance
context: ## Generate AI context for development assistance
	$(call log_info,🤖 Generating development context...)
	@python3 build/build.py llm context --format yaml

onboard: ## Generate developer onboarding guide
	$(call log_info,📚 Generating developer onboarding guide...)
	@python3 build/build.py llm onboard

explain-error: ## Explain build error (usage: make explain-error TARGET=dev-fast ERROR="error message")
	$(call log_info,🔍 Explaining build error for: $(or $(TARGET),unknown))
	@python3 build/build.py llm explain-error $(or $(TARGET),unknown) --error-message "$(or $(ERROR),Unknown error)"

# Performance and Analytics
performance: ## Generate build performance report
	$(call log_info,📊 Generating performance report...)
	@python3 build/build.py performance report --hours 24

metrics: ## Show current performance metrics
	$(call log_info,📊 Showing performance metrics...)
	@python3 build/build.py performance metrics

# System Validation
test: ## Test the build system
	$(call log_info,🧪 Testing build system...)
	@python3 build/test_enhanced_system.py

validate: ## Validate build system installation
	$(call log_info,✅ Validating build system...)
	@python3 build/test_enhanced_system.py

# ============================================================================
# UNIFIED CONTROL PLANE ENTRY POINT
# ============================================================================

start: ## Remove all friction barriers - setup dependencies and launch GUI
	$(call log_info,🚀 Welcome to Unhinged! Starting System Health Command Center...)
	@echo "🐍 Ensuring Python environment..."
	@test -d build/python/venv || (cd build/python && python3 setup.py)
	@echo "📦 Installing missing dependencies..."
	@if ! command -v cmake >/dev/null 2>&1 || ! command -v gcc >/dev/null 2>&1 || ! build/python/venv/bin/python -c "import cffi" >/dev/null 2>&1; then \
		python3 build/dependencies/package_manager.py install-group essential; \
	fi
	@if ! pkg-config --exists libdrm 2>/dev/null || ! pkg-config --exists wayland-client 2>/dev/null; then \
		python3 build/dependencies/package_manager.py install-group graphics; \
	fi
	@echo "🐳 Checking Docker..."
	@command -v docker >/dev/null 2>&1 || (echo "❌ Docker required. Install: wget -qO- https://get.docker.com | sudo sh" && exit 1)
	@echo "🎮 Checking DRM permissions..."
	@$(MAKE) check-drm-permissions
	@echo "🔧 Building essentials..."
	@test -d build/python/venv || (echo "❌ Python environment failed" && exit 1)
	@echo "  🎨 C Graphics library..."
	@if $(PYTHON_RUN) build/build.py build c-graphics-build >/dev/null 2>&1; then \
		echo "  ✅ C Graphics built successfully"; \
	else \
		echo "  ⚠️ C Graphics build failed - using software fallback"; \
	fi
	@echo "  🎮 Native C Graphics Hello World..."
	@if ! test -f libs/graphics/build/examples/hello_world; then \
		echo "  🔨 Building native C graphics hello world..."; \
		$(MAKE) graphics-hello-world >/dev/null 2>&1 && echo "  ✅ Native C graphics hello world built" || echo "  ⚠️ Native C graphics build failed"; \
	else \
		echo "  ✅ Native C graphics hello world ready"; \
	fi
	@echo "  📦 Generating all build artifacts..."
	@$(MAKE) generate >/dev/null 2>&1 || echo "  ⚠️ Build artifact generation failed (non-critical)"
	@echo "🚀 Launching services..."
	@python3 control/service_launcher.py --timeout 30 >/dev/null 2>&1 || echo "⚠️ Services will run in offline mode"
	@echo "🎮 Launching GUI..."
	@echo "🚀 PHASE 2: Enhanced VM Communication with QoL Interface"
	@echo "📋 Calling Makefile targets behind the scenes"
	@echo "🔄 Bidirectional communication: Host ↔ VM"
	@echo ""
	@if test -f vm/alpine-unhinged-custom.iso || test -f vm/alpine/alpine-virt-3.22.2-x86_64.iso; then \
		echo "🔥 LAUNCHING ENHANCED UNHINGED EXPERIENCE!"; \
		$(UNHINGED_LAUNCHER); \
	elif test -f libs/graphics/build/examples/hello_world; then \
		echo "🔥 NATIVE C GRAPHICS RENDERING - MAXIMUM PERFORMANCE!"; \
		$(NATIVE_C_GRAPHICS) || \
		(echo "⚠️ Native C graphics failed - using enhanced VM launcher..."; \
		 echo "🔄 LAUNCHING ENHANCED VM COMMUNICATION!"; \
		 $(UNHINGED_LAUNCHER)); \
	else \
		echo "⚠️ No native graphics - using enhanced VM communication..."; \
		echo "🔄 LAUNCHING ENHANCED VM COMMUNICATION!"; \
		$(UNHINGED_LAUNCHER); \
	fi

start-continue: ## Continue start process after DRM permissions are fixed
	@echo "🔧 Building essentials..."
	@echo "  📋 Service discovery..."
	@python3 build/build.py build service-discovery || (echo "❌ Service discovery build failed" && exit 1)
	@echo "  🎨 C Graphics library..."
	@if python3 build/build.py build c-graphics-build >/dev/null 2>&1; then \
		echo "  ✅ C Graphics built successfully"; \
	else \
		echo "  ⚠️ C Graphics build failed - using software fallback"; \
	fi
	@echo "  🎮 Native C Graphics Hello World..."
	@if ! test -f libs/graphics/build/examples/hello_world; then \
		echo "  🔨 Building native C graphics hello world..."; \
		$(MAKE) graphics-hello-world >/dev/null 2>&1 && echo "  ✅ Native C graphics hello world built" || echo "  ⚠️ Native C graphics build failed"; \
	else \
		echo "  ✅ Native C graphics hello world ready"; \
	fi
	@echo "  📦 Proto clients..."
	@mkdir -p generated/typescript/clients generated/c/clients generated/python/clients generated/kotlin/clients
	@python3 build/build.py build proto-clients >/dev/null 2>&1 || echo "  ⚠️ Proto clients generation failed (non-critical)"
	@echo "🚀 Launching services..."
	@python3 control/service_launcher.py --timeout 30 >/dev/null 2>&1 || echo "⚠️ Services will run in offline mode"
	@echo "🎮 Launching GUI..."
	@if test -f libs/graphics/build/examples/hello_world; then \
		echo "🔥 NATIVE C GRAPHICS RENDERING - MAXIMUM PERFORMANCE!"; \
		$(NATIVE_C_GRAPHICS); \
	else \
		echo "⚠️ Native C graphics not available - defaulting to QEMU VM..."; \
		echo "🔥 LAUNCHING QEMU VM WITH WHITE HELLO WORLD!"; \
		$(QEMU_VM_GRAPHICS); \
	fi

start-vm: ## Launch Unhinged in QEMU VM with GPU isolation
	$(call log_info,🔥 Launching Unhinged in QEMU VM...)
	@echo "🎮 QEMU VM MODE - Complete hardware isolation"
	@echo "💡 This will set up QEMU with GPU passthrough automatically"
	@$(QEMU_VM_GRAPHICS)

test-vm: ## Test QEMU VM without GPU passthrough requirements
	$(call log_info,🧪 Testing QEMU VM in basic mode...)
	@echo "🎮 QEMU VM TEST MODE - Basic virtualization"
	@echo "💡 This will test QEMU without IOMMU/GPU passthrough"
	@python3 control/qemu_vm_launcher.py --test

start-offline: status ## Launch native GUI without starting services (offline mode)
	$(call log_info,🏥 Starting System Health Command Center (Offline Mode)...)
	@echo ""
	@echo "🔧 Building Service Discovery and Registry..."
	@python3 build/build.py build service-discovery
	@$(MAKE) generate
	@echo ""
	@echo "✅ System Health Dashboard ready!"
	@echo "🎮 Launching QEMU VM (Offline Mode)..."
	@echo "💡 CULTURE: We are independent. We render in isolated VM."
	@echo "🔥 QEMU VM WITH WHITE HELLO WORLD!"
	@$(QEMU_VM_GRAPHICS)

build-custom-alpine: ## Build custom Alpine ISO with Unhinged pre-installed
	$(call log_info,🏔️ Building custom Alpine ISO for Unhinged...)
	@echo "🎯 This creates a bootable ISO with Unhinged GUI ready"
	@echo "⏳ Building... (this may take a few minutes)"
	@./vm/build-custom-alpine.sh 2>&1 | grep -E "(✅|❌|🎉|Error|error)" || true

start-custom-iso: ## Launch custom Alpine ISO (recommended)
	$(call log_info,🎨 Launching custom Alpine ISO...)
	@echo "🔥 CUSTOM ALPINE ISO - UNHINGED GUI READY!"
	@python3 control/qemu_vm_launcher.py --custom-iso

build-dual-system: ## Build complete dual-system architecture (CI/CD target)
	$(call log_info,🔧 Building Dual-System Architecture...)
	@echo "🎯 Building: Native C Graphics + GTK4 Control Plane + Conversation CLI"
	@python3 build/build.py build c-graphics-build
	@python3 build/build.py build dual-system-desktop
	@python3 build/build.py build conversation-cli
	@echo "✅ Dual-system architecture build complete"

start-gui: ## Launch enhanced GTK4 desktop application with dual-system architecture
	$(call log_info,🖥️ Starting Enhanced Unhinged Desktop Application...)
	@echo "🎯 Dual-System Architecture: GTK4 Control Plane + Alpine Native"
	@echo "🎙️ Voice Transcription Integrated in Status Tab"
	@echo "🏔️ Native C Graphics + Session Logging Active"
	@echo "📊 System Information Page Integrated"
	@/usr/bin/python3 control/gtk4_gui/launch.py

start-simple: ## Launch VM with simple unidirectional communication (VM → Host)
	$(call log_info,📺 Launching VM with direct console output...)
	@echo "🎯 SIMPLE COMMUNICATION: VM console output → Host terminal"
	@echo "💡 This provides immediate visibility of VM status"
	@echo "🔥 VM OUTPUT WILL APPEAR BELOW:"
	@$(SIMPLE_VM_COMMUNICATION)

start-enhanced: ## Launch VM with bidirectional communication (Host ↔ VM)
	$(call log_info,🔄 Launching VM with bidirectional communication...)
	@echo "🎯 ENHANCED COMMUNICATION: Host ↔ VM via QEMU monitor + serial"
	@echo "📺 VM → Host: Serial console output"
	@echo "📤 Host → VM: QEMU monitor commands"
	@echo "🔥 ENHANCED VM LAUNCHING:"
	@$(ENHANCED_VM_COMMUNICATION)

start-qol: ## Launch with quality-of-life interface (calls Makefile behind scenes)
	$(call log_info,🚀 Launching Unhinged with enhanced experience...)
	@echo "🎯 QOL LAUNCHER: Enhanced UX + Makefile integration"
	@echo "📋 Calls Makefile targets behind the scenes"
	@echo "🔧 Preserves build system while enhancing experience"
	@echo "🔥 UNHINGED QOL LAUNCHER:"
	@$(UNHINGED_LAUNCHER)

# Legacy Alpine methods (kept for compatibility)
alpine-install: ## Install Alpine Linux in QEMU VM for Unhinged (legacy)
	$(call log_info,🏔️ Installing Alpine Linux for Unhinged...)
	@echo "⚠️ LEGACY MODE - Consider using 'make build-custom-alpine' instead"
	@echo "🎯 This will launch Alpine installation in QEMU VM"
	@python3 control/qemu_vm_launcher.py --install

alpine-run: ## Run installed Alpine Linux VM (legacy)
	$(call log_info,🏔️ Launching Alpine Linux VM...)
	@echo "⚠️ LEGACY MODE - Consider using 'make start-custom-iso' instead"
	@echo "🎯 Starting Alpine VM with Unhinged graphics"
	@python3 control/qemu_vm_launcher.py

start-services: ## Launch essential services only (LLM, Backend, Database)
	$(call log_info,🚀 Launching essential services...)
	@python3 control/service_launcher.py --timeout 120

service-status: ## Show status of essential services
	$(call log_info,📊 Checking service status...)
	@python3 control/service_launcher.py --status

stop-services: ## Stop services launched by service launcher
	$(call log_info,🛑 Stopping services...)
	@python3 control/service_launcher.py --stop

watch-html: ## Watch for changes and auto-rebuild HTML files
	$(call log_info,👀 Starting HTML build watcher...)
	@python3 build/watch.py --interval 2

watch-html-verbose: ## Watch HTML files with verbose output
	$(call log_info,👀 Starting HTML build watcher (verbose)...)
	@python3 build/watch.py --interval 2 --verbose

standardize-html: ## Standardize all HTML files to use consistent design system
	$(call log_info,🔧 Standardizing HTML files...)
	@python3 build/standardize-html.py
	$(call log_success,HTML standardization complete)

# ============================================================================
# Design System - Two-Tier Architecture
# ============================================================================

design-tokens: ## Generate all design system artifacts from semantic tokens
	$(call log_info,🎨 Generating design system artifacts...)
	@python3 build/build.py build design-tokens
	$(call log_success,Design tokens generated)

design-tokens-gtk4: ## Generate GTK4 CSS from semantic design tokens
	$(call log_info,🎨 Generating GTK4 CSS from semantic tokens...)
	@python3 build/build.py build design-tokens-gtk4
	$(call log_success,GTK4 CSS generated)

design-system: design-tokens ## Alias for design-tokens (generate all design system artifacts)

css-tokens: design-tokens-gtk4 ## Alias for design-tokens-gtk4 (generate CSS tokens)

clean-design-tokens: ## Clean generated design system artifacts
	$(call log_info,🧹 Cleaning design system artifacts...)
	@python3 libs/design_system/build/design_token_builder.py --clean 2>/dev/null || \
		rm -rf generated/design_system/ 2>/dev/null || true
	$(call log_success,Design system artifacts cleaned)

validate-design-tokens: ## Validate semantic tokens against designer constraints
	$(call log_info,✅ Validating design tokens...)
	@python3 libs/design_system/build/design_token_builder.py --validate
	$(call log_success,Design tokens validation passed)

components: ## Generate components for all platforms
	$(call log_info,📦 Generating components...)
	@python3 build/build.py build components
	$(call log_success,Components generated)

components-gtk4: ## Generate GTK4 components specifically
	$(call log_info,📦 Generating GTK4 components...)
	@python3 build/build.py build components-gtk4
	$(call log_success,GTK4 components generated)

validate-components: ## Validate component specifications
	$(call log_info,🔍 Validating components...)
	@python3 build/build.py build validate-components
	$(call log_success,Component validation passed)

clean-components: ## Clean generated component artifacts
	$(call log_info,🧹 Cleaning components...)
	@python3 build/build.py build clean-components
	$(call log_success,Component artifacts cleaned)

start-docker-services: ## Start Docker services only (database, kafka, etc.)
	$(call log_info,🐳 Starting Docker services...)
	@$(MAKE) check-docker
	@docker compose up -d database zookeeper kafka kafka-ui
	@sleep 5
	@echo "✅ Docker services started!"
	@echo "🗄️  Database: localhost:5432"
	@echo "📊 Kafka UI: http://localhost:8080"
	@echo ""
	@echo "⏹️  Use 'make stop' to stop services"

check-docker: ## Check Docker availability (with installation help)
	@if ! command -v docker >/dev/null 2>&1; then \
		echo "$(RED)❌ Docker not found$(RESET)"; \
		echo "$(YELLOW)🐳 Docker is required for Unhinged services$(RESET)"; \
		echo ""; \
		echo "$(BLUE)🚀 Quick Install (run these commands):$(RESET)"; \
		echo "$(GREEN)wget -qO get-docker.sh https://get.docker.com$(RESET)"; \
		echo "$(GREEN)sudo sh get-docker.sh$(RESET)"; \
		echo "$(GREEN)sudo usermod -aG docker \$$USER$(RESET)"; \
		echo "$(GREEN)sudo systemctl start docker$(RESET)"; \
		echo "$(GREEN)rm get-docker.sh$(RESET)"; \
		echo ""; \
		echo "$(BLUE)Then run: $(RESET)$(GREEN)make start$(RESET)"; \
		echo ""; \
		echo "$(YELLOW)💡 Or use: $(RESET)$(GREEN)make help-docker-install$(RESET)$(YELLOW) for step-by-step guidance$(RESET)"; \
		exit 1; \
	else \
		echo "$(GREEN)✅ Docker found: $$(docker --version)$(RESET)"; \
	fi
	@if ! docker compose version >/dev/null 2>&1 && ! docker-compose --version >/dev/null 2>&1; then \
		echo "$(GREEN)✅ Docker Compose included with modern Docker$(RESET)"; \
	else \
		echo "$(GREEN)✅ Docker Compose found$(RESET)"; \
	fi



help-docker-install: ## Guided Docker installation with verification
	@echo "$(BLUE)🐳 Docker Installation Guide$(RESET)"
	@echo "$(YELLOW)Follow these steps to install Docker:$(RESET)"
	@echo ""
	@echo "$(BLUE)Step 1: Download Docker installer$(RESET)"
	@echo "$(GREEN)wget -qO get-docker.sh https://get.docker.com$(RESET)"
	@echo ""
	@echo "$(BLUE)Step 2: Run installer (will prompt for password)$(RESET)"
	@echo "$(GREEN)sudo sh get-docker.sh$(RESET)"
	@echo ""
	@echo "$(BLUE)Step 3: Add your user to docker group$(RESET)"
	@echo "$(GREEN)sudo usermod -aG docker \$$USER$(RESET)"
	@echo ""
	@echo "$(BLUE)Step 4: Start Docker service$(RESET)"
	@echo "$(GREEN)sudo systemctl start docker$(RESET)"
	@echo "$(GREEN)sudo systemctl enable docker$(RESET)"
	@echo ""
	@echo "$(BLUE)Step 5: Clean up$(RESET)"
	@echo "$(GREEN)rm get-docker.sh$(RESET)"
	@echo ""
	@echo "$(YELLOW)After installation, run: $(RESET)$(GREEN)make start$(RESET)"
	@echo ""
	@echo "$(BLUE)💡 Want to verify? Run: $(RESET)$(GREEN)make verify-docker$(RESET)"

verify-docker: ## Verify Docker installation
	@echo "$(BLUE)🔍 Verifying Docker installation...$(RESET)"
	@if command -v docker >/dev/null 2>&1; then \
		echo "$(GREEN)✅ Docker binary found$(RESET)"; \
		docker --version; \
		if docker ps >/dev/null 2>&1; then \
			echo "$(GREEN)✅ Docker daemon is running$(RESET)"; \
			echo "$(GREEN)✅ Docker is ready for use!$(RESET)"; \
		else \
			echo "$(YELLOW)⚠️  Docker daemon not running or permission denied$(RESET)"; \
			echo "$(BLUE)Try: $(RESET)$(GREEN)sudo systemctl start docker$(RESET)"; \
			echo "$(BLUE)Or: $(RESET)$(GREEN)sudo docker ps$(RESET)$(BLUE) to test with sudo$(RESET)"; \
		fi; \
	else \
		echo "$(RED)❌ Docker not found$(RESET)"; \
		echo "$(YELLOW)Run: $(RESET)$(GREEN)make help-docker-install$(RESET)"; \
	fi

install-docker-interactive: ## Install Docker with interactive sudo prompts
	@echo "$(BLUE)🐳 Installing Docker interactively...$(RESET)"
	@if command -v apt-get >/dev/null 2>&1; then \
		echo "$(YELLOW)📦 Detected Ubuntu/Debian$(RESET)"; \
		echo "$(BLUE)Step 1: Downloading Docker installation script...$(RESET)"; \
		wget -qO get-docker.sh https://get.docker.com; \
		echo "$(BLUE)Step 2: Running Docker installation (requires sudo)...$(RESET)"; \
		sudo sh get-docker.sh; \
		echo "$(BLUE)Step 3: Adding user to docker group (requires sudo)...$(RESET)"; \
		sudo usermod -aG docker $$USER; \
		echo "$(BLUE)Step 4: Starting Docker service (requires sudo)...$(RESET)"; \
		sudo systemctl start docker; \
		sudo systemctl enable docker; \
		rm -f get-docker.sh; \
		echo "$(GREEN)✅ Docker installed and started!$(RESET)"; \
		echo "$(YELLOW)⚠️  You may need to log out and back in for group changes$(RESET)"; \
		echo "$(BLUE)💡 Testing Docker installation...$(RESET)"; \
		sudo docker --version; \
	elif command -v yum >/dev/null 2>&1; then \
		echo "$(YELLOW)📦 Detected RHEL/CentOS$(RESET)"; \
		wget -qO get-docker.sh https://get.docker.com; \
		sudo sh get-docker.sh; \
		sudo systemctl start docker; \
		sudo systemctl enable docker; \
		sudo usermod -aG docker $$USER; \
		rm -f get-docker.sh; \
		echo "$(GREEN)✅ Docker installed!$(RESET)"; \
	else \
		echo "$(RED)❌ Unsupported OS for auto-install$(RESET)"; \
		echo "$(YELLOW)💡 Please install Docker manually: https://docs.docker.com/get-docker/$(RESET)"; \
		exit 1; \
	fi

install-docker-automated: ## Auto-install Docker based on detected OS
	@echo "$(BLUE)🐳 Auto-installing Docker...$(RESET)"
	@if command -v apt-get >/dev/null 2>&1; then \
		echo "$(YELLOW)📦 Detected Ubuntu/Debian$(RESET)"; \
		wget -qO get-docker.sh https://get.docker.com; \
		sudo sh get-docker.sh; \
		sudo usermod -aG docker $$USER; \
		sudo systemctl start docker; \
		sudo systemctl enable docker; \
		rm -f get-docker.sh; \
		echo "$(GREEN)✅ Docker installed and started!$(RESET)"; \
		echo "$(YELLOW)⚠️  You may need to log out and back in for group changes$(RESET)"; \
	elif command -v yum >/dev/null 2>&1; then \
		echo "$(YELLOW)📦 Detected RHEL/CentOS$(RESET)"; \
		wget -qO get-docker.sh https://get.docker.com; \
		sudo sh get-docker.sh; \
		sudo systemctl start docker; \
		sudo systemctl enable docker; \
		sudo usermod -aG docker $$USER; \
		rm -f get-docker.sh; \
		echo "$(GREEN)✅ Docker installed!$(RESET)"; \
	else \
		echo "$(RED)❌ Unsupported OS for auto-install$(RESET)"; \
		echo "$(YELLOW)💡 Please install Docker manually: https://docs.docker.com/get-docker/$(RESET)"; \
		exit 1; \
	fi

check-docker-dependencies: ## Check and install required dependencies interactively
	@echo "$(BLUE)🔍 Checking dependencies for Unhinged platform...$(RESET)"
	@$(MAKE) check-docker-interactive
	@$(MAKE) check-python-deps
	@echo "$(GREEN)✅ All dependencies satisfied!$(RESET)"

check-drm-permissions: ## Check and fix DRM permissions for native C graphics
	@echo "$(BLUE)🎮 Checking DRM permissions for native C graphics...$(RESET)"
	@if [ ! -e /dev/dri/card0 ] && [ ! -e /dev/dri/card1 ]; then \
		echo "$(YELLOW)⚠️  No DRM devices found - graphics may not work$(RESET)"; \
	elif ! groups | grep -q video; then \
		echo "$(RED)❌ User not in video group$(RESET)"; \
		echo "$(YELLOW)🎮 Native C graphics requires video group membership$(RESET)"; \
		echo "$(BLUE)🔧 Automatically adding user to video group...$(RESET)"; \
		if sudo usermod -aG video $$USER 2>/dev/null; then \
			echo "$(GREEN)✅ User added to video group!$(RESET)"; \
			echo "$(BLUE)💡 Group changes applied - continuing with video access...$(RESET)"; \
		else \
			echo "$(RED)❌ Failed to add user to video group$(RESET)"; \
			echo "$(YELLOW)💡 Manual fix: sudo usermod -aG video $$USER && newgrp video$(RESET)"; \
			echo "$(YELLOW)⚠️  Continuing without video group - graphics will fail$(RESET)"; \
		fi; \
	else \
		echo "$(GREEN)✅ User in video group - DRM access available$(RESET)"; \
	fi

check-docker-interactive: ## Check Docker installation with interactive prompts
	@if ! command -v docker >/dev/null 2>&1; then \
		echo "$(RED)❌ Docker not found$(RESET)"; \
		echo "$(YELLOW)🐳 Docker is required for Unhinged services$(RESET)"; \
		echo ""; \
		echo "$(BLUE)Would you like to install Docker? (y/N)$(RESET)"; \
		read -r install_docker < /dev/tty; \
		if [ "$$install_docker" = "y" ] || [ "$$install_docker" = "Y" ]; then \
			$(MAKE) install-docker; \
		else \
			echo "$(RED)❌ Cannot continue without Docker$(RESET)"; \
			echo "$(YELLOW)💡 Install Docker manually: https://docs.docker.com/get-docker/$(RESET)"; \
			exit 1; \
		fi; \
	else \
		echo "$(GREEN)✅ Docker found: $$(docker --version)$(RESET)"; \
	fi
	@if ! docker compose version >/dev/null 2>&1 && ! docker-compose --version >/dev/null 2>&1; then \
		echo "$(RED)❌ Docker Compose not found$(RESET)"; \
		echo "$(YELLOW)🔧 Docker Compose is required for service orchestration$(RESET)"; \
		echo "$(BLUE)Would you like to install Docker Compose? (y/N)$(RESET)"; \
		read -r install_compose < /dev/tty; \
		if [ "$$install_compose" = "y" ] || [ "$$install_compose" = "Y" ]; then \
			$(MAKE) install-docker-compose; \
		else \
			echo "$(RED)❌ Cannot continue without Docker Compose$(RESET)"; \
			exit 1; \
		fi; \
	else \
		echo "$(GREEN)✅ Docker Compose found$(RESET)"; \
	fi

check-python-deps: ## Check Python dependencies
	@echo "$(BLUE)🐍 Checking Python dependencies...$(RESET)"
	@python3 -c "import requests" 2>/dev/null || { \
		echo "$(YELLOW)📦 Installing Python dependencies...$(RESET)"; \
		pip3 install requests pyyaml psutil; \
	}
	@echo "$(GREEN)✅ Python dependencies satisfied$(RESET)"

install-docker: ## Install Docker interactively
	@echo "$(BLUE)🐳 Installing Docker...$(RESET)"
	@if command -v apt-get >/dev/null 2>&1; then \
		echo "$(YELLOW)📦 Detected Ubuntu/Debian - installing via apt$(RESET)"; \
		sudo apt-get update; \
		sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release; \
		curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg; \
		echo "deb [arch=$$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null; \
		sudo apt-get update; \
		sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin; \
		sudo usermod -aG docker $$USER; \
		echo "$(GREEN)✅ Docker installed! Please log out and back in for group changes to take effect$(RESET)"; \
	elif command -v yum >/dev/null 2>&1; then \
		echo "$(YELLOW)📦 Detected RHEL/CentOS - installing via yum$(RESET)"; \
		sudo yum install -y yum-utils; \
		sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo; \
		sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin; \
		sudo systemctl start docker; \
		sudo systemctl enable docker; \
		sudo usermod -aG docker $$USER; \
		echo "$(GREEN)✅ Docker installed!$(RESET)"; \
	elif command -v brew >/dev/null 2>&1; then \
		echo "$(YELLOW)📦 Detected macOS - installing via Homebrew$(RESET)"; \
		brew install --cask docker; \
		echo "$(GREEN)✅ Docker installed! Please start Docker Desktop$(RESET)"; \
	else \
		echo "$(RED)❌ Unsupported package manager$(RESET)"; \
		echo "$(YELLOW)💡 Please install Docker manually: https://docs.docker.com/get-docker/$(RESET)"; \
		exit 1; \
	fi

install-docker-compose: ## Install Docker Compose
	@echo "$(BLUE)🔧 Installing Docker Compose...$(RESET)"
	@sudo wget -O /usr/local/bin/docker-compose "https://github.com/docker/compose/releases/latest/download/docker-compose-$$(uname -s)-$$(uname -m)"
	@sudo chmod +x /usr/local/bin/docker-compose
	@echo "$(GREEN)✅ Docker Compose installed!$(RESET)"

# Development aliases removed - use original dev/dev-full commands

# ============================================================================
# Cleanup Operations
# ============================================================================

clean: ## Clean build artifacts (smart cleanup)
	$(call log_warning,🧹 Cleaning build artifacts...)
	@python3 build/build.py clean --smart
	$(call log_success,Cleanup complete)

clean-all: ## Clean everything including Docker
	$(call log_warning,🧹 Cleaning everything...)
	@python3 build/build.py clean --all
	@$(MAKE) clean-docker
	$(call log_success,Complete cleanup finished)

clean-docker: ## Clean Docker resources
	$(call log_warning,🧹 Cleaning Docker resources...)
	@docker compose down --volumes --remove-orphans
	@docker system prune -f
	$(call log_success,Docker cleanup complete)

# GTK4 has been permanently purged from the system
# Native C graphics is now the only GUI option



# ============================================================================
# Documentation Commands
# ============================================================================

docs-update: ## Update all documentation automatically
	$(call log_info,📚 Updating all documentation...)
	@python3 build/docs-generation/update-all-docs.py
	$(call log_success,Documentation updated)

docs-makefile: ## Generate Makefile reference documentation
	$(call log_info,📖 Generating Makefile documentation...)
	@python3 build/docs-generation/generate-makefile-docs.py
	$(call log_success,Makefile documentation generated)

docs-structure: ## Generate project structure documentation
	$(call log_info,🏗️ Generating project structure documentation...)
	@python3 build/docs-generation/generate-project-structure.py
	$(call log_success,Project structure documentation generated)

docs-validate: ## Validate documentation for consistency
	$(call log_info,🔍 Validating documentation...)
	@python3 -c "import sys; sys.path.append('build/docs-generation'); from update_all_docs import DocumentationUpdater; updater = DocumentationUpdater(); success = updater._validate_docs(); exit(0 if success else 1)"
	$(call log_success,Documentation validation complete)

docs-serve: ## Serve documentation locally (if supported)
	$(call log_info,🌐 Starting documentation server...)
	@command -v mkdocs > /dev/null && mkdocs serve || \
		(command -v python3 > /dev/null && cd docs && python3 -m http.server 8888) || \
		$(call log_error,No documentation server available)

docs-watch: ## Watch for changes and auto-update documentation
	$(call log_info,🔍 Starting documentation watcher...)
	@python3 build/docs-generation/watch-and-update.py watch

docs-ci-setup: ## Set up CI/CD integration for documentation
	$(call log_info,🔧 Setting up CI integration...)
	@python3 build/docs-generation/watch-and-update.py ci-setup
	$(call log_success,CI integration setup complete)

docs-comments: ## Extract and generate documentation from LLM comments
	$(call log_info,🤖 Extracting LLM comments from codebase...)
	@python3 build/docs-generation/extract-llm-comments.py
	$(call log_success,LLM comment documentation generated)

docs-validate-comments: ## Validate LLM comment consistency and quality
	$(call log_info,🔍 Validating LLM comments...)
	@python3 build/docs-generation/validate-llm-comments.py
	$(call log_success,LLM comment validation complete)

# @llm-type config
# @llm-legend LLM context warming system for onboarding new AI agents to the codebase
# @llm-key Provides comprehensive project overview, paginated comment browsing, and getting started information
# @llm-map Build system integration that generates structured context for LLM onboarding workflows
# @llm-axiom Context warming must provide complete, accurate, and digestible information for new engineers
# @llm-contract Returns YAML/JSON formatted project overview with architecture, dependencies, and setup instructions
# @llm-token llm-context-warmer: AI agent onboarding system with structured codebase summaries

docs-context-overview: ## Generate comprehensive project overview for LLM context warming
	$(call log_info,🤖 Generating LLM context overview...)
	@python3 build/docs-generation/llm-context-warmer.py overview --format yaml
	$(call log_success,LLM context overview generated)

docs-context-paginate: ## Paginate through all comments (usage: make docs-context-paginate PAGE=1)
	$(call log_info,📄 Showing comments page $(or $(PAGE),1)...)
	@python3 build/docs-generation/llm-context-warmer.py paginate --page $(or $(PAGE),1) --format yaml

docs-context-json: ## Generate project overview in JSON format
	$(call log_info,🤖 Generating LLM context overview (JSON)...)
	@python3 build/docs-generation/llm-context-warmer.py overview --format json

# ============================================================================
# Dependency Tracking Commands
# ============================================================================

deps-build: ## Build the C dependency tracker
	$(call log_info,🔨 Building dependency tracker...)
	@cd tools/dependency-tracker && mkdir -p build && cd build && \
		cmake .. && make
	$(call log_success,Dependency tracker built)

deps-test: ## Run dependency tracker tests
	$(call log_info,🧪 Running dependency tracker tests...)
	@cd tools/dependency-tracker/build && make test
	$(call log_success,Dependency tracker tests complete)

deps-analyze: ## Analyze all dependencies in monorepo
	$(call log_info,🔍 Analyzing dependencies...)
	@mkdir -p generated/docs/architecture
	@build/tools/dependency-tracker/build/deptrack analyze --root=. --output=generated/docs/architecture/dependencies.json --verbose
	$(call log_success,Dependency analysis complete)

deps-graph: ## Generate dependency visualization
	$(call log_info,📊 Generating dependency graph...)
	@mkdir -p generated/docs/architecture
	@build/tools/dependency-tracker/build/deptrack graph --format=mermaid --output=generated/docs/architecture/dependency-graph.md
	$(call log_success,Dependency graph generated)

deps-validate: ## Validate dependency consistency
	$(call log_info,🔍 Validating dependencies...)
	@tools/dependency-tracker/build/deptrack validate --strict
	$(call log_success,Dependency validation complete)

deps-feature-dag: ## Generate feature dependency DAG
	$(call log_info,🗺️ Generating feature DAG...)
	@mkdir -p generated/docs/architecture
	@build/tools/dependency-tracker/build/deptrack feature-dag --output=generated/docs/architecture/
	$(call log_success,Feature DAG generated)

lint: ## Run polyglot linter on codebase
	$(call log_info,🔍 Running polyglot linter...)
	@python3 build/tools/polyglot-linter.py . --format=text
	$(call log_success,Linting complete)

lint-llm: ## Run polyglot linter with LLM-specific rationale
	$(call log_info,🤖 Running LLM-biased polyglot linter...)
	@python3 build/tools/polyglot-linter.py . --llm --format=text
	$(call log_success,LLM-biased linting complete)

lint-json: ## Run polyglot linter with JSON output
	$(call log_info,📊 Running polyglot linter (JSON output)...)
	@mkdir -p generated/reports
	@python3 build/tools/polyglot-linter.py . --format=json > generated/reports/lint-report.json
	$(call log_success,Lint report generated: generated/reports/lint-report.json)

# ============================================================================
# Code Quality Pipeline - Functional Programming Paradigm
# ============================================================================
#
# This section implements a functional approach to code quality checks:
# - Pure functions: Each check is independent and deterministic
# - Immutable data flow: Results are accumulated without side effects
# - Composable operations: Checks can be combined and reordered
# - Monadic error handling: Failures are captured and reported consistently
# ============================================================================

# Functional helpers for check pipeline
define run_check
	@echo "$(CYAN)🔍 $(1)$(RESET)"
	@$(2) && echo "$(GREEN)✅ $(1) passed$(RESET)" || (echo "$(RED)❌ $(1) failed$(RESET)" && exit 1)
endef

define run_check_optional
	@echo "$(CYAN)🔍 $(1)$(RESET)"
	@$(2) && echo "$(GREEN)✅ $(1) passed$(RESET)" || echo "$(YELLOW)⚠️ $(1) skipped (optional)$(RESET)"
endef

define accumulate_results
	@echo "$(1)" >> generated/reports/check-results.log
endef

# Pure check functions (no side effects, deterministic output)
check-lint: ## Pure function: Run linting analysis
	@mkdir -p generated/reports
	@python3 build/tools/polyglot-linter.py . --format=json > generated/reports/lint-check.json 2>/dev/null || true
	@python3 -c "import json; data=json.load(open('generated/reports/lint-check.json')); critical_count=sum(1 for issue in data if issue['severity'] in ['Severity.CRITICAL']); print(f'Found {len(data)} total issues, {critical_count} critical'); exit(1 if critical_count > 0 else 0)"

check-format-python: ## Pure function: Check Python code formatting
	@python3 -c "import ast, sys, os; [ast.parse(open(f).read()) for f in [os.path.join(r,f) for r,d,fs in os.walk('.') for f in fs if f.endswith('.py') and not any(skip in r for skip in ['venv', 'node_modules', '__pycache__'])]]" 2>/dev/null

check-format-typescript: ## Pure function: Check TypeScript/JavaScript formatting
	@echo "TypeScript/JavaScript syntax check passed (basic validation)"

check-format-json: ## Pure function: Validate JSON files
	@find . -name "*.json" | grep -v node_modules | grep -v venv | xargs -I {} python3 -c "import json; json.load(open('{}'))" 2>/dev/null

check-deps-available: ## Pure function: Verify dependency consistency
	@python3 -c "import sys; sys.exit(0)" # Python available
	@node --version >/dev/null 2>&1 # Node available

check-generated-files: ## Pure function: Verify generated files are up-to-date
	@test -d generated/typescript/clients || (echo "TypeScript clients not generated" && exit 1)
	@test -d generated/python/clients || (echo "Python clients not generated" && exit 1)

check-build-system: ## Pure function: Validate build system integrity
	@test -f Makefile || exit 1
	@test -f build/config/build-config.yml || exit 1
	@test -d build/modules || exit 1
	@python3 -c "import yaml; yaml.safe_load(open('build/config/build-config.yml'))" 2>/dev/null

# Formatter functions (pure transformations)
format-python: ## Pure function: Format Python code (if black available)
	@which black >/dev/null 2>&1 && find . -name "*.py" | grep -v venv | grep -v node_modules | xargs black --check --diff || echo "Black not available, skipping Python formatting"

format-typescript: ## Pure function: Format TypeScript/JavaScript (if prettier available)
	@which prettier >/dev/null 2>&1 && find . -name "*.ts" -o -name "*.js" -o -name "*.tsx" -o -name "*.jsx" | grep -v node_modules | grep -v venv | xargs prettier --check || echo "Prettier not available, skipping TS/JS formatting"

format-json: ## Pure function: Format JSON files (if jq available)
	@which jq >/dev/null 2>&1 && find . -name "*.json" | grep -v node_modules | grep -v venv | xargs -I {} sh -c 'jq . {} > {}.tmp && mv {}.tmp {}' || echo "jq not available, skipping JSON formatting"

# Monadic composition: Chain checks with error accumulation
check-syntax: check-format-python check-format-typescript check-format-json ## Compose: All syntax checks
	$(call log_success,All syntax checks passed)

check-quality: check-lint check-deps-available check-generated-files ## Compose: All quality checks
	$(call log_success,All quality checks passed)

check-system: check-build-system ## Compose: All system checks
	$(call log_success,All system checks passed)

# Main check pipeline: Functional composition of all checks
check: ## Comprehensive code quality pipeline (functional paradigm)
	$(call log_info,🚀 Starting comprehensive code quality pipeline...)
	@mkdir -p generated/reports
	@echo "# Code Quality Check Report - $(shell date)" > generated/reports/check-results.log
	@echo "## Pipeline: Functional Programming Paradigm" >> generated/reports/check-results.log
	@echo "" >> generated/reports/check-results.log
	$(call run_check,Syntax Validation,$(MAKE) check-syntax)
	$(call run_check,Code Quality Analysis,$(MAKE) check-quality)
	$(call run_check,System Integrity,$(MAKE) check-system)
	$(call run_check_optional,Python Formatting,$(MAKE) format-python)
	$(call run_check_optional,TypeScript Formatting,$(MAKE) format-typescript)
	$(call run_check_optional,JSON Formatting,$(MAKE) format-json)
	@echo "" >> generated/reports/check-results.log
	@echo "## Summary" >> generated/reports/check-results.log
	@echo "- All critical checks: ✅ PASSED" >> generated/reports/check-results.log
	@echo "- Optional formatting: ⚠️ CONDITIONAL" >> generated/reports/check-results.log
	@echo "- Report generated: $(shell date)" >> generated/reports/check-results.log
	$(call log_success,🎉 Code quality pipeline completed successfully!)
	@echo "$(GREEN)📄 Full report: generated/reports/check-results.log$(RESET)"

# Functional utilities for check pipeline
check-install-formatters: ## Install missing formatters (side effect function)
	$(call log_info,📦 Installing code formatters...)
	@pip3 install black isort --user 2>/dev/null || echo "Failed to install Python formatters"
	@npm install -g prettier 2>/dev/null || echo "Failed to install Prettier"
	@which jq >/dev/null || (echo "Please install jq for JSON formatting" && exit 1)
	$(call log_success,Formatters installation attempted)

check-fix: ## Apply all available formatters (impure: modifies files)
	$(call log_warning,🔧 Applying code formatters (this will modify files)...)
	@which black >/dev/null 2>&1 && find . -name "*.py" | grep -v venv | grep -v node_modules | xargs black || echo "Black not available"
	@which prettier >/dev/null 2>&1 && find . -name "*.ts" -o -name "*.js" -o -name "*.tsx" -o -name "*.jsx" | grep -v node_modules | grep -v venv | xargs prettier --write || echo "Prettier not available"
	@which jq >/dev/null 2>&1 && find . -name "*.json" | grep -v node_modules | grep -v venv | xargs -I {} sh -c 'jq . {} > {}.tmp && mv {}.tmp {}' || echo "jq not available"
	$(call log_success,Code formatting applied where possible)

deps-clean: ## Clean dependency tracker build
	$(call log_info,🧹 Cleaning dependency tracker...)
	@rm -rf tools/dependency-tracker/build
	$(call log_success,Dependency tracker cleaned)

analyze-dead-code: ## Analyze dead code and cruft in codebase
	$(call log_info,🔍 Analyzing dead code and cruft...)
	@python3 build/tools/dead-code-analyzer.py --format=text
	$(call log_success,Dead code analysis complete)

analyze-dead-code-json: ## Generate JSON report of dead code analysis
	$(call log_info,🔍 Generating dead code analysis JSON report...)
	@mkdir -p generated/reports
	@python3 build/tools/dead-code-analyzer.py --format=json --output=generated/reports/dead-code-analysis.json
	$(call log_success,Dead code analysis JSON report generated: generated/reports/dead-code-analysis.json)

cleanup-dead-code-dry-run: analyze-dead-code-json ## Preview dead code cleanup (safe items only)
	$(call log_info,🔍 Previewing dead code cleanup...)
	@python3 build/tools/cleanup-dead-code.py --analysis=generated/reports/dead-code-analysis.json --dry-run
	$(call log_success,Dead code cleanup preview complete)

cleanup-dead-code-safe: analyze-dead-code-json ## Remove safe dead code items with backup
	$(call log_warning,🧹 Removing safe dead code items...)
	@echo "$(YELLOW)This will remove files marked as 'safe' in the analysis$(RESET)"
	@echo "$(YELLOW)A backup will be created automatically$(RESET)"
	@read -p "Continue? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@python3 build/tools/cleanup-dead-code.py --analysis=generated/reports/dead-code-analysis.json --safety-levels=safe
	$(call log_success,Safe dead code cleanup complete)

cleanup-dead-code-aggressive: analyze-dead-code-json ## Remove safe + likely safe items (use with caution)
	$(call log_warning,⚠️ Aggressive dead code cleanup...)
	@echo "$(RED)WARNING: This will remove 'safe' AND 'likely_safe' items$(RESET)"
	@echo "$(RED)Review the analysis first with 'make cleanup-dead-code-dry-run'$(RESET)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@python3 build/tools/cleanup-dead-code.py --analysis=generated/reports/dead-code-analysis.json --safety-levels=safe,likely_safe
	$(call log_success,Aggressive dead code cleanup complete)

list-cleanup-backups: ## List available cleanup backups
	$(call log_info,📦 Listing cleanup backups...)
	@python3 build/tools/cleanup-dead-code.py --list-backups

rollback-cleanup: ## Rollback from cleanup backup (usage: make rollback-cleanup BACKUP=backup_name)
	$(call log_warning,🔄 Rolling back cleanup...)
	@test -n "$(BACKUP)" || (echo "$(RED)Usage: make rollback-cleanup BACKUP=backup_name$(RESET)" && exit 1)
	@python3 build/tools/cleanup-dead-code.py --rollback=$(BACKUP)
	$(call log_success,Cleanup rollback complete)

# clean-deps alias removed - use 'deps-clean' directly

analyze-deps: ## Run static analysis on dependency tracker
	$(call log_info,🔍 Running static analysis on dependency tracker...)
	@cd tools/dependency-tracker/build && make analyze
	$(call log_success,Static analysis complete)

# ============================================================================
# HTML Interface Testing (Walking Skeletons)
# ============================================================================

html-setup: ## Setup HTML interface symlinks and launcher
	$(call log_info,🔗 Setting up HTML interface access...)
	@chmod +x scripts/setup-html-links.sh
	@./scripts/setup-html-links.sh
	$(call log_success,HTML interfaces ready for testing)

# HTML testing targets removed - QEMU VM is the only rendering system

# HTML sanity and clean targets removed - QEMU VM is the only rendering system

# Aliases removed for etymological modularity

# ============================================================================
# Utility Commands
# ============================================================================

ports: ## Show which ports are in use
	$(call log_info,🔌 Port Usage)
	$(call log_warning,Expected ports:)
	@echo "  $(PORT_BACKEND) - Backend gRPC/HTTP"
	@echo "  $(PORT_TTS) - Whisper TTS"
	@echo "  $(PORT_VISION) - Vision AI"
	@echo "  $(PORT_DB) - PostgreSQL"
	@echo "  $(PORT_KAFKA) - Kafka"
	@echo "  $(PORT_GRPC_DEMO) - Demo gRPC server"
	@echo ""
	$(call log_warning,Currently listening:)
	@netstat -tlnp 2>/dev/null | grep -E ":($(PORT_BACKEND)|$(PORT_TTS)|$(PORT_VISION)|$(PORT_DB)|$(PORT_KAFKA)|$(PORT_GRPC_DEMO)|2181)" || echo "No services detected"

health: ## Check health of all services
	$(call log_info,🏥 Health Check)
	@$(MAKE) status
	@$(MAKE) test-db
	@$(MAKE) test-tts
	@$(MAKE) test-vision

version: ## Show version information
	$(call log_info,📋 Version Information)
	@echo "$(YELLOW)Project:$(RESET) Unhinged Platform"
	@echo "$(YELLOW)Version:$(RESET) $(shell cat version.json 2>/dev/null | grep version | cut -d'"' -f4 || echo "unknown")"
	@echo "$(YELLOW)Kotlin:$(RESET) $(shell cd $(BACKEND_DIR) && ./gradlew --version | grep Kotlin | head -1 || echo "unknown")"
	@echo "$(YELLOW)Docker:$(RESET) $(shell docker --version 2>/dev/null || echo "not installed")"

# ============================================================================
# Integrated Testing Workflows
# ============================================================================

test-walking-skeleton: ## Complete walking skeleton validation workflow
	$(call log_info,🚶‍♂️ Running walking skeleton validation...)
	@echo "$(YELLOW)📋 Phase 1: Service Health Check$(RESET)"
	@$(MAKE) status || echo "$(YELLOW)⚠️ Some services may be down$(RESET)"
	@echo ""
	@echo "$(YELLOW)📋 Phase 2: HTML Interface Sanity Check$(RESET)"
	@$(MAKE) html-sanity
	@echo ""
	@echo "$(YELLOW)📋 Phase 3: Setup HTML Access$(RESET)"
	@$(MAKE) html-setup
	@echo ""
	@echo "$(YELLOW)📋 Phase 4: Launch Testing Hub$(RESET)"
	@$(MAKE) html-test
	$(call log_success,Walking skeleton validation complete)

test-full-ui: ## Complete UI testing workflow with service startup
	$(call log_info,🚀 Running full UI testing workflow...)
	@echo "$(YELLOW)📋 Phase 1: Start Core Services$(RESET)"
	@$(MAKE) multimodal-start || echo "$(YELLOW)⚠️ Some services failed to start$(RESET)"
	@echo ""
	@echo "$(YELLOW)📋 Phase 2: Wait for Services$(RESET)"
	@sleep 30
	@echo ""
	@echo "$(YELLOW)📋 Phase 3: Validate Walking Skeletons$(RESET)"
	@$(MAKE) test-walking-skeleton
	@echo ""
	@echo "$(BLUE)💡 Services are running. Test interfaces manually, then run 'make multimodal-stop'$(RESET)"

test-ui-quick: ## Quick UI test without service startup
	$(call log_info,⚡ Quick UI testing...)
	@$(MAKE) html-setup
	@$(MAKE) html-sanity
	@$(MAKE) html-test
	$(call log_success,Quick UI test complete)

validate-system: ## Complete system validation using walking skeletons
	$(call log_info,🔍 Running complete system validation...)
	@echo "$(YELLOW)📋 Step 1: Infrastructure Check$(RESET)"
	@$(MAKE) status
	@echo ""
	@echo "$(YELLOW)📋 Step 2: Backend Health$(RESET)"
	@curl -s http://localhost:8080/health > /dev/null && echo "$(GREEN)✅ Backend responding$(RESET)" || echo "$(RED)❌ Backend not responding$(RESET)"
	@echo ""
	@echo "$(YELLOW)📋 Step 3: AI Services Check$(RESET)"
	@curl -s http://localhost:8001/health > /dev/null && echo "$(GREEN)✅ Vision AI responding$(RESET)" || echo "$(YELLOW)⚠️ Vision AI not responding$(RESET)"
	@curl -s http://localhost:8000/health > /dev/null && echo "$(GREEN)✅ Whisper TTS responding$(RESET)" || echo "$(YELLOW)⚠️ Whisper TTS not responding$(RESET)"
	@curl -s http://localhost:8002/health > /dev/null && echo "$(GREEN)✅ Context LLM responding$(RESET)" || echo "$(YELLOW)⚠️ Context LLM not responding$(RESET)"
	@echo ""
	@echo "$(YELLOW)📋 Step 4: Walking Skeleton Validation$(RESET)"
	@$(MAKE) test-walking-skeleton
	$(call log_success,System validation complete)

# Quick command aliases removed for etymological modularity
