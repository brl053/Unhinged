"""Backwards-compatible connector shims for external SaaS APIs.

@llm-type library.connectors
@llm-does provide backwards-compatible shims to driver implementations

DEPRECATED: This module provides shims for legacy code that imports from
connectors. New code should use the driver registry pattern directly:

    from libs.python.drivers.google.gmail import GmailDriver
    from libs.python.drivers.social.discord import DiscordDriver

The connectors module now delegates to the drivers module, which is the
single source of truth for external service integrations.

Lazy imports to avoid requiring optional dependencies at import time.
"""

from __future__ import annotations


def __getattr__(name: str):
    """Lazy import of connector shims."""
    if name == "DiscordConnectorError":
        from .discord import DiscordConnectorError

        return DiscordConnectorError
    if name == "post_message":
        from .discord import post_message

        return post_message
    if name == "GmailConnectorError":
        from .gmail import GmailConnectorError

        return GmailConnectorError
    if name == "list_unread_messages":
        from .gmail import list_unread_messages

        return list_unread_messages
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "DiscordConnectorError",
    "GmailConnectorError",
    "list_unread_messages",
    "post_message",
]
