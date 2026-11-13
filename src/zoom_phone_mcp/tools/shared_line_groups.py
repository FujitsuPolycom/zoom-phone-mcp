"""Shared Line Groups — Zoom Phone SLG management tools."""

from __future__ import annotations

from typing import Any

from ..client import normalize_members_payload, normalize_phone_numbers


def register(mcp: Any, get_client, json_result, error_result):
    client = get_client

    @mcp.tool(description="List all Zoom Phone shared line groups.")
    async def list_shared_line_groups(page_size: int | None = 100, next_page_token: str | None = None) -> str:
        """List all shared line groups in the account."""
        try:
            params: dict[str, Any] = {"page_size": page_size}
            if next_page_token:
                params["next_page_token"] = next_page_token
            data = await client().get("/phone/shared_line_groups", params=params)
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Get details of a specific Zoom Phone shared line group.")
    async def get_shared_line_group(shared_line_group_id: str) -> str:
        """Get details of a specific shared line group by ID."""
        try:
            data = await client().get(f"/phone/shared_line_groups/{shared_line_group_id}")
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Create a new Zoom Phone shared line group.")
    async def create_shared_line_group(
        name: str | None = None,
        extension_number: int | None = None,
        site_id: str | None = None,
        display_name: str | None = None,
        description: str | None = None,
    ) -> str:
        """Create a new shared line group. Accepts display_name (or name alias)."""
        try:
            resolved_name = display_name if display_name is not None else name
            if not resolved_name:
                raise ValueError("Either display_name or name is required to create a shared line group.")
            body: dict[str, Any] = {"display_name": resolved_name}
            if extension_number is not None:
                body["extension_number"] = extension_number
            if site_id:
                body["site_id"] = site_id
            if description is not None:
                body["description"] = description
            data = await client().post("/phone/shared_line_groups", json=body)
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Update a Zoom Phone shared line group's details.")
    async def update_shared_line_group(
        shared_line_group_id: str,
        name: str | None = None,
        display_name: str | None = None,
        description: str | None = None,
        extension_number: int | None = None,
    ) -> str:
        """Update a shared line group's display_name (or name alias), description, or extension_number."""
        try:
            body: dict[str, Any] = {}
            resolved_name = display_name if display_name is not None else name
            if resolved_name is not None:
                body["display_name"] = resolved_name
            if description is not None:
                body["description"] = description
            if extension_number is not None:
                body["extension_number"] = extension_number
            data = await client().patch(f"/phone/shared_line_groups/{shared_line_group_id}", json=body)
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Delete a Zoom Phone shared line group.")
    async def delete_shared_line_group(shared_line_group_id: str) -> str:
        """Delete a shared line group."""
        try:
            data = await client().delete(f"/phone/shared_line_groups/{shared_line_group_id}")
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Add members to a Zoom Phone shared line group.")
    async def add_slg_members(
        shared_line_group_id: str,
        members: list[str | dict[str, Any]] | None = None,
        common_area_ids: list[str] | None = None,
    ) -> str:
        """Add members (user IDs/emails and/or common_area_ids) to a shared line group."""
        try:
            body = normalize_members_payload(members, common_area_ids)
            data = await client().post(f"/phone/shared_line_groups/{shared_line_group_id}/members", json=body)
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Remove a specific member (or all members if member_id is omitted) from a Zoom Phone shared line group.")
    async def remove_slg_members(
        shared_line_group_id: str,
        member_id: str | None = None,
    ) -> str:
        """Remove a specific member or all members from a shared line group."""
        try:
            path = f"/phone/shared_line_groups/{shared_line_group_id}/members"
            if member_id:
                path = f"{path}/{member_id}"
            data = await client().delete(path)
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Assign phone numbers to a Zoom Phone shared line group.")
    async def assign_slg_phone_numbers(
        shared_line_group_id: str,
        phone_numbers: list[str | dict[str, Any]],
    ) -> str:
        """Assign phone numbers (E.164 strings, phone number IDs, or dicts) to a shared line group."""
        try:
            body = {"phone_numbers": normalize_phone_numbers(phone_numbers)}
            data = await client().post(f"/phone/shared_line_groups/{shared_line_group_id}/phone_numbers", json=body)
            return json_result(data)
        except Exception as e:
            return error_result(e)
