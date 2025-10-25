"""
@llm-type control-system
@llm-legend __init__.py - system control component
@llm-key Core functionality for __init__
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token __init__: system control component
"""
"""
🏗️ Core Application Framework

Base classes and utilities for the native GTK application.
Provides the foundation for tool plugins and shared functionality.

Components:
- Application: Main application class
- ToolManager: Tool registration and lifecycle
- ThemeManager: Application-wide theming
- Shortcuts: Global keyboard shortcuts
"""

from .application import UnhingedApplication
from .tool_manager import ToolManager
from .theme_manager import ThemeManager

__all__ = [
    "UnhingedApplication",
    "ToolManager", 
    "ThemeManager"
]
