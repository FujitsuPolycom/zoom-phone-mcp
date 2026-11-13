"""Tests for MCP tool registration and Zoom Phone API payload correctness."""

from __future__ import annotations

import json
import httpx
import pytest
import respx

import zoom_phone_mcp.server as server_mod
from zoom_phone_mcp.auth import API_BASE, OAUTH_URL, ZoomAuth
from zoom_phone_mcp.client import ZoomPhoneClient


@pytest.fixture(autouse=True)
async def configured_server_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ZOOM_ACCOUNT_ID", "test_acc")
    monkeypatch.setenv("ZOOM_CLIENT_ID", "test_cid")
    monkeypatch.setenv("ZOOM_CLIENT_SECRET", "test_sec")
    monkeypatch.setenv("ZOOM_PHONE_MCP_READ_ONLY", "false")
    auth = ZoomAuth("test_acc", "test_cid", "test_sec")
    auth._token = "valid_test_token"
    auth._expires_at = 9999999999.0
    client = ZoomPhoneClient(auth, retry_base_delay=0.01)
    server_mod._auth = auth
    server_mod._client = client
    yield client
    await client.close()
    server_mod._client = None


async def _call_mcp_tool(name: str, arguments: dict | None = None) -> dict:
    res = await server_mod.mcp.call_tool(name, arguments or {})
    # FastMCP call_tool returns a sequence of TextContent (or tuple)
    blocks = res[0] if isinstance(res, tuple) else res
    text = blocks[0].text
    return json.loads(text)


async def test_all_tools_registered() -> None:
    tools = await server_mod.mcp.list_tools()
    tool_names = {t.name for t in tools}
    assert "server_info" in tool_names
    assert len(tool_names) >= 118

    info = await _call_mcp_tool("server_info")
    assert info["server"] == "zoom-phone-mcp"
    assert info["read_only"] is False
    assert len(info["tool_categories"]) == 14


@respx.mock
async def test_send_sms_payload_schema() -> None:
    route = respx.post(f"{API_BASE}/phone/sms/messages").mock(
        return_value=httpx.Response(201, json={"session_id": "sess_123"})
    )
    out = await _call_mcp_tool(
        "send_sms",
        {
            "to_number": "+19876543210",
            "from_number": "+12345678901",
            "message": "Hello from test",
            "sender_user_id": "user_abc",
        },
    )
    assert out == {"session_id": "sess_123"}
    sent_json = json.loads(route.calls.last.request.content)
    assert sent_json == {
        "sender": {"phone_number": "+12345678901", "user_id": "user_abc"},
        "to_members": [{"phone_number": "+19876543210"}],
        "message": "Hello from test",
    }


@respx.mock
async def test_add_queue_and_slg_members_payload_schema() -> None:
    cq_route = respx.post(f"{API_BASE}/phone/call_queues/cq_1/members").mock(
        return_value=httpx.Response(201, json={})
    )
    slg_route = respx.post(f"{API_BASE}/phone/shared_line_groups/slg_1/members").mock(
        return_value=httpx.Response(201, json={})
    )

    await _call_mcp_tool(
        "add_queue_members",
        {
            "call_queue_id": "cq_1",
            "members": ["u_123", "agent@example.com"],
            "common_area_ids": ["ca_99"],
        },
    )
    assert json.loads(cq_route.calls.last.request.content) == {
        "members": {
            "users": [{"id": "u_123"}, {"email": "agent@example.com"}],
            "common_area_ids": ["ca_99"],
        }
    }

    await _call_mcp_tool(
        "add_slg_members",
        {
            "shared_line_group_id": "slg_1",
            "members": ["u_456"],
        },
    )
    assert json.loads(slg_route.calls.last.request.content) == {
        "members": {
            "users": [{"id": "u_456"}],
        }
    }


@respx.mock
async def test_phone_number_assignment_payload_schemas() -> None:
    user_route = respx.post(f"{API_BASE}/phone/users/u1/phone_numbers").mock(
        return_value=httpx.Response(201, json={})
    )
    ar_route = respx.post(f"{API_BASE}/phone/auto_receptionists/ar1/phone_numbers").mock(
        return_value=httpx.Response(201, json={})
    )
    cq_route = respx.post(f"{API_BASE}/phone/call_queues/cq1/phone_numbers").mock(
        return_value=httpx.Response(201, json={})
    )
    slg_route = respx.post(f"{API_BASE}/phone/shared_line_groups/slg1/phone_numbers").mock(
        return_value=httpx.Response(201, json={})
    )

    await _call_mcp_tool(
        "assign_phone_number_to_user",
        {"user_id": "u1", "phone_number": "+12058945717"},
    )
    assert json.loads(user_route.calls.last.request.content) == {
        "phone_numbers": [{"number": "+12058945717"}]
    }

    await _call_mcp_tool(
        "assign_ar_phone_numbers",
        {"auto_receptionist_id": "ar1", "phone_numbers": ["+12058945717", "num_id_abc"]},
    )
    assert json.loads(ar_route.calls.last.request.content) == {
        "phone_numbers": [{"number": "+12058945717"}, {"id": "num_id_abc"}]
    }

    await _call_mcp_tool(
        "assign_queue_phone_numbers",
        {"call_queue_id": "cq1", "phone_numbers": ["+12058945717"]},
    )
    assert json.loads(cq_route.calls.last.request.content) == {
        "phone_numbers": [{"number": "+12058945717"}]
    }

    await _call_mcp_tool(
        "assign_slg_phone_numbers",
        {"shared_line_group_id": "slg1", "phone_numbers": ["num_id_xyz"]},
    )
    assert json.loads(slg_route.calls.last.request.content) == {
        "phone_numbers": [{"id": "num_id_xyz"}]
    }


@respx.mock
async def test_common_area_and_slg_display_name_schema() -> None:
    ca_post = respx.post(f"{API_BASE}/phone/common_areas").mock(
        return_value=httpx.Response(201, json={"id": "ca_new"})
    )
    ca_patch = respx.patch(f"{API_BASE}/phone/common_areas/ca_new").mock(
        return_value=httpx.Response(204)
    )
    slg_post = respx.post(f"{API_BASE}/phone/shared_line_groups").mock(
        return_value=httpx.Response(201, json={"id": "slg_new"})
    )
    slg_patch = respx.patch(f"{API_BASE}/phone/shared_line_groups/slg_new").mock(
        return_value=httpx.Response(204)
    )

    await _call_mcp_tool("create_common_area", {"name": "Lobby Phone", "extension_number": 105})
    assert json.loads(ca_post.calls.last.request.content) == {
        "display_name": "Lobby Phone",
        "extension_number": 105,
    }

    await _call_mcp_tool("update_common_area", {"common_area_id": "ca_new", "name": "Lobby 2"})
    assert json.loads(ca_patch.calls.last.request.content) == {
        "display_name": "Lobby 2",
    }

    await _call_mcp_tool("create_shared_line_group", {"name": "Support SLG", "extension_number": 205})
    assert json.loads(slg_post.calls.last.request.content) == {
        "display_name": "Support SLG",
        "extension_number": 205,
    }

    await _call_mcp_tool("update_shared_line_group", {"shared_line_group_id": "slg_new", "name": "VIP SLG"})
    assert json.loads(slg_patch.calls.last.request.content) == {
        "display_name": "VIP SLG",
    }


@respx.mock
async def test_devices_and_voicemail_status_schema() -> None:
    dev_post = respx.post(f"{API_BASE}/phone/devices").mock(
        return_value=httpx.Response(201, json={"id": "dev_1"})
    )
    dev_patch = respx.patch(f"{API_BASE}/phone/devices/dev_1").mock(
        return_value=httpx.Response(204)
    )
    vm_patch = respx.patch(f"{API_BASE}/phone/voice_mails/vm_1").mock(
        return_value=httpx.Response(204)
    )

    await _call_mcp_tool(
        "add_device",
        {
            "mac_address": "001122334455",
            "model": "VVX250",
            "display_name": "Front Desk",
            "device_type": "Poly",
            "user_id": "u_1",
            "extension_id": "ext_1",
        },
    )
    assert json.loads(dev_post.calls.last.request.content) == {
        "display_name": "Front Desk",
        "mac_address": "001122334455",
        "model": "VVX250",
        "type": "Poly",
        "assigned_to": "u_1",
        "assignee_extension_ids": ["ext_1"],
    }

    await _call_mcp_tool(
        "update_device",
        {"device_id": "dev_1", "name": "Back Office Phone"},
    )
    assert json.loads(dev_patch.calls.last.request.content) == {
        "display_name": "Back Office Phone",
    }

    await _call_mcp_tool(
        "update_voicemail_read_status",
        {"voicemail_id": "vm_1", "is_read": False},
    )
    assert json.loads(vm_patch.calls.last.request.content) == {
        "status": "unread",
    }
