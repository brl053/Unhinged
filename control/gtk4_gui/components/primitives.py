"""
Primitive GTK4 Components - Refactored Package

This module provides backward compatibility by re-exporting all components
from the primitives package. Individual components are now in separate files
for better maintainability.

See primitives/ directory for individual component implementations.
"""

from .primitives import (
    ActionButton,
    StatusLabel,
    ProgressIndicator,
    HardwareInfoRow,
    ProcessRow,
    BluetoothRow,
    AudioDeviceRow,
    ChatBubble,
    LoadingDots,
    CopyButton,
    TextEditor,
)

__all__ = [
    "ActionButton",
    "StatusLabel",
    "ProgressIndicator",
    "HardwareInfoRow",
    "ProcessRow",
    "BluetoothRow",
    "AudioDeviceRow",
    "ChatBubble",
    "LoadingDots",
    "CopyButton",
    "TextEditor",
]
