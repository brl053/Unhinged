# ============================================================================
# Unhinged Platforms - Makefile
# ============================================================================
#
# @file Makefile
# @version 1.0.0
# @author Unhinged Team
# @date 2025-10-19
# @description Build and deployment automation for all Unhinged platforms
#
# This Makefile provides convenient commands for building, testing, and
# deploying all platform-level services including persistence, agent,
# and workflow platforms.
#
# ============================================================================

.PHONY: help build test deploy clean start stop logs health

# Default target
help: ## Show this help message
	@echo "🏗️  Unhinged Platforms - Build & Deployment"
	@echo ""
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Platform-specific commands:"
	@echo "  make persistence-*     - Commands for persistence platform"
	@echo "  make agent-*           - Commands for agent platform (future)"
	@echo "  make workflow-*        - Commands for workflow platform (future)"

# ==========================================================================
# All Platforms Commands
# ==========================================================================

build: ## Build all platforms
	@echo "🔨 Building all platforms..."
	@$(MAKE) persistence-build
	@echo "✅ All platforms built successfully"

test: ## Test all platforms
	@echo "🧪 Testing all platforms..."
	@$(MAKE) persistence-test
	@echo "✅ All platform tests completed"

start: ## Start all platforms with dependencies
	@echo "🚀 Starting all platforms..."
	@docker-compose -f docker-compose.all.yml up -d
	@echo "✅ All platforms started"
	@echo "🌐 Persistence Platform: http://localhost:8090/api/v1"
	@echo "📊 Grafana Dashboard: http://localhost:3000 (admin/admin)"
	@echo "🔍 Prometheus: http://localhost:9090"

stop: ## Stop all platforms
	@echo "🛑 Stopping all platforms..."
	@docker-compose -f docker-compose.all.yml down
	@echo "✅ All platforms stopped"

restart: stop start ## Restart all platforms

logs: ## Show logs for all platforms
	@docker-compose -f docker-compose.all.yml logs -f

health: ## Check health of all platforms
	@echo "🏥 Checking platform health..."
	@echo "Persistence Platform:"
	@curl -s http://localhost:8090/api/v1/health | jq '.' || echo "❌ Persistence platform not responding"
	@echo ""

clean: ## Clean all platform resources
	@echo "🧹 Cleaning all platform resources..."
	@docker-compose -f docker-compose.all.yml down -v --remove-orphans
	@docker system prune -f
	@echo "✅ Cleanup completed"

# ==========================================================================
# Persistence Platform Commands
# ==========================================================================

persistence-build: ## Build persistence platform
	@echo "🔨 Building persistence platform..."
	@cd persistence && ./gradlew clean build
	@cd persistence && docker build -t unhinged/persistence-platform:latest .
	@echo "✅ Persistence platform built"

persistence-test: ## Test persistence platform
	@echo "🧪 Testing persistence platform..."
	@cd persistence && ./gradlew test integrationTest
	@echo "✅ Persistence platform tests completed"

persistence-start: ## Start persistence platform only
	@echo "🚀 Starting persistence platform..."
	@cd persistence && docker-compose up -d
	@echo "✅ Persistence platform started"
	@echo "🌐 API: http://localhost:8090/api/v1"

persistence-stop: ## Stop persistence platform
	@echo "🛑 Stopping persistence platform..."
	@cd persistence && docker-compose down
	@echo "✅ Persistence platform stopped"

persistence-logs: ## Show persistence platform logs
	@cd persistence && docker-compose logs -f

persistence-health: ## Check persistence platform health
	@echo "🏥 Checking persistence platform health..."
	@curl -s http://localhost:8090/api/v1/health | jq '.' || echo "❌ Not responding"

persistence-metrics: ## Show persistence platform metrics
	@echo "📊 Persistence platform metrics:"
	@curl -s http://localhost:8090/api/v1/metrics | head -20

persistence-shell: ## Open shell in persistence platform container
	@docker exec -it unhinged-persistence-platform /bin/bash

persistence-dev: ## Run persistence platform in development mode
	@echo "🔧 Starting persistence platform in development mode..."
	@cd persistence && ./gradlew dev

# ==========================================================================
# Future Platform Commands (Placeholders)
# ==========================================================================

agent-build: ## Build agent platform (future)
	@echo "⚠️  Agent platform not implemented yet"

agent-test: ## Test agent platform (future)
	@echo "⚠️  Agent platform not implemented yet"

agent-start: ## Start agent platform (future)
	@echo "⚠️  Agent platform not implemented yet"

workflow-build: ## Build workflow platform (future)
	@echo "⚠️  Workflow platform not implemented yet"

workflow-test: ## Test workflow platform (future)
	@echo "⚠️  Workflow platform not implemented yet"

workflow-start: ## Start workflow platform (future)
	@echo "⚠️  Workflow platform not implemented yet"

# ==========================================================================
# Development Commands
# ==========================================================================

dev-setup: ## Set up development environment
	@echo "🔧 Setting up development environment..."
	@echo "Installing development dependencies..."
	@cd persistence && ./gradlew build
	@echo "✅ Development environment ready"

dev-start: ## Start all platforms in development mode
	@echo "🔧 Starting platforms in development mode..."
	@$(MAKE) persistence-dev &
	@echo "✅ Development mode started"

format: ## Format all code
	@echo "🎨 Formatting code..."
	@cd persistence && ./gradlew ktlintFormat
	@echo "✅ Code formatted"

lint: ## Lint all code
	@echo "🔍 Linting code..."
	@cd persistence && ./gradlew ktlintCheck
	@echo "✅ Linting completed"

# ==========================================================================
# Monitoring Commands
# ==========================================================================

monitoring-start: ## Start monitoring stack only
	@echo "📊 Starting monitoring stack..."
	@docker-compose -f docker-compose.all.yml up -d prometheus grafana jaeger
	@echo "✅ Monitoring stack started"
	@echo "📊 Grafana: http://localhost:3000 (admin/admin)"
	@echo "🔍 Prometheus: http://localhost:9090"
	@echo "🔗 Jaeger: http://localhost:16686"

monitoring-stop: ## Stop monitoring stack
	@echo "🛑 Stopping monitoring stack..."
	@docker-compose -f docker-compose.all.yml stop prometheus grafana jaeger
	@echo "✅ Monitoring stack stopped"

# ==========================================================================
# Database Commands
# ==========================================================================

db-start: ## Start all databases
	@echo "🗄️ Starting all databases..."
	@docker-compose -f docker-compose.all.yml up -d redis cockroachdb mongodb weaviate elasticsearch cassandra neo4j minio
	@echo "✅ All databases started"

db-stop: ## Stop all databases
	@echo "🛑 Stopping all databases..."
	@docker-compose -f docker-compose.all.yml stop redis cockroachdb mongodb weaviate elasticsearch cassandra neo4j minio
	@echo "✅ All databases stopped"

db-reset: ## Reset all database data
	@echo "⚠️  This will delete all database data!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@$(MAKE) stop
	@docker-compose -f docker-compose.all.yml down -v
	@echo "✅ All database data reset"

# ==========================================================================
# Utility Commands
# ==========================================================================

status: ## Show status of all services
	@echo "📊 Platform Status:"
	@docker-compose -f docker-compose.all.yml ps

ps: status ## Alias for status

top: ## Show resource usage
	@docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

images: ## Show platform images
	@echo "🐳 Platform Images:"
	@docker images | grep -E "(unhinged|redis|cockroach|mongo|weaviate|elastic|cassandra|neo4j|minio|prometheus|grafana|jaeger)"

volumes: ## Show platform volumes
	@echo "💾 Platform Volumes:"
	@docker volume ls | grep -E "(redis|cockroach|mongo|weaviate|elastic|cassandra|neo4j|minio|prometheus|grafana)"

networks: ## Show platform networks
	@echo "🌐 Platform Networks:"
	@docker network ls | grep unhinged

# ==========================================================================
# Documentation Commands
# ==========================================================================

docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	@cd persistence && ./gradlew generateApiDocs
	@echo "✅ Documentation generated"

docs-serve: ## Serve documentation locally
	@echo "📚 Serving documentation..."
	@echo "⚠️  Documentation server not implemented yet"

# ==========================================================================
# Release Commands
# ==========================================================================

release-prepare: ## Prepare release
	@echo "📦 Preparing release..."
	@$(MAKE) clean
	@$(MAKE) build
	@$(MAKE) test
	@echo "✅ Release preparation completed"

release-build: ## Build release artifacts
	@echo "📦 Building release artifacts..."
	@$(MAKE) persistence-build
	@echo "✅ Release artifacts built"

# ==========================================================================
# CI/CD Commands
# ==========================================================================

ci-test: ## Run CI tests
	@echo "🤖 Running CI tests..."
	@$(MAKE) build
	@$(MAKE) test
	@$(MAKE) lint
	@echo "✅ CI tests completed"

ci-deploy: ## Deploy for CI/CD
	@echo "🚀 Deploying for CI/CD..."
	@$(MAKE) release-build
	@echo "✅ CI/CD deployment completed"
