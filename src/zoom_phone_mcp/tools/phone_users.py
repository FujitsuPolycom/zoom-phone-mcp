"""Zoom Phone user management MCP tools.

Registers 10 tools for listing, retrieving, updating, and configuring
Zoom Phone users via the Zoom Phone REST API.
"""

from typing import Any, Callable

from ..client import ZoomPhoneClient, ZoomAPIError

def register(
    mcp: Any,
    get_client: Callable[[], ZoomPhoneClient],
    json_result: Callable[[Any], str],
    error_result: Callable[[Exception], str],
) -> None:
    """Register all Zoom Phone user management tools on the MCP server.

    Parameters
    ----------
    mcp
        The Any server instance.
    get_client
        Callable returning an initialised ``ZoomPhoneClient``.
    json_result
        Serialiser that converts API data to a JSON string for MCP return.
    error_result
        Serialiser that converts an exception to a JSON error string.
    """

    # ── 1. list_phone_users ────────────────────────────────────────────────

    @mcp.tool(description="List all Zoom Phone users with optional pagination and site filter.")
    async def list_phone_users(
        site_id: str | None = None,
        page_size: int | None = 100,
        next_page_token: str | None = None,
    ) -> str:
        """List Zoom Phone users.

        Parameters
        ----------
        site_id
            Filter users by site ID.  If omitted, users from all sites are returned.
        page_size
            Number of records per page (default 100, max 300).
        next_page_token
            Token from a previous response to fetch the next page of results.

        Returns
        -------
        str
            JSON string containing the list of phone users and pagination info.
        """
        try:
            client = get_client()
            params: dict[str, Any] = {}
            if site_id is not None:
                params["site_id"] = site_id
            if page_size is not None:
                params["page_size"] = page_size
            if next_page_token is not None:
                params["next_page_token"] = next_page_token
            data = await client.get("/phone/users", params=params or None)
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ── 2. get_phone_user ─────────────────────────────────────────────────

    @mcp.tool(description="Retrieve details for a specific Zoom Phone user by ID or email.")
    async def get_phone_user(user_id: str) -> str:
        """Get a single Zoom Phone user's details.

        Parameters
        ----------
        user_id
            The Zoom user ID or email address of the phone user.

        Returns
        -------
        str
            JSON string with the user's phone profile information.
        """
        try:
            client = get_client()
            data = await client.get(f"/phone/users/{user_id}")
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ── 3. update_phone_user ─────────────────────────────────────────────

    @mcp.tool(description="Update a Zoom Phone user's extension number and/or site assignment.")
    async def update_phone_user(
        user_id: str,
        extension_number: str | None = None,
        site_id: str | None = None,
    ) -> str:
        """Update a Zoom Phone user's settings.

        Parameters
        ----------
        user_id
            The Zoom user ID or email address.
        extension_number
            New extension number for the user.
        site_id
            New site ID to assign the user to.

        Returns
        -------
        str
            JSON string confirming the update or describing an error.
        """
        try:
            client = get_client()
            body: dict[str, Any] = {}
            if extension_number is not None:
                body["extension_number"] = extension_number
            if site_id is not None:
                body["site_id"] = site_id
            data = await client.patch(f"/phone/users/{user_id}", json=body or None)
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ── 4. get_user_call_handling ─────────────────────────────────────────

    @mcp.tool(description="Retrieve call handling settings for a Zoom Phone user.")
    async def get_user_call_handling(user_id: str) -> str:
        """Get call handling settings for a phone user.

        Parameters
        ----------
        user_id
            The Zoom user ID or email address.

        Returns
        -------
        str
            JSON string with the user's call handling configuration.
        """
        try:
            client = get_client()
            data = await client.get(f"/phone/users/{user_id}/call_handling/settings")
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ── 5. update_user_call_handling ─────────────────────────────────────

    @mcp.tool(description="Update call handling settings for a Zoom Phone user by hour type (business, closed, or holiday hours).")
    async def update_user_call_handling(
        user_id: str,
        hour_type: str,
        call_handling_settings: dict,
    ) -> str:
        """Update call handling settings for a phone user.

        Parameters
        ----------
        user_id
            The Zoom user ID or email address.
        hour_type
            The hours category to update — one of ``business_hours``,
            ``closed_hours``, or ``holiday_hours``.
        call_handling_settings
            Dictionary of call handling settings to apply for the given hour type.

        Returns
        -------
        str
            JSON string confirming the update or describing an error.
        """
        try:
            client = get_client()
            data = await client.patch(
                f"/phone/users/{user_id}/call_handling/settings/{hour_type}",
                json=call_handling_settings,
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ── 6. get_user_policies ─────────────────────────────────────────────

    @mcp.tool(description="Retrieve a specific policy type for a Zoom Phone user.")
    async def get_user_policies(
        user_id: str,
        policy_type: str,
    ) -> str:
        """Get policies for a phone user.

        Parameters
        ----------
        user_id
            The Zoom user ID or email address.
        policy_type
            The policy category to retrieve (e.g. ``outbound``, ``international_calling``).

        Returns
        -------
        str
            JSON string with the requested policy settings.
        """
        try:
            client = get_client()
            data = await client.get(f"/phone/users/{user_id}/policies/{policy_type}")
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ── 7. update_user_policies ──────────────────────────────────────────

    @mcp.tool(description="Update a specific policy type for a Zoom Phone user.")
    async def update_user_policies(
        user_id: str,
        policy_type: str,
        policy_settings: dict,
    ) -> str:
        """Update policies for a phone user.

        Parameters
        ----------
        user_id
            The Zoom user ID or email address.
        policy_type
            The policy category to update (e.g. ``outbound``, ``international_calling``).
        policy_settings
            Dictionary of policy settings to apply.

        Returns
        -------
        str
            JSON string confirming the update or describing an error.
        """
        try:
            client = get_client()
            data = await client.patch(
                f"/phone/users/{user_id}/policies/{policy_type}",
                json=policy_settings,
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ── 8. get_user_settings ──────────────────────────────────────────────

    @mcp.tool(description="Retrieve phone settings for a Zoom Phone user.")
    async def get_user_settings(user_id: str) -> str:
        """Get the phone settings for a user.

        Parameters
        ----------
        user_id
            The Zoom user ID or email address.

        Returns
        -------
        str
            JSON string with the user's phone settings.
        """
        try:
            client = get_client()
            data = await client.get(f"/phone/users/{user_id}/settings")
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ── 9. update_user_settings ───────────────────────────────────────────

    @mcp.tool(description="Update phone settings for a Zoom Phone user.")
    async def update_user_settings(
        user_id: str,
        settings: dict,
    ) -> str:
        """Update the phone settings for a user.

        Parameters
        ----------
        user_id
            The Zoom user ID or email address.
        settings
            Dictionary of phone settings to apply.

        Returns
        -------
        str
            JSON string confirming the update or describing an error.
        """
        try:
            client = get_client()
            data = await client.patch(
                f"/phone/users/{user_id}/settings",
                json=settings,
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ── 10. assign_phone_number_to_user ──────────────────────────────────

    @mcp.tool(description="Assign a phone number to a Zoom Phone user.")
    async def assign_phone_number_to_user(
        user_id: str,
        phone_number: str,
    ) -> str:
        """Assign a phone number to a phone user.

        Parameters
        ----------
        user_id
            The Zoom user ID or email address.
        phone_number
            The phone number to assign to the user.

        Returns
        -------
        str
            JSON string confirming the assignment or describing an error.
        """
        try:
            client = get_client()
            body: dict[str, Any] = {"phone_number": phone_number}
            data = await client.post(
                f"/phone/users/{user_id}/phone_numbers",
                json=body,
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)
