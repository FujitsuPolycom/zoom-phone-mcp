"""Zoom Phone Auto Receptionists MCP tool module.

Registers MCP tools for managing Zoom Phone auto receptionists, including
IVR configuration, call handling, policies, settings, and phone number
assignment.
"""

from __future__ import annotations

from typing import Any

from ..client import normalize_phone_numbers


def register(mcp: Any, get_client: Any, json_result: Any, error_result: Any) -> None:
    """Register all auto receptionist MCP tools on the FastMCP instance."""

    # ------------------------------------------------------------------
    # 1. list_auto_receptionists
    # ------------------------------------------------------------------
    @mcp.tool()
    async def list_auto_receptionists(
        site_id: str | None = None,
        page_size: int | None = 100,
        next_page_token: str | None = None,
    ) -> str:
        """List all auto receptionists for the Zoom Phone account.

        Supports pagination and optional filtering by site.
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
            data = await client.get("/phone/auto_receptionists", params=params)
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ------------------------------------------------------------------
    # 2. get_auto_receptionist
    # ------------------------------------------------------------------
    @mcp.tool()
    async def get_auto_receptionist(auto_receptionist_id: str) -> str:
        """Get details of a specific auto receptionist by ID."""
        try:
            client = get_client()
            data = await client.get(
                f"/phone/auto_receptionists/{auto_receptionist_id}"
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ------------------------------------------------------------------
    # 3. create_auto_receptionist
    # ------------------------------------------------------------------
    @mcp.tool()
    async def create_auto_receptionist(
        name: str,
        extension_number: int | None = None,
        site_id: str | None = None,
    ) -> str:
        """Create a new auto receptionist.

        Requires a display name. Optional extension number and site ID
        can be provided to assign the receptionist to a specific site
        with a chosen extension.
        """
        try:
            client = get_client()
            body: dict[str, Any] = {"name": name}
            if extension_number is not None:
                body["extension_number"] = extension_number
            if site_id is not None:
                body["site_id"] = site_id
            data = await client.post("/phone/auto_receptionists", json=body)
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ------------------------------------------------------------------
    # 4. update_auto_receptionist
    # ------------------------------------------------------------------
    @mcp.tool()
    async def update_auto_receptionist(
        auto_receptionist_id: str,
        name: str | None = None,
        extension_number: int | None = None,
        site_id: str | None = None,
    ) -> str:
        """Update an existing auto receptionist's properties."""
        try:
            client = get_client()
            body: dict[str, Any] = {}
            if name is not None:
                body["name"] = name
            if extension_number is not None:
                body["extension_number"] = extension_number
            if site_id is not None:
                body["site_id"] = site_id
            data = await client.patch(
                f"/phone/auto_receptionists/{auto_receptionist_id}", json=body
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ------------------------------------------------------------------
    # 5. delete_auto_receptionist
    # ------------------------------------------------------------------
    @mcp.tool()
    async def delete_auto_receptionist(auto_receptionist_id: str) -> str:
        """Delete an auto receptionist by ID."""
        try:
            client = get_client()
            data = await client.delete(
                f"/phone/auto_receptionists/{auto_receptionist_id}"
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ------------------------------------------------------------------
    # 6. get_auto_receptionist_ivr
    # ------------------------------------------------------------------
    @mcp.tool()
    async def get_auto_receptionist_ivr(auto_receptionist_id: str) -> str:
        """Get the IVR menu tree for an auto receptionist.

        Returns the configured key-press-to-destination mappings.
        """
        try:
            client = get_client()
            data = await client.get(
                f"/phone/auto_receptionists/{auto_receptionist_id}/ivr"
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ------------------------------------------------------------------
    # 7. update_auto_receptionist_ivr
    # ------------------------------------------------------------------
    @mcp.tool()
    async def update_auto_receptionist_ivr(
        auto_receptionist_id: str,
        ivr_settings: dict,
    ) -> str:
        """Update the IVR menu tree for an auto receptionist.

        The ``ivr_settings`` dict describes the full IVR menu tree mapping
        key presses to destinations (e.g. extensions, voicemail, external
        numbers, sub-menus).
        """
        try:
            client = get_client()
            data = await client.patch(
                f"/phone/auto_receptionists/{auto_receptionist_id}/ivr",
                json=ivr_settings,
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ------------------------------------------------------------------
    # 8. get_ar_call_handling
    # ------------------------------------------------------------------
    @mcp.tool()
    async def get_ar_call_handling(auto_receptionist_id: str) -> str:
        """Get call handling settings for an auto receptionist."""
        try:
            client = get_client()
            data = await client.get(
                f"/phone/auto_receptionists/{auto_receptionist_id}/call_handling/settings"
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ------------------------------------------------------------------
    # 9. update_ar_call_handling
    # ------------------------------------------------------------------
    @mcp.tool()
    async def update_ar_call_handling(
        auto_receptionist_id: str,
        hour_type: str,
        call_handling_settings: dict,
    ) -> str:
        """Update call handling settings for an auto receptionist.

        ``hour_type`` must be one of: ``business_hours``, ``closed_hours``,
        or ``holiday_hours``.
        """
        try:
            client = get_client()
            data = await client.patch(
                f"/phone/auto_receptionists/{auto_receptionist_id}/call_handling/settings/{hour_type}",
                json=call_handling_settings,
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ------------------------------------------------------------------
    # 10. get_ar_policies
    # ------------------------------------------------------------------
    @mcp.tool()
    async def get_ar_policies(auto_receptionist_id: str) -> str:
        """Get policies for an auto receptionist."""
        try:
            client = get_client()
            data = await client.get(
                f"/phone/auto_receptionists/{auto_receptionist_id}/policies"
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ------------------------------------------------------------------
    # 11. update_ar_policies
    # ------------------------------------------------------------------
    @mcp.tool()
    async def update_ar_policies(
        auto_receptionist_id: str,
        policies: dict,
    ) -> str:
        """Update policies for an auto receptionist."""
        try:
            client = get_client()
            data = await client.patch(
                f"/phone/auto_receptionists/{auto_receptionist_id}/policies",
                json=policies,
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ------------------------------------------------------------------
    # 12. get_ar_settings
    # ------------------------------------------------------------------
    @mcp.tool()
    async def get_ar_settings(auto_receptionist_id: str) -> str:
        """Get all settings for an auto receptionist."""
        try:
            client = get_client()
            data = await client.get(
                f"/phone/auto_receptionists/{auto_receptionist_id}/settings"
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ------------------------------------------------------------------
    # 13. update_ar_settings
    # ------------------------------------------------------------------
    @mcp.tool()
    async def update_ar_settings(
        auto_receptionist_id: str,
        setting_type: str,
        settings: dict,
    ) -> str:
        """Update settings of a specific type for an auto receptionist."""
        try:
            client = get_client()
            data = await client.patch(
                f"/phone/auto_receptionists/{auto_receptionist_id}/settings/{setting_type}",
                json=settings,
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ------------------------------------------------------------------
    # 14. add_ar_setting
    # ------------------------------------------------------------------
    @mcp.tool()
    async def add_ar_setting(
        auto_receptionist_id: str,
        setting_type: str,
        settings: dict,
    ) -> str:
        """Add a new setting entry of a specific type for an auto receptionist."""
        try:
            client = get_client()
            data = await client.post(
                f"/phone/auto_receptionists/{auto_receptionist_id}/settings/{setting_type}",
                json=settings,
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ------------------------------------------------------------------
    # 15. delete_ar_setting
    # ------------------------------------------------------------------
    @mcp.tool()
    async def delete_ar_setting(
        auto_receptionist_id: str,
        setting_type: str,
    ) -> str:
        """Delete settings of a specific type for an auto receptionist."""
        try:
            client = get_client()
            data = await client.delete(
                f"/phone/auto_receptionists/{auto_receptionist_id}/settings/{setting_type}"
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ------------------------------------------------------------------
    # 16. assign_ar_phone_numbers
    # ------------------------------------------------------------------
    @mcp.tool()
    async def assign_ar_phone_numbers(
        auto_receptionist_id: str,
        phone_numbers: list[str | dict[str, Any]],
    ) -> str:
        """Assign phone numbers to an auto receptionist.

        Each item in ``phone_numbers`` can be an E.164 number string (e.g.
        '+12058945717'), a phone number ID string, or a dict with 'id'/'number'.
        """
        try:
            client = get_client()
            body = {"phone_numbers": normalize_phone_numbers(phone_numbers)}
            data = await client.post(
                f"/phone/auto_receptionists/{auto_receptionist_id}/phone_numbers",
                json=body,
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ------------------------------------------------------------------
    # 17. unassign_ar_phone_numbers
    # ------------------------------------------------------------------
    @mcp.tool()
    async def unassign_ar_phone_numbers(
        auto_receptionist_id: str,
        phone_number_id: str | None = None,
    ) -> str:
        """Unassign a specific phone number (or all phone numbers if phone_number_id is omitted) from an auto receptionist."""
        try:
            client = get_client()
            path = f"/phone/auto_receptionists/{auto_receptionist_id}/phone_numbers"
            if phone_number_id:
                path = f"{path}/{phone_number_id}"
            data = await client.delete(path)
            return json_result(data)
        except Exception as err:
            return error_result(err)
