#!/bin/bash
# ============================================================================
# Start Persistence Platform for Dev Tool Testing
# ============================================================================

set -e

echo "🏗️ Starting Persistence Platform for Dev Tool Testing..."

# Check if we're in the right directory
if [ ! -d "platforms/persistence" ]; then
    echo "❌ Error: Must be run from project root directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

# Start the persistence platform with minimal dependencies
echo "🚀 Starting persistence platform with dependencies..."

cd platforms/persistence

# Start only essential services for dev tool testing
echo "📦 Starting Redis (cache)..."
docker run -d --name unhinged-redis-dev \
    -p 6379:6379 \
    redis:7.2-alpine \
    redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru \
    || echo "Redis already running or failed to start"

echo "🗄️ Starting CockroachDB (SQL)..."
docker run -d --name unhinged-cockroachdb-dev \
    -p 26257:26257 \
    -p 8080:8080 \
    cockroachdb/cockroach:v23.1.11 \
    start-single-node --insecure --store=attrs=ssd,path=/cockroach/cockroach-data --listen-addr=0.0.0.0:26257 --http-addr=0.0.0.0:8080 \
    || echo "CockroachDB already running or failed to start"

# Wait for databases to be ready
echo "⏳ Waiting for databases to be ready..."
sleep 10

# Check if databases are responding
echo "🔍 Checking database connectivity..."
redis_status=$(docker exec unhinged-redis-dev redis-cli ping 2>/dev/null || echo "FAILED")
echo "Redis status: $redis_status"

cockroach_status=$(curl -s http://localhost:8080/health?ready=1 2>/dev/null | grep -o "ok" || echo "FAILED")
echo "CockroachDB status: $cockroach_status"

# Build and start the persistence platform
echo "🔨 Building persistence platform..."
./gradlew clean build -x test

echo "🚀 Starting persistence platform..."
echo "📍 Platform will be available at: http://localhost:8090"
echo "🔧 Dev tool will be available at: file://$(pwd)/../../static-dashboard/persistence-dev-tool.html"
echo ""
echo "Press Ctrl+C to stop the platform"
echo ""

# Start the platform
java -jar build/libs/persistence-platform.jar config/persistence-platform.yaml

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping persistence platform..."
    echo "🧹 Cleaning up containers..."
    docker stop unhinged-redis-dev unhinged-cockroachdb-dev 2>/dev/null || true
    docker rm unhinged-redis-dev unhinged-cockroachdb-dev 2>/dev/null || true
    echo "✅ Cleanup completed"
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM
