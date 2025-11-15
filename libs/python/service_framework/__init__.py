"""
Python Service Framework for Unhinged Platform

Provides base classes and utilities for creating gRPC services with:
- Automatic health endpoints
- Hardware-aware resource management
- Connection pooling and retry logic
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
from .resource_manager import HardwareInfo, ResourceManager
from .service_base import ServiceBase

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
    "IntentResult",
    "IntentType",
    "detect_intent",
    "get_global_pool",
    "call_service",
    "stream_service",
    "register_service",
]
