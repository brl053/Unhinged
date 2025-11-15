"""
@llm-doc Container GTK4 Components
@llm-version 1.0.0
@llm-date 2025-11-15

Container components for organizing and grouping content.
Re-exports from specialized container modules for backward compatibility.
"""

# Re-export all container classes from specialized modules
from .log_containers import LogContainer
from .status_containers import ServicePanel, StatusCard
from .system_containers import SystemInfoCard, SystemStatusGrid
from .window_containers import AbstractWindow

__all__ = [
    "AbstractWindow",
    "StatusCard",
    "ServicePanel",
    "LogContainer",
    "SystemInfoCard",
    "SystemStatusGrid",
]
