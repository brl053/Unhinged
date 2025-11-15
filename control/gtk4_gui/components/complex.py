"""
Complex GTK4 Components - Refactored Package

This module provides backward compatibility by re-exporting all components
from the complex package. Individual components are now in separate files
for better maintainability.

See complex/ directory for individual component implementations.
"""

from .complex import (
    LogViewer,
    ServiceRow,
    SystemStatus,
    PerformanceIndicator,
    ProcessTable,
    BluetoothTable,
    AudioTable,
)

__all__ = [
    "LogViewer",
    "ServiceRow",
    "SystemStatus",
    "PerformanceIndicator",
    "ProcessTable",
    "BluetoothTable",
    "AudioTable",
]
