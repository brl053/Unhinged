#!/usr/bin/env python3
"""
@llm-type service.util
@llm-does shared utilities for service path management and
@llm-rule service utilities must be simple, reusable, and eliminate path hardcoding
"""

import os
from pathlib import Path
from typing import Optional


def get_service_path(subdir: str = "") -> str:
    """
    Get service-relative path, eliminating hardcoded /app/ Docker paths
    
    Args:
        subdir: Subdirectory relative to service root (e.g., 'uploads', 'models', 'outputs')
        
    Returns:
        Absolute path to service subdirectory
        
    Examples:
        get_service_path('uploads') → '/path/to/service/uploads'
        get_service_path('models') → '/path/to/service/models'
        get_service_path() → '/path/to/service'
    """
    service_root = os.getcwd()
    if subdir:
        return os.path.join(service_root, subdir)
    return service_root


def ensure_service_directory(subdir: str) -> str:
    """
    Ensure service subdirectory exists, create if missing
    
    Args:
        subdir: Subdirectory to create (e.g., 'uploads', 'models', 'outputs')
        
    Returns:
        Absolute path to created directory
    """
    dir_path = get_service_path(subdir)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def get_upload_directory() -> str:
    """Get standardized upload directory for service file uploads"""
    return ensure_service_directory('uploads')


def get_models_directory() -> str:
    """Get standardized models directory for ML model storage"""
    return ensure_service_directory('models')


def get_outputs_directory() -> str:
    """Get standardized outputs directory for service-generated files"""
    return ensure_service_directory('outputs')


def get_cache_directory() -> str:
    """Get standardized cache directory for service caching"""
    return ensure_service_directory('cache')


def get_logs_directory() -> str:
    """Get standardized logs directory for service logging"""
    return ensure_service_directory('logs')


class ServicePaths:
    """
@llm-type service.api
@llm-does service path manager providing standardized directory access
@llm-rule service paths must be consistent, predictable, and environment-agnostic
"""
    
    def __init__(self, service_root: Optional[str] = None):
        """
        Initialize service path manager
        
        Args:
            service_root: Optional service root directory (defaults to current working directory)
        """
        self.service_root = service_root or os.getcwd()
    
    def get_path(self, subdir: str = "") -> str:
        """Get path relative to service root"""
        if subdir:
            return os.path.join(self.service_root, subdir)
        return self.service_root
    
    def ensure_directory(self, subdir: str) -> str:
        """Ensure directory exists, create if missing"""
        dir_path = self.get_path(subdir)
        os.makedirs(dir_path, exist_ok=True)
        return dir_path
    
    @property
    def uploads(self) -> str:
        """Upload directory for file uploads"""
        return self.ensure_directory('uploads')
    
    @property
    def models(self) -> str:
        """Models directory for ML model storage"""
        return self.ensure_directory('models')
    
    @property
    def outputs(self) -> str:
        """Outputs directory for generated files"""
        return self.ensure_directory('outputs')
    
    @property
    def cache(self) -> str:
        """Cache directory for service caching"""
        return self.ensure_directory('cache')
    
    @property
    def logs(self) -> str:
        """Logs directory for service logging"""
        return self.ensure_directory('logs')


# Global service paths instance for convenience
service_paths = ServicePaths()


def get_service_config_path(config_name: str = "config.yml") -> str:
    """
    Get path to service configuration file
    
    Args:
        config_name: Configuration file name (defaults to 'config.yml')
        
    Returns:
        Path to service configuration file
    """
    return get_service_path(config_name)


def get_service_env_path(env_name: str = ".env") -> str:
    """
    Get path to service environment file
    
    Args:
        env_name: Environment file name (defaults to '.env')
        
    Returns:
        Path to service environment file
    """
    return get_service_path(env_name)


# Convenience exports for common patterns
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
