"""Routing Rules — Zoom Phone directory backup routing rules."""

from typing import Any

def register(mcp: Any, get_client, json_result, error_result):
    client = get_client

    @mcp.tool(description="List all Zoom Phone directory backup routing rules.")
    async def list_routing_rules(page_size: int | None = 100, next_page_token: str | None = None) -> str:
        """List all directory backup routing rules."""
        try:
            params: dict[str, Any] = {"page_size": page_size}
            if next_page_token:
                params["next_page_token"] = next_page_token
            data = await client().get("/phone/routing_rules", params=params)
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Get details of a specific Zoom Phone routing rule.")
    async def get_routing_rule(routing_rule_id: str) -> str:
        """Get details of a specific routing rule by ID."""
        try:
            data = await client().get(f"/phone/routing_rules/{routing_rule_id}")
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Create a new Zoom Phone directory backup routing rule.")
    async def create_routing_rule(
        name: str,
        description: str | None = None,
        routing_rule: dict[str, Any] | None = None,
    ) -> str:
        """Create a new directory backup routing rule."""
        try:
            body: dict[str, Any] = {"name": name, "routing_rule": routing_rule or {}}
            if description:
                body["description"] = description
            data = await client().post("/phone/routing_rules", json=body)
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Update a Zoom Phone directory backup routing rule.")
    async def update_routing_rule(routing_rule_id: str, name: str | None = None, description: str | None = None, routing_rule: dict | None = None) -> str:
        """Update a routing rule's name, description, or routing configuration."""
        try:
            body: dict[str, Any] = {}
            if name is not None:
                body["name"] = name
            if description is not None:
                body["description"] = description
            if routing_rule is not None:
                body["routing_rule"] = routing_rule
            data = await client().patch(f"/phone/routing_rules/{routing_rule_id}", json=body)
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Delete a Zoom Phone directory backup routing rule.")
    async def delete_routing_rule(routing_rule_id: str) -> str:
        """Delete a routing rule."""
        try:
            data = await client().delete(f"/phone/routing_rules/{routing_rule_id}")
            return json_result(data)
        except Exception as e:
            return error_result(e)
