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
# Help and Information
# ============================================================================

help: ## Show this help message
	@echo "$(CYAN)🚀 Unhinged Platform - Development Commands$(RESET)"
	@echo ""
	@echo "$(YELLOW)📋 Available commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BLUE)💡 Quick start: make setup && make dev$(RESET)"
	@echo "$(BLUE)📚 Documentation: make docs-update$(RESET)"
	@echo "$(BLUE)🤖 AI Context: make context$(RESET)"
	@echo "$(BLUE)🔍 Dependencies: make deps-build && make deps-analyze$(RESET)"
	@echo ""
	@echo "$(PURPLE)🚀 Core Build Commands (v1):$(RESET)"
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

services-status: ## Show status of all services
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

install: setup ## Alias for setup

# ============================================================================
# Docker Services Management
# ============================================================================

up: ## Start all services
	$(call log_info,🚀 Starting all services...)
	@docker compose up -d
	$(call log_success,Services started)
	@$(MAKE) status

down: ## Stop all services
	$(call log_warning,🛑 Stopping all services...)
	@docker compose down
	$(call log_success,Services stopped)

restart: down up ## Restart all services

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
# Protobuf Operations
# ============================================================================

proto-gen: ## Generate protobuf code
	$(call log_info,🔧 Generating protobuf code...)
	$(call run_gradle,generateProto)
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

status: ## Show build system status and performance metrics
	$(call log_info,📊 Build system status...)
	@python3 build/build.py status

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

start: ## Start the unified control plane with browser interface (auto-installs dependencies)
	$(call log_info,🎛️ Starting Unhinged Control Plane...)
	@$(MAKE) ensure-docker
	@python3 build/generate-registry.py
	@echo "🔄 Stopping any existing DAG server..."
	@-pkill -f "python3 -m control" 2>/dev/null || true
	@sleep 1
	@echo "🚀 Launching fresh DAG Control Plane on port 9000..."
	@python3 -m control --port 9000 &
	@sleep 3
	@echo "🌐 Opening browser interface..."
	@./control/open.sh --status
	@echo "✅ Control plane started successfully!"
	@echo "📊 DAG Control: http://localhost:9000/dag/health"
	@echo "🌐 Browser: file://$(PWD)/control/static_html/index.html"
	@echo "⏹️  Press Ctrl+C to stop"

ensure-docker: ## Ensure Docker is available (with installation help)
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
		echo "$(YELLOW)💡 Or use: $(RESET)$(GREEN)make install-docker-help$(RESET)$(YELLOW) for step-by-step guidance$(RESET)"; \
		exit 1; \
	else \
		echo "$(GREEN)✅ Docker found: $$(docker --version)$(RESET)"; \
	fi
	@if ! docker compose version >/dev/null 2>&1 && ! docker-compose --version >/dev/null 2>&1; then \
		echo "$(GREEN)✅ Docker Compose included with modern Docker$(RESET)"; \
	else \
		echo "$(GREEN)✅ Docker Compose found$(RESET)"; \
	fi

install-docker-help: ## Guided Docker installation with verification
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
		echo "$(YELLOW)Run: $(RESET)$(GREEN)make install-docker-help$(RESET)"; \
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

install-docker-auto: ## Auto-install Docker based on detected OS
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

check-dependencies: ## Check and install required dependencies interactively
	@echo "$(BLUE)🔍 Checking dependencies for Unhinged platform...$(RESET)"
	@$(MAKE) check-docker
	@$(MAKE) check-python-deps
	@echo "$(GREEN)✅ All dependencies satisfied!$(RESET)"

check-docker: ## Check Docker installation
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
	@echo "station1" | sudo -S wget -O /usr/local/bin/docker-compose "https://github.com/docker/compose/releases/latest/download/docker-compose-$$(uname -s)-$$(uname -m)"
	@echo "station1" | sudo -S chmod +x /usr/local/bin/docker-compose
	@echo "$(GREEN)✅ Docker Compose installed!$(RESET)"

# Development Aliases (v1 clean interface)
dev: build ## Start development environment
dev-full: build-full ## Start complete development environment

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



# ============================================================================
# Documentation Commands
# ============================================================================

docs-update: ## Update all documentation automatically
	$(call log_info,📚 Updating all documentation...)
	@python3 scripts/docs/update-all-docs.py
	$(call log_success,Documentation updated)

docs-makefile: ## Generate Makefile reference documentation
	$(call log_info,📖 Generating Makefile documentation...)
	@python3 scripts/docs/generate-makefile-docs.py
	$(call log_success,Makefile documentation generated)

docs-structure: ## Generate project structure documentation
	$(call log_info,🏗️ Generating project structure documentation...)
	@python3 scripts/docs/generate-project-structure.py
	$(call log_success,Project structure documentation generated)

docs-validate: ## Validate documentation for consistency
	$(call log_info,🔍 Validating documentation...)
	@python3 -c "from scripts.docs.update_all_docs import DocumentationUpdater; updater = DocumentationUpdater(); success = updater._validate_docs(); exit(0 if success else 1)"
	$(call log_success,Documentation validation complete)

docs-serve: ## Serve documentation locally (if supported)
	$(call log_info,🌐 Starting documentation server...)
	@command -v mkdocs > /dev/null && mkdocs serve || \
		(command -v python3 > /dev/null && cd docs && python3 -m http.server 8888) || \
		$(call log_error,No documentation server available)

docs-watch: ## Watch for changes and auto-update documentation
	$(call log_info,🔍 Starting documentation watcher...)
	@python3 scripts/docs/watch-and-update.py watch

docs-ci-setup: ## Set up CI/CD integration for documentation
	$(call log_info,🔧 Setting up CI integration...)
	@python3 scripts/docs/watch-and-update.py ci-setup
	$(call log_success,CI integration setup complete)

docs-comments: ## Extract and generate documentation from LLM comments
	$(call log_info,🤖 Extracting LLM comments from codebase...)
	@python3 scripts/docs/extract-llm-comments.py
	$(call log_success,LLM comment documentation generated)

docs-validate-comments: ## Validate LLM comment consistency and quality
	$(call log_info,🔍 Validating LLM comments...)
	@python3 scripts/docs/validate-llm-comments.py
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
	@python3 scripts/docs/llm-context-warmer.py overview --format yaml
	$(call log_success,LLM context overview generated)

docs-context-paginate: ## Paginate through all comments (usage: make docs-context-paginate PAGE=1)
	$(call log_info,📄 Showing comments page $(or $(PAGE),1)...)
	@python3 scripts/docs/llm-context-warmer.py paginate --page $(or $(PAGE),1) --format yaml

docs-context-json: ## Generate project overview in JSON format
	$(call log_info,🤖 Generating LLM context overview (JSON)...)
	@python3 scripts/docs/llm-context-warmer.py overview --format json

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
	@tools/dependency-tracker/build/deptrack analyze --root=. --output=docs/architecture/dependencies.json --verbose
	$(call log_success,Dependency analysis complete)

deps-graph: ## Generate dependency visualization
	$(call log_info,📊 Generating dependency graph...)
	@tools/dependency-tracker/build/deptrack graph --format=mermaid --output=docs/architecture/dependency-graph.md
	$(call log_success,Dependency graph generated)

deps-validate: ## Validate dependency consistency
	$(call log_info,🔍 Validating dependencies...)
	@tools/dependency-tracker/build/deptrack validate --strict
	$(call log_success,Dependency validation complete)

deps-feature-dag: ## Generate feature dependency DAG
	$(call log_info,🗺️ Generating feature DAG...)
	@tools/dependency-tracker/build/deptrack feature-dag --output=docs/architecture/
	$(call log_success,Feature DAG generated)

deps-clean: ## Clean dependency tracker build
	$(call log_info,🧹 Cleaning dependency tracker...)
	@rm -rf tools/dependency-tracker/build
	$(call log_success,Dependency tracker cleaned)

clean-deps: ## Alias for deps-clean (disk space management)
	$(MAKE) deps-clean

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

html-test: ## Launch HTML testing interface hub
	$(call log_info,🧪 Opening HTML testing interfaces...)
	@./static_html/html-links/open.sh index || (echo "$(RED)❌ Run 'make html-setup' first$(RESET)" && exit 1)
	$(call log_success,HTML testing hub opened)

html-dashboard: ## Open health monitoring dashboard
	$(call log_info,📊 Opening health dashboard...)
	@./static_html/html-links/open.sh dashboard || (echo "$(RED)❌ Run 'make html-setup' first$(RESET)" && exit 1)

html-vision: ## Open Vision AI testing interface
	$(call log_info,👁️ Opening Vision AI testing...)
	@./static_html/html-links/open.sh vision || (echo "$(RED)❌ Run 'make html-setup' first$(RESET)" && exit 1)

html-audio: ## Open Whisper TTS testing interface
	$(call log_info,🎤 Opening Audio processing testing...)
	@./static_html/html-links/open.sh audio || (echo "$(RED)❌ Run 'make html-setup' first$(RESET)" && exit 1)

html-context: ## Open Context LLM testing interface
	$(call log_info,🧠 Opening Context LLM testing...)
	@./static_html/html-links/open.sh context || (echo "$(RED)❌ Run 'make html-setup' first$(RESET)" && exit 1)

html-list: ## List all available HTML interfaces
	$(call log_info,📋 Available HTML interfaces:)
	@./static_html/html-links/open.sh || (echo "$(RED)❌ Run 'make html-setup' first$(RESET)" && exit 1)

html-server: ## Start local HTTP server for HTML interfaces
	$(call log_info,🌐 Starting HTTP server for HTML interfaces...)
	@echo "$(YELLOW)📍 Server URLs:$(RESET)"
	@echo "  Main Hub: http://localhost:8080/static_html/"
	@echo "  Dashboard: http://localhost:8080/unhinged-health-dashboard.html"
	@echo "  Vision: http://localhost:8080/static_html/image-test.html"
	@echo "  Audio: http://localhost:8080/static_html/voice-test.html"
	@echo "  Context: http://localhost:8080/static_html/text-test.html"
	@echo ""
	@echo "$(BLUE)💡 Press Ctrl+C to stop server$(RESET)"
	@python3 -m http.server 8080

html-sanity: ## Run complete HTML interface sanity check
	$(call log_info,🔍 Running HTML interface sanity check...)
	@echo "$(YELLOW)📋 Checking HTML interface files...$(RESET)"
	@test -f static_html/index.html && echo "$(GREEN)✅ Main hub found$(RESET)" || echo "$(RED)❌ Main hub missing$(RESET)"
	@test -f static_html/image-test.html && echo "$(GREEN)✅ Vision AI interface found$(RESET)" || echo "$(RED)❌ Vision AI interface missing$(RESET)"
	@test -f static_html/voice-test.html && echo "$(GREEN)✅ Audio interface found$(RESET)" || echo "$(RED)❌ Audio interface missing$(RESET)"
	@test -f static_html/text-test.html && echo "$(GREEN)✅ Context LLM interface found$(RESET)" || echo "$(RED)❌ Context LLM interface missing$(RESET)"
	@test -f unhinged-health-dashboard.html && echo "$(GREEN)✅ Health dashboard found$(RESET)" || echo "$(RED)❌ Health dashboard missing$(RESET)"
	@echo "$(YELLOW)📋 Checking symlink system...$(RESET)"
	@test -d static_html/html-links && echo "$(GREEN)✅ Symlink directory exists$(RESET)" || echo "$(YELLOW)⚠️ Run 'make html-setup' to create symlinks$(RESET)"
	@test -x static_html/html-links/open.sh && echo "$(GREEN)✅ Launcher script ready$(RESET)" || echo "$(YELLOW)⚠️ Run 'make html-setup' to create launcher$(RESET)"
	$(call log_success,HTML interface sanity check complete)

html-clean: ## Clean HTML interface symlinks and generated files
	$(call log_warning,🧹 Cleaning HTML interface symlinks...)
	@rm -rf static_html/html-links/
	@rm -f ~/Desktop/Unhinged-HTML.desktop
	$(call log_success,HTML interface symlinks cleaned)

# Aliases for convenience
test-ui: html-test ## Alias for html-test
ui-setup: html-setup ## Alias for html-setup
ui-test: html-test ## Alias for html-test
ui-dashboard: html-dashboard ## Alias for html-dashboard
ui-vision: html-vision ## Alias for html-vision
ui-audio: html-audio ## Alias for html-audio
ui-context: html-context ## Alias for html-context
ui-sanity: html-sanity ## Alias for html-sanity

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

# ============================================================================
# Quick Commands (Aliases)
# ============================================================================

build: backend-build ## Alias for backend-build
run: backend-run ## Alias for backend-run
demo: backend-demo ## Alias for backend-demo
test: backend-test ## Alias for backend-test
