"""Async Zoom Phone API client with automatic auth and pagination."""

import logging
from typing import Any

import httpx

from .auth import ZoomAuth, API_BASE

logger = logging.getLogger(__name__)


class ZoomAPIError(Exception):
    """Raised when the Zoom API returns an error."""

    def __init__(self, status_code: int, message: str, details: Any = None):
        self.status_code = status_code
        self.message = message
        self.details = details
        super().__init__(f"Zoom API {status_code}: {message}")


class ZoomPhoneClient:
    """HTTP client wrapping Zoom Phone REST API calls."""

    def __init__(self, auth: ZoomAuth):
        self.auth = auth
        self._client: httpx.AsyncClient | None = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=API_BASE,
                timeout=httpx.Timeout(30.0, connect=10.0),
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            base_url=API_BASE,
            timeout=httpx.Timeout(30.0, connect=10.0),
        )
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _headers(self) -> dict[str, str]:
        token = await self.auth.get_token()
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        json: dict | None = None,
    ) -> Any:
        if not self._client:
            self._client = await self._ensure_client()

        headers = await self._headers()
        resp = await self._client.request(method, path, params=params, json=json, headers=headers)

        if resp.status_code == 401:
            # Token might be stale — force refresh and retry once
            logger.warning("Got 401, refreshing token and retrying")
            self.auth._token = None
            headers = await self._headers()
            resp = await self._client.request(method, path, params=params, json=json, headers=headers)

        if resp.status_code >= 400:
            try:
                err_data = resp.json()
                msg = err_data.get("message", resp.text)
            except Exception:
                msg = resp.text
                err_data = None
            raise ZoomAPIError(resp.status_code, msg, err_data)

        if resp.status_code == 204 or not resp.text:
            return {}

        return resp.json()

    async def get(self, path: str, params: dict | None = None) -> Any:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, json: dict | None = None, params: dict | None = None) -> Any:
        return await self._request("POST", path, params=params, json=json)

    async def patch(self, path: str, json: dict | None = None) -> Any:
        return await self._request("PATCH", path, json=json)

    async def delete(self, path: str, params: dict | None = None) -> Any:
        return await self._request("DELETE", path, params=params)

    async def get_all(self, path: str, params: dict | None = None, key: str = "data") -> list[dict]:
        """Paginate through all results using next_page_token."""
        results: list[dict] = []
        current_params = dict(params or {})
        while True:
            data = await self.get(path, params=current_params)
            page = data.get(key, [])
            results.extend(page)
            next_token = data.get("next_page_token")
            if not next_token:
                break
            current_params["next_page_token"] = next_token
        return results
