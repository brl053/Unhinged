"""Tests for the Gmail connector shim.

These tests are headless and rely on mocking the Google API client
rather than performing real network calls or OAuth flows.
The connector shim now delegates to GmailDriver, so we patch at the driver level.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from libs.python.connectors.gmail import GmailConnectorError, list_unread_messages

# Patch locations are where google APIs are used: the driver module
_PATCH_BUILD = "libs.python.drivers.google.gmail.build"
_PATCH_CREDS = "libs.python.drivers.google.gmail.GmailDriver._get_credentials"


def _reset_driver_singleton() -> None:
    """Reset singleton driver to pick up fresh mocks."""
    import libs.python.connectors.gmail as gmail_connector

    gmail_connector._driver = None


@pytest.mark.asyncio
async def test_list_unread_messages_happy_path() -> None:
    """Connector returns normalized message structures on success."""

    mock_service = MagicMock()
    mock_users = mock_service.users.return_value
    mock_messages = mock_users.messages.return_value

    mock_messages.list.return_value.execute.return_value = {
        "messages": [{"id": "1"}, {"id": "2"}],
    }

    def _make_get_response(message_id: str) -> dict[str, Any]:
        return {
            "id": message_id,
            "snippet": f"snippet-{message_id}",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": f"Subject {message_id}"},
                    {"name": "From", "value": f"sender-{message_id}@example.com"},
                    {"name": "Date", "value": "2024-01-01"},
                ]
            },
        }

    mock_messages.get.side_effect = lambda userId, id, format, metadataHeaders: MagicMock(  # noqa: N803
        execute=lambda: _make_get_response(id)
    )

    with (
        patch(_PATCH_BUILD, return_value=mock_service),
        patch(_PATCH_CREDS),
    ):
        _reset_driver_singleton()
        messages = await list_unread_messages(limit=2)

    # Driver now returns 'date' field too
    assert len(messages) == 2
    assert messages[0]["id"] == "1"
    assert messages[0]["subject"] == "Subject 1"
    assert messages[0]["from"] == "sender-1@example.com"
    assert messages[1]["id"] == "2"


@pytest.mark.asyncio
async def test_list_unread_messages_auth_failure_raises_custom_error() -> None:
    """HTTP errors from the Gmail API are wrapped in GmailConnectorError."""

    # Create a mock exception that looks like HttpError
    class MockHttpError(Exception):
        def __init__(self):
            self.resp = MagicMock()
            self.resp.status = 401
            super().__init__("Unauthorized")

    mock_error = MockHttpError()

    with patch(_PATCH_BUILD) as mock_build:
        mock_service = MagicMock()
        mock_service.users.return_value.messages.return_value.list.side_effect = mock_error
        mock_build.return_value = mock_service

        with patch(_PATCH_CREDS):
            _reset_driver_singleton()
            with pytest.raises(GmailConnectorError) as excinfo:
                await list_unread_messages(limit=1)

    err = excinfo.value
    assert isinstance(err, GmailConnectorError)
