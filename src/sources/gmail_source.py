"""A Source backed by the Gmail API (read-only)."""
from __future__ import annotations

import base64
from datetime import datetime, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from ..clean import html_to_text, normalise
from .base import Item, Source

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_DIR = Path(__file__).resolve().parent.parent.parent / "credentials"
TOKEN_FILE = CREDENTIALS_DIR / "token.json"


class GmailSource(Source):
    name = "Inbox"

    def __init__(self, senders: list[str], since: datetime, max_items: int = 8):
        self.senders = senders
        self.since = since
        self.max_items = max_items

    def fetch(self) -> list[Item]:
        service = _build_service()
        query = _build_query(self.senders, self.since)
        resp = (
            service.users()
            .messages()
            .list(userId="me", q=query, maxResults=self.max_items)
            .execute()
        )
        items: list[Item] = []
        for ref in resp.get("messages", []):
            msg = (
                service.users()
                .messages()
                .get(userId="me", id=ref["id"], format="full")
                .execute()
            )
            items.append(_to_item(msg))
        return items


def _build_service():
    if not TOKEN_FILE.exists():
        raise FileNotFoundError("No token.json — run `python -m src.gmail_auth` first.")
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())          # silently get a fresh access token
        TOKEN_FILE.write_text(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def _build_query(senders: list[str], since: datetime) -> str:
    from_clause = " OR ".join(f"from:{s}" for s in senders)
    epoch = int(since.timestamp())
    return f"({from_clause}) after:{epoch}"


def _to_item(msg) -> Item:
    headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}
    return Item(
        title=headers.get("subject", "(no subject)"),
        body=_extract_body(msg["payload"]),
        source=f"Inbox: {headers.get('from', 'unknown')}",
        published=_msg_dt(msg),
    )


def _extract_body(payload) -> str:
    # Prefer the plain-text part; fall back to cleaning the HTML part.
    plain = _find_part(payload, "text/plain")
    if plain:
        return normalise(plain)
    html = _find_part(payload, "text/html")
    if html:
        return html_to_text(html)
    return ""


def _find_part(payload, mime: str) -> str | None:
    if payload.get("mimeType") == mime and payload.get("body", {}).get("data"):
        return _decode(payload["body"]["data"])
    for part in payload.get("parts", []) or []:
        found = _find_part(part, mime)
        if found:
            return found
    return None


def _decode(data: str) -> str:
    return base64.urlsafe_b64decode(data.encode("utf-8")).decode("utf-8", errors="replace")


def _msg_dt(msg) -> datetime | None:
    ms = msg.get("internalDate")
    return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc) if ms else None
