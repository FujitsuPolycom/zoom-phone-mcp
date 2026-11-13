"""Zoom Server-to-Server OAuth authentication with token caching."""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
import time

import httpx

logger = logging.getLogger(__name__)

OAUTH_URL = "https://zoom.us/oauth/token"
API_BASE = "https://api.zoom.us/v2"


def load_dotenv_if_present(dotenv_path: str | Path | None = None) -> None:
    """Load key=value pairs from a .env file into os.environ if not already set."""
    candidates = [Path(dotenv_path)] if dotenv_path else [Path.cwd() / ".env"]
    for path in candidates:
        if not path.is_file():
            continue
        try:
            for raw_line in path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                    value = value[1:-1]
                if key and key not in os.environ:
                    os.environ[key] = value
        except OSError as exc:
            logger.debug("Could not read .env file %s: %s", path, exc)


class ZoomAuth:
    """Manages Zoom S2S OAuth tokens with automatic refresh."""

    def __init__(
        self,
        account_id: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ):
        load_dotenv_if_present()
        self.account_id = account_id or os.environ.get("ZOOM_ACCOUNT_ID", "")
        self.client_id = client_id or os.environ.get("ZOOM_CLIENT_ID", "")
        self.client_secret = client_secret or os.environ.get("ZOOM_CLIENT_SECRET", "")

        if not all([self.account_id, self.client_id, self.client_secret]):
            raise ValueError(
                "Missing Zoom OAuth credentials. Set ZOOM_ACCOUNT_ID, "
                "ZOOM_CLIENT_ID, and ZOOM_CLIENT_SECRET environment variables."
            )

        self._token: str | None = None
        self._expires_at: float = 0
        self._lock = asyncio.Lock()

    @property
    def is_valid(self) -> bool:
        return self._token is not None and time.time() < self._expires_at - 60

    def invalidate(self) -> None:
        """Mark the cached token as invalid so the next get_token() refreshes it."""
        self._token = None
        self._expires_at = 0

    async def get_token(self) -> str:
        """Return a valid access token, fetching/refreshing as needed."""
        if self.is_valid:
            assert self._token is not None
            return self._token

        async with self._lock:
            # Double-check after acquiring lock
            if self.is_valid:
                assert self._token is not None
                return self._token
            await self._fetch_token()
            assert self._token is not None
            return self._token

    async def _fetch_token(self) -> None:
        """Fetch a new access token from Zoom OAuth."""
        timeout = httpx.Timeout(15.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                OAUTH_URL,
                params={
                    "grant_type": "account_credentials",
                    "account_id": self.account_id,
                },
                auth=(self.client_id, self.client_secret),
            )
            if resp.status_code != 200:
                raise RuntimeError(
                    f"Zoom OAuth failed ({resp.status_code}): {resp.text}"
                )
            data = resp.json()
            self._token = data["access_token"]
            expires_in = int(data.get("expires_in", 3600))
            self._expires_at = time.time() + expires_in
            logger.info("Zoom OAuth token refreshed, expires in %ds", expires_in)

