"""Google service drivers.

@llm-type library.drivers.google
@llm-does provide drivers for Google Workspace services (Gmail, etc.)
"""

from __future__ import annotations

from .gmail import GmailDriver

__all__ = ["GmailDriver"]
