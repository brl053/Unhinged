"""Minimal Discord connector for Unhinged (Phase 2).

Single async capability to post a message to a channel.
No shared abstractions, no CLI/graph integration.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

_CREDENTIALS_DIR = Path.home() / ".unhinged" / "credentials"
_TOKEN_PATH = _CREDENTIALS_DIR / "discord_token.txt"
_API_BASE = "https://discord.com/api/v10"
_ENV_TOKEN_KEY = "UNHINGED_DISCORD_TOKEN"


@dataclass
class DiscordConnectorError(Exception):
    """Raised when the Discord connector encounters an error."""

    message: str
    status_code: int | None = None

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"[{self.status_code}] {self.message}" if self.status_code is not None else self.message


def _load_token() -> str:
    token = os.getenv(_ENV_TOKEN_KEY)
    if token:
        return token
    if _TOKEN_PATH.exists():
        return _TOKEN_PATH.read_text(encoding="utf-8").strip()
    raise DiscordConnectorError(
        f"Discord bot token not found; set {_ENV_TOKEN_KEY} or create {_TOKEN_PATH}",
    )


def _post_message_sync(channel_id: str, content: str) -> dict[str, Any]:
    url = f"{_API_BASE}/channels/{channel_id}/messages"
    headers = {
        "Authorization": f"Bot {_load_token()}",
        "Content-Type": "application/json",
    }
    payload = {"content": content}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
    except requests.RequestException as exc:  # pragma: no cover - network failure path
        raise DiscordConnectorError(str(exc)) from exc

    if not 200 <= response.status_code < 300:
        raise DiscordConnectorError(f"Discord API error: {response.text}", status_code=response.status_code)

    return response.json()  # type: ignore[no-any-return]


async def post_message(channel_id: str, content: str) -> dict[str, Any]:
    """Post ``content`` to the given Discord ``channel_id``.

    Returns the JSON response from the Discord API as a dict.
    """

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _post_message_sync, channel_id, content)
