"""Base driver abstractions and registry.

@llm-type library.drivers.base
@llm-does define Driver ABC and DriverRegistry for service integration
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class DriverCapability(Enum):
    """Capabilities that drivers can expose."""

    READ = "read"  # Fetch/list data
    WRITE = "write"  # Create/update data
    DELETE = "delete"  # Delete data
    STREAM = "stream"  # Streaming operations


@dataclass
class DriverError(Exception):
    """Base error for all driver operations."""

    message: str
    status_code: int | None = None
    driver_name: str | None = None

    def __str__(self) -> str:
        prefix = f"[{self.driver_name}]" if self.driver_name else ""
        suffix = f" ({self.status_code})" if self.status_code is not None else ""
        return f"{prefix} {self.message}{suffix}".strip()


class Driver(ABC):
    """Abstract base for all external service drivers.

    Drivers encapsulate service-specific authentication, endpoints, and protocols.
    Each driver exposes one or more capabilities (READ, WRITE, DELETE, STREAM).
    """

    def __init__(self, driver_id: str) -> None:
        self.driver_id = driver_id

    @abstractmethod
    def get_capabilities(self) -> list[DriverCapability]:
        """Return list of capabilities this driver supports."""

    @abstractmethod
    async def execute(
        self,
        operation: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a driver operation.

        Args:
            operation: Operation name (e.g., "list_messages", "post_update")
            params: Operation-specific parameters

        Returns:
            Operation result as a dictionary with at least:
            - success: bool
            - data: operation-specific payload (optional)
            - error: error message if success=False (optional)
        """


class DriverRegistry:
    """Global registry for driver instances.

    Drivers are registered by namespace (e.g., "google.gmail", "meta.threads")
    and can be retrieved for use by APINode instances.
    """

    def __init__(self) -> None:
        self._drivers: dict[str, Driver] = {}

    def register(self, namespace: str, driver: Driver) -> None:
        """Register a driver under a namespace.

        Args:
            namespace: Dot-separated namespace (e.g., "google.gmail")
            driver: Driver instance
        """
        if namespace in self._drivers:
            raise ValueError(f"Driver already registered: {namespace}")
        self._drivers[namespace] = driver

    def get(self, namespace: str) -> Driver:
        """Retrieve a driver by namespace.

        Args:
            namespace: Dot-separated namespace

        Returns:
            Driver instance

        Raises:
            KeyError: If namespace not registered
        """
        if namespace not in self._drivers:
            raise KeyError(f"Driver not found: {namespace}")
        return self._drivers[namespace]

    def list_namespaces(self) -> list[str]:
        """Return all registered driver namespaces."""
        return list(self._drivers.keys())

    def has(self, namespace: str) -> bool:
        """Check if a driver is registered."""
        return namespace in self._drivers


# Global singleton registry
_global_registry: DriverRegistry | None = None


def get_global_registry() -> DriverRegistry:
    """Get or create the global driver registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = DriverRegistry()
    return _global_registry
