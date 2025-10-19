#!/usr/bin/env python3
"""
Simple Mock Persistence Platform Server for Dev Tool Testing
"""

import json
import time
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

class MockHandler(BaseHTTPRequestHandler):
    
    def _send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    
    def _send_json_response(self, data, status=200):
        """Send JSON response with CORS headers"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        
        if path == '/api/v1/health':
            data = {
                "healthy": True,
                "version": "1.0.0",
                "uptime_seconds": int(time.time() % 3600),
                "technology_health": [
                    {"technology": "redis", "healthy": True, "status": "connected", "response_time_ms": 5},
                    {"technology": "cockroachdb", "healthy": True, "status": "connected", "response_time_ms": 15}
                ]
            }
            self._send_json_response(data)
            
        elif path == '/api/v1/info':
            data = {
                "platform_name": "Unhinged Persistence Platform",
                "version": "1.0.0",
                "supported_technologies": ["redis", "cockroachdb", "mongodb", "weaviate"],
                "supported_features": ["CRUD", "VECTOR_SEARCH", "GRAPH_TRAVERSAL"]
            }
            self._send_json_response(data)
            
        elif path == '/api/v1/metrics':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self._send_cors_headers()
            self.end_headers()
            metrics = """# HELP persistence_query_count_total Total queries
persistence_query_count_total{success="true"} 100
persistence_query_count_total{success="false"} 5
"""
            self.wfile.write(metrics.encode())
        else:
            self._send_json_response({"error": "Not found"}, 404)
    
    def do_POST(self):
        """Handle POST requests"""
        path = urlparse(self.path).path
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            data = json.loads(body) if body.strip() else {}
        except json.JSONDecodeError:
            self._send_json_response({"error": "Invalid JSON"}, 400)
            return
        
        if path.startswith('/api/v1/tables/'):
            # Insert record
            table_name = path.split('/')[-1]
            record = {
                "id": str(uuid.uuid4()),
                "data": data,
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
            response = {
                "success": True,
                "record": record,
                "execution_time_ms": 45
            }
            self._send_json_response(response)
            
        elif path.startswith('/api/v1/query/'):
            # Execute query
            query_name = path.split('/')[-1]
            results = [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "data": {"email": "user@example.com", "profile": {"name": "John Doe"}},
                    "created_at": "2025-10-19T10:00:00Z"
                }
            ]
            response = {
                "success": True,
                "results": results,
                "count": len(results),
                "execution_time_ms": 120,
                "from_cache": False
            }
            self._send_json_response(response)
            
        elif path.startswith('/api/v1/vector/search/'):
            # Vector search
            results = [
                {
                    "record": {
                        "id": "doc-1",
                        "data": {"title": "Similar Document", "content": "This is similar"}
                    },
                    "similarity_score": 0.95,
                    "distance": 0.05
                }
            ]
            response = {
                "success": True,
                "results": results,
                "execution_time_ms": 200
            }
            self._send_json_response(response)
            
        elif path.startswith('/api/v1/operations/'):
            # Execute operation
            operation_name = path.split('/')[-1]
            result = {
                "userId": str(uuid.uuid4()),
                "sessionId": f"session-{uuid.uuid4()}",
                "profileCreated": True
            }
            response = {
                "success": True,
                "result": result,
                "execution_time_ms": 350,
                "affected_tables": ["users", "user_sessions"]
            }
            self._send_json_response(response)
            
        else:
            self._send_json_response({"error": "Endpoint not found"}, 404)
    
    def log_message(self, format, *args):
        """Override to provide cleaner logging"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

def run_server(port=8090):
    """Run the mock server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, MockHandler)
    
    print(f"🏗️ Mock Persistence Platform Server")
    print(f"🌐 Running on http://localhost:{port}")
    print(f"📊 Health: http://localhost:{port}/api/v1/health")
    print(f"ℹ️  Info: http://localhost:{port}/api/v1/info")
    print("")
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down mock server...")
        httpd.shutdown()

if __name__ == '__main__':
    run_server()
