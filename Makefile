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

status: ## Show status of all services
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
# Cleanup Operations
# ============================================================================

clean: ## Clean all build artifacts
	$(call log_warning,🧹 Cleaning all build artifacts...)
	@$(MAKE) backend-clean
	@$(MAKE) proto-clean
	$(call log_success,Cleanup complete)

clean-docker: ## Clean Docker resources
	$(call log_warning,🧹 Cleaning Docker resources...)
	@docker compose down --volumes --remove-orphans
	@docker system prune -f
	$(call log_success,Docker cleanup complete)

clean-all: clean clean-docker ## Clean everything

# ============================================================================
# Utility Commands
# ============================================================================

ports: ## Show which ports are in use
	$(call log_info,🔌 Port Usage)
	$(call log_warning,Expected ports:)
	@echo "  $(PORT_BACKEND) - Backend gRPC/HTTP"
	@echo "  $(PORT_TTS) - Whisper TTS"
	@echo "  $(PORT_DB) - PostgreSQL"
	@echo "  $(PORT_KAFKA) - Kafka"
	@echo "  $(PORT_GRPC_DEMO) - Demo gRPC server"
	@echo ""
	$(call log_warning,Currently listening:)
	@netstat -tlnp 2>/dev/null | grep -E ":($(PORT_BACKEND)|$(PORT_TTS)|$(PORT_DB)|$(PORT_KAFKA)|$(PORT_GRPC_DEMO)|2181)" || echo "No services detected"

health: ## Check health of all services
	$(call log_info,🏥 Health Check)
	@$(MAKE) status
	@$(MAKE) test-db
	@$(MAKE) test-tts

version: ## Show version information
	$(call log_info,📋 Version Information)
	@echo "$(YELLOW)Project:$(RESET) Unhinged Platform"
	@echo "$(YELLOW)Version:$(RESET) $(shell cat version.json 2>/dev/null | grep version | cut -d'"' -f4 || echo "unknown")"
	@echo "$(YELLOW)Kotlin:$(RESET) $(shell cd $(BACKEND_DIR) && ./gradlew --version | grep Kotlin | head -1 || echo "unknown")"
	@echo "$(YELLOW)Docker:$(RESET) $(shell docker --version 2>/dev/null || echo "not installed")"

# ============================================================================
# Quick Commands (Aliases)
# ============================================================================

build: backend-build ## Alias for backend-build
run: backend-run ## Alias for backend-run
demo: backend-demo ## Alias for backend-demo
test: backend-test ## Alias for backend-test
