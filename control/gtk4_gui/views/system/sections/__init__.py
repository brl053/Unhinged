"""System view sections - Specialized system information sections."""

from .cpu import SystemViewCPU
from .memory import SystemViewMemory
from .storage import SystemViewStorage
from .motherboard import SystemViewMotherboard
from .platform import SystemViewPlatform

__all__ = [
    "SystemViewCPU",
    "SystemViewMemory",
    "SystemViewStorage",
    "SystemViewMotherboard",
    "SystemViewPlatform",
]

