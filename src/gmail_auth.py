"""
One-time Gmail OAuth setup: mints a READ-ONLY refresh token.

Run this once locally:  python -m src.gmail_auth

It opens a browser, you grant read-only access (clicking through the
"unverified app" warning once), and it saves your credentials to
credentials/token.json. After that, GmailSource reuses that token
silently and refreshes the short-lived access token as needed.
"""
from __future__ import annotations

from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

# Read-only: this token can read mail but never send, modify, or delete.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

CREDENTIALS_DIR = Path(__file__).resolve().parent.parent / "credentials"
CLIENT_SECRETS = CREDENTIALS_DIR / "client.json"  # the OAuth client you downloaded
TOKEN_FILE = CREDENTIALS_DIR / "token.json"        # where the refresh token is saved


def mint_token() -> None:
    if not CLIENT_SECRETS.exists():
        raise FileNotFoundError(
            f"Put your downloaded OAuth client JSON at: {CLIENT_SECRETS}"
        )
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS), SCOPES)
    # Opens your browser and runs a tiny local server to catch the redirect.
    creds = flow.run_local_server(port=0)
    TOKEN_FILE.write_text(creds.to_json())
    print(f"Saved credentials to {TOKEN_FILE}")
    print("Refresh token present:", bool(creds.refresh_token))


if __name__ == "__main__":
    mint_token()
