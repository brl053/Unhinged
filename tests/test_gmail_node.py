"""Tests for the GmailAPINode graph node.

@llm-type test.graph.gmail_node
@llm-does unit tests for GmailAPINode fetching behaviour
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

try:
    import libs  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover - defensive path setup
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import libs  # type: ignore[import-not-found]  # noqa: F401

from libs.python.graph import GmailAPINode


@pytest.mark.asyncio
async def test_gmail_api_node_fetches_emails_with_default_limit() -> None:
    """Node fetches emails via connector and marks success.

    The node's default configuration should request 25 messages.
    """

    sample_emails = [
        {"id": "1", "subject": "s1", "from": "a@example.com", "snippet": "x"},
        {"id": "2", "subject": "s2", "from": "b@example.com", "snippet": "y"},
    ]

    mock_list = AsyncMock(return_value=sample_emails)

    with patch("libs.python.connectors.gmail.list_unread_messages", mock_list):
        node = GmailAPINode(node_id="gmail_fetch")
        result = await node.execute()

    mock_list.assert_awaited_once_with(limit=25)
    assert result["success"] is True
    assert result["emails"] == sample_emails


@pytest.mark.asyncio
async def test_gmail_api_node_reports_connector_error() -> None:
    """Connector errors are surfaced as a failed node output."""

    from libs.python.connectors.gmail import GmailConnectorError

    mock_list = AsyncMock(side_effect=GmailConnectorError("boom", status_code=500))

    with patch("libs.python.connectors.gmail.list_unread_messages", mock_list):
        node = GmailAPINode(node_id="gmail_fail")
        result = await node.execute()

    assert result["success"] is False
    assert "boom" in result["error"]
