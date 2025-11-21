"""Tests for the Gmail driver.

@llm-type test.drivers.gmail
@llm-does unit tests for GmailDriver operations
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
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
from libs.python.drivers.google.gmail import GmailDriver


@pytest.mark.asyncio
async def test_gmail_driver_list_unread_operation() -> None:
    """GmailDriver executes list_unread and returns emails."""
    sample_emails = [
        {"id": "1", "subject": "Test 1", "from": "a@example.com", "snippet": "x"},
        {"id": "2", "subject": "Test 2", "from": "b@example.com", "snippet": "y"},
    ]

    driver = GmailDriver()

    # Mock the sync method
    with patch.object(driver, "_list_unread_messages_sync", return_value=sample_emails):
        result = await driver.execute("list_unread", {"limit": 10})

    assert result["success"] is True
    assert result["data"]["emails"] == sample_emails


@pytest.mark.asyncio
async def test_gmail_driver_unsupported_operation() -> None:
    """GmailDriver returns error for unsupported operations."""
    driver = GmailDriver()

    result = await driver.execute("unsupported_op", {})

    assert result["success"] is False
    assert "Unsupported operation" in result["error"]


@pytest.mark.asyncio
async def test_gmail_driver_http_error_raises_driver_error() -> None:
    """GmailDriver wraps HttpError in DriverError."""
    from googleapiclient.errors import HttpError

    driver = GmailDriver()

    # Create mock HttpError
    mock_response = MagicMock()
    mock_response.status = 403
    mock_error = HttpError(resp=mock_response, content=b"Forbidden")

    with (
        patch.object(driver, "_list_unread_messages_sync", side_effect=mock_error),
        pytest.raises(DriverError) as excinfo,
    ):
        await driver.execute("list_unread", {"limit": 5})

    err = excinfo.value
    assert err.driver_name == "google.gmail"
    assert err.status_code == 403


def test_gmail_driver_capabilities() -> None:
    """GmailDriver reports READ capability."""
    driver = GmailDriver()
    capabilities = driver.get_capabilities()

    assert DriverCapability.READ in capabilities
    assert DriverCapability.WRITE not in capabilities
