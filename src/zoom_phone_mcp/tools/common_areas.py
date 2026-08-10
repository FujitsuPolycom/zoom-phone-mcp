"""Common Areas — Zoom Phone common area (lobby/shared phone) management tools."""

from typing import Any

def register(mcp: Any, get_client, json_result, error_result):
    client = get_client

    @mcp.tool(description="List all Zoom Phone common areas (lobby/shared phones).")
    async def list_common_areas(page_size: int | None = 100, next_page_token: str | None = None) -> str:
        """List all common areas in the account."""
        try:
            params: dict[str, Any] = {"page_size": page_size}
            if next_page_token:
                params["next_page_token"] = next_page_token
            data = await client().get("/phone/common_areas", params=params)
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Get details of a specific Zoom Phone common area.")
    async def get_common_area(common_area_id: str) -> str:
        """Get details of a specific common area by ID."""
        try:
            data = await client().get(f"/phone/common_areas/{common_area_id}")
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Create a new Zoom Phone common area (e.g. lobby phone).")
    async def create_common_area(name: str, extension_number: int | None = None, site_id: str | None = None) -> str:
        """Create a new common area."""
        try:
            body: dict[str, Any] = {"name": name}
            if extension_number is not None:
                body["extension_number"] = extension_number
            if site_id:
                body["site_id"] = site_id
            data = await client().post("/phone/common_areas", json=body)
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Update a Zoom Phone common area's details.")
    async def update_common_area(common_area_id: str, name: str | None = None) -> str:
        """Update a common area's name."""
        try:
            body: dict[str, Any] = {}
            if name is not None:
                body["name"] = name
            data = await client().patch(f"/phone/common_areas/{common_area_id}", json=body)
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Delete a Zoom Phone common area.")
    async def delete_common_area(common_area_id: str) -> str:
        """Delete a common area."""
        try:
            data = await client().delete(f"/phone/common_areas/{common_area_id}")
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Get call handling settings for a Zoom Phone common area.")
    async def get_common_area_call_handling(common_area_id: str) -> str:
        """Get call handling settings (business hours, closed hours, holiday hours) for a common area."""
        try:
            data = await client().get(f"/phone/common_areas/{common_area_id}/call_handling/settings")
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Update call handling settings for a Zoom Phone common area by hour type.")
    async def update_common_area_call_handling(common_area_id: str, hour_type: str, call_handling_settings: dict) -> str:
        """Update call handling settings for a common area. hour_type: 'business_hours', 'closed_hours', or 'holiday_hours'."""
        try:
            data = await client().patch(
                f"/phone/common_areas/{common_area_id}/call_handling/settings/{hour_type}",
                json=call_handling_settings,
            )
            return json_result(data)
        except Exception as e:
            return error_result(e)
