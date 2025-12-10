"""Discord connector shim - delegates to drivers.social.discord.

@llm-type library.connectors.discord
@llm-does backwards-compatible shim for Discord access

This module provides the original Phase 2 async API for backwards
compatibility. New code should use DiscordDriver directly via the
driver registry pattern.

DEPRECATED: Use libs.python.drivers.social.discord.DiscordDriver instead.
"""

from __future__ import annotations

from typing import Any

from libs.python.drivers.base import DriverError
from libs.python.drivers.social.discord import DiscordDriver


# Backwards-compatible error alias
class DiscordConnectorError(DriverError):
    """Raised when the Discord connector encounters an error.

    DEPRECATED: Use DriverError from libs.python.drivers.base instead.
    """

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message, status_code=status_code, driver_name="social.discord")
        self.message = message
        self.status_code = status_code


# Singleton driver instance for shim functions
_driver: DiscordDriver | None = None


def _get_driver() -> DiscordDriver:
    """Get or create the singleton DiscordDriver instance."""
    global _driver
    if _driver is None:
        _driver = DiscordDriver()
    return _driver


async def post_message(channel_id: str, content: str) -> dict[str, Any]:
    """Post ``content`` to the given Discord ``channel_id``.

    Returns the JSON response from the Discord API as a dict.

    DEPRECATED: Use DiscordDriver.execute("post_message", {...}) instead.
    """
    driver = _get_driver()
    try:
        result = await driver.execute("post_message", {"channel_id": channel_id, "content": content})
        if result.get("success"):
            data: dict[str, Any] = result.get("data", {})
            return data
        raise DiscordConnectorError(result.get("error", "Unknown error"))
    except DriverError as exc:
        raise DiscordConnectorError(str(exc), status_code=exc.status_code) from exc
