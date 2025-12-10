"""Google service drivers.

@llm-type library.drivers.google
@llm-does provide drivers for Google Workspace services (Gmail, etc.)

Lazy imports to avoid requiring google-api-python-client at import time.
"""

from __future__ import annotations


def __getattr__(name: str):
    """Lazy import of Google drivers."""
    if name == "GmailDriver":
        from .gmail import GmailDriver

        return GmailDriver
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["GmailDriver"]
