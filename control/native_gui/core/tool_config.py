"""
@llm-type tool-configuration
@llm-legend Tool Configuration System - Standardized tool initialization and metadata
@llm-key Provides unified tool configuration to eliminate duplicate initialization patterns
@llm-map Central tool configuration component in Unhinged native GUI architecture
@llm-axiom Tool configuration must be consistent and follow established patterns
@llm-contract Provides standardized tool configuration interface for all tools
@llm-token tool_config: Unified tool configuration system for standardized initialization
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable
from enum import Enum


class ToolCategory(Enum):
    """
    @llm-type enum
    @llm-legend Tool category types for organization and filtering
    @llm-key Defines tool categories for consistent organization
    """
    SYSTEM = "system"
    DEVELOPMENT = "development"
    MONITORING = "monitoring"
    UTILITIES = "utilities"
    COMMUNICATION = "communication"
    SECURITY = "security"
    PRODUCTIVITY = "productivity"


class ToolPriority(Enum):
    """
    @llm-type enum
    @llm-legend Tool priority levels for mobile interface ordering
    @llm-key Defines priority levels for mobile tool display order
    """
    CRITICAL = 1    # Always visible, top priority
    HIGH = 2        # High priority, visible in main view
    MEDIUM = 3      # Medium priority, secondary view
    LOW = 4         # Low priority, accessible via menu
    HIDDEN = 5      # Hidden by default, accessible via settings


@dataclass
class ToolConfig:
    """
    @llm-type configuration
    @llm-legend Comprehensive tool configuration with mobile-responsive properties
    @llm-key Defines all tool parameters for consistent initialization and behavior
    """
    # Basic tool information
    name: str
    icon: str
    description: str
    
    # Optional metadata
    shortcut: Optional[str] = None
    category: ToolCategory = ToolCategory.UTILITIES
    version: str = "1.0.0"
    author: str = "Unhinged"
    
    # Mobile and responsive configuration
    supports_mobile: bool = True
    mobile_priority: ToolPriority = ToolPriority.MEDIUM
    tablet_optimized: bool = True
    desktop_optimized: bool = True
    
    # Feature flags
    supports_dark_theme: bool = True
    supports_high_contrast: bool = True
    requires_permissions: List[str] = field(default_factory=list)
    
    # Performance and behavior
    lazy_load: bool = True
    cache_widgets: bool = True
    auto_refresh: bool = False
    refresh_interval: int = 5000  # milliseconds
    
    # Advanced configuration
    custom_css_classes: List[str] = field(default_factory=list)
    custom_properties: Dict[str, Any] = field(default_factory=dict)
    
    # Callbacks and hooks
    on_activate: Optional[Callable] = None
    on_deactivate: Optional[Callable] = None
    on_mobile_mode_changed: Optional[Callable[[bool], None]] = None


@dataclass
class ToolMetadata:
    """
    @llm-type metadata
    @llm-legend Tool metadata for runtime information and statistics
    @llm-key Contains runtime metadata and usage statistics for tools
    """
    # Runtime information
    is_loaded: bool = False
    is_active: bool = False
    load_time: float = 0.0
    last_used: Optional[float] = None
    usage_count: int = 0
    
    # Performance metrics
    memory_usage: int = 0  # bytes
    cpu_usage: float = 0.0  # percentage
    render_time: float = 0.0  # milliseconds
    
    # Error tracking
    error_count: int = 0
    last_error: Optional[str] = None
    last_error_time: Optional[float] = None


class ToolConfigFactory:
    """
    @llm-type factory-class
    @llm-legend Factory for creating standardized tool configurations
    @llm-key Provides convenient methods for creating common tool configuration patterns
    @llm-map Central factory for tool configuration creation in Unhinged native GUI
    @llm-axiom Factory methods must provide sensible defaults and consistent patterns
    @llm-contract Provides standardized tool configuration creation interface
    @llm-token ToolConfigFactory: Factory for standardized tool configuration creation
    
    Factory class for creating standardized tool configurations.
    Provides convenient methods for common tool patterns.
    """
    
    @staticmethod
    def create_system_tool(name: str, icon: str, description: str, **kwargs) -> ToolConfig:
        """
        @llm-type factory-method
        @llm-legend Create configuration for system monitoring tools
        @llm-key Creates system tool configuration with appropriate defaults
        """
        return ToolConfig(
            name=name,
            icon=icon,
            description=description,
            category=ToolCategory.SYSTEM,
            mobile_priority=ToolPriority.HIGH,
            auto_refresh=True,
            refresh_interval=3000,
            **kwargs
        )
    
    @staticmethod
    def create_development_tool(name: str, icon: str, description: str, **kwargs) -> ToolConfig:
        """
        @llm-type factory-method
        @llm-legend Create configuration for development tools
        @llm-key Creates development tool configuration with appropriate defaults
        """
        return ToolConfig(
            name=name,
            icon=icon,
            description=description,
            category=ToolCategory.DEVELOPMENT,
            mobile_priority=ToolPriority.MEDIUM,
            supports_mobile=True,
            tablet_optimized=True,
            **kwargs
        )
    
    @staticmethod
    def create_monitoring_tool(name: str, icon: str, description: str, **kwargs) -> ToolConfig:
        """
        @llm-type factory-method
        @llm-legend Create configuration for monitoring tools
        @llm-key Creates monitoring tool configuration with appropriate defaults
        """
        return ToolConfig(
            name=name,
            icon=icon,
            description=description,
            category=ToolCategory.MONITORING,
            mobile_priority=ToolPriority.HIGH,
            auto_refresh=True,
            refresh_interval=2000,
            cache_widgets=True,
            **kwargs
        )
    
    @staticmethod
    def create_utility_tool(name: str, icon: str, description: str, **kwargs) -> ToolConfig:
        """
        @llm-type factory-method
        @llm-legend Create configuration for utility tools
        @llm-key Creates utility tool configuration with appropriate defaults
        """
        return ToolConfig(
            name=name,
            icon=icon,
            description=description,
            category=ToolCategory.UTILITIES,
            mobile_priority=ToolPriority.MEDIUM,
            lazy_load=True,
            **kwargs
        )
    
    @staticmethod
    def create_communication_tool(name: str, icon: str, description: str, **kwargs) -> ToolConfig:
        """
        @llm-type factory-method
        @llm-legend Create configuration for communication tools
        @llm-key Creates communication tool configuration with appropriate defaults
        """
        return ToolConfig(
            name=name,
            icon=icon,
            description=description,
            category=ToolCategory.COMMUNICATION,
            mobile_priority=ToolPriority.CRITICAL,
            supports_mobile=True,
            auto_refresh=True,
            refresh_interval=1000,
            **kwargs
        )
    
    @staticmethod
    def create_mobile_optimized_tool(name: str, icon: str, description: str, 
                                   priority: ToolPriority = ToolPriority.HIGH, **kwargs) -> ToolConfig:
                                       pass
        """
        @llm-type factory-method
        @llm-legend Create configuration for mobile-optimized tools
        @llm-key Creates mobile-first tool configuration with touch optimization
        """
        return ToolConfig(
            name=name,
            icon=icon,
            description=description,
            supports_mobile=True,
            mobile_priority=priority,
            tablet_optimized=True,
            desktop_optimized=True,
            cache_widgets=True,
            custom_css_classes=["mobile-optimized", "touch-friendly"],
            **kwargs
        )


class ToolConfigValidator:
    """
    @llm-type validator-class
    @llm-legend Validator for tool configuration consistency and correctness
    @llm-key Validates tool configurations to ensure consistency and prevent errors
    """
    
    @staticmethod
    def validate_config(config: ToolConfig) -> List[str]:
        """
        @llm-type method
        @llm-legend Validate tool configuration for consistency and correctness
        @llm-key Returns list of validation errors, empty if valid
        """
        errors = []
        
        # Basic validation
        if not config.name or not config.name.strip():
            errors.append("Tool name cannot be empty")
        
        if not config.icon or not config.icon.strip():
            errors.append("Tool icon cannot be empty")
        
        if not config.description or not config.description.strip():
            errors.append("Tool description cannot be empty")
        
        # Mobile configuration validation
        if config.supports_mobile and config.mobile_priority == ToolPriority.HIDDEN:
            errors.append("Mobile-supported tools should not have HIDDEN priority")
        
        # Performance validation
        if config.auto_refresh and config.refresh_interval < 1000:
            errors.append("Auto-refresh interval should be at least 1000ms for performance")
        
        # Permission validation
        if config.requires_permissions:
            for permission in config.requires_permissions:
                if not isinstance(permission, str) or not permission.strip():
                    errors.append(f"Invalid permission: {permission}")
        
        return errors
    
    @staticmethod
    def is_valid(config: ToolConfig) -> bool:
        """
        @llm-type method
        @llm-legend Check if tool configuration is valid
        @llm-key Returns True if configuration is valid, False otherwise
        """
        return len(ToolConfigValidator.validate_config(config)) == 0


# Predefined configurations for common tool patterns
SYSTEM_MONITOR_CONFIG = ToolConfigFactory.create_system_tool(
    name="System Monitor",
    icon="🖥️",
    description="Real-time system monitoring and performance metrics",
    shortcut="Ctrl+Shift+M"
)

LOG_VIEWER_CONFIG = ToolConfigFactory.create_monitoring_tool(
    name="Log Viewer",
    icon="📋",
    description="View and analyze system logs in real-time",
    shortcut="Ctrl+Shift+L"
)

SERVICE_MANAGER_CONFIG = ToolConfigFactory.create_system_tool(
    name="Service Manager",
    icon="⚙️",
    description="Manage system services and processes",
    shortcut="Ctrl+Shift+S"
)

INPUT_CAPTURE_CONFIG = ToolConfig(
    name="Input Capture",
    icon="⌨️",
    description="Monitor and analyze keyboard and mouse input patterns",
    category=ToolCategory.UTILITIES,
    mobile_priority=ToolPriority.HIGH,
    requires_permissions=["input_monitoring"]
)
