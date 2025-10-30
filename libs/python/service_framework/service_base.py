"""
Python Service Framework Base Class

Equivalent to Kotlin ServiceBase, optimized for local OS deployment.
Implements expert recommendations for simplified local architecture.
"""

import asyncio
import signal
import threading
import time
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Callable
from concurrent.futures import ThreadPoolExecutor

from .health_manager import HealthManager, HealthStatus
from .resource_manager import ResourceManager
from .connection_pool import ConnectionPool


class ServiceBase(ABC):
    """
    Base class for all Python services in Unhinged platform
    
    Provides:
    - Automatic health endpoints
    - Hardware-aware resource management
    - Connection pooling
    - Local OS optimized patterns
    """
    
    def __init__(self, service_id: str, version: str, port: int = 8080):
        self.service_id = service_id
        self.version = version
        self.port = port
        
        # Setup logging
        self.logger = logging.getLogger(f"{service_id}")
        self.logger.info(f"Initializing service: {service_id} v{version}")
        
        # Core components
        self.health_manager = HealthManager(service_id, version)
        self.resource_manager = ResourceManager(service_id)
        self.connection_pool = ConnectionPool()
        
        # Service state
        self._running = False
        self._shutdown_event = threading.Event()
        
        # gRPC server (if needed)
        self._grpc_server: Optional[Any] = None
        
        # Register signal handlers for graceful shutdown
        self._setup_signal_handlers()
    
    async def start(self) -> None:
        """Start the service"""
        try:
            self.logger.info(f"Starting service: {self.service_id}")
            
            # Update health status
            self.health_manager.update_status(HealthStatus.UNKNOWN)
            
            # Initialize service-specific components
            await self.initialize()
            
            # Start gRPC server if needed
            if self.should_start_grpc_server():
                await self.start_grpc_server()
            
            # Register default health checks
            self._register_default_health_checks()
            
            # Service is now healthy
            self.health_manager.update_status(HealthStatus.HEALTHY)
            self._running = True
            
            self.logger.info(f"Service started successfully: {self.service_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to start service: {e}")
            self.health_manager.update_status(HealthStatus.UNHEALTHY)
            raise
    
    async def stop(self) -> None:
        """Stop the service gracefully"""
        try:
            self.logger.info(f"Stopping service: {self.service_id}")
            
            # Update health status
            self.health_manager.update_status(HealthStatus.MAINTENANCE)
            self._running = False
            
            # Stop gRPC server
            if self._grpc_server:
                self._grpc_server.stop(grace=30)
            
            # Cleanup service-specific resources
            await self.cleanup()
            
            # Shutdown core components
            self.resource_manager.shutdown()
            self.connection_pool.shutdown()
            
            # Signal shutdown complete
            self._shutdown_event.set()
            
            self.logger.info(f"Service stopped: {self.service_id}")
            
        except Exception as e:
            self.logger.error(f"Error stopping service: {e}")
            raise
    
    def wait_for_termination(self) -> None:
        """Wait for service termination"""
        try:
            self._shutdown_event.wait()
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
    
    # Abstract methods for service implementation
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize service-specific components"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup service-specific resources"""
        pass
    
    def should_start_grpc_server(self) -> bool:
        """Override to control gRPC server startup"""
        return False
    
    async def start_grpc_server(self) -> None:
        """Start gRPC server (override in subclasses)"""
        pass
    
    # Health and monitoring
    
    def register_health_check(self, name: str, check_func: Callable) -> None:
        """Register custom health check"""
        self.health_manager.register_health_check(name, check_func)
    
    def register_dependency(self, name: str, type_: str, endpoint: str, check_func: Callable) -> None:
        """Register dependency for monitoring"""
        self.health_manager.register_dependency(name, type_, endpoint, check_func)
    
    def update_health_status(self, status: HealthStatus) -> None:
        """Update service health status"""
        self.health_manager.update_status(status)
    
    # Resource management helpers
    
    def submit_io_task(self, func: Callable, *args, **kwargs):
        """Submit I/O bound task"""
        return self.resource_manager.submit_io_task(func, *args, **kwargs)
    
    def submit_cpu_task(self, func: Callable, *args, **kwargs):
        """Submit CPU bound task"""
        return self.resource_manager.submit_cpu_task(func, *args, **kwargs)
    
    def submit_image_task(self, func: Callable, *args, **kwargs):
        """Submit image generation task"""
        return self.resource_manager.submit_image_task(func, *args, **kwargs)
    
    # Service discovery and communication
    
    def register_service_dependency(self, name: str, address: str, stub_class=None) -> None:
        """Register a service dependency"""
        from .connection_pool import ServiceConfig
        config = ServiceConfig(name=name, address=address, stub_class=stub_class)
        self.connection_pool.register_service(config)
    
    def call_service(self, service_name: str, method_name: str, request, timeout: Optional[float] = None):
        """Call another service"""
        return self.connection_pool.call_service(service_name, method_name, request, timeout)
    
    def stream_service(self, service_name: str, method_name: str, request, timeout: Optional[float] = None):
        """Call streaming service method"""
        return self.connection_pool.stream_service(service_name, method_name, request, timeout)
    
    # Monitoring and diagnostics
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get comprehensive service information"""
        return {
            "service": {
                "id": self.service_id,
                "version": self.version,
                "port": self.port,
                "running": self._running,
                "uptime_seconds": time.time() - self.health_manager.start_time
            },
            "health": self.health_manager.get_diagnostics(),
            "resources": self.resource_manager.get_resource_stats(),
            "connections": self.connection_pool.get_connection_stats()
        }
    
    def _register_default_health_checks(self) -> None:
        """Register default health checks"""
        # Service-specific health checks are already registered by HealthManager
        
        # Add service running check
        def service_running_check():
            from .health_manager import HealthCheckResult
            return HealthCheckResult(
                healthy=self._running,
                message="Service running" if self._running else "Service not running",
                response_time_ms=1.0
            )
        
        self.register_health_check("service_running", service_running_check)
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown")
            asyncio.create_task(self.stop())
        
        # Register handlers for common shutdown signals
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


class SimpleService(ServiceBase):
    """
    Simple service implementation for basic use cases
    
    Provides minimal implementation for services that don't need gRPC.
    """
    
    def __init__(self, service_id: str, version: str = "1.0.0"):
        super().__init__(service_id, version)
    
    async def initialize(self) -> None:
        """Default initialization - override as needed"""
        self.logger.info(f"Initializing simple service: {self.service_id}")
    
    async def cleanup(self) -> None:
        """Default cleanup - override as needed"""
        self.logger.info(f"Cleaning up simple service: {self.service_id}")


class GrpcService(ServiceBase):
    """
    gRPC service implementation
    
    Provides gRPC server management for services that need it.
    """
    
    def __init__(self, service_id: str, version: str = "1.0.0", port: int = 8080):
        super().__init__(service_id, version, port)
        self._server_builder = None
    
    def should_start_grpc_server(self) -> bool:
        """Enable gRPC server for this service type"""
        return True
    
    async def start_grpc_server(self) -> None:
        """Start gRPC server with registered services"""
        try:
            import grpc
            from concurrent import futures
            
            # Create server
            server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
            
            # Register services
            self.register_grpc_services(server)
            
            # Add health service
            from grpc_health.v1 import health, health_pb2_grpc
            health_servicer = health.HealthServicer()
            health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
            
            # Start server
            listen_addr = f'[::]:{self.port}'
            server.add_insecure_port(listen_addr)
            server.start()
            
            self._grpc_server = server
            self.logger.info(f"gRPC server started on {listen_addr}")
            
        except Exception as e:
            self.logger.error(f"Failed to start gRPC server: {e}")
            raise
    
    @abstractmethod
    def register_grpc_services(self, server) -> None:
        """Register gRPC services with server (implement in subclass)"""
        pass
    
    async def initialize(self) -> None:
        """Default gRPC service initialization"""
        self.logger.info(f"Initializing gRPC service: {self.service_id}")
    
    async def cleanup(self) -> None:
        """Default gRPC service cleanup"""
        self.logger.info(f"Cleaning up gRPC service: {self.service_id}")


# Convenience functions for common patterns

def run_service(service: ServiceBase) -> None:
    """Run a service with proper async handling"""
    async def main():
        await service.start()
        service.wait_for_termination()
        await service.stop()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Service interrupted by user")
    except Exception as e:
        logging.error(f"Service failed: {e}")
        raise
