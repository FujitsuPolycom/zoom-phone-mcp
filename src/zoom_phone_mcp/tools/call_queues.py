"""MCP tools for Zoom Phone call queues."""

from __future__ import annotations

from typing import Any

from ..client import normalize_members_payload, normalize_phone_numbers


def register(mcp: Any, get_client: Any, json_result: Any, error_result: Any) -> None:
    """Register all call-queue MCP tools on the given FastMCP instance."""

    @mcp.tool()
    async def list_call_queues(
        site_id: str | None = None,
        page_size: int | None = 100,
        next_page_token: str | None = None,
    ) -> str:
        """List all call queues for the account, optionally filtered by site."""
        try:
            client = get_client()
            params: dict[str, Any] = {}
            if site_id is not None:
                params["site_id"] = site_id
            if page_size is not None:
                params["page_size"] = page_size
            if next_page_token is not None:
                params["next_page_token"] = next_page_token
            data = await client.get("/phone/call_queues", params=params)
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def get_call_queue(call_queue_id: str) -> str:
        """Get details of a specific call queue by ID."""
        try:
            client = get_client()
            data = await client.get(f"/phone/call_queues/{call_queue_id}")
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def create_call_queue(
        name: str,
        extension_number: int | None = None,
        site_id: str | None = None,
        description: str | None = None,
    ) -> str:
        """Create a new call queue."""
        try:
            client = get_client()
            body: dict[str, Any] = {"name": name}
            if extension_number is not None:
                body["extension_number"] = extension_number
            if site_id is not None:
                body["site_id"] = site_id
            if description is not None:
                body["description"] = description
            data = await client.post("/phone/call_queues", json=body)
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def update_call_queue(
        call_queue_id: str,
        name: str | None = None,
        extension_number: int | None = None,
        description: str | None = None,
    ) -> str:
        """Update an existing call queue's properties."""
        try:
            client = get_client()
            body: dict[str, Any] = {}
            if name is not None:
                body["name"] = name
            if extension_number is not None:
                body["extension_number"] = extension_number
            if description is not None:
                body["description"] = description
            data = await client.patch(f"/phone/call_queues/{call_queue_id}", json=body)
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def delete_call_queue(call_queue_id: str) -> str:
        """Delete a call queue by ID."""
        try:
            client = get_client()
            data = await client.delete(f"/phone/call_queues/{call_queue_id}")
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def list_queue_members(
        call_queue_id: str,
        page_size: int | None = None,
        next_page_token: str | None = None,
    ) -> str:
        """List all members of a call queue."""
        try:
            client = get_client()
            params: dict[str, Any] = {}
            if page_size is not None:
                params["page_size"] = page_size
            if next_page_token is not None:
                params["next_page_token"] = next_page_token
            data = await client.get(
                f"/phone/call_queues/{call_queue_id}/members", params=params
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def add_queue_members(
        call_queue_id: str,
        members: list[str | dict[str, Any]] | None = None,
        common_area_ids: list[str] | None = None,
    ) -> str:
        """Add members (user IDs/emails and/or common_area_ids) to a call queue."""
        try:
            client = get_client()
            body = normalize_members_payload(members, common_area_ids)
            data = await client.post(
                f"/phone/call_queues/{call_queue_id}/members", json=body
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def remove_queue_member(call_queue_id: str, member_id: str) -> str:
        """Remove a specific member from a call queue."""
        try:
            client = get_client()
            data = await client.delete(
                f"/phone/call_queues/{call_queue_id}/members/{member_id}"
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def remove_all_queue_members(call_queue_id: str) -> str:
        """Remove all members from a call queue."""
        try:
            client = get_client()
            data = await client.delete(f"/phone/call_queues/{call_queue_id}/members")
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def get_queue_call_handling(call_queue_id: str) -> str:
        """Get call handling settings for a call queue."""
        try:
            client = get_client()
            data = await client.get(
                f"/phone/call_queues/{call_queue_id}/call_handling/settings"
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def update_queue_call_handling(
        call_queue_id: str,
        hour_type: str,
        call_handling_settings: dict,
    ) -> str:
        """Update call handling settings for a call queue by hour type
        ('business_hours', 'closed_hours', or 'holiday_hours')."""
        try:
            client = get_client()
            data = await client.patch(
                f"/phone/call_queues/{call_queue_id}/call_handling/settings/{hour_type}",
                json=call_handling_settings,
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def get_queue_settings(call_queue_id: str) -> str:
        """Get settings for a call queue."""
        try:
            client = get_client()
            data = await client.get(f"/phone/call_queues/{call_queue_id}/settings")
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def update_queue_settings(
        call_queue_id: str,
        setting_type: str,
        settings: dict,
    ) -> str:
        """Update settings for a call queue by setting type."""
        try:
            client = get_client()
            data = await client.patch(
                f"/phone/call_queues/{call_queue_id}/settings/{setting_type}",
                json=settings,
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def add_queue_setting(
        call_queue_id: str,
        setting_type: str,
        settings: dict,
    ) -> str:
        """Add a new setting entry for a call queue by setting type."""
        try:
            client = get_client()
            data = await client.post(
                f"/phone/call_queues/{call_queue_id}/settings/{setting_type}",
                json=settings,
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def delete_queue_setting(call_queue_id: str, setting_type: str) -> str:
        """Delete a setting entry for a call queue by setting type."""
        try:
            client = get_client()
            data = await client.delete(
                f"/phone/call_queues/{call_queue_id}/settings/{setting_type}"
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def get_queue_policies(call_queue_id: str) -> str:
        """Get policies for a call queue."""
        try:
            client = get_client()
            data = await client.get(f"/phone/call_queues/{call_queue_id}/policies")
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def update_queue_policies(call_queue_id: str, policies: dict) -> str:
        """Update policies for a call queue."""
        try:
            client = get_client()
            data = await client.patch(
                f"/phone/call_queues/{call_queue_id}/policies", json=policies
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def assign_queue_phone_numbers(
        call_queue_id: str,
        phone_numbers: list[str | dict[str, Any]],
    ) -> str:
        """Assign phone numbers (E.164 strings, phone number IDs, or dicts) to a call queue."""
        try:
            client = get_client()
            body: dict[str, Any] = {"phone_numbers": normalize_phone_numbers(phone_numbers)}
            data = await client.post(
                f"/phone/call_queues/{call_queue_id}/phone_numbers", json=body
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def unassign_queue_phone_numbers(
        call_queue_id: str,
        phone_number_id: str | None = None,
    ) -> str:
        """Unassign a specific phone number (or all phone numbers if phone_number_id is omitted) from a call queue."""
        try:
            client = get_client()
            path = f"/phone/call_queues/{call_queue_id}/phone_numbers"
            if phone_number_id:
                path = f"{path}/{phone_number_id}"
            data = await client.delete(path)
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def get_queue_recordings(
        call_queue_id: str,
        page_size: int | None = None,
        next_page_token: str | None = None,
    ) -> str:
        """Get recordings for a call queue."""
        try:
            client = get_client()
            params: dict[str, Any] = {}
            if page_size is not None:
                params["page_size"] = page_size
            if next_page_token is not None:
                params["next_page_token"] = next_page_token
            data = await client.get(
                f"/phone/call_queues/{call_queue_id}/recordings", params=params
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def get_call_queue_analytics(
        from_date: str | None = None,
        to_date: str | None = None,
        page_size: int | None = None,
        next_page_token: str | None = None,
    ) -> str:
        """Get call queue analytics, optionally filtered by date range."""
        try:
            client = get_client()
            params: dict[str, Any] = {}
            if from_date is not None:
                params["from"] = from_date
            if to_date is not None:
                params["to"] = to_date
            if page_size is not None:
                params["page_size"] = page_size
            if next_page_token is not None:
                params["next_page_token"] = next_page_token
            data = await client.get("/phone/call_queue_analytics", params=params)
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def list_queue_custom_groups(
        call_queue_id: str,
        page_size: int | None = None,
        next_page_token: str | None = None,
    ) -> str:
        """List custom groups for a call queue."""
        try:
            client = get_client()
            params: dict[str, Any] = {}
            if page_size is not None:
                params["page_size"] = page_size
            if next_page_token is not None:
                params["next_page_token"] = next_page_token
            data = await client.get(
                f"/phone/call_queues/{call_queue_id}/custom_groups", params=params
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)
