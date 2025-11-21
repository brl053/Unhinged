"""Discord driver for posting messages to channels.

@llm-type library.drivers.social.discord
@llm-does provide Discord API driver for posting messages
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, cast

import requests

from libs.python.drivers.base import Driver, DriverCapability, DriverError

_CREDENTIALS_DIR = Path.home() / ".unhinged" / "credentials"
_TOKEN_PATH = _CREDENTIALS_DIR / "discord_token.txt"
_API_BASE = "https://discord.com/api/v10"
_ENV_TOKEN_KEY = "UNHINGED_DISCORD_TOKEN"


class DiscordDriver(Driver):
    """Driver for Discord API operations.

    Supports:
    - post_message: Post a message to a channel
    """

    def __init__(self, driver_id: str = "social.discord") -> None:
        super().__init__(driver_id)

    def get_capabilities(self) -> list[DriverCapability]:
        """Discord driver supports WRITE operations."""
        return [DriverCapability.WRITE]

    def _load_token(self) -> str:
        """Load Discord bot token from environment or file."""
        token = os.getenv(_ENV_TOKEN_KEY)
        if token:
            return token
        if _TOKEN_PATH.exists():
            return _TOKEN_PATH.read_text(encoding="utf-8").strip()
        raise DriverError(
            f"Discord bot token not found; set {_ENV_TOKEN_KEY} or create {_TOKEN_PATH}",
            driver_name=self.driver_id,
        )

    def _post_message_sync(self, channel_id: str, content: str) -> dict[str, Any]:
        """Synchronous implementation of post_message."""
        url = f"{_API_BASE}/channels/{channel_id}/messages"
        headers = {
            "Authorization": f"Bot {self._load_token()}",
            "Content-Type": "application/json",
        }
        payload = {"content": content}

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
        except requests.RequestException as exc:  # pragma: no cover - network failure
            raise DriverError(str(exc), driver_name=self.driver_id) from exc

        if not 200 <= response.status_code < 300:
            raise DriverError(
                f"Discord API error: {response.text}",
                status_code=response.status_code,
                driver_name=self.driver_id,
            )

        return cast(dict[str, Any], response.json())

    async def execute(
        self,
        operation: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute Discord operation.

        Supported operations:
        - post_message: params={channel_id: str, content: str}
        """
        params = params or {}

        try:
            if operation == "post_message":
                channel_id = params.get("channel_id")
                content = params.get("content")

                if not channel_id or not content:
                    return {
                        "success": False,
                        "error": "Missing required params: channel_id, content",
                    }

                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, self._post_message_sync, channel_id, content)

                return {
                    "success": True,
                    "data": result,
                }
            else:
                return {
                    "success": False,
                    "error": f"Unsupported operation: {operation}",
                }
        except DriverError:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            raise DriverError(str(exc), driver_name=self.driver_id) from exc
