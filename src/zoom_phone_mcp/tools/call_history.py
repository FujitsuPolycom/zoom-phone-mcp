"""MCP tools for Zoom Phone call history and call logs."""

from typing import Any

def register(mcp: Any, get_client, json_result, error_result) -> None:
    """Register call-history tools on the MCP server."""

    @mcp.tool()
    async def get_account_call_history(
        from_date: str | None = None,
        to_date: str | None = None,
        page_size: int | None = 100,
        next_page_token: str | None = None,
    ) -> str:
        """Retrieve call history logs for the entire account.

        Optionally filter by date range. Results are paginated.

        Args:
            from_date: Start date in YYYY-MM-DD format (inclusive).
            to_date: End date in YYYY-MM-DD format (inclusive).
            page_size: Number of records per page (default 100, max 300).
            next_page_token: Token for retrieving the next page of results.

        Returns:
            JSON string containing call history entries and pagination info.
        """
        try:
            client = get_client()
            params: dict[str, Any] = {"page_size": page_size or 100}
            if from_date:
                params["from"] = from_date
            if to_date:
                params["to"] = to_date
            if next_page_token:
                params["next_page_token"] = next_page_token
            data = await client.get("/phone/call_history", params=params)
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def get_call_history_detail(
        call_history_uuid: str,
    ) -> str:
        """Retrieve detailed information for a single call history entry.

        Args:
            call_history_uuid: Unique identifier of the call history record.

        Returns:
            JSON string with the full call detail record.
        """
        try:
            client = get_client()
            data = await client.get(f"/phone/call_history/{call_history_uuid}")
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def get_user_call_history(
        user_id: str,
        from_date: str | None = None,
        to_date: str | None = None,
        page_size: int | None = 100,
        next_page_token: str | None = None,
    ) -> str:
        """Retrieve call history logs for a specific Zoom Phone user.

        Optionally filter by date range. Results are paginated.

        Args:
            user_id: Zoom user ID or extension number.
            from_date: Start date in YYYY-MM-DD format (inclusive).
            to_date: End date in YYYY-MM-DD format (inclusive).
            page_size: Number of records per page (default 100, max 300).
            next_page_token: Token for retrieving the next page of results.

        Returns:
            JSON string containing the user's call history entries and pagination info.
        """
        try:
            client = get_client()
            params: dict[str, Any] = {"page_size": page_size or 100}
            if from_date:
                params["from"] = from_date
            if to_date:
                params["to"] = to_date
            if next_page_token:
                params["next_page_token"] = next_page_token
            data = await client.get(
                f"/phone/users/{user_id}/call_history", params=params
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def sync_user_call_history(
        user_id: str,
        sync_token: str | None = None,
    ) -> str:
        """Sync (incremental fetch) call history for a specific Zoom Phone user.

        Uses a sync token to retrieve only records created or modified since
        the last sync. On the first call, omit the sync_token to get an initial
        delta; subsequent calls should pass the token returned in the previous
        response.

        Args:
            user_id: Zoom user ID or extension number.
            sync_token: Token from the previous sync response (omit on first sync).

        Returns:
            JSON string containing synced call history entries and the next sync token.
        """
        try:
            client = get_client()
            params: dict[str, Any] = {}
            if sync_token:
                params["sync_token"] = sync_token
            data = await client.get(
                f"/phone/users/{user_id}/call_history/sync", params=params
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def delete_user_call_history_entry(
        user_id: str,
        call_log_id: str,
    ) -> str:
        """Delete a single call log entry from a user's call history.

        This operation is irreversible. The call log is permanently removed
        from the user's call history.

        Args:
            user_id: Zoom user ID or extension number.
            call_log_id: Unique identifier of the call log entry to delete.

        Returns:
            JSON string confirming deletion (HTTP 204 → empty object on success).
        """
        try:
            client = get_client()
            data = await client.delete(
                f"/phone/users/{user_id}/call_history/{call_log_id}"
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    async def add_client_code_to_call(
        call_log_id: str,
        client_code: str,
    ) -> str:
        """Attach a client code to an existing call log entry.

        Client codes are used for billing, CRM lookups, or custom labeling
        of call records. This PATCHes the call history record with the
        provided code.

        Args:
            call_log_id: Unique identifier of the call log entry.
            client_code: Client code string to associate with the call.

        Returns:
            JSON string confirming the client code was applied.
        """
        try:
            client = get_client()
            body = {"client_code": client_code}
            data = await client.patch(
                f"/phone/call_history/{call_log_id}/client_code", json=body
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)
