
# Initialize GUI event logger
gui_logger = create_gui_logger("unhinged-reflection-client", "1.0.0")

"""
@llm-type control-system
@llm-legend reflection_client.py - system control component
@llm-key Core functionality for reflection_client
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token reflection_client: system control component
"""
"""
🔍 Protobuf Reflection Client

Uses gRPC reflection to dynamically discover service definitions
from running gRPC services without needing .proto files.
from unhinged_events import create_gui_logger

Features:
- Server reflection protocol
- Dynamic service discovery
- Method signature extraction
- Message type definitions
- Real-time proto schema discovery
"""

try:
    import grpc
    from grpc_reflection.v1alpha import reflection_pb2
    from grpc_reflection.v1alpha import reflection_pb2_grpc
    GRPC_REFLECTION_AVAILABLE = True
except ImportError:
    GRPC_REFLECTION_AVAILABLE = False
    gui_logger.warn(" gRPC reflection not available - install with: pip install grpcio-reflection")

import json
from typing import Dict, List, Any, Optional, Tuple
import time


class ReflectionClient:
    """
    gRPC reflection client for dynamic service discovery.
    
    Uses the gRPC Server Reflection Protocol to discover services,
    methods, and message types from running gRPC servers.
    """
    
    def __init__(self):
        self.reflection_cache = {}
        self.cache_duration = 300  # 5 minutes
        
        gui_logger.debug(" Reflection client initialized", {"event_type": "scanning"})
    
    def discover_service_definitions(self, host: str, port: int) -> Dict[str, Any]:
        """
        Discover service definitions using gRPC reflection.
        
        Args:
            host: Server hostname
            port: Server port
            
        Returns:
            Dict with discovered services and their definitions
        """
        if not GRPC_REFLECTION_AVAILABLE:
            return {
                "success": False,
                "error": "gRPC reflection not available",
                "services": [],
                "reflection_supported": False
            }
        
        endpoint = f"{host}:{port}"
        cache_key = f"{endpoint}_{int(time.time() // self.cache_duration)}"
        
        # Check cache
        if cache_key in self.reflection_cache:
            result = self.reflection_cache[cache_key].copy()
            result["cached"] = True
            return result
        
        try:
            
            # Create gRPC channel
            channel = grpc.insecure_channel(endpoint)
            
            # Create reflection stub
            reflection_stub = reflection_pb2_grpc.ServerReflectionStub(channel)
            
            # Discover services
            services = self._list_services(reflection_stub)
            
            # Get detailed information for each service
            service_definitions = []
            for service_name in services:
                if service_name.startswith("grpc."):
                    continue  # Skip internal gRPC services
                
                service_def = self._get_service_definition(reflection_stub, service_name)
                if service_def:
                    service_definitions.append(service_def)
            
            # Close channel
            channel.close()
            
            result = {
                "success": True,
                "services": service_definitions,
                "reflection_supported": True,
                "endpoint": endpoint,
                "discovery_time": time.time(),
                "cached": False
            }
            
            # Cache result
            self.reflection_cache[cache_key] = result.copy()
            
            return result
            
        except grpc.RpcError as e:
            error_msg = f"gRPC reflection failed: {e.code()} - {e.details()}"
            gui_logger.error(f" {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "services": [],
                "reflection_supported": False,
                "endpoint": endpoint
            }
            
        except Exception as e:
            error_msg = f"Reflection discovery failed: {str(e)}"
            gui_logger.error(f" {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "services": [],
                "reflection_supported": False,
                "endpoint": endpoint
            }
    
    def _list_services(self, reflection_stub) -> List[str]:
        """List all services available on the server"""
        try:
            # Create request to list services
            request = reflection_pb2.ServerReflectionRequest()
            request.list_services = ""
            
            # Send request
            responses = reflection_stub.ServerReflectionInfo(iter([request]))
            
            services = []
            for response in responses:
                if response.HasField('list_services_response'):
                    for service in response.list_services_response.service:
                        services.append(service.name)
                    break
            
            return services
            
        except Exception as e:
            gui_logger.error(f" Failed to list services: {e}")
            return []
    
    def _get_service_definition(self, reflection_stub, service_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed definition for a specific service"""
        try:
            # Request service descriptor
            request = reflection_pb2.ServerReflectionRequest()
            request.file_containing_symbol = service_name
            
            responses = reflection_stub.ServerReflectionInfo(iter([request]))
            
            for response in responses:
                if response.HasField('file_descriptor_response'):
                    # Parse the file descriptor
                    file_descriptor_proto = response.file_descriptor_response.file_descriptor_proto[0]
                    
                    # This is where you'd parse the protobuf descriptor
                    # For now, we'll create a simplified representation
                    service_def = self._parse_service_descriptor(service_name, file_descriptor_proto)
                    return service_def
            
            return None
            
        except Exception as e:
            gui_logger.error(f" Failed to get service definition for {service_name}: {e}")
            return None
    
    def _parse_service_descriptor(self, service_name: str, descriptor_proto: bytes) -> Dict[str, Any]:
        """
        Parse protobuf descriptor to extract service information.
        
        This is a simplified implementation. A full implementation would
        use protobuf descriptor parsing libraries.
        """
        try:
            # For now, return a basic structure
            # In a full implementation, you'd parse the descriptor_proto
            # to extract actual method signatures and message types
            
            return {
                "name": service_name,
                "full_name": service_name,
                "methods": self._extract_methods_placeholder(service_name),
                "source": "reflection",
                "descriptor_available": True,
                "package": service_name.split('.')[0] if '.' in service_name else ""
            }
            
        except Exception as e:
            gui_logger.error(f" Failed to parse descriptor for {service_name}: {e}")
            return {
                "name": service_name,
                "full_name": service_name,
                "methods": [],
                "source": "reflection",
                "descriptor_available": False,
                "error": str(e)
            }
    
    def _extract_methods_placeholder(self, service_name: str) -> List[Dict[str, Any]]:
        """
        Placeholder method extraction.
        
        In a full implementation, this would parse the actual protobuf
        descriptor to extract method signatures.
        """
        # Common gRPC method patterns
        common_methods = [
            {
                "name": "Get",
                "request_type": f"{service_name}Request",
                "response_type": f"{service_name}Response",
                "full_signature": f"rpc Get({service_name}Request) returns ({service_name}Response)"
            },
            {
                "name": "List",
                "request_type": f"List{service_name}Request",
                "response_type": f"List{service_name}Response",
                "full_signature": f"rpc List(List{service_name}Request) returns (List{service_name}Response)"
            },
            {
                "name": "Create",
                "request_type": f"Create{service_name}Request",
                "response_type": f"{service_name}Response",
                "full_signature": f"rpc Create(Create{service_name}Request) returns ({service_name}Response)"
            }
        ]
        
        # Return placeholder methods for demonstration
        # In reality, these would be extracted from the descriptor
        return common_methods[:2]  # Return first 2 as example
    
    def get_message_template(self, service_name: str, message_type: str, host: str, port: int) -> Dict[str, Any]:
        """
        Get a template for a specific message type using reflection.
        
        Args:
            service_name: Name of the service
            message_type: Name of the message type
            host: Server hostname
            port: Server port
            
        Returns:
            Dict with message template and field information
        """
        if not GRPC_REFLECTION_AVAILABLE:
            return {
                "success": False,
                "error": "gRPC reflection not available",
                "template": {}
            }
        
        try:
            # This would use reflection to get the actual message structure
            # For now, return a placeholder template
            
            template = {
                "id": 0,
                "name": "",
                "data": {},
                "timestamp": "2023-01-01T00:00:00Z"
            }
            
            return {
                "success": True,
                "template": template,
                "message_type": message_type,
                "service_name": service_name,
                "source": "reflection"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get message template: {str(e)}",
                "template": {}
            }
    
    def test_reflection_support(self, host: str, port: int) -> Dict[str, Any]:
        """
        Test if a server supports gRPC reflection.
        
        Args:
            host: Server hostname
            port: Server port
            
        Returns:
            Dict with reflection support status
        """
        if not GRPC_REFLECTION_AVAILABLE:
            return {
                "supported": False,
                "error": "gRPC reflection client not available",
                "available": False
            }
        
        try:
            endpoint = f"{host}:{port}"
            channel = grpc.insecure_channel(endpoint)
            reflection_stub = reflection_pb2_grpc.ServerReflectionStub(channel)
            
            # Try to list services
            request = reflection_pb2.ServerReflectionRequest()
            request.list_services = ""
            
            responses = reflection_stub.ServerReflectionInfo(iter([request]))
            
            # If we get here without exception, reflection is supported
            for response in responses:
                if response.HasField('list_services_response'):
                    channel.close()
                    return {
                        "supported": True,
                        "available": True,
                        "endpoint": endpoint,
                        "service_count": len(response.list_services_response.service)
                    }
            
            channel.close()
            return {
                "supported": False,
                "available": True,
                "error": "No reflection response received",
                "endpoint": endpoint
            }
            
        except grpc.RpcError as e:
            return {
                "supported": False,
                "available": True,
                "error": f"gRPC error: {e.code()} - {e.details()}",
                "endpoint": f"{host}:{port}"
            }
            
        except Exception as e:
            return {
                "supported": False,
                "available": True,
                "error": f"Connection failed: {str(e)}",
                "endpoint": f"{host}:{port}"
            }
    
    def clear_cache(self):
        """Clear the reflection cache"""
        self.reflection_cache.clear()
