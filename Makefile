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
	@echo "$(CYAN)📊 Service Status$(RESET)"
	@echo "$(YELLOW)Docker Services:$(RESET)"
	@docker compose ps || echo "$(RED)❌ Docker Compose not running$(RESET)"
	@echo ""
	@echo "$(YELLOW)Backend Health:$(RESET)"
	@curl -s http://localhost:8080/health > /dev/null && echo "$(GREEN)✅ Backend healthy$(RESET)" || echo "$(RED)❌ Backend not responding$(RESET)"
	@echo "$(YELLOW)Database:$(RESET)"
	@docker exec postgres-db pg_isready -U postgres > /dev/null 2>&1 && echo "$(GREEN)✅ Database ready$(RESET)" || echo "$(RED)❌ Database not ready$(RESET)"
	@echo "$(YELLOW)Whisper TTS:$(RESET)"
	@curl -s http://localhost:8000/health > /dev/null && echo "$(GREEN)✅ TTS service healthy$(RESET)" || echo "$(RED)❌ TTS service not responding$(RESET)"

# ============================================================================
# Setup and Installation
# ============================================================================

setup: ## Initial project setup
	@echo "$(CYAN)🔧 Setting up Unhinged platform...$(RESET)"
	@echo "$(YELLOW)Installing dependencies...$(RESET)"
	@cd $(BACKEND_DIR) && ./gradlew build --no-daemon
	@echo "$(YELLOW)Generating protobuf code...$(RESET)"
	@$(MAKE) proto-gen
	@echo "$(GREEN)✅ Setup complete!$(RESET)"

install: setup ## Alias for setup

# ============================================================================
# Docker Services Management
# ============================================================================

up: ## Start all services
	@echo "$(CYAN)🚀 Starting all services...$(RESET)"
	@docker compose up -d
	@echo "$(GREEN)✅ Services started$(RESET)"
	@$(MAKE) status

down: ## Stop all services
	@echo "$(YELLOW)🛑 Stopping all services...$(RESET)"
	@docker compose down
	@echo "$(GREEN)✅ Services stopped$(RESET)"

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
	@echo "$(CYAN)🗄️ Starting database...$(RESET)"
	@docker compose up -d database
	@echo "$(GREEN)✅ Database started$(RESET)"

db-shell: ## Connect to database shell
	@echo "$(CYAN)🗄️ Connecting to database...$(RESET)"
	@docker exec -it postgres-db psql -U postgres -d unhinged_db

db-migrate: ## Run database migrations
	@echo "$(CYAN)🗄️ Running database migrations...$(RESET)"
	@cd $(BACKEND_DIR) && ./gradlew flywayMigrate

db-reset: ## Reset database (WARNING: destroys all data)
	@echo "$(RED)⚠️  WARNING: This will destroy all database data!$(RESET)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@docker compose down database
	@docker volume rm unhinged_postgres_data || true
	@docker compose up -d database
	@sleep 5
	@$(MAKE) db-migrate
	@echo "$(GREEN)✅ Database reset complete$(RESET)"

db-backup: ## Backup database
	@echo "$(CYAN)💾 Backing up database...$(RESET)"
	@mkdir -p backups
	@docker exec postgres-db pg_dump -U postgres unhinged_db > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Database backed up$(RESET)"

# ============================================================================
# Protobuf Operations
# ============================================================================

proto-gen: ## Generate protobuf code
	@echo "$(CYAN)🔧 Generating protobuf code...$(RESET)"
	@cd $(BACKEND_DIR) && ./gradlew generateProto
	@echo "$(GREEN)✅ Protobuf code generated$(RESET)"

proto-clean: ## Clean generated protobuf code
	@echo "$(YELLOW)🧹 Cleaning protobuf generated code...$(RESET)"
	@cd $(BACKEND_DIR) && ./gradlew clean
	@echo "$(GREEN)✅ Protobuf code cleaned$(RESET)"

proto-count: ## Count generated protobuf files
	@echo "$(CYAN)📊 Protobuf Statistics$(RESET)"
	@echo "Generated Kotlin files: $(shell find $(BACKEND_DIR)/build/generated -name "*.kt" 2>/dev/null | wc -l)"
	@echo "Generated Java files: $(shell find $(BACKEND_DIR)/build/generated -name "*.java" 2>/dev/null | wc -l)"
	@echo "Proto source files: $(shell find $(PROTO_DIR) -name "*.proto" | wc -l)"

# ============================================================================
# Backend Development
# ============================================================================

backend-build: ## Build backend
	@echo "$(CYAN)🔨 Building backend...$(RESET)"
	@cd $(BACKEND_DIR) && ./gradlew build --no-daemon
	@echo "$(GREEN)✅ Backend built$(RESET)"

backend-compile: ## Compile backend (faster than full build)
	@echo "$(CYAN)⚡ Compiling backend...$(RESET)"
	@cd $(BACKEND_DIR) && ./gradlew compileKotlin --no-daemon
	@echo "$(GREEN)✅ Backend compiled$(RESET)"

backend-run: ## Run backend locally
	@echo "$(CYAN)🚀 Starting backend...$(RESET)"
	@cd $(BACKEND_DIR) && ./gradlew run --no-daemon

backend-demo: ## Run the working demo
	@echo "$(CYAN)🎯 Starting working demo...$(RESET)"
	@cd $(BACKEND_DIR) && ./gradlew run --args="com.unhinged.demo.WorkingDemoKt" --no-daemon

backend-test: ## Run backend tests
	@echo "$(CYAN)🧪 Running backend tests...$(RESET)"
	@cd $(BACKEND_DIR) && ./gradlew test
	@echo "$(GREEN)✅ Tests completed$(RESET)"

backend-clean: ## Clean backend build
	@echo "$(YELLOW)🧹 Cleaning backend...$(RESET)"
	@cd $(BACKEND_DIR) && ./gradlew clean
	@echo "$(GREEN)✅ Backend cleaned$(RESET)"

# ============================================================================
# Development Workflow
# ============================================================================

dev: ## Start development environment
	@echo "$(CYAN)🚀 Starting development environment...$(RESET)"
	@$(MAKE) db-up
	@sleep 3
	@$(MAKE) backend-run

dev-demo: ## Start development with demo
	@echo "$(CYAN)🎯 Starting development with demo...$(RESET)"
	@$(MAKE) db-up
	@sleep 3
	@$(MAKE) backend-demo

dev-full: ## Start full development environment
	@echo "$(CYAN)🚀 Starting full development environment...$(RESET)"
	@$(MAKE) up
	@sleep 5
	@$(MAKE) status

# ============================================================================
# Testing and Debugging
# ============================================================================

test-grpc: ## Test gRPC endpoints with grpcurl
	@echo "$(CYAN)🧪 Testing gRPC endpoints...$(RESET)"
	@echo "$(YELLOW)Available services:$(RESET)"
	@grpcurl -plaintext localhost:9090 list || echo "$(RED)❌ gRPC server not running$(RESET)"

test-tts: ## Test TTS service
	@echo "$(CYAN)🎵 Testing TTS service...$(RESET)"
	@curl -X POST "http://localhost:8000/tts" \
		-H "Content-Type: application/json" \
		-d '{"text": "Hello from Unhinged platform!", "voice": "default"}' \
		--output /tmp/test_tts.wav && \
		echo "$(GREEN)✅ TTS test successful - audio saved to /tmp/test_tts.wav$(RESET)" || \
		echo "$(RED)❌ TTS test failed$(RESET)"

test-db: ## Test database connection
	@echo "$(CYAN)🗄️ Testing database connection...$(RESET)"
	@docker exec postgres-db psql -U postgres -d unhinged_db -c "SELECT 'Database connection successful!' as status;" && \
		echo "$(GREEN)✅ Database test successful$(RESET)" || \
		echo "$(RED)❌ Database test failed$(RESET)"

debug-memory: ## Show memory usage for compilation
	@echo "$(CYAN)🧠 Memory Usage Information$(RESET)"
	@echo "$(YELLOW)JVM Memory Settings:$(RESET)"
	@cd $(BACKEND_DIR) && grep -E "(jvmargs|daemon)" gradle.properties || echo "No memory settings found"
	@echo "$(YELLOW)System Memory:$(RESET)"
	@free -h || echo "Memory info not available"

# ============================================================================
# Cleanup Operations
# ============================================================================

clean: ## Clean all build artifacts
	@echo "$(YELLOW)🧹 Cleaning all build artifacts...$(RESET)"
	@$(MAKE) backend-clean
	@$(MAKE) proto-clean
	@echo "$(GREEN)✅ Cleanup complete$(RESET)"

clean-docker: ## Clean Docker resources
	@echo "$(YELLOW)🧹 Cleaning Docker resources...$(RESET)"
	@docker compose down --volumes --remove-orphans
	@docker system prune -f
	@echo "$(GREEN)✅ Docker cleanup complete$(RESET)"

clean-all: clean clean-docker ## Clean everything

# ============================================================================
# Utility Commands
# ============================================================================

ports: ## Show which ports are in use
	@echo "$(CYAN)🔌 Port Usage$(RESET)"
	@echo "$(YELLOW)Expected ports:$(RESET)"
	@echo "  8080 - Backend gRPC/HTTP"
	@echo "  8000 - Whisper TTS"
	@echo "  5432 - PostgreSQL"
	@echo "  9092 - Kafka"
	@echo "  9090 - Demo gRPC server"
	@echo ""
	@echo "$(YELLOW)Currently listening:$(RESET)"
	@netstat -tlnp 2>/dev/null | grep -E ":(8080|8000|5432|9092|9090|2181)" || echo "No services detected"

health: ## Check health of all services
	@echo "$(CYAN)🏥 Health Check$(RESET)"
	@$(MAKE) status
	@$(MAKE) test-db
	@$(MAKE) test-tts

version: ## Show version information
	@echo "$(CYAN)📋 Version Information$(RESET)"
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
