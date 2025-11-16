"""
@llm-doc Memory Information Collection
@llm-version 1.0.0
@llm-date 2025-11-15

Memory and swap information collection using psutil.
"""

import logging

# Import psutil with fallback
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class MemoryCollector:
    """Collects memory and swap information."""

    def collect_memory_info(self):
        """Collect memory information"""
        from .system_info import MemoryInfo

        memory_info = MemoryInfo()

        if PSUTIL_AVAILABLE:
            # Get memory info
            memory = psutil.virtual_memory()
            memory_info.total_gb = memory.total / (1024**3)
            memory_info.available_gb = memory.available / (1024**3)
            memory_info.used_gb = memory.used / (1024**3)
            memory_info.usage_percent = memory.percent

            # Get swap info
            try:
                swap = psutil.swap_memory()
                memory_info.swap_total_gb = swap.total / (1024**3)
                memory_info.swap_used_gb = swap.used / (1024**3)
                memory_info.swap_percent = swap.percent
            except Exception as e:
                logger.debug(f"Failed to get swap info: {e}")

        return memory_info

