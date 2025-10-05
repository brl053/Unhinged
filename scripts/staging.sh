#!/bin/bash
# Staging Environment Startup Script
# Production-like environment for testing

set -e

echo "🎭 Starting Unhinged Staging Environment..."
echo "This provides:"
echo "  ✅ Production-like build process"
echo "  ✅ Optimized bundles"
echo "  ✅ Performance testing"
echo "  ✅ Pre-production validation"
echo ""

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker compose -f docker-compose.staging.yml down 2>/dev/null || true
docker compose -f docker-compose.dev.yml down 2>/dev/null || true
docker compose down 2>/dev/null || true

# Build and start staging environment
echo "🔨 Building staging containers..."
docker compose -f docker-compose.staging.yml build

echo "🎯 Starting staging services..."
docker compose -f docker-compose.staging.yml up -d

echo ""
echo "🎉 Staging environment is starting up!"
echo ""
echo "📍 Services available at:"
echo "  🌐 Frontend:     http://localhost:3000"
echo "  🔧 Backend API:  http://localhost:8080"
echo "  🤖 LLM Service:  http://localhost:11434"
echo "  🎤 Whisper TTS:  http://localhost:8000"
echo "  🗄️  Database:     localhost:5432"
echo ""
echo "📊 To view logs:"
echo "  docker compose -f docker-compose.staging.yml logs -f"
echo ""
echo "🛑 To stop:"
echo "  docker compose -f docker-compose.staging.yml down"
echo ""
echo "🧪 This environment mimics production for testing"
