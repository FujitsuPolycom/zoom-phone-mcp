"""Zoom Phone audio library MCP tools.

Tools for managing Zoom Phone audio library items (greetings, prompts,
hold music, etc.) — list, get, add (single + batch), update, and delete.
"""

from __future__ import annotations

from typing import Any

def register(mcp: Any, get_client: Any, json_result: Any, error_result: Any) -> None:
    """Register all Zoom Phone audio-library tools with the MCP server."""

    @mcp.tool()
    def list_audio_items(
        user_id: str,
        page_size: int | None = None,
        next_page_token: str | None = None,
    ) -> str:
        """List audio library items for a Zoom Phone user.

        Retrieves all audio items (greetings, prompts, etc.) belonging to
        the specified user's audio library.

        Args:
            user_id: The Zoom user ID (e.g. 'me' or a specific user ID).
            page_size: Number of results per page (max 300). Defaults to server default.
            next_page_token: Pagination token from a previous response.

        Returns:
            JSON string with the list of audio items or an error message.
        """
        try:
            client = get_client()
            params: dict[str, Any] = {}
            if page_size is not None:
                params["page_size"] = page_size
            if next_page_token is not None:
                params["next_page_token"] = next_page_token

            data = client.get(f"/phone/users/{user_id}/audios", params=params)
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    def get_audio_item(audio_id: str) -> str:
        """Retrieve a single audio library item by its ID.

        Fetches the details of a specific audio item from the Zoom Phone
        audio library, including its name, text content, and TTS settings.

        Args:
            audio_id: The unique identifier of the audio item.

        Returns:
            JSON string with the audio item details or an error message.
        """
        try:
            client = get_client()
            data = client.get(f"/phone/audios/{audio_id}")
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    def add_audio_item(
        user_id: str,
        name: str,
        text: str,
        voice_accent: str | None = None,
        voice_language: str | None = None,
    ) -> str:
        """Add a new audio item to a user's audio library.

        Creates a new text-to-speech audio item. The ``text`` field is the
        TTS message content (max 3000 characters). Optional voice settings
        control the accent and language of the generated speech.

        Args:
            user_id: The Zoom user ID who will own the audio item.
            name: Display name for the audio item.
            text: The TTS message text (max 3000 characters).
            voice_accent: Voice accent, e.g. 'Joanna-Female'.
            voice_language: Voice language code, e.g. 'en-US'.

        Returns:
            JSON string with the created audio item or an error message.
        """
        try:
            client = get_client()
            body: dict[str, Any] = {"name": name, "text": text}
            if voice_accent is not None:
                body["voice_accent"] = voice_accent
            if voice_language is not None:
                body["voice_language"] = voice_language

            data = client.post(f"/phone/users/{user_id}/audios", json_body=body)
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    def add_audio_items_batch(
        user_id: str,
        audio_items: list[dict],
    ) -> str:
        """Add multiple audio items to a user's audio library in a single request.

        Each entry in ``audio_items`` should contain:
            - name (str): Display name for the audio item.
            - text (str): TTS message text (max 3000 chars).
            - voice_accent (str, optional): e.g. 'Joanna-Female'.
            - voice_language (str, optional): e.g. 'en-US'.

        Args:
            user_id: The Zoom user ID who will own the audio items.
            audio_items: List of dicts, each describing an audio item.

        Returns:
            JSON string with the batch creation result or an error message.
        """
        try:
            client = get_client()
            body: dict[str, Any] = {"audio_items": audio_items}

            data = client.post(
                f"/phone/users/{user_id}/audios/batch", json_body=body
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    def update_audio_item(
        audio_id: str,
        name: str | None = None,
        text: str | None = None,
    ) -> str:
        """Update an existing audio library item.

        Only the provided (non-None) fields are updated. The audio item's
        name and/or TTS text can be modified.

        Args:
            audio_id: The unique identifier of the audio item.
            name: New display name for the audio item (optional).
            text: New TTS message text, max 3000 chars (optional).

        Returns:
            JSON string with the updated audio item or an error message.
        """
        try:
            client = get_client()
            body: dict[str, Any] = {}
            if name is not None:
                body["name"] = name
            if text is not None:
                body["text"] = text

            data = client.patch(f"/phone/audios/{audio_id}", json_body=body)
            return json_result(data)
        except Exception as err:
            return error_result(err)

    @mcp.tool()
    def delete_audio_item(audio_id: str) -> str:
        """Delete an audio library item.

        Permanently removes the specified audio item from the Zoom Phone
        audio library. This action cannot be undone.

        Args:
            audio_id: The unique identifier of the audio item to delete.

        Returns:
            JSON string confirming deletion or an error message.
        """
        try:
            client = get_client()
            data = client.delete(f"/phone/audios/{audio_id}")
            return json_result(data)
        except Exception as err:
            return error_result(err)
