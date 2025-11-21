"""Gmail driver for Google Workspace email operations.

@llm-type library.drivers.google.gmail
@llm-does provide Gmail API driver for reading and sending emails
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from libs.python.drivers.base import Driver, DriverCapability, DriverError

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from google.oauth2.credentials import Credentials


_CREDENTIALS_DIR = Path.home() / ".unhinged" / "credentials"
_CLIENT_SECRET_PATH = _CREDENTIALS_DIR / "gmail.json"
_TOKEN_PATH = _CREDENTIALS_DIR / "gmail_token.json"
_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailDriver(Driver):
    """Driver for Gmail API operations.

    Supports:
    - list_unread: Fetch unread messages
    - list_messages: Fetch messages with query
    - get_message: Fetch single message by ID
    """

    def __init__(self, driver_id: str = "google.gmail") -> None:
        super().__init__(driver_id)
        self._credentials: Credentials | None = None

    def get_capabilities(self) -> list[DriverCapability]:
        """Gmail driver supports READ operations."""
        return [DriverCapability.READ]

    def _get_credentials(self) -> Credentials:
        """Load or obtain OAuth2 credentials for Gmail."""
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow

        if self._credentials is not None and self._credentials.valid:
            return self._credentials

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

        self._credentials = creds
        return creds

    def _list_unread_messages_sync(self, limit: int) -> list[dict[str, Any]]:
        """Synchronous implementation of list_unread."""
        service = build("gmail", "v1", credentials=self._get_credentials())
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

    async def execute(
        self,
        operation: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute Gmail operation.

        Supported operations:
        - list_unread: params={limit: int}
        """
        params = params or {}

        try:
            if operation == "list_unread":
                limit = params.get("limit", 25)
                loop = asyncio.get_running_loop()
                emails = await loop.run_in_executor(None, self._list_unread_messages_sync, limit)
                return {
                    "success": True,
                    "data": {"emails": emails},
                }
            else:
                return {
                    "success": False,
                    "error": f"Unsupported operation: {operation}",
                }
        except HttpError as exc:  # pragma: no cover - exercised via mocks
            status_obj = getattr(exc, "resp", getattr(exc, "response", None))
            status_code = getattr(status_obj, "status", None)
            raise DriverError(str(exc), status_code=status_code, driver_name=self.driver_id) from exc
        except Exception as exc:  # pragma: no cover - defensive
            raise DriverError(str(exc), driver_name=self.driver_id) from exc
