"""Driver framework for external service integrations.

@llm-type library.drivers
@llm-does provide driver registry and base abstractions for external API integrations

Drivers are service-specific adapters that encapsulate:
- Authentication and credential management
- API endpoint behaviors and protocols
- Request/response transformations
- Error handling and retry logic

Each driver lives in its own namespace (e.g., drivers/google/gmail, drivers/meta/threads)
and exposes a consistent async interface for graph node consumption.
"""

from __future__ import annotations

from .base import Driver, DriverCapability, DriverError, DriverRegistry

__all__ = [
    "Driver",
    "DriverCapability",
    "DriverError",
    "DriverRegistry",
]
