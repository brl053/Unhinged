"""
@llm-type client
@llm-legend gRPC health client for native GUI service discovery and monitoring
@llm-key Provides health.proto client for checking service status via gRPC
@llm-map Health client for native GUI to communicate with gRPC services
@llm-axiom All services must implement health.proto for service discovery
@llm-contract Returns service health status and diagnostics via gRPC calls
@llm-token health-client: gRPC client for health.proto service discovery

gRPC Health Client for Native GUI

Implements health.proto client for service discovery:
- Heartbeat calls: Fast service status checks
- Diagnostics calls: Detailed service information
- Service discovery: Automatic service detection
- Error handling: Graceful failure handling
"""

import grpc
from typing import Dict, List, Optional, Tuple
import time
from unhinged_events import create_service_logger

# Health proto imports
from health import health_pb2
from health import health_pb2_grpc

# Initialize event logger
events = create_service_logger("health-client", "1.0.0")


class HealthClient:
    """gRPC Health Client for service discovery and monitoring"""
    
    def __init__(self):
        self.services = {
            "speech-to-text": {"host": "localhost", "port": 9091},
            "text-to-speech": {"host": "localhost", "port": 9092}, 
            "vision-ai": {"host": "localhost", "port": 9093},
        }
        self.timeout = 5.0  # 5 second timeout for health calls
        
    def check_service_heartbeat(self, service_name: str) -> Tuple[bool, Dict]:
        """
        Check service heartbeat (fast <10ms call)
        
        Returns:
            Tuple[bool, Dict]: (is_healthy, response_data)
        """
        if service_name not in self.services:
            return False, {"error": f"Unknown service: {service_name}"}
            
        service_config = self.services[service_name]
        address = f"{service_config['host']}:{service_config['port']}"
        
        try:
            with grpc.insecure_channel(address) as channel:
                stub = health_pb2_grpc.HealthServiceStub(channel)
                request = health_pb2.HeartbeatRequest()
                
                start_time = time.time()
                response = stub.Heartbeat(request, timeout=self.timeout)
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                return response.alive, {
                    "service_id": response.service_id,
                    "version": response.version,
                    "status": self._status_to_string(response.status),
                    "uptime_ms": response.uptime_ms,
                    "response_time_ms": round(response_time, 2),
                    "timestamp_ms": response.timestamp_ms
                }
                
        except grpc.RpcError as e:
            events.warn("gRPC health check error", {"service": service_name, "code": str(e.code())})
            return False, {
                "error": f"gRPC error: {e.code()}",
                "details": str(e.details()) if e.details() else "Connection failed"
            }
        except Exception as e:
            events.error("Health check connection error", exception=e, metadata={"service": service_name})
            return False, {"error": f"Connection error: {str(e)}"}
    
    def get_service_diagnostics(self, service_name: str, include_metrics: bool = True) -> Tuple[bool, Dict]:
        """
        Get detailed service diagnostics (<1s call)
        
        Returns:
            Tuple[bool, Dict]: (is_healthy, diagnostics_data)
        """
        if service_name not in self.services:
            return False, {"error": f"Unknown service: {service_name}"}
            
        service_config = self.services[service_name]
        address = f"{service_config['host']}:{service_config['port']}"
        
        try:
            with grpc.insecure_channel(address) as channel:
                stub = health_pb2_grpc.HealthServiceStub(channel)
                request = health_pb2.DiagnosticsRequest()
                request.include_metrics = include_metrics
                request.include_dependencies = True
                request.include_resources = True
                request.include_custom_checks = True
                
                start_time = time.time()
                response = stub.Diagnostics(request, timeout=self.timeout)
                response_time = (time.time() - start_time) * 1000
                
                # Extract heartbeat info
                heartbeat = response.heartbeat
                
                return heartbeat.alive, {
                    "heartbeat": {
                        "service_id": heartbeat.service_id,
                        "version": heartbeat.version,
                        "status": self._status_to_string(heartbeat.status),
                        "uptime_ms": heartbeat.uptime_ms,
                        "alive": heartbeat.alive
                    },
                    "metadata": dict(response.metadata),
                    "response_time_ms": round(response_time, 2),
                    "last_updated": response.last_updated.seconds if response.last_updated else None
                }
                
        except grpc.RpcError as e:
            events.warn("gRPC diagnostics error", {"service": service_name, "code": str(e.code())})
            return False, {
                "error": f"gRPC error: {e.code()}",
                "details": str(e.details()) if e.details() else "Connection failed"
            }
        except Exception as e:
            events.error("Diagnostics connection error", exception=e, metadata={"service": service_name})
            return False, {"error": f"Connection error: {str(e)}"}
    
    def check_all_services(self) -> Dict[str, Dict]:
        """
        Check health of all known services
        
        Returns:
            Dict[str, Dict]: Service name -> health data
        """
        results = {}
        
        for service_name in self.services.keys():
            is_healthy, data = self.check_service_heartbeat(service_name)
            results[service_name] = {
                "healthy": is_healthy,
                "data": data
            }
            
        return results
    
    def _status_to_string(self, status: int) -> str:
        """Convert health status enum to string"""
        status_map = {
            health_pb2.HEALTH_STATUS_UNKNOWN: "unknown",
            health_pb2.HEALTH_STATUS_HEALTHY: "healthy", 
            health_pb2.HEALTH_STATUS_DEGRADED: "degraded",
            health_pb2.HEALTH_STATUS_UNHEALTHY: "unhealthy",
            health_pb2.HEALTH_STATUS_MAINTENANCE: "maintenance"
        }
        return status_map.get(status, "unknown")
    
    def get_service_list(self) -> List[str]:
        """Get list of known services"""
        return list(self.services.keys())
    
    def add_service(self, name: str, host: str, port: int):
        """Add a new service to monitor"""
        self.services[name] = {"host": host, "port": port}
    
    def remove_service(self, name: str):
        """Remove a service from monitoring"""
        if name in self.services:
            del self.services[name]
