"""System view sections - Specialized system information sections."""

from .cpu import CPUSectionHandler
from .memory import MemorySectionHandler
from .motherboard import OverviewSectionHandler
from .platform import PlatformSectionHandler
from .storage import StorageSectionHandler

__all__ = [
    "CPUSectionHandler",
    "MemorySectionHandler",
    "StorageSectionHandler",
    "OverviewSectionHandler",
    "PlatformSectionHandler",
]
