"""Zoom Phone voicemail management MCP tools."""

from typing import Any

from ..client import ZoomAPIError, ZoomPhoneClient

def register(mcp, get_client, json_result, error_result):
    """Register all voicemail-related MCP tools.

    Args:
        mcp: FastMCP server instance.
        get_client: Callable returning the active ZoomPhoneClient.
        json_result: Callable serializing data to a JSON string.
        error_result: Callable formatting an exception as a JSON string.
    """

    # ── 1. Account-wide voicemails ───────────────────────────────────────────

    @mcp.tool()
    async def get_account_voicemails(
        page_size: int | None = 100,
        next_page_token: str | None = None,
    ) -> str:
        """List all voicemails for the Zoom Phone account.

        Args:
            page_size: Number of records per page (default 100, max 300).
            next_page_token: Pagination token from a previous response.

        Returns:
            JSON string with voicemail records and pagination info.
        """
        client: ZoomPhoneClient = get_client()
        params: dict[str, Any] = {"page_size": page_size}
        if next_page_token:
            params["next_page_token"] = next_page_token
        try:
            data = await client.get("/phone/voice_mails", params=params)
            return json_result(data)
        except (ZoomAPIError, Exception) as err:
            return error_result(err)

    # ── 2. User-specific voicemails ──────────────────────────────────────────

    @mcp.tool()
    async def get_user_voicemails(
        user_id: str,
        page_size: int | None = 100,
        next_page_token: str | None = None,
    ) -> str:
        """List voicemails for a specific Zoom Phone user.

        Args:
            user_id: The Zoom user ID (e.g. 'me' or a UUID).
            page_size: Number of records per page (default 100, max 300).
            next_page_token: Pagination token from a previous response.

        Returns:
            JSON string with the user's voicemail records and pagination info.
        """
        client: ZoomPhoneClient = get_client()
        params: dict[str, Any] = {"page_size": page_size}
        if next_page_token:
            params["next_page_token"] = next_page_token
        try:
            data = await client.get(
                f"/phone/users/{user_id}/voice_mails", params=params
            )
            return json_result(data)
        except (ZoomAPIError, Exception) as err:
            return error_result(err)

    # ── 3. Voicemail details ─────────────────────────────────────────────────

    @mcp.tool()
    async def get_voicemail_details(
        voicemail_id: str,
    ) -> str:
        """Get details of a single voicemail by ID.

        Args:
            voicemail_id: The unique identifier of the voicemail.

        Returns:
            JSON string with full voicemail details (caller, duration, transcript, etc.).
        """
        client: ZoomPhoneClient = get_client()
        try:
            data = await client.get(f"/phone/voice_mails/{voicemail_id}")
            return json_result(data)
        except (ZoomAPIError, Exception) as err:
            return error_result(err)

    # ── 4. Delete voicemail ──────────────────────────────────────────────────

    @mcp.tool()
    async def delete_voicemail(
        voicemail_id: str,
    ) -> str:
        """Delete a voicemail by ID.

        Args:
            voicemail_id: The unique identifier of the voicemail to delete.

        Returns:
            JSON string confirming deletion (empty object on success).
        """
        client: ZoomPhoneClient = get_client()
        try:
            data = await client.delete(f"/phone/voice_mails/{voicemail_id}")
            return json_result(data)
        except (ZoomAPIError, Exception) as err:
            return error_result(err)

    # ── 5. Update read status ────────────────────────────────────────────────

    @mcp.tool()
    async def update_voicemail_read_status(
        voicemail_id: str,
        is_read: bool = True,
        status: str | None = None,
    ) -> str:
        """Mark a voicemail as read or unread.

        Args:
            voicemail_id: The unique identifier of the voicemail.
            is_read: True to mark as 'read', False to mark as 'unread' (default True).
            status: Explicit status ('read' or 'unread'); overrides is_read if provided.

        Returns:
            JSON string confirming the updated read status.
        """
        client: ZoomPhoneClient = get_client()
        resolved_status = status if status is not None else ("read" if is_read else "unread")
        body: dict[str, Any] = {"status": resolved_status}
        try:
            data = await client.patch(
                f"/phone/voice_mails/{voicemail_id}", json=body
            )
            return json_result(data)
        except (ZoomAPIError, Exception) as err:
            return error_result(err)

    # ── 6. Download voicemail ────────────────────────────────────────────────

    @mcp.tool()
    async def download_voicemail(
        file_id: str,
    ) -> str:
        """Get the download URL for a voicemail audio file.

        Args:
            file_id: The file ID of the voicemail audio recording.

        Returns:
            JSON string containing the download URL and related metadata.
        """
        client: ZoomPhoneClient = get_client()
        try:
            data = await client.get(f"/phone/voice_mails/download/{file_id}")
            return json_result(data)
        except (ZoomAPIError, Exception) as err:
            return error_result(err)

    # ── 7. Voicemail by call element ─────────────────────────────────────────

    @mcp.tool()
    async def get_voicemail_by_call_element(
        call_element_id: str,
    ) -> str:
        """Get the voicemail associated with a specific call element.

        Args:
            call_element_id: The unique identifier of the call element.

        Returns:
            JSON string with the voicemail record linked to the call element.
        """
        client: ZoomPhoneClient = get_client()
        try:
            data = await client.get(
                f"/phone/call_element/{call_element_id}/voice_mail"
            )
            return json_result(data)
        except (ZoomAPIError, Exception) as err:
            return error_result(err)
