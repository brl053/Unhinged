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
