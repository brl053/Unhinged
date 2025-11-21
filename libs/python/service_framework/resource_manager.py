"""
Resource Management for Local OS Context

Hardware-aware thread pooling and resource limits based on expert feedback.
Optimized for local deployment rather than distributed systems.
"""

import contextlib
import logging
import threading
import time
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from queue import Empty, Queue
from typing import Any

import psutil


@dataclass
class HardwareInfo:
    """Hardware capabilities detected at runtime"""

    cpu_cores: int
    cpu_threads: int
    memory_gb: float
    cpu_freq_mhz: float
    has_ssd: bool

    @classmethod
    def detect(cls) -> "HardwareInfo":
        """Detect hardware capabilities"""
        cpu_info = psutil.cpu_count(logical=False) or 1
        cpu_threads = psutil.cpu_count(logical=True) or 1
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)

        # Try to detect CPU frequency
        try:
            cpu_freq = psutil.cpu_freq()
            cpu_freq_mhz = cpu_freq.current if cpu_freq else 2000.0
        except:
            cpu_freq_mhz = 2000.0  # Default assumption

        # Simple SSD detection (not perfect but good enough for local OS)
        has_ssd = True  # Assume SSD for modern systems
        try:
            # Check if any disk has high random read performance
            disk_io = psutil.disk_io_counters()
            if disk_io and disk_io.read_time > 0:
                # Very rough heuristic
                has_ssd = (disk_io.read_count / disk_io.read_time) > 100
        except:
            pass

        return cls(
            cpu_cores=cpu_info,
            cpu_threads=cpu_threads,
            memory_gb=memory_gb,
            cpu_freq_mhz=cpu_freq_mhz,
            has_ssd=has_ssd,
        )


class ResourceManager:
    """
    Hardware-aware resource management for local OS context

    Implements expert recommendations:
    - Dynamic thread pool scaling based on hardware
    - Resource pressure relief
    - Local deployment optimizations
    """

    def __init__(self, service_id: str):
        self.service_id = service_id
        self.logger = logging.getLogger(f"{__name__}.{service_id}")

        # Detect hardware capabilities
        self.hardware = HardwareInfo.detect()
        self.logger.info(f"Detected hardware: {self.hardware}")

        # Calculate optimal thread pool sizes
        self._calculate_thread_limits()

        # Thread pools for different workload types
        self._io_pool: ThreadPoolExecutor | None = None
        self._cpu_pool: ThreadPoolExecutor | None = None
        self._image_pool: ThreadPoolExecutor | None = None

        # Resource monitoring
        self._monitoring = True
        self._monitor_thread: threading.Thread | None = None
        self._resource_pressure = False

        # Rate limiting
        self._rate_limits: dict[str, Queue] = {}

        self._start_monitoring()

    def _calculate_thread_limits(self) -> None:
        """Calculate optimal thread pool sizes based on hardware"""
        # I/O bound tasks: can use more threads since they're waiting
        self.max_io_threads = min(self.hardware.cpu_threads * 2, 32)

        # CPU bound tasks: limit to actual cores to avoid context switching
        self.max_cpu_threads = self.hardware.cpu_cores

        # Image generation: memory intensive, limit based on available RAM
        # Assume ~2GB per concurrent image generation
        max_by_memory = max(1, int(self.hardware.memory_gb / 2))
        self.max_image_threads = min(max_by_memory, 4)  # Cap at 4 for stability

        self.logger.info(
            f"Thread limits - IO: {self.max_io_threads}, CPU: {self.max_cpu_threads}, Image: {self.max_image_threads}"
        )

    def get_io_pool(self) -> ThreadPoolExecutor:
        """Get thread pool for I/O bound tasks (gRPC calls, file operations)"""
        if self._io_pool is None:
            self._io_pool = ThreadPoolExecutor(
                max_workers=self.max_io_threads,
                thread_name_prefix=f"{self.service_id}-io",
            )
        return self._io_pool

    def get_cpu_pool(self) -> ThreadPoolExecutor:
        """Get thread pool for CPU bound tasks"""
        if self._cpu_pool is None:
            self._cpu_pool = ThreadPoolExecutor(
                max_workers=self.max_cpu_threads,
                thread_name_prefix=f"{self.service_id}-cpu",
            )
        return self._cpu_pool

    def get_image_pool(self) -> ThreadPoolExecutor:
        """Get thread pool for memory-intensive image generation"""
        if self._image_pool is None:
            self._image_pool = ThreadPoolExecutor(
                max_workers=self.max_image_threads,
                thread_name_prefix=f"{self.service_id}-image",
            )
        return self._image_pool

    def submit_io_task(self, func: Callable, *args, **kwargs) -> Future:
        """Submit I/O bound task with resource pressure checking"""
        if self._resource_pressure:
            # Queue task instead of running immediately
            self.logger.warning("Resource pressure detected, queueing I/O task")
            time.sleep(0.1)  # Brief backpressure

        return self.get_io_pool().submit(func, *args, **kwargs)

    def submit_cpu_task(self, func: Callable, *args, **kwargs) -> Future:
        """Submit CPU bound task with resource pressure checking"""
        if self._resource_pressure:
            self.logger.warning("Resource pressure detected, queueing CPU task")
            time.sleep(0.2)  # More backpressure for CPU tasks

        return self.get_cpu_pool().submit(func, *args, **kwargs)

    def submit_image_task(self, func: Callable, *args, **kwargs) -> Future:
        """Submit image generation task with memory pressure checking"""
        memory = psutil.virtual_memory()
        if memory.percent > 80.0:
            self.logger.warning(f"High memory usage ({memory.percent:.1f}%), delaying image generation")
            time.sleep(1.0)  # Significant backpressure for memory-intensive tasks

        return self.get_image_pool().submit(func, *args, **kwargs)

    def create_rate_limiter(self, name: str, max_per_second: float) -> None:
        """Create a rate limiter for specific operations"""
        self._rate_limits[name] = Queue(maxsize=int(max_per_second))

        # Fill the bucket initially
        for _ in range(int(max_per_second)):
            try:
                self._rate_limits[name].put_nowait(True)
            except:
                break

        # Start refill thread
        def refill():
            while self._monitoring:
                time.sleep(1.0 / max_per_second)
                with contextlib.suppress(BaseException):
                    # Bucket is full
                    self._rate_limits[name].put_nowait(True)

        thread = threading.Thread(target=refill, daemon=True)
        thread.start()

    def check_rate_limit(self, name: str, timeout: float = 0.1) -> bool:
        """Check if operation is allowed by rate limiter"""
        if name not in self._rate_limits:
            return True  # No limit configured

        try:
            self._rate_limits[name].get(timeout=timeout)
            return True
        except Empty:
            return False

    def _start_monitoring(self) -> None:
        """Start resource monitoring thread"""

        def monitor():
            while self._monitoring:
                try:
                    # Check resource pressure
                    memory = psutil.virtual_memory()
                    cpu_percent = psutil.cpu_percent(interval=1.0)

                    # Determine if we're under resource pressure
                    memory_pressure = memory.percent > 85.0
                    cpu_pressure = cpu_percent > 90.0

                    old_pressure = self._resource_pressure
                    self._resource_pressure = memory_pressure or cpu_pressure

                    if self._resource_pressure != old_pressure:
                        if self._resource_pressure:
                            self.logger.warning(
                                f"Resource pressure detected - Memory: {memory.percent:.1f}%, CPU: {cpu_percent:.1f}%"
                            )
                        else:
                            self.logger.info("Resource pressure relieved")

                    # Adjust thread pool sizes if needed
                    if memory_pressure and self._image_pool:
                        # Reduce image generation concurrency under memory pressure
                        current_workers = self._image_pool._max_workers
                        if current_workers > 1:
                            self.logger.warning("Reducing image generation concurrency due to memory pressure")
                            # Note: ThreadPoolExecutor doesn't support dynamic resizing
                            # In a production system, we'd implement a custom pool

                except Exception as e:
                    self.logger.error(f"Resource monitoring error: {e}")

                time.sleep(5.0)  # Monitor every 5 seconds

        self._monitor_thread = threading.Thread(target=monitor, daemon=True)
        self._monitor_thread.start()

    def get_resource_stats(self) -> dict[str, Any]:
        """Get current resource statistics"""
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=0.1)

        stats = {
            "hardware": {
                "cpu_cores": self.hardware.cpu_cores,
                "cpu_threads": self.hardware.cpu_threads,
                "memory_gb": self.hardware.memory_gb,
                "cpu_freq_mhz": self.hardware.cpu_freq_mhz,
                "has_ssd": self.hardware.has_ssd,
            },
            "current": {
                "memory_percent": memory.percent,
                "cpu_percent": cpu_percent,
                "resource_pressure": self._resource_pressure,
            },
            "thread_pools": {
                "io_max": self.max_io_threads,
                "cpu_max": self.max_cpu_threads,
                "image_max": self.max_image_threads,
                "io_active": getattr(self._io_pool, "_threads", 0) if self._io_pool else 0,
                "cpu_active": getattr(self._cpu_pool, "_threads", 0) if self._cpu_pool else 0,
                "image_active": getattr(self._image_pool, "_threads", 0) if self._image_pool else 0,
            },
        }

        return stats

    def shutdown(self) -> None:
        """Shutdown resource manager and thread pools"""
        self.logger.info("Shutting down resource manager")

        self._monitoring = False

        # Shutdown thread pools
        for pool in [self._io_pool, self._cpu_pool, self._image_pool]:
            if pool:
                pool.shutdown(wait=True, timeout=30)

        # Wait for monitor thread
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
