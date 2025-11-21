"""Tests for the minimal Gmail connector.

These tests are headless and rely on mocking the Google API client
rather than performing real network calls or OAuth flows.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from libs.python.connectors.gmail import GmailConnectorError, list_unread_messages


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
                ]
            },
        }

    mock_messages.get.side_effect = lambda userId, id, format, metadataHeaders: MagicMock(
        execute=lambda: _make_get_response(id)
    )

    with patch("libs.python.connectors.gmail.build", return_value=mock_service), patch(
        "libs.python.connectors.gmail._get_credentials"
    ):
        messages = await list_unread_messages(limit=2)

    assert messages == [
        {
            "id": "1",
            "subject": "Subject 1",
            "from": "sender-1@example.com",
            "snippet": "snippet-1",
        },
        {
            "id": "2",
            "subject": "Subject 2",
            "from": "sender-2@example.com",
            "snippet": "snippet-2",
        },
    ]


@pytest.mark.asyncio
async def test_list_unread_messages_auth_failure_raises_custom_error() -> None:
    """HTTP errors from the Gmail API are wrapped in GmailConnectorError."""

    from googleapiclient.errors import HttpError

    class DummyResponse:
        status = 401

    http_error = HttpError(resp=DummyResponse(), content=b"Unauthorized")

    with patch("libs.python.connectors.gmail._list_unread_messages_sync", side_effect=http_error):
        with pytest.raises(GmailConnectorError) as excinfo:
            await list_unread_messages(limit=1)

    err = excinfo.value
    assert isinstance(err, GmailConnectorError)
    assert err.status_code == 401
    assert "Unauthorized" in str(err)
