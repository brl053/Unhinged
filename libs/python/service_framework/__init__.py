"""
Python Service Framework for Unhinged Platform

Provides base classes and utilities for creating gRPC services with:
- Automatic health endpoints
- Hardware-aware resource management  
- Connection pooling and retry logic
- Local OS optimized patterns

Based on expert review feedback for local deployment context.
"""

from .service_base import ServiceBase
from .health_manager import HealthManager, HealthStatus
from .resource_manager import ResourceManager, HardwareInfo
from .connection_pool import ConnectionPool, ServiceClient
from .intent_detector import IntentDetector, IntentResult

__version__ = "1.0.0"
__all__ = [
    "ServiceBase",
    "HealthManager", 
    "HealthStatus",
    "ResourceManager",
    "HardwareInfo", 
    "ConnectionPool",
    "ServiceClient",
    "IntentDetector",
    "IntentResult"
]
