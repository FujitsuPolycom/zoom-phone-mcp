"""Tests for ZoomAuth, ZoomPhoneClient, read-only mode, retries, and pagination."""

from __future__ import annotations

import httpx
import pytest
import respx

from zoom_phone_mcp.auth import API_BASE, OAUTH_URL, ZoomAuth, load_dotenv_if_present
from zoom_phone_mcp.client import (
    ZoomAPIError,
    ZoomPhoneClient,
    normalize_members_payload,
    normalize_phone_numbers,
)


def test_missing_credentials_raises(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("ZOOM_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("ZOOM_CLIENT_ID", raising=False)
    monkeypatch.delenv("ZOOM_CLIENT_SECRET", raising=False)
    with pytest.raises(ValueError, match="Missing Zoom OAuth credentials"):
        ZoomAuth()


def test_load_dotenv_if_present(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# comment\nZOOM_ACCOUNT_ID=acc_from_dotenv\nZOOM_CLIENT_ID='cid_from_dotenv'\nZOOM_CLIENT_SECRET=\"sec_from_dotenv\"\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("ZOOM_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("ZOOM_CLIENT_ID", raising=False)
    monkeypatch.delenv("ZOOM_CLIENT_SECRET", raising=False)

    load_dotenv_if_present(env_file)
    auth = ZoomAuth()
    assert auth.account_id == "acc_from_dotenv"
    assert auth.client_id == "cid_from_dotenv"
    assert auth.client_secret == "sec_from_dotenv"


@respx.mock
async def test_auth_token_caching_and_invalidation() -> None:
    route = respx.post(OAUTH_URL).mock(
        side_effect=[
            httpx.Response(200, json={"access_token": "tok_1", "expires_in": 3600}),
            httpx.Response(200, json={"access_token": "tok_2", "expires_in": 3600}),
        ]
    )
    auth = ZoomAuth("acc", "cid", "sec")
    t1 = await auth.get_token()
    t2 = await auth.get_token()
    assert t1 == "tok_1"
    assert t2 == "tok_1"
    assert route.call_count == 1

    auth.invalidate()
    assert not auth.is_valid
    t3 = await auth.get_token()
    assert t3 == "tok_2"
    assert route.call_count == 2


@respx.mock
async def test_client_401_auto_refresh() -> None:
    respx.post(OAUTH_URL).mock(
        side_effect=[
            httpx.Response(200, json={"access_token": "stale_tok", "expires_in": 3600}),
            httpx.Response(200, json={"access_token": "fresh_tok", "expires_in": 3600}),
        ]
    )
    users_route = respx.get(f"{API_BASE}/phone/users").mock(
        side_effect=[
            httpx.Response(401, json={"message": "Invalid access token"}),
            httpx.Response(200, json={"users": [{"id": "u1"}]}),
        ]
    )

    auth = ZoomAuth("acc", "cid", "sec")
    async with ZoomPhoneClient(auth, retry_base_delay=0.01) as client:
        data = await client.get("/phone/users")
        assert data == {"users": [{"id": "u1"}]}
        assert users_route.call_count == 2


@respx.mock
async def test_client_429_rate_limit_retry() -> None:
    respx.post(OAUTH_URL).mock(
        return_value=httpx.Response(200, json={"access_token": "tok", "expires_in": 3600})
    )
    route = respx.get(f"{API_BASE}/phone/sites").mock(
        side_effect=[
            httpx.Response(429, headers={"Retry-After": "0.01"}, json={"message": "Rate limit"}),
            httpx.Response(200, json={"sites": [{"id": "s1"}]}),
        ]
    )

    auth = ZoomAuth("acc", "cid", "sec")
    async with ZoomPhoneClient(auth, retry_base_delay=0.01) as client:
        data = await client.get("/phone/sites")
        assert data == {"sites": [{"id": "s1"}]}
        assert route.call_count == 2


@respx.mock
async def test_client_read_only_mode_blocks_writes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOOM_PHONE_MCP_READ_ONLY", "true")
    respx.post(OAUTH_URL).mock(
        return_value=httpx.Response(200, json={"access_token": "tok", "expires_in": 3600})
    )
    respx.get(f"{API_BASE}/phone/sites").mock(
        return_value=httpx.Response(200, json={"sites": []})
    )

    auth = ZoomAuth("acc", "cid", "sec")
    async with ZoomPhoneClient(auth) as client:
        # GET is permitted in read-only mode
        assert await client.get("/phone/sites") == {"sites": []}

        # POST, PATCH, PUT, DELETE are blocked before hitting the network
        for call in (
            lambda: client.post("/phone/sites", json={"name": "HQ"}),
            lambda: client.patch("/phone/sites/s1", json={"name": "HQ2"}),
            lambda: client.put("/phone/sites/s1", json={"name": "HQ3"}),
            lambda: client.delete("/phone/sites/s1"),
        ):
            with pytest.raises(ZoomAPIError) as exc_info:
                await call()
            assert exc_info.value.status_code == 403
            assert "read-only mode" in exc_info.value.message


@respx.mock
async def test_get_all_pagination_auto_detects_key() -> None:
    respx.post(OAUTH_URL).mock(
        return_value=httpx.Response(200, json={"access_token": "tok", "expires_in": 3600})
    )
    respx.get(f"{API_BASE}/phone/call_queues").mock(
        side_effect=[
            httpx.Response(
                200,
                json={
                    "call_queues": [{"id": "cq1"}],
                    "next_page_token": "page2_tok",
                },
            ),
            httpx.Response(
                200,
                json={
                    "call_queues": [{"id": "cq2"}],
                    "next_page_token": "",
                },
            ),
        ]
    )

    auth = ZoomAuth("acc", "cid", "sec")
    async with ZoomPhoneClient(auth) as client:
        items = await client.get_all("/phone/call_queues")
        assert items == [{"id": "cq1"}, {"id": "cq2"}]


def test_normalize_phone_numbers() -> None:
    assert normalize_phone_numbers("+12058945717") == [{"number": "+12058945717"}]
    assert normalize_phone_numbers("KsxwNLEhQ0SJ4U4Bor4ShA") == [{"id": "KsxwNLEhQ0SJ4U4Bor4ShA"}]
    assert normalize_phone_numbers(["+12058945717", "num_id_1", {"id": "x", "number": "+19998887777"}]) == [
        {"number": "+12058945717"},
        {"id": "num_id_1"},
        {"id": "x", "number": "+19998887777"},
    ]


def test_normalize_members_payload() -> None:
    payload = normalize_members_payload(
        members=["user_id_1", "alice@example.com"],
        common_area_ids=["ca_1"],
    )
    assert payload == {
        "members": {
            "users": [{"id": "user_id_1"}, {"email": "alice@example.com"}],
            "common_area_ids": ["ca_1"],
        }
    }
