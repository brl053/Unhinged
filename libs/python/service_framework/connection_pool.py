"""
Connection Pool for gRPC Services

Consolidates gRPC client management with local OS optimizations.
Implements expert recommendations for simplified local deployment.
"""

import logging
import threading
import time
from dataclasses import dataclass
from typing import Any

import grpc


@dataclass
class ServiceConfig:
    """Configuration for a gRPC service"""
    name: str
    address: str
    timeout: float = 120.0  # Expert recommended 120s for local image generation
    max_retries: int = 3
    stub_class: type | None = None


class ServiceClient:
    """
    Wrapper for gRPC service clients with local OS optimizations
    
    Simplified for localhost deployment - no complex retry logic needed
    since network partitions don't exist locally.
    """

    def __init__(self, config: ServiceConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{config.name}")

        self._channel: grpc.Channel | None = None
        self._stub: Any | None = None
        self._lock = threading.RLock()
        self._last_used = time.time()
        self._connection_count = 0

    def get_stub(self):
        """Get gRPC stub, creating connection if needed"""
        with self._lock:
            if self._stub is None:
                self._connect()

            self._last_used = time.time()
            return self._stub

    def _connect(self) -> None:
        """Establish gRPC connection"""
        try:
            self.logger.info(f"Connecting to {self.config.name} at {self.config.address}")

            # For local deployment, use insecure channel
            # Handle different gRPC versions and imports
            try:
                # Debug: check what grpc module we have
                print(f"🔍 grpc module: {grpc}")
                print(f"🔍 grpc dir: {dir(grpc)[:10]}")
                print(f"🔍 has insecure_channel: {'insecure_channel' in dir(grpc)}")

                self._channel = grpc.insecure_channel(self.config.address)
                print(f"✅ Created channel: {self._channel}")
            except AttributeError as e:
                print(f"❌ AttributeError: {e}")
                # Try alternative import path
                try:
                    from grpc import insecure_channel
                    self._channel = insecure_channel(self.config.address)
                    print(f"✅ Created channel with direct import: {self._channel}")
                except ImportError as e2:
                    print(f"❌ ImportError: {e2}")
                    raise RuntimeError(f"Failed to create gRPC channel: {e}")
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                raise

            # Create stub if class provided
            if self.config.stub_class:
                self._stub = self.config.stub_class(self._channel)
            else:
                self._stub = self._channel  # Return channel directly

            self._connection_count += 1
            self.logger.info(f"Connected to {self.config.name} (connection #{self._connection_count})")

        except Exception as e:
            self.logger.error(f"Failed to connect to {self.config.name}: {e}")
            self._cleanup()
            raise

    def call_with_timeout(self, method_name: str, request, timeout: float | None = None) -> Any:
        """
        Call gRPC method with timeout and simple retry logic
        
        Simplified for local deployment - just retry on connection errors.
        """
        stub = self.get_stub()
        call_timeout = timeout or self.config.timeout

        for attempt in range(self.config.max_retries):
            try:
                method = getattr(stub, method_name)
                return method(request, timeout=call_timeout)

            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.UNAVAILABLE and attempt < self.config.max_retries - 1:
                    self.logger.warning(f"Service {self.config.name} unavailable, retrying... (attempt {attempt + 1})")
                    self._reconnect()
                    time.sleep(0.5 * (attempt + 1))  # Simple backoff
                    continue
                else:
                    self.logger.error(f"gRPC call failed: {e}")
                    raise
            except Exception as e:
                self.logger.error(f"Unexpected error calling {method_name}: {e}")
                raise

        raise RuntimeError(f"Failed to call {method_name} after {self.config.max_retries} attempts")

    def stream_with_timeout(self, method_name: str, request, timeout: float | None = None):
        """
        Call streaming gRPC method with timeout
        
        For image generation and other streaming operations.
        """
        stub = self.get_stub()
        call_timeout = timeout or self.config.timeout

        try:
            method = getattr(stub, method_name)
            return method(request, timeout=call_timeout)
        except Exception as e:
            self.logger.error(f"Streaming call failed: {e}")
            raise

    def _reconnect(self) -> None:
        """Reconnect to service"""
        with self._lock:
            self._cleanup()
            self._connect()

    def _cleanup(self) -> None:
        """Clean up connection resources"""
        if self._channel:
            try:
                self._channel.close()
            except:
                pass

        self._channel = None
        self._stub = None

    def is_healthy(self) -> bool:
        """Check if connection is healthy"""
        if not self._stub:
            return False

        try:
            # Try a simple call if health check method exists
            if hasattr(self._stub, 'Check'):
                try:
                    from grpc_health.v1 import health_pb2
                    request = health_pb2.HealthCheckRequest()
                    response = self._stub.Check(request, timeout=5.0)
                    return response.status == health_pb2.HealthCheckResponse.SERVING
                except ImportError:
                    pass  # Health check not available
        except:
            pass

        return True  # Assume healthy if no health check available

    def get_stats(self) -> dict[str, Any]:
        """Get connection statistics"""
        return {
            "name": self.config.name,
            "address": self.config.address,
            "connected": self._stub is not None,
            "connection_count": self._connection_count,
            "last_used": self._last_used,
            "idle_time": time.time() - self._last_used
        }

    def close(self) -> None:
        """Close connection"""
        with self._lock:
            self._cleanup()


class ConnectionPool:
    """
    Connection pool for gRPC services
    
    Optimized for local OS deployment with simplified management.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._clients: dict[str, ServiceClient] = {}
        self._configs: dict[str, ServiceConfig] = {}
        self._lock = threading.RLock()

        # Connection monitoring
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_connections, daemon=True)
        self._monitor_thread.start()

    def register_service(self, config: ServiceConfig) -> None:
        """Register a service configuration"""
        with self._lock:
            self._configs[config.name] = config
            self.logger.info(f"Registered service: {config.name} at {config.address}")

    def get_client(self, service_name: str) -> ServiceClient:
        """Get client for service, creating if needed"""
        with self._lock:
            if service_name not in self._clients:
                if service_name not in self._configs:
                    raise ValueError(f"Service {service_name} not registered")

                config = self._configs[service_name]
                self._clients[service_name] = ServiceClient(config)

            return self._clients[service_name]

    def call_service(self, service_name: str, method_name: str, request,
                    timeout: float | None = None) -> Any:
        """Convenience method to call service method"""
        client = self.get_client(service_name)
        return client.call_with_timeout(method_name, request, timeout)

    def stream_service(self, service_name: str, method_name: str, request,
                      timeout: float | None = None):
        """Convenience method to call streaming service method"""
        client = self.get_client(service_name)
        return client.stream_with_timeout(method_name, request, timeout)

    def get_service_health(self) -> dict[str, bool]:
        """Get health status of all services"""
        health = {}
        with self._lock:
            for name, client in self._clients.items():
                health[name] = client.is_healthy()
        return health

    def get_connection_stats(self) -> dict[str, dict[str, Any]]:
        """Get statistics for all connections"""
        stats = {}
        with self._lock:
            for name, client in self._clients.items():
                stats[name] = client.get_stats()
        return stats

    def _monitor_connections(self) -> None:
        """Monitor connections and clean up idle ones"""
        while self._monitoring:
            try:
                current_time = time.time()
                idle_threshold = 300.0  # 5 minutes for local deployment

                with self._lock:
                    idle_clients = []
                    for name, client in self._clients.items():
                        if current_time - client._last_used > idle_threshold:
                            idle_clients.append(name)

                    # Close idle connections
                    for name in idle_clients:
                        self.logger.info(f"Closing idle connection to {name}")
                        self._clients[name].close()
                        del self._clients[name]

                time.sleep(60.0)  # Check every minute

            except Exception as e:
                self.logger.error(f"Connection monitoring error: {e}")
                time.sleep(60.0)

    def shutdown(self) -> None:
        """Shutdown connection pool"""
        self.logger.info("Shutting down connection pool")

        self._monitoring = False

        with self._lock:
            for client in self._clients.values():
                client.close()
            self._clients.clear()

        # Wait for monitor thread
        if self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)


# Global connection pool instance
_global_pool: ConnectionPool | None = None
_pool_lock = threading.Lock()


def get_global_pool() -> ConnectionPool:
    """Get global connection pool instance"""
    global _global_pool

    if _global_pool is None:
        with _pool_lock:
            if _global_pool is None:
                _global_pool = ConnectionPool()

    return _global_pool


def register_service(name: str, address: str, stub_class: type | None = None,
                    timeout: float = 120.0) -> None:
    """Register a service with the global pool"""
    config = ServiceConfig(
        name=name,
        address=address,
        timeout=timeout,
        stub_class=stub_class
    )
    get_global_pool().register_service(config)


def call_service(service_name: str, method_name: str, request,
                timeout: float | None = None) -> Any:
    """Call service method using global pool"""
    return get_global_pool().call_service(service_name, method_name, request, timeout)


def stream_service(service_name: str, method_name: str, request,
                  timeout: float | None = None):
    """Call streaming service method using global pool"""
    return get_global_pool().stream_service(service_name, method_name, request, timeout)
