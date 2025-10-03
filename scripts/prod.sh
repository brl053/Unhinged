#!/bin/bash
# Production Environment Startup Script
# Full production deployment

set -e

echo "🚀 Starting Unhinged Production Environment..."
echo "This provides:"
echo "  ✅ Optimized production builds"
echo "  ✅ Production security settings"
echo "  ✅ Performance optimizations"
echo "  ✅ Production monitoring"
echo ""

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker compose -f docker-compose.prod.yml down 2>/dev/null || true
docker compose -f docker-compose.staging.yml down 2>/dev/null || true
docker compose -f docker-compose.dev.yml down 2>/dev/null || true
docker compose down 2>/dev/null || true

# Build and start production environment
echo "🔨 Building production containers..."
docker compose -f docker-compose.prod.yml build

echo "🎯 Starting production services..."
docker compose -f docker-compose.prod.yml up -d

echo ""
echo "🎉 Production environment is running!"
echo ""
echo "📍 Services available at:"
echo "  🌐 Frontend:     http://localhost:3000"
echo "  🔧 Backend API:  http://localhost:8080"
echo "  🤖 LLM Service:  http://localhost:11434"
echo "  🎤 Whisper TTS:  http://localhost:8000"
echo "  🗄️  Database:     localhost:5432"
echo ""
echo "📊 To view logs:"
echo "  docker compose -f docker-compose.prod.yml logs -f"
echo ""
echo "🛑 To stop:"
echo "  docker compose -f docker-compose.prod.yml down"
echo ""
echo "⚠️  This is the production environment!"
echo "   Use staging for testing changes first"
