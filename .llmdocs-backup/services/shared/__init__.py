#!/usr/bin/env python3
"""
@llm-type service-shared
@llm-legend Shared service utilities and base classes for Unhinged services
@llm-key Common service functionality eliminating DRY violations across services
@llm-map Shared service components enabling consistent service architecture
@llm-axiom Shared service code must be simple, reusable, and eliminate duplication
@llm-contract Provides common service utilities, paths, and base classes
@llm-token service-shared: Shared utilities and base classes for service consistency

Shared Service Components for Unhinged Services
Eliminates DRY violations and provides consistent service architecture
"""

from .paths import (
    get_service_path,
    ensure_service_directory,
    get_upload_directory,
    get_models_directory,
    get_outputs_directory,
    get_cache_directory,
    get_logs_directory,
    ServicePaths,
    service_paths,
    get_service_config_path,
    get_service_env_path
)

__all__ = [
    'get_service_path',
    'ensure_service_directory',
    'get_upload_directory', 
    'get_models_directory',
    'get_outputs_directory',
    'get_cache_directory',
    'get_logs_directory',
    'ServicePaths',
    'service_paths',
    'get_service_config_path',
    'get_service_env_path'
]
