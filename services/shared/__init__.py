#!/usr/bin/env python3
"""
@llm-type service.shared
@llm-does shared service utilities, registry, and base classes
@llm-rule shared service code must be simple, reusable, and eliminate duplication
"""

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
from .service_registry import (
    ServiceEndpoint,
    ServiceRegistry,
    ServiceStatus,
    get_service_registry,
)

__all__ = [
    # Paths
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
    # Registry
    "ServiceRegistry",
    "ServiceEndpoint",
    "ServiceStatus",
    "get_service_registry",
]
