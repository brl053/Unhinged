#!/bin/bash
# Development Environment Startup Script
# Provides hot reloading and development tools

set -e

echo "🚀 Starting Unhinged Development Environment..."
echo "This will provide:"
echo "  ✅ Hot reloading for frontend changes"
echo "  ✅ Real-time error feedback"
echo "  ✅ Development tools and debugging"
echo ""

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker compose -f docker-compose.dev.yml down 2>/dev/null || true
docker compose down 2>/dev/null || true

# Build and start development environment
echo "🔨 Building development containers..."
docker compose -f docker-compose.dev.yml build

echo "🎯 Starting development services..."
docker compose -f docker-compose.dev.yml up -d

echo ""
echo "🎉 Development environment is starting up!"
echo ""
echo "📍 Services will be available at:"
echo "  🌐 Frontend (Hot Reload): http://localhost:3000"
echo "  🔧 Backend API:           http://localhost:8080"
echo "  🤖 LLM Service:           http://localhost:11434"
echo "  🎤 Whisper TTS:           http://localhost:8000"
echo "  🗄️  Database:              localhost:5432"
echo ""
echo "📊 To view logs:"
echo "  docker compose -f docker-compose.dev.yml logs -f"
echo ""
echo "🛑 To stop:"
echo "  docker compose -f docker-compose.dev.yml down"
echo ""
echo "⚡ Frontend changes will auto-reload!"
echo "   Edit files in frontend/src/ and see changes instantly"
