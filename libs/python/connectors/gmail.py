"""Gmail connector shim - delegates to drivers.google.gmail.

@llm-type library.connectors.gmail
@llm-does backwards-compatible shim for Gmail access

This module provides the original Phase 1 async API for backwards
compatibility. New code should use GmailDriver directly via the
driver registry pattern.

DEPRECATED: Use libs.python.drivers.google.gmail.GmailDriver instead.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from libs.python.drivers.base import DriverError

if TYPE_CHECKING:
    from libs.python.drivers.google.gmail import GmailDriver


# Backwards-compatible error alias
class GmailConnectorError(DriverError):
    """Raised when the Gmail connector encounters an error.

    DEPRECATED: Use DriverError from libs.python.drivers.base instead.
    """

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message, status_code=status_code, driver_name="google.gmail")
        self.message = message
        self.status_code = status_code


# Singleton driver instance for shim functions
_driver: GmailDriver | None = None


def _get_driver() -> GmailDriver:
    """Get or create the singleton GmailDriver instance."""
    from libs.python.drivers.google.gmail import GmailDriver

    global _driver
    if _driver is None:
        _driver = GmailDriver()
    return _driver


async def list_unread_messages(limit: int = 10) -> list[dict[str, Any]]:
    """Return up to ``limit`` unread messages from the user's Gmail inbox.

    Each message is a dict with keys: ``id``, ``subject``, ``from``, ``date``, ``snippet``.

    DEPRECATED: Use GmailDriver.execute("list_unread", {"limit": N}) instead.
    """
    driver = _get_driver()
    try:
        result = await driver.execute("list_unread", {"limit": limit})
        if result.get("success"):
            emails: list[dict[str, Any]] = result.get("data", {}).get("emails", [])
            return emails
        raise GmailConnectorError(result.get("error", "Unknown error"))
    except DriverError as exc:
        raise GmailConnectorError(str(exc), status_code=exc.status_code) from exc
