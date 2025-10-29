"""
@llm-type control-system
@llm-legend __init__.py - Network control system module initialization
@llm-key Network subsystem providing service discovery and health monitoring
@llm-map Core network control components for unified service management
@llm-axiom Network layer maintains service discovery and health monitoring independence
@llm-contract Provides standardized network control interface for system components
@llm-token network-control: Unified network service management subsystem
"""

from .service_registry import ServiceRegistry, ServiceEndpoint, ServiceStatus, get_service_registry

__all__ = ['ServiceRegistry', 'ServiceEndpoint', 'ServiceStatus', 'get_service_registry']
