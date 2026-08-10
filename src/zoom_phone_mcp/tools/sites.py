"""Sites — Zoom Phone site management tools."""

from typing import Any

def register(mcp: Any, get_client, json_result, error_result):
    client = get_client

    @mcp.tool(description="List all Zoom Phone sites.")
    async def list_sites(page_size: int | None = 100, next_page_token: str | None = None) -> str:
        """List all phone sites in the account."""
        try:
            params: dict[str, Any] = {"page_size": page_size}
            if next_page_token:
                params["next_page_token"] = next_page_token
            data = await client().get("/phone/sites", params=params)
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Get details of a specific Zoom Phone site.")
    async def get_site(site_id: str) -> str:
        """Get details of a specific phone site by ID."""
        try:
            data = await client().get(f"/phone/sites/{site_id}")
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Create a new Zoom Phone site.")
    async def create_site(name: str, extension_number: int | None = None, description: str | None = None) -> str:
        """Create a new phone site."""
        try:
            body: dict[str, Any] = {"name": name}
            if extension_number is not None:
                body["extension_number"] = extension_number
            if description:
                body["description"] = description
            data = await client().post("/phone/sites", json=body)
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Update a Zoom Phone site's details.")
    async def update_site(site_id: str, name: str | None = None, description: str | None = None) -> str:
        """Update a phone site's name or description."""
        try:
            body: dict[str, Any] = {}
            if name is not None:
                body["name"] = name
            if description is not None:
                body["description"] = description
            data = await client().patch(f"/phone/sites/{site_id}", json=body)
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Delete a Zoom Phone site.")
    async def delete_site(site_id: str) -> str:
        """Delete a phone site."""
        try:
            data = await client().delete(f"/phone/sites/{site_id}")
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Get a specific setting type for a phone site.")
    async def get_site_settings(site_id: str, setting_type: str) -> str:
        """Get a specific setting type for a phone site (e.g. 'business_hours', 'closed_hours', 'holiday_hours')."""
        try:
            data = await client().get(f"/phone/sites/{site_id}/settings/{setting_type}")
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Update a specific setting type for a phone site.")
    async def update_site_settings(site_id: str, setting_type: str, settings: dict) -> str:
        """Update a specific setting type for a phone site."""
        try:
            data = await client().patch(f"/phone/sites/{site_id}/settings/{setting_type}", json=settings)
            return json_result(data)
        except Exception as e:
            return error_result(e)
