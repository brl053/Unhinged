#!/bin/bash
# ============================================================================
# Test Persistence Platform Dev Tool End-to-End
# ============================================================================

set -e

echo "🧪 Testing Persistence Platform Dev Tool End-to-End"
echo ""

# Start the mock server in background
echo "🚀 Starting mock persistence server..."
python3 static-dashboard/mock-persistence-server.py &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Function to cleanup
cleanup() {
    echo ""
    echo "🛑 Stopping mock server..."
    kill $SERVER_PID 2>/dev/null || true
    wait $SERVER_PID 2>/dev/null || true
    echo "✅ Cleanup completed"
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

echo "📡 Testing API endpoints..."

# Test health endpoint
echo "🏥 Testing health endpoint..."
health_response=$(curl -s http://localhost:8090/api/v1/health)
if echo "$health_response" | grep -q '"healthy": true'; then
    echo "✅ Health endpoint working"
else
    echo "❌ Health endpoint failed"
    echo "Response: $health_response"
    exit 1
fi

# Test platform info endpoint
echo "ℹ️  Testing platform info endpoint..."
info_response=$(curl -s http://localhost:8090/api/v1/info)
if echo "$info_response" | grep -q '"platform_name"'; then
    echo "✅ Platform info endpoint working"
else
    echo "❌ Platform info endpoint failed"
    echo "Response: $info_response"
    exit 1
fi

# Test insert record endpoint
echo "➕ Testing insert record endpoint..."
insert_response=$(curl -s -X POST http://localhost:8090/api/v1/tables/users \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "name": "Test User"}')
if echo "$insert_response" | grep -q '"success": true'; then
    echo "✅ Insert record endpoint working"
else
    echo "❌ Insert record endpoint failed"
    echo "Response: $insert_response"
    exit 1
fi

# Test query endpoint
echo "🔍 Testing query endpoint..."
query_response=$(curl -s -X POST http://localhost:8090/api/v1/query/get_user_by_id \
    -H "Content-Type: application/json" \
    -d '{"parameters": {"user_id": "123"}}')
if echo "$query_response" | grep -q '"success": true'; then
    echo "✅ Query endpoint working"
else
    echo "❌ Query endpoint failed"
    echo "Response: $query_response"
    exit 1
fi

# Test vector search endpoint
echo "🎯 Testing vector search endpoint..."
vector_response=$(curl -s -X POST http://localhost:8090/api/v1/vector/search/documents \
    -H "Content-Type: application/json" \
    -d '{"queryVector": [0.1, 0.2, 0.3], "limit": 5}')
if echo "$vector_response" | grep -q '"success": true'; then
    echo "✅ Vector search endpoint working"
else
    echo "❌ Vector search endpoint failed"
    echo "Response: $vector_response"
    exit 1
fi

# Test operation endpoint
echo "⚙️ Testing operation endpoint..."
operation_response=$(curl -s -X POST http://localhost:8090/api/v1/operations/create_user_complete \
    -H "Content-Type: application/json" \
    -d '{"parameters": {"userId": "123", "name": "Test User"}}')
if echo "$operation_response" | grep -q '"success": true'; then
    echo "✅ Operation endpoint working"
else
    echo "❌ Operation endpoint failed"
    echo "Response: $operation_response"
    exit 1
fi

# Test CORS headers
echo "🌐 Testing CORS headers..."
cors_response=$(curl -s -I -X OPTIONS http://localhost:8090/api/v1/health)
if echo "$cors_response" | grep -q "Access-Control-Allow-Origin"; then
    echo "✅ CORS headers present"
else
    echo "❌ CORS headers missing"
    echo "Response: $cors_response"
    exit 1
fi

echo ""
echo "🎉 All API endpoints are working correctly!"
echo ""
echo "🔧 Dev Tool Information:"
echo "📍 Mock Server: http://localhost:8090"
echo "🌐 Dev Tool: file://$(pwd)/static-dashboard/persistence-dev-tool.html"
echo ""
echo "📋 Test Summary:"
echo "✅ Health endpoint"
echo "✅ Platform info endpoint" 
echo "✅ Insert record endpoint"
echo "✅ Query endpoint"
echo "✅ Vector search endpoint"
echo "✅ Operation endpoint"
echo "✅ CORS headers"
echo ""
echo "🚀 Ready for manual testing!"
echo "   1. Open persistence-dev-tool.html in your browser"
echo "   2. The mock server will respond to all API calls"
echo "   3. Test all operations through the UI"
echo ""
echo "Press Ctrl+C to stop the mock server"

# Keep the server running for manual testing
wait $SERVER_PID
