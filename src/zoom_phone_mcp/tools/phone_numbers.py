"""Zoom Phone number management MCP tools.

Provides tools for listing, retrieving, updating, and unassigning phone
numbers, as well as listing calling plans via the Zoom Phone API.
"""

from typing import Any

def register(
    mcp: Any,
    get_client: Any,
    json_result: Any,
    error_result: Any,
) -> None:
    """Register Zoom Phone number management tools with the MCP server.

    Args:
        mcp: The FastMCP server instance to register tools on.
        get_client: Callable that returns a configured Zoom Phone API client.
        json_result: Callable that wraps data as a successful JSON result.
        error_result: Callable that wraps an error message as a JSON error result.
    """

    @mcp.tool()
    async def list_phone_numbers(
        type: str | None = None,
        page_size: int | None = 100,
        next_page_token: str | None = None,
    ) -> str:
        """List phone numbers in the Zoom Phone account.

        Retrieves a paginated list of all phone numbers, optionally filtered
        by assignment status.

        Args:
            type: Filter by assignment status. One of 'assigned',
                'unassigned', or 'all'. Defaults to 'all' if omitted.
            page_size: Number of results per page (max 300). Defaults to 100.
            next_page_token: Token for retrieving the next page of results.

        Returns:
            JSON string containing the list of phone numbers and pagination info.
        """
        try:
            client = get_client()
            params: dict[str, Any] = {}
            if type is not None:
                params["type"] = type
            if page_size is not None:
                params["page_size"] = page_size
            if next_page_token is not None:
                params["next_page_token"] = next_page_token
            data = await client.get("/phone/numbers", params=params)
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def get_phone_number(
        phone_number_id: str,
    ) -> str:
        """Retrieve details for a specific phone number.

        Fetches the full configuration and metadata for a single phone number
        by its unique identifier.

        Args:
            phone_number_id: The unique identifier of the phone number.

        Returns:
            JSON string containing the phone number details.
        """
        try:
            client = get_client()
            data = await client.get(f"/phone/numbers/{phone_number_id}")
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def update_phone_number(
        phone_number_id: str,
        phone_number_settings: dict,
    ) -> str:
        """Update settings for a specific phone number.

        Applies a partial update to the configuration of an existing phone
        number using the provided settings dictionary.

        Args:
            phone_number_id: The unique identifier of the phone number to update.
            phone_number_settings: Dictionary of phone number settings to update.
                Keys and values follow the Zoom Phone API PATCH /phone/numbers
                schema (e.g. display name, caller ID, emergency address).

        Returns:
            JSON string confirming the update result.
        """
        try:
            client = get_client()
            data = await client.patch(
                f"/phone/numbers/{phone_number_id}",
                json=phone_number_settings,
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def unassign_phone_number_from_user(
        user_id: str,
        phone_number_id: str,
    ) -> str:
        """Unassign a phone number from a Zoom Phone user.

        Removes the specified phone number from the specified user's account,
        making it available for reassignment.

        Args:
            user_id: The unique identifier of the Zoom Phone user.
            phone_number_id: The unique identifier of the phone number to unassign.

        Returns:
            JSON string confirming the unassignment result.
        """
        try:
            client = get_client()
            data = await client.delete(
                f"/phone/users/{user_id}/phone_numbers/{phone_number_id}"
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def list_calling_plans() -> str:
        """List all available calling plans for the Zoom Phone account.

        Retrieves the full set of calling plans that can be assigned to users
        in the account.

        Returns:
            JSON string containing the list of calling plans.
        """
        try:
            client = get_client()
            data = await client.get("/phone/calling_plans")
            return json_result(data)
        except Exception as err:
            return error_result(err)
