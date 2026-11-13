"""SMS & Recordings — Zoom Phone SMS messaging and call recording tools."""

from typing import Any

def register(mcp: Any, get_client, json_result, error_result):
    client = get_client

    # ── SMS ───────────────────────────────────────────────────────────────

    @mcp.tool(description="Send an SMS message from a Zoom Phone number.")
    async def send_sms(
        to_number: str | list[str],
        from_number: str,
        message: str,
        sender_user_id: str | None = None,
    ) -> str:
        """Send an SMS message via POST /phone/sms/messages.

        Args:
            to_number: Recipient phone number in E.164 format (or list of recipient E.164 numbers).
            from_number: Sender's SMS-capable Zoom Phone number in E.164 format.
            message: The text message body to send.
            sender_user_id: Optional Zoom user ID of the sender owning from_number.
        """
        try:
            recipients = [to_number] if isinstance(to_number, str) else list(to_number)
            sender: dict[str, str] = {"phone_number": from_number}
            if sender_user_id:
                sender["user_id"] = sender_user_id
            body: dict[str, Any] = {
                "sender": sender,
                "to_members": [{"phone_number": num} for num in recipients],
                "message": message,
            }
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
