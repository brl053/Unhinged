"""Social media platform drivers.

@llm-type library.drivers.social
@llm-does provide drivers for social media platforms (Discord, LinkedIn, Meta Threads, etc.)
"""

from __future__ import annotations

from .discord import DiscordDriver

__all__ = ["DiscordDriver"]
