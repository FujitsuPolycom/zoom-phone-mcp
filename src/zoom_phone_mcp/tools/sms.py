"""SMS & Recordings — Zoom Phone SMS messaging and call recording tools."""

from typing import Any

def register(mcp: Any, get_client, json_result, error_result):
    client = get_client

    # ── SMS ───────────────────────────────────────────────────────────────

    @mcp.tool(description="Send an SMS message from a Zoom Phone number.")
    async def send_sms(to_number: str, from_number: str, message: str) -> str:
        """Send an SMS message. The from_number must be assigned to a user with SMS capability."""
        try:
            body = {"to_number": to_number, "from_number": from_number, "message": message}
            data = await client().post("/phone/sms/messages", json=body)
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="List all Zoom Phone SMS sessions for the account.")
    async def list_sms_sessions(page_size: int | None = 100, next_page_token: str | None = None) -> str:
        """List all SMS sessions."""
        try:
            params: dict[str, Any] = {"page_size": page_size}
            if next_page_token:
                params["next_page_token"] = next_page_token
            data = await client().get("/phone/sms/sessions", params=params)
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Get details of a specific Zoom Phone SMS session.")
    async def get_sms_session(session_id: str) -> str:
        """Get details of a specific SMS session by ID."""
        try:
            data = await client().get(f"/phone/sms/sessions/{session_id}")
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Get a specific SMS message within a session.")
    async def get_sms_message(session_id: str, message_id: str) -> str:
        """Get a specific SMS message by ID within a session."""
        try:
            data = await client().get(f"/phone/sms/sessions/{session_id}/messages/{message_id}")
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="List SMS sessions for a specific Zoom Phone user.")
    async def list_user_sms_sessions(user_id: str, page_size: int | None = 100, next_page_token: str | None = None) -> str:
        """List SMS sessions for a specific user."""
        try:
            params: dict[str, Any] = {"page_size": page_size}
            if next_page_token:
                params["next_page_token"] = next_page_token
            data = await client().get(f"/phone/users/{user_id}/sms/sessions", params=params)
            return json_result(data)
        except Exception as e:
            return error_result(e)

    # ── Recordings ─────────────────────────────────────────────────────────

    @mcp.tool(description="List all Zoom Phone call recordings.")
    async def list_call_recordings(page_size: int | None = 100, next_page_token: str | None = None) -> str:
        """List all call recordings for the account."""
        try:
            params: dict[str, Any] = {"page_size": page_size}
            if next_page_token:
                params["next_page_token"] = next_page_token
            data = await client().get("/phone/recordings", params=params)
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Get download info for a Zoom Phone call recording file.")
    async def download_recording(file_id: str) -> str:
        """Get download URL info for a recording file by file ID."""
        try:
            data = await client().get(f"/phone/recording/download/{file_id}")
            return json_result(data)
        except Exception as e:
            return error_result(e)
