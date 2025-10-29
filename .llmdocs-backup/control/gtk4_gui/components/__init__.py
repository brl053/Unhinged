"""
@llm-doc GTK4 Component Library for Unhinged
@llm-version 1.0.0
@llm-date 2025-10-27
@llm-author Unhinged Team

## Overview
Focused GTK4 component library that integrates with the Unhinged design system.
Provides reusable, accessible widgets following GNOME HIG patterns.

## Design Principles
- **Design System Integration**: Uses semantic tokens from libs/design_system/
- **Libadwaita First**: Builds on Adw widgets for native GNOME experience
- **Focused Components**: Only components actually needed by the application
- **Type Safety**: Proper GTK4 typing and signal handling
- **Accessibility**: ARIA labels, keyboard navigation, screen reader support

## Component Categories
- **Primitives**: Basic building blocks (buttons, inputs, labels)
- **Containers**: Layout and grouping (cards, panels, sections)
- **Complex**: Stateful components (log viewer, progress indicators)
- **System**: Application-level components (status displays, service rows)

@llm-principle Focused, practical components with design system integration
@llm-culture Independence through reusable, accessible UI components
"""

# Component imports organized by category
from .base import ComponentBase, ComponentError
from .primitives import ActionButton, StatusLabel, ProgressIndicator, HardwareInfoRow, ProcessRow, BluetoothRow, AudioDeviceRow
from .containers import StatusCard, ServicePanel, LogContainer, SystemInfoCard, SystemStatusGrid
from .complex import LogViewer, ServiceRow, SystemStatus, PerformanceIndicator, ProcessTable, BluetoothTable, AudioTable
from .tables import GenericTable, TableColumn

# Version and metadata
__version__ = "1.0.0"
__author__ = "Unhinged Team"

# Public API - components that should be imported by applications
__all__ = [
    # Base classes
    "ComponentBase",
    "ComponentError",

    # Primitive components
    "ActionButton",
    "StatusLabel",
    "ProgressIndicator",
    "HardwareInfoRow",
    "ProcessRow",
    "BluetoothRow",
    "AudioDeviceRow",

    # Container components
    "StatusCard",
    "ServicePanel",
    "LogContainer",
    "SystemInfoCard",
    "SystemStatusGrid",

    # Complex components
    "LogViewer",
    "ServiceRow",
    "SystemStatus",
    "PerformanceIndicator",
    "ProcessTable",
    "BluetoothTable",
    "AudioTable",

    # Table components
    "GenericTable",
    "TableColumn",
]

# Component registry for introspection and tooling
COMPONENT_REGISTRY = {
    "primitives": [
        "ActionButton",
        "StatusLabel",
        "ProgressIndicator",
        "HardwareInfoRow",
        "ProcessRow",
        "BluetoothRow",
        "AudioDeviceRow",
    ],
    "containers": [
        "StatusCard",
        "ServicePanel",
        "LogContainer",
        "SystemInfoCard",
        "SystemStatusGrid",
    ],
    "complex": [
        "LogViewer",
        "ServiceRow",
        "SystemStatus",
        "PerformanceIndicator",
        "ProcessTable",
        "BluetoothTable",
        "AudioTable",
    ],
    "tables": [
        "GenericTable",
        "TableColumn",
    ]
}

def get_component_info():
    """
    Get information about available components.
    
    Returns:
        dict: Component registry with categories and component lists
    """
    return {
        "version": __version__,
        "components": COMPONENT_REGISTRY,
        "total_components": sum(len(components) for components in COMPONENT_REGISTRY.values())
    }

def list_components():
    """Print available components organized by category."""
    info = get_component_info()
    print(f"🎨 Unhinged GTK4 Component Library v{info['version']}")
    print(f"📦 Total Components: {info['total_components']}")
    print()
    
    for category, components in info['components'].items():
        print(f"📂 {category.title()}:")
        for component in components:
            print(f"  • {component}")
        print()
