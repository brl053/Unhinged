#!/usr/bin/env python3
"""
Mock Persistence Platform Server for Dev Tool Testing
Provides basic endpoints to test the persistence dev tool interface
"""

import json
import time
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

class MockPersistenceHandler(BaseHTTPRequestHandler):
    
    # In-memory storage for demo
    storage = {
        'users': [],
        'documents': [],
        'document_embeddings': []
    }
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/v1/health':
            self.handle_health_check()
        elif path == '/api/v1/info':
            self.handle_platform_info()
        elif path == '/api/v1/metrics':
            self.handle_metrics()
        else:
            self.send_error(404, 'Endpoint not found')
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            data = json.loads(body) if body.strip() else {}
        except json.JSONDecodeError:
            self.send_error(400, 'Invalid JSON')
            return
        
        if path.startswith('/api/v1/tables/'):
            table_name = path.split('/')[-1]
            self.handle_insert_record(table_name, data)
        elif path.startswith('/api/v1/query/'):
            query_name = path.split('/')[-1]
            self.handle_execute_query(query_name, data)
        elif path.startswith('/api/v1/vector/search/'):
            table_name = path.split('/')[-1]
            self.handle_vector_search(table_name, data)
        elif path.startswith('/api/v1/operations/'):
            operation_name = path.split('/')[-1]
            self.handle_execute_operation(operation_name, data)
        else:
            self.send_error(404, 'Endpoint not found')
    
    def handle_health_check(self):
        """Mock health check endpoint"""
        health_data = {
            "healthy": True,
            "version": "1.0.0",
            "uptime_seconds": int(time.time() % 3600),  # Mock uptime
            "technology_health": [
                {"technology": "redis", "healthy": True, "status": "connected", "response_time_ms": 5},
                {"technology": "cockroachdb", "healthy": True, "status": "connected", "response_time_ms": 15},
                {"technology": "mongodb", "healthy": True, "status": "connected", "response_time_ms": 12},
                {"technology": "weaviate", "healthy": True, "status": "connected", "response_time_ms": 8}
            ]
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        self.wfile.write(json.dumps(health_data, indent=2).encode())
    
    def handle_platform_info(self):
        """Mock platform info endpoint"""
        info_data = {
            "platform_name": "Unhinged Persistence Platform",
            "version": "1.0.0",
            "supported_technologies": [
                "redis", "cockroachdb", "mongodb", "weaviate",
                "elasticsearch", "cassandra", "neo4j", "data_lake"
            ],
            "supported_features": [
                "CRUD", "VECTOR_SEARCH", "GRAPH_TRAVERSAL", 
                "FULL_TEXT_SEARCH", "TRANSACTIONS", "CACHING"
            ],
            "configuration": {
                "api_version": "v1",
                "max_query_limit": 1000,
                "default_timeout": 30
            }
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(info_data, indent=2).encode())
    
    def handle_metrics(self):
        """Mock metrics endpoint"""
        metrics_data = """# HELP persistence_query_duration_seconds Query execution duration
# TYPE persistence_query_duration_seconds histogram
persistence_query_duration_seconds_bucket{query="get_user_by_id",technology="redis",le="0.005"} 100
persistence_query_duration_seconds_bucket{query="get_user_by_id",technology="redis",le="0.01"} 150
persistence_query_duration_seconds_count{query="get_user_by_id",technology="redis"} 200
persistence_query_duration_seconds_sum{query="get_user_by_id",technology="redis"} 1.5

# HELP persistence_query_count_total Total number of queries executed
# TYPE persistence_query_count_total counter
persistence_query_count_total{query="get_user_by_id",technology="redis",success="true"} 195
persistence_query_count_total{query="get_user_by_id",technology="redis",success="false"} 5
"""
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(metrics_data.encode())
    
    def handle_insert_record(self, table_name, data):
        """Mock insert record endpoint"""
        # Generate a mock record
        record_id = str(uuid.uuid4())
        record = {
            "id": record_id,
            "data": data,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "version": "1"
        }
        
        # Store in mock storage
        if table_name not in self.storage:
            self.storage[table_name] = []
        self.storage[table_name].append(record)
        
        response_data = {
            "success": True,
            "record": record,
            "execution_time_ms": 45
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data, indent=2).encode())
    
    def handle_execute_query(self, query_name, data):
        """Mock execute query endpoint"""
        parameters = data.get('parameters', {})
        
        # Mock query results based on query name
        if query_name == 'get_user_by_id':
            results = [
                {
                    "id": parameters.get('user_id', '123e4567-e89b-12d3-a456-426614174000'),
                    "data": {
                        "email": "user@example.com",
                        "profile": {"name": "John Doe", "age": 30}
                    },
                    "created_at": "2025-10-19T10:00:00Z"
                }
            ]
        elif query_name == 'get_active_users':
            results = [
                {
                    "id": "user-1",
                    "data": {"email": "user1@example.com", "status": "active"},
                    "created_at": "2025-10-19T09:00:00Z"
                },
                {
                    "id": "user-2", 
                    "data": {"email": "user2@example.com", "status": "active"},
                    "created_at": "2025-10-19T09:30:00Z"
                }
            ]
        else:
            results = []
        
        response_data = {
            "success": True,
            "results": results,
            "count": len(results),
            "execution_time_ms": 120,
            "from_cache": False
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data, indent=2).encode())
    
    def handle_vector_search(self, table_name, data):
        """Mock vector search endpoint"""
        query_vector = data.get('queryVector', [])
        limit = data.get('limit', 10)
        
        # Mock vector search results
        results = [
            {
                "record": {
                    "id": "doc-1",
                    "data": {"title": "Similar Document 1", "content": "This is a similar document"}
                },
                "similarity_score": 0.95,
                "distance": 0.05
            },
            {
                "record": {
                    "id": "doc-2",
                    "data": {"title": "Similar Document 2", "content": "Another similar document"}
                },
                "similarity_score": 0.87,
                "distance": 0.13
            }
        ]
        
        response_data = {
            "success": True,
            "results": results[:limit],
            "execution_time_ms": 200
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data, indent=2).encode())
    
    def handle_execute_operation(self, operation_name, data):
        """Mock execute operation endpoint"""
        parameters = data.get('parameters', {})
        
        # Mock operation results
        if operation_name == 'create_user_complete':
            result = {
                "userId": parameters.get('userId', str(uuid.uuid4())),
                "sessionId": f"session-{uuid.uuid4()}",
                "profileCreated": True,
                "cacheUpdated": True
            }
            affected_tables = ["users", "user_sessions", "user_profiles"]
        else:
            result = {"operation": operation_name, "status": "completed"}
            affected_tables = ["unknown"]
        
        response_data = {
            "success": True,
            "result": result,
            "execution_time_ms": 350,
            "affected_tables": affected_tables
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data, indent=2).encode())
    
    def log_message(self, format, *args):
        """Override to provide cleaner logging"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

def run_mock_server(port=8090):
    """Run the mock persistence server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, MockPersistenceHandler)
    
    print(f"🏗️ Mock Persistence Platform Server")
    print(f"🌐 Running on http://localhost:{port}")
    print(f"🔧 Dev tool: file://{__file__.replace('mock-persistence-server.py', 'persistence-dev-tool.html')}")
    print(f"📊 Health: http://localhost:{port}/api/v1/health")
    print(f"ℹ️  Info: http://localhost:{port}/api/v1/info")
    print(f"📈 Metrics: http://localhost:{port}/api/v1/metrics")
    print("")
    print("Press Ctrl+C to stop the server")
    print("")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down mock server...")
        httpd.shutdown()

if __name__ == '__main__':
    run_mock_server()
