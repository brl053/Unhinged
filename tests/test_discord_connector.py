"""Tests for the Discord connector shim.

All network and credential access is mocked; no real Discord calls occur.
The connector shim now delegates to DiscordDriver, so we patch at the driver level.
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from libs.python.connectors.discord import DiscordConnectorError, post_message

# Patch location is where requests is used: the driver module
_PATCH_REQUESTS = "libs.python.drivers.social.discord.requests.post"


@pytest.mark.asyncio
async def test_post_message_happy_path() -> None:
    """Connector posts message and returns parsed JSON on success."""

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "msg-1", "content": "hello"}

    with (
        patch(_PATCH_REQUESTS, return_value=mock_response) as mock_post,
        patch.dict(os.environ, {"UNHINGED_DISCORD_TOKEN": "test-token"}, clear=False),
    ):
        # Reset singleton driver to pick up fresh mock
        import libs.python.connectors.discord as discord_connector

        discord_connector._driver = None

        result = await post_message("channel-123", "hello")

    mock_post.assert_called_once()
    args, _kwargs = mock_post.call_args
    assert "/channels/channel-123/messages" in args[0]
    assert result == {"id": "msg-1", "content": "hello"}


@pytest.mark.asyncio
async def test_post_message_api_error_raises_custom_error() -> None:
    """Non-2xx responses are wrapped in DiscordConnectorError."""

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"

    with (
        patch(_PATCH_REQUESTS, return_value=mock_response),
        patch.dict(os.environ, {"UNHINGED_DISCORD_TOKEN": "test-token"}, clear=False),
        pytest.raises(DiscordConnectorError) as excinfo,
    ):
        # Reset singleton driver to pick up fresh mock
        import libs.python.connectors.discord as discord_connector

        discord_connector._driver = None

        await post_message("channel-123", "hello")

    err = excinfo.value
    assert isinstance(err, DiscordConnectorError)
    assert err.status_code == 401
    assert "Unauthorized" in str(err)
