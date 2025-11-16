#!/usr/bin/env python3
"""
Service Error Types

Custom exception types for service-related errors with event integration.
Enables error handling framework to trigger automatic recovery actions.
"""

from typing import Any


class ServiceError(Exception):
    """Base exception for service-related errors."""

    def __init__(self, message: str, service_name: str = "", metadata: dict[str, Any] | None = None):
        """
        Initialize service error.

        Args:
            message: Error message
            service_name: Name of the service that failed
            metadata: Additional error context
        """
        self.message = message
        self.service_name = service_name
        self.metadata = metadata or {}
        super().__init__(self.message)


class ServiceNotRunningError(ServiceError):
    """Raised when a required service is not running.

    This error type is designed to be caught by the event framework
    and trigger automatic service startup via 'unhinged vm services up'.
    """

    def __init__(
        self,
        service_name: str,
        port: int | None = None,
        install_url: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Initialize service not running error.

        Args:
            service_name: Name of the service (e.g., "Ollama", "Vision AI")
            port: Port where service should be listening
            install_url: URL for installation instructions
            metadata: Additional context
        """
        self.service_name = service_name
        self.port = port
        self.install_url = install_url

        message = f"{service_name} service is not running"
        if port:
            message += f" (expected on port {port})"

        if install_url:
            message += f"\nInstall from: {install_url}"

        message += "\nStart with: unhinged vm services up"

        meta = metadata or {}
        meta.update(
            {
                "service": service_name,
                "port": port,
                "install_url": install_url,
                "recovery_command": "unhinged vm services up",
            }
        )

        super().__init__(message, service_name, meta)


class ServiceHealthCheckError(ServiceError):
    """Raised when a service health check fails."""

    def __init__(self, service_name: str, reason: str = "", metadata: dict[str, Any] | None = None):
        """
        Initialize health check error.

        Args:
            service_name: Name of the service
            reason: Reason for health check failure
            metadata: Additional context
        """
        message = f"{service_name} health check failed"
        if reason:
            message += f": {reason}"

        meta = metadata or {}
        meta.update({"service": service_name, "reason": reason})

        super().__init__(message, service_name, meta)


class ServiceTimeoutError(ServiceError):
    """Raised when a service operation times out."""

    def __init__(self, service_name: str, operation: str = "", timeout_seconds: int = 0):
        """
        Initialize timeout error.

        Args:
            service_name: Name of the service
            operation: Operation that timed out
            timeout_seconds: Timeout duration
        """
        message = f"{service_name} operation timed out"
        if operation:
            message += f" ({operation})"
        if timeout_seconds:
            message += f" after {timeout_seconds}s"

        meta = {
            "service": service_name,
            "operation": operation,
            "timeout_seconds": timeout_seconds,
        }

        super().__init__(message, service_name, meta)
