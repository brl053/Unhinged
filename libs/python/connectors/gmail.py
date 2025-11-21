"""Minimal Gmail connector for Unhinged (Phase 1).

Single async entrypoint to list unread messages.
No shared abstractions, no CLI/graph integration.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from google.oauth2.credentials import Credentials


_CREDENTIALS_DIR = Path.home() / ".unhinged" / "credentials"
_CLIENT_SECRET_PATH = _CREDENTIALS_DIR / "gmail.json"
_TOKEN_PATH = _CREDENTIALS_DIR / "gmail_token.json"
_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


@dataclass
class GmailConnectorError(Exception):
    """Raised when the Gmail connector encounters an error."""

    message: str
    status_code: int | None = None

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"[{self.status_code}] {self.message}" if self.status_code is not None else self.message


def _get_credentials() -> Credentials:
    """Load or obtain OAuth2 credentials for Gmail.

    May launch a local browser window for user consent on first run.
    """

    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds: Credentials | None = None
    if _TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(_TOKEN_PATH), _SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(_CLIENT_SECRET_PATH), _SCOPES)
            creds = flow.run_local_server(port=0)
        _CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
        _TOKEN_PATH.write_text(creds.to_json())

    return creds


def _list_unread_messages_sync(limit: int) -> list[dict[str, Any]]:
    service = build("gmail", "v1", credentials=_get_credentials())
    response = service.users().messages().list(userId="me", q="is:unread", maxResults=limit).execute()
    messages = response.get("messages", [])
    results: list[dict[str, Any]] = []

    for msg in messages:
        detail = (
            service.users()
            .messages()
            .get(userId="me", id=msg["id"], format="metadata", metadataHeaders=["Subject", "From"])
            .execute()
        )
        headers = {h["name"].lower(): h["value"] for h in detail.get("payload", {}).get("headers", [])}
        results.append(
            {
                "id": detail.get("id", ""),
                "subject": headers.get("subject", ""),
                "from": headers.get("from", ""),
                "snippet": detail.get("snippet", ""),
            }
        )

    return results


async def list_unread_messages(limit: int = 10) -> list[dict[str, Any]]:
    """Return up to ``limit`` unread messages from the user's Gmail inbox.

    Each message is a dict with keys: ``id``, ``subject``, ``from``, ``snippet``.
    """

    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(None, _list_unread_messages_sync, limit)
    except HttpError as exc:  # pragma: no cover - exercised via mocks
        status_obj = getattr(exc, "resp", getattr(exc, "response", None))
        status_code = getattr(status_obj, "status", None)
        raise GmailConnectorError(str(exc), status_code=status_code) from exc
