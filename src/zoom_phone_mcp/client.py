"""Async Zoom Phone API client with automatic auth, rate-limit retry, and pagination."""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any
from urllib.parse import quote

import httpx

from .auth import API_BASE, ZoomAuth

logger = logging.getLogger(__name__)

_WRITE_METHODS = frozenset({"POST", "PATCH", "PUT", "DELETE"})
_RETRYABLE_STATUS_CODES = frozenset({429, 502, 503, 504})


def is_read_only_env() -> bool:
    """Return True if ZOOM_PHONE_MCP_READ_ONLY is enabled in the environment."""
    val = os.environ.get("ZOOM_PHONE_MCP_READ_ONLY", "").strip().lower()
    return val in {"1", "true", "yes", "on"}


def encode_path_segment(segment: str) -> str:
    """URL-encode a single path parameter segment safely."""
    return quote(str(segment), safe="")


def normalize_phone_numbers(
    phone_numbers: str | dict[str, Any] | list[str | dict[str, Any]],
) -> list[dict[str, str]]:
    """Normalize phone numbers into Zoom API's [{'id': ...} | {'number': ...}] format.

    Accepts:
        - A single phone number string (E.164 like '+12058945717' or a Zoom phone_number_id)
        - A single dict ({'id': ...} and/or {'number': ...})
        - A list of strings or dicts
    """
    items = [phone_numbers] if isinstance(phone_numbers, (str, dict)) else list(phone_numbers)
    normalized: list[dict[str, str]] = []
    for item in items:
        if isinstance(item, dict):
            normalized.append(item)
        elif isinstance(item, str):
            val = item.strip()
            # E.164 numbers start with '+' or consist purely of digits/formatting
            cleaned = val.lstrip("+").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
            if val.startswith("+") or (cleaned.isdigit() and len(cleaned) >= 7):
                normalized.append({"number": val})
            else:
                normalized.append({"id": val})
        else:
            raise ValueError(f"Invalid phone number entry: {item!r}")
    return normalized


def normalize_members_payload(
    members: list[str | dict[str, Any]] | dict[str, Any] | None = None,
    common_area_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Normalize call queue / shared line group member additions into Zoom API schema.

    Zoom Phone API expects:
        {"members": {"users": [{"id": "..."} or {"email": "..."}], "common_area_ids": ["..."]}}
    """
    if isinstance(members, dict):
        # Caller already passed the inner {"users": ..., "common_area_ids": ...} or {"members": ...}
        inner = dict(members.get("members", members))
        if common_area_ids is not None:
            inner["common_area_ids"] = common_area_ids
        return {"members": inner}

    inner_members: dict[str, Any] = {}
    if members:
        users: list[dict[str, Any]] = []
        for entry in members:
            if isinstance(entry, dict):
                users.append(entry)
            elif isinstance(entry, str):
                val = entry.strip()
                if "@" in val:
                    users.append({"email": val})
                else:
                    users.append({"id": val})
            else:
                raise ValueError(f"Invalid member entry: {entry!r}")
        if users:
            inner_members["users"] = users

    if common_area_ids:
        inner_members["common_area_ids"] = list(common_area_ids)

    return {"members": inner_members}


class ZoomAPIError(Exception):
    """Raised when the Zoom API returns an error."""

    def __init__(self, status_code: int, message: str, details: Any = None):
        self.status_code = status_code
        self.message = message
        self.details = details
        super().__init__(f"Zoom API {status_code}: {message}")


class ZoomPhoneClient:
    """HTTP client wrapping Zoom Phone REST API calls."""

    def __init__(
        self,
        auth: ZoomAuth,
        *,
        read_only: bool | None = None,
        max_retries: int = 3,
        retry_base_delay: float = 0.5,
    ):
        self.auth = auth
        self._read_only = read_only
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay
        self._client: httpx.AsyncClient | None = None

    @property
    def read_only(self) -> bool:
        if self._read_only is not None:
            return self._read_only
        return is_read_only_env()

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=API_BASE,
                timeout=httpx.Timeout(30.0, connect=10.0),
            )
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> ZoomPhoneClient:
        await self._ensure_client()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def _headers(self) -> dict[str, str]:
        token = await self.auth.get_token()
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def _retry_delay(self, attempt: int, resp: httpx.Response | None = None) -> float:
        if resp is not None:
            retry_after = resp.headers.get("Retry-After")
            if retry_after:
                try:
                    return min(float(retry_after), 30.0)
                except ValueError:
                    pass
        return min(self.retry_base_delay * (2**attempt), 15.0)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        upper_method = method.upper()
        if self.read_only and upper_method in _WRITE_METHODS:
            raise ZoomAPIError(
                403,
                f"Write operation ({upper_method} {path}) blocked: server is running in read-only mode "
                "(ZOOM_PHONE_MCP_READ_ONLY=true).",
            )

        client = await self._ensure_client()

        for attempt in range(self.max_retries + 1):
            headers = await self._headers()
            try:
                resp = await client.request(
                    upper_method, path, params=params, json=json, headers=headers
                )
            except httpx.TransportError as exc:
                if attempt < self.max_retries:
                    delay = self._retry_delay(attempt)
                    logger.warning(
                        "Transport error on %s %s (%s), retrying in %.2fs (attempt %d/%d)",
                        upper_method,
                        path,
                        exc,
                        delay,
                        attempt + 1,
                        self.max_retries,
                    )
                    await asyncio.sleep(delay)
                    continue
                raise ZoomAPIError(503, f"Network transport error: {exc}") from exc

            if resp.status_code == 401:
                # Token might be stale — force refresh and retry once
                logger.warning("Got 401 on %s %s, refreshing token and retrying", upper_method, path)
                self.auth.invalidate()
                headers = await self._headers()
                resp = await client.request(
                    upper_method, path, params=params, json=json, headers=headers
                )

            if resp.status_code in _RETRYABLE_STATUS_CODES and attempt < self.max_retries:
                delay = self._retry_delay(attempt, resp)
                logger.warning(
                    "Got %d on %s %s, retrying in %.2fs (attempt %d/%d)",
                    resp.status_code,
                    upper_method,
                    path,
                    delay,
                    attempt + 1,
                    self.max_retries,
                )
                await asyncio.sleep(delay)
                continue

            break

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

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return await self._request("GET", path, params=params)

    async def post(
        self, path: str, json: dict[str, Any] | None = None, params: dict[str, Any] | None = None
    ) -> Any:
        return await self._request("POST", path, params=params, json=json)

    async def patch(
        self, path: str, json: dict[str, Any] | None = None, params: dict[str, Any] | None = None
    ) -> Any:
        return await self._request("PATCH", path, params=params, json=json)

    async def put(
        self, path: str, json: dict[str, Any] | None = None, params: dict[str, Any] | None = None
    ) -> Any:
        return await self._request("PUT", path, params=params, json=json)

    async def delete(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return await self._request("DELETE", path, params=params)

    async def get_all(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        key: str | None = None,
        *,
        max_pages: int = 50,
    ) -> list[dict[str, Any]]:
        """Paginate through all results using next_page_token.

        If ``key`` is None (or not found in the response), automatically selects
        the first list-valued field in the response payload.
        """
        results: list[dict[str, Any]] = []
        current_params = dict(params or {})
        seen_tokens: set[str] = set()

        for _ in range(max_pages):
            data = await self.get(path, params=current_params)
            if not isinstance(data, dict):
                break

            target_key = key
            if not target_key or target_key not in data:
                target_key = next(
                    (k for k, v in data.items() if isinstance(v, list)),
                    None,
                )

            if target_key and isinstance(data.get(target_key), list):
                results.extend(data[target_key])

            next_token = data.get("next_page_token")
            if not next_token or next_token in seen_tokens:
                break
            seen_tokens.add(next_token)
            current_params["next_page_token"] = next_token

        return results

