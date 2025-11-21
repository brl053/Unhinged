"""Tests for the Discord driver.

@llm-type test.drivers.discord
@llm-does unit tests for DiscordDriver operations
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

try:
    import libs  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover - defensive path setup
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import libs  # type: ignore[import-not-found]  # noqa: F401

from libs.python.drivers.base import DriverCapability, DriverError
from libs.python.drivers.social.discord import DiscordDriver


@pytest.mark.asyncio
async def test_discord_driver_post_message_operation() -> None:
    """DiscordDriver executes post_message and returns API response."""
    driver = DiscordDriver()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "msg-123", "content": "Hello"}

    with (
        patch("libs.python.drivers.social.discord.requests.post", return_value=mock_response),
        patch.dict(os.environ, {"UNHINGED_DISCORD_TOKEN": "test-token"}, clear=False),
    ):
        result = await driver.execute(
            "post_message",
            {"channel_id": "channel-456", "content": "Hello"},
        )

    assert result["success"] is True
    assert result["data"]["id"] == "msg-123"


@pytest.mark.asyncio
async def test_discord_driver_missing_params() -> None:
    """DiscordDriver returns error when required params missing."""
    driver = DiscordDriver()

    result = await driver.execute("post_message", {"channel_id": "123"})

    assert result["success"] is False
    assert "Missing required params" in result["error"]


@pytest.mark.asyncio
async def test_discord_driver_unsupported_operation() -> None:
    """DiscordDriver returns error for unsupported operations."""
    driver = DiscordDriver()

    result = await driver.execute("unsupported_op", {})

    assert result["success"] is False
    assert "Unsupported operation" in result["error"]


@pytest.mark.asyncio
async def test_discord_driver_api_error_raises_driver_error() -> None:
    """DiscordDriver wraps API errors in DriverError."""
    driver = DiscordDriver()

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"

    with (
        patch("libs.python.drivers.social.discord.requests.post", return_value=mock_response),
        patch.dict(os.environ, {"UNHINGED_DISCORD_TOKEN": "test-token"}, clear=False),
        pytest.raises(DriverError) as excinfo,
    ):
        await driver.execute(
            "post_message",
            {"channel_id": "channel-456", "content": "Hello"},
        )

    err = excinfo.value
    assert err.driver_name == "social.discord"
    assert err.status_code == 401


def test_discord_driver_capabilities() -> None:
    """DiscordDriver reports WRITE capability."""
    driver = DiscordDriver()
    capabilities = driver.get_capabilities()

    assert DriverCapability.WRITE in capabilities
    assert DriverCapability.READ not in capabilities
