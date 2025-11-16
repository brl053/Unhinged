"""System view sections - Specialized system information sections."""

from .cpu import SystemViewCPU
from .memory import SystemViewMemory
from .motherboard import SystemViewMotherboard
from .platform import SystemViewPlatform
from .storage import SystemViewStorage

__all__ = [
    "SystemViewCPU",
    "SystemViewMemory",
    "SystemViewStorage",
    "SystemViewMotherboard",
    "SystemViewPlatform",
]

