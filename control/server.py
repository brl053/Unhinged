#!/usr/bin/env python3

"""
@llm-type http-service
@llm-legend Minimal HTTP server for DAG control plane on port 9000
@llm-key Zero-dependency HTTP service using Python standard library
@llm-map HTTP API server that provides RESTful interface for DAG control and monitoring
@llm-axiom HTTP service must be lightweight, CORS-enabled, and integrate with existing service patterns
@llm-contract Returns JSON responses with consistent error handling and status codes
@llm-token dag-server: HTTP service for DAG control plane

DAG Control Plane HTTP Service

Minimal HTTP server providing:
- RESTful API for DAG operations
- CORS support for browser access
- Health check compatibility
- Service integration status
- Human approval workflows

Author: Unhinged Team
Version: 1.0.0
Date: 2025-10-19
"""

import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional

from .dag import DAG, DAGNode, NodeStatus
from .config import CONTROL_PLANE_CONFIG, DAG_TARGETS

class DAGHandler(BaseHTTPRequestHandler):
    """HTTP request handler for DAG control plane with existing service integration"""
    
    # Class-level DAG instance (shared across requests)
    dag_instance: Optional[DAG] = None
    
    @classmethod
    def get_dag(cls) -> DAG:
        """Get or create DAG instance"""
        if cls.dag_instance is None:
            cls.dag_instance = DAG()
            cls._initialize_dag_targets()
        return cls.dag_instance
    
    @classmethod
    def _initialize_dag_targets(cls):
        """Initialize DAG with targets from config"""
        from .config import get_node_command

        dag = cls.dag_instance
        all_nodes = set()

        # Collect all unique nodes from all targets
        for target_name, target_config in DAG_TARGETS.items():
            all_nodes.update(target_config["nodes"])

        # Create all unique nodes
        for node_name in all_nodes:
            if node_name not in dag.nodes:
                node = DAGNode(
                    name=node_name,
                    description=f"Build node: {node_name}",
                    command=get_node_command(node_name)
                )
                dag.add_node(node)

        # Add all dependencies from all targets
        for target_name, target_config in DAG_TARGETS.items():
            dependencies = target_config.get("dependencies", {})
            for child, parents in dependencies.items():
                if isinstance(parents, list):
                    for parent in parents:
                        dag.add_dependency(child, parent)
                else:
                    dag.add_dependency(child, parents)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        try:
            if path == '/dag/health':
                self.send_health_response()
            elif path == '/dag/status':
                self.send_dag_status()
            elif path == '/dag/targets':
                self.send_available_targets()
            elif path.startswith('/dag/plan/'):
                target = path.split('/')[-1]
                self.send_execution_plan(target)
            elif path == '/dag/history':
                self.send_execution_history()
            else:
                self.send_error_response(404, "Endpoint not found")

        except Exception as e:
            self.send_error_response(500, f"Internal server error: {e}")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')

            if path == '/dag/execute':
                self.handle_execution_request(post_data)
            elif path == '/dag/approve':
                self.handle_approval(post_data)
            elif path == '/dag/reset':
                self.handle_reset_request()
            else:
                self.send_error_response(404, "Endpoint not found")

        except Exception as e:
            self.send_error_response(500, f"Internal server error: {e}")
    
    def send_cors_headers(self):
        """Send CORS headers for browser compatibility"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def send_json_headers(self):
        """Send JSON content type header"""
        self.send_header('Content-Type', 'application/json')
    
    def send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_cors_headers()
        self.send_json_headers()
        self.end_headers()

        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def send_error_response(self, status_code: int, message: str):
        """Send error response"""
        error_data = {
            "error": True,
            "status_code": status_code,
            "message": message,
            "timestamp": time.time()
        }
        self.send_json_response(error_data, status_code)
    
    def send_health_response(self):
        """Health check response matching existing service patterns"""
        dag = self.get_dag()
        
        health_data = {
            "status": "healthy",
            "service": "dag-control-plane",
            "port": CONTROL_PLANE_CONFIG["server_port"],
            "timestamp": time.time(),
            "capabilities": [
                "dag-execution",
                "human-approval", 
                "service-integration",
                "parallel-execution"
            ],
            "integration": {
                "static_html": "connected",
                "dag_nodes": len(dag.nodes),
                "current_execution": dag.current_execution
            }
        }
        self.send_json_response(health_data)
    
    def send_dag_status(self):
        """Send current DAG status"""
        dag = self.get_dag()
        status_data = dag.get_status()
        status_data["timestamp"] = time.time()
        self.send_json_response(status_data)
    
    def send_available_targets(self):
        """Send list of available build targets"""
        targets_data = {
            "targets": {
                name: {
                    "description": config["description"],
                    "nodes": config["nodes"],
                    "dependencies": config.get("dependencies", {})
                }
                for name, config in DAG_TARGETS.items()
            },
            "timestamp": time.time()
        }
        self.send_json_response(targets_data)
    
    def send_execution_plan(self, target: str):
        """Send execution plan for a target"""
        dag = self.get_dag()

        try:
            # Validate target exists
            if target not in DAG_TARGETS:
                self.send_error_response(404, f"Target '{target}' not found")
                return

            # Get target configuration
            target_config = DAG_TARGETS[target]
            target_nodes = target_config["nodes"]

            # Get execution order for all nodes in target
            all_needed_nodes = set()
            for node_name in target_nodes:
                if node_name in dag.nodes:
                    needed_nodes = dag._get_dependencies(node_name)
                    all_needed_nodes.update(needed_nodes)

            # Generate execution groups using topological sort
            execution_groups = self._get_execution_groups_for_nodes(dag, all_needed_nodes)

            plan_data = {
                "target": target,
                "target_nodes": target_nodes,
                "execution_groups": execution_groups,
                "total_nodes": sum(len(group) for group in execution_groups),
                "estimated_duration": len(execution_groups) * 30,  # Rough estimate
                "requires_approval": target_config.get("human_approval_required", False),
                "timestamp": time.time()
            }
            self.send_json_response(plan_data)

        except Exception as e:
            self.send_error_response(400, f"Failed to generate execution plan: {e}")

    def _get_execution_groups_for_nodes(self, dag, needed_nodes):
        """Generate execution groups for a set of nodes"""
        if not needed_nodes:
            return []

        # Calculate in-degrees for topological sort
        in_degree = {node: 0 for node in needed_nodes}
        for node in needed_nodes:
            for dep in dag.nodes[node].dependencies:
                if dep in needed_nodes:
                    in_degree[node] += 1

        # Generate execution groups
        execution_groups = []
        remaining = set(needed_nodes)

        while remaining:
            # Find nodes with no dependencies (in-degree 0)
            ready_nodes = [node for node in remaining if in_degree[node] == 0]

            if not ready_nodes:
                # This shouldn't happen if validation passed
                raise RuntimeError("No ready nodes found - possible cycle")

            execution_groups.append(ready_nodes)

            # Remove ready nodes and update in-degrees
            for node in ready_nodes:
                remaining.remove(node)
                # Update in-degrees of dependent nodes
                for other_node in remaining:
                    if node in dag.nodes[other_node].dependencies:
                        in_degree[other_node] -= 1

        return execution_groups
    
    def send_execution_history(self):
        """Send execution history"""
        dag = self.get_dag()
        
        history_data = {
            "history": [
                {
                    "node_name": result.node_name,
                    "success": result.success,
                    "duration": result.duration,
                    "start_time": result.start_time,
                    "end_time": result.end_time,
                    "error_message": result.error_message
                }
                for result in dag.execution_history
            ],
            "total_executions": len(dag.execution_history),
            "timestamp": time.time()
        }
        self.send_json_response(history_data)
    
    def handle_execution_request(self, post_data: str):
        """Handle DAG execution request"""
        try:
            request_data = json.loads(post_data) if post_data else {}
            target = request_data.get('target')
            
            if not target:
                self.send_error_response(400, "Missing 'target' parameter")
                return
            
            if target not in DAG_TARGETS:
                self.send_error_response(404, f"Target '{target}' not found")
                return
            
            dag = self.get_dag()
            
            # Check if already executing
            if dag.current_execution:
                self.send_error_response(409, f"Already executing target '{dag.current_execution}'")
                return
            
            # Start execution in background thread
            def execute_dag():
                results = dag.execute(target, human_approval=False)  # TODO: Implement human approval
                print(f"🎉 DAG execution completed for '{target}' with {len(results)} results")
            
            execution_thread = threading.Thread(target=execute_dag, daemon=True)
            execution_thread.start()
            
            response_data = {
                "message": f"Started execution of target '{target}'",
                "target": target,
                "timestamp": time.time()
            }
            self.send_json_response(response_data)
            
        except json.JSONDecodeError:
            self.send_error_response(400, "Invalid JSON in request body")
        except Exception as e:
            self.send_error_response(500, f"Execution failed: {e}")
    
    def handle_approval(self, post_data: str):
        """Handle human approval request"""
        try:
            request_data = json.loads(post_data) if post_data else {}
            approved = request_data.get('approved', False)
            node_name = request_data.get('node_name')
            
            # TODO: Implement actual approval workflow
            response_data = {
                "message": f"Approval {'granted' if approved else 'denied'} for node '{node_name}'",
                "approved": approved,
                "timestamp": time.time()
            }
            self.send_json_response(response_data)
            
        except json.JSONDecodeError:
            self.send_error_response(400, "Invalid JSON in request body")
    
    def handle_reset_request(self):
        """Handle DAG reset request"""
        dag = self.get_dag()
        dag.reset()
        
        response_data = {
            "message": "DAG reset successfully",
            "timestamp": time.time()
        }
        self.send_json_response(response_data)
    
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        # Only log errors and important events
        if format.startswith('code 4') or format.startswith('code 5'):
            super().log_message(format, *args)

def start_dag_server(port: int = None):
    """Start the DAG control plane HTTP server"""
    if port is None:
        port = CONTROL_PLANE_CONFIG["server_port"]
    
    try:
        server = HTTPServer(('localhost', port), DAGHandler)
        print(f"🎛️ DAG Control Plane running on http://localhost:{port}")
        print(f"📊 Health check: http://localhost:{port}/dag/health")
        print(f"🎯 Available targets: http://localhost:{port}/dag/targets")
        print(f"📈 DAG status: http://localhost:{port}/dag/status")
        print()
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 DAG Control Plane shutting down...")
        server.shutdown()
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use. Is another DAG server running?")
        else:
            print(f"❌ Failed to start server: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    start_dag_server()
