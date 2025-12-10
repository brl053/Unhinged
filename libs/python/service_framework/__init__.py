"""
Python Service Framework for Unhinged Platform

Provides base classes and utilities for creating gRPC services with:
- Automatic health endpoints
- Hardware-aware resource management
- Connection pooling and retry logic
- Service registry and discovery
- Service launcher and orchestration
- Health monitoring with auto-recovery
- Local OS optimized patterns

Based on expert review feedback for local deployment context.
"""

from .connection_pool import (
    ConnectionPool,
    ServiceClient,
    call_service,
    get_global_pool,
    register_service,
    stream_service,
)
from .health_manager import HealthManager, HealthStatus
from .intent_detector import IntentDetector, IntentResult, IntentType, detect_intent
from .paths import (
    ServicePaths,
    ensure_service_directory,
    get_cache_directory,
    get_logs_directory,
    get_models_directory,
    get_outputs_directory,
    get_service_config_path,
    get_service_env_path,
    get_service_path,
    get_upload_directory,
    service_paths,
)
from .resource_manager import HardwareInfo, ResourceManager
from .service_base import ServiceBase
from .service_health_monitor import ServiceHealthMonitor
from .service_launcher import ServiceLauncher
from .service_registry import (
    ServiceEndpoint,
    ServiceRegistry,
    ServiceStatus,
    get_service_registry,
)

__version__ = "1.0.0"
__all__ = [
    # Base classes
    "ServiceBase",
    # Health management
    "HealthManager",
    "HealthStatus",
    "ServiceHealthMonitor",
    # Resource management
    "ResourceManager",
    "HardwareInfo",
    # Connection pooling
    "ConnectionPool",
    "ServiceClient",
    "get_global_pool",
    "call_service",
    "stream_service",
    "register_service",
    # Intent detection
    "IntentDetector",
    "IntentResult",
    "IntentType",
    "detect_intent",
    # Service registry
    "ServiceRegistry",
    "ServiceEndpoint",
    "ServiceStatus",
    "get_service_registry",
    # Service launcher
    "ServiceLauncher",
    # Path utilities
    "get_service_path",
    "ensure_service_directory",
    "get_upload_directory",
    "get_models_directory",
    "get_outputs_directory",
    "get_cache_directory",
    "get_logs_directory",
    "ServicePaths",
    "service_paths",
    "get_service_config_path",
    "get_service_env_path",
]
