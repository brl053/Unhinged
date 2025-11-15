"""
Health Management for Python Services

Provides health monitoring, dependency tracking, and resource metrics
optimized for local OS deployment context.
"""

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import psutil


class HealthStatus(Enum):
    """Health status enumeration matching protobuf definition"""

    UNKNOWN = "UNKNOWN"
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    MAINTENANCE = "MAINTENANCE"


@dataclass
class HealthCheckResult:
    """Result of a health check operation"""

    healthy: bool
    message: str
    response_time_ms: float
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class DependencyCheckResult:
    """Result of a dependency health check"""

    name: str
    type: str
    endpoint: str
    healthy: bool
    response_time_ms: float
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceMetrics:
    """System resource metrics for local OS context"""

    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_percent: float
    load_average: list[float]
    thread_count: int
    process_count: int


class HealthManager:
    """
    Health management for Python services

    Optimized for local OS deployment - focuses on resource monitoring
    rather than distributed systems concerns.
    """

    def __init__(self, service_id: str, version: str):
        self.service_id = service_id
        self.version = version
        self.start_time = time.time()

        # Health state
        self._status = HealthStatus.UNKNOWN
        self._status_lock = threading.RLock()

        # Health checks and dependencies
        self._health_checks: dict[str, Callable[[], HealthCheckResult]] = {}
        self._dependencies: dict[str, Callable[[], DependencyCheckResult]] = {}

        # Metrics collection
        self._last_metrics: ResourceMetrics | None = None
        self._metrics_lock = threading.RLock()

        # Register default health checks
        self._register_default_checks()

    def update_status(self, status: HealthStatus) -> None:
        """Update service health status"""
        with self._status_lock:
            self._status = status

    def get_status(self) -> HealthStatus:
        """Get current health status"""
        with self._status_lock:
            return self._status

    def register_health_check(
        self, name: str, check_func: Callable[[], HealthCheckResult]
    ) -> None:
        """Register a custom health check"""
        self._health_checks[name] = check_func

    def register_dependency(
        self,
        name: str,
        type_: str,
        endpoint: str,
        check_func: Callable[[], DependencyCheckResult],
    ) -> None:
        """Register a dependency for monitoring"""
        self._dependencies[name] = check_func

    def get_heartbeat(self) -> dict[str, Any]:
        """Get fast heartbeat response (< 10ms target)"""
        uptime_ms = int((time.time() - self.start_time) * 1000)

        return {
            "alive": True,
            "timestamp_ms": int(time.time() * 1000),
            "service_id": self.service_id,
            "version": self.version,
            "uptime_ms": uptime_ms,
            "status": self._status.value,
        }

    def get_diagnostics(
        self,
        include_metrics: bool = True,
        include_dependencies: bool = True,
        include_custom_checks: bool = True,
    ) -> dict[str, Any]:
        """Get detailed diagnostics"""
        diagnostics = {
            "heartbeat": self.get_heartbeat(),
            "last_updated": datetime.now(UTC).isoformat(),
        }

        if include_metrics:
            diagnostics["resources"] = self._collect_resource_metrics()

        if include_dependencies:
            diagnostics["dependencies"] = self._check_dependencies()

        if include_custom_checks:
            diagnostics["custom_checks"] = self._run_health_checks()

        return diagnostics

    def _register_default_checks(self) -> None:
        """Register default health checks for local OS context"""

        def memory_check() -> HealthCheckResult:
            """Check memory usage - critical for local deployment"""
            start_time = time.time()
            memory = psutil.virtual_memory()
            response_time = (time.time() - start_time) * 1000

            # Local OS context: be more aggressive about memory limits
            healthy = memory.percent < 85.0

            return HealthCheckResult(
                healthy=healthy,
                message=f"Memory usage: {memory.percent:.1f}%",
                response_time_ms=response_time,
                details={
                    "percent": memory.percent,
                    "used_mb": memory.used / (1024 * 1024),
                    "total_mb": memory.total / (1024 * 1024),
                    "available_mb": memory.available / (1024 * 1024),
                },
            )

        def cpu_check() -> HealthCheckResult:
            """Check CPU usage"""
            start_time = time.time()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            response_time = (time.time() - start_time) * 1000

            # Local OS: allow higher CPU usage since we control the workload
            healthy = cpu_percent < 90.0

            return HealthCheckResult(
                healthy=healthy,
                message=f"CPU usage: {cpu_percent:.1f}%",
                response_time_ms=response_time,
                details={
                    "percent": cpu_percent,
                    "core_count": psutil.cpu_count(),
                    "load_avg": list(psutil.getloadavg())
                    if hasattr(psutil, "getloadavg")
                    else [],
                },
            )

        def disk_check() -> HealthCheckResult:
            """Check disk usage"""
            start_time = time.time()
            disk = psutil.disk_usage("/")
            response_time = (time.time() - start_time) * 1000

            disk_percent = (disk.used / disk.total) * 100
            healthy = disk_percent < 90.0

            return HealthCheckResult(
                healthy=healthy,
                message=f"Disk usage: {disk_percent:.1f}%",
                response_time_ms=response_time,
                details={
                    "percent": disk_percent,
                    "used_gb": disk.used / (1024**3),
                    "total_gb": disk.total / (1024**3),
                    "free_gb": disk.free / (1024**3),
                },
            )

        self.register_health_check("memory", memory_check)
        self.register_health_check("cpu", cpu_check)
        self.register_health_check("disk", disk_check)

    def _collect_resource_metrics(self) -> dict[str, Any]:
        """Collect system resource metrics"""
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            disk = psutil.disk_usage("/")

            metrics = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": memory.used / (1024 * 1024),
                "memory_total_mb": memory.total / (1024 * 1024),
                "disk_percent": (disk.used / disk.total) * 100,
                "thread_count": threading.active_count(),
                "process_count": len(psutil.pids()),
            }

            # Add load average if available (Unix systems)
            if hasattr(psutil, "getloadavg"):
                metrics["load_average"] = list(psutil.getloadavg())

            with self._metrics_lock:
                self._last_metrics = metrics

            return metrics

        except Exception as e:
            return {"error": f"Failed to collect metrics: {e}"}

    def _check_dependencies(self) -> list[dict[str, Any]]:
        """Check all registered dependencies"""
        results = []
        for name, check_func in self._dependencies.items():
            try:
                result = check_func()
                results.append(
                    {
                        "name": result.name,
                        "type": result.type,
                        "endpoint": result.endpoint,
                        "healthy": result.healthy,
                        "response_time_ms": result.response_time_ms,
                        "message": result.message,
                        "details": result.details,
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "name": name,
                        "healthy": False,
                        "message": f"Check failed: {e}",
                        "response_time_ms": 0,
                    }
                )
        return results

    def _run_health_checks(self) -> list[dict[str, Any]]:
        """Run all registered health checks"""
        results = []
        for name, check_func in self._health_checks.items():
            try:
                result = check_func()
                results.append(
                    {
                        "name": name,
                        "healthy": result.healthy,
                        "message": result.message,
                        "response_time_ms": result.response_time_ms,
                        "details": result.details,
                        "timestamp": result.timestamp.isoformat(),
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "name": name,
                        "healthy": False,
                        "message": f"Check failed: {e}",
                        "response_time_ms": 0,
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                )
        return results

    def get_last_metrics(self) -> dict[str, Any] | None:
        """Get last collected resource metrics"""
        with self._metrics_lock:
            return self._last_metrics.copy() if self._last_metrics else None
