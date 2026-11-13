"""MCP tools for Zoom Phone device / deskphone management."""

from typing import Any

def register(mcp: Any, get_client: Any, json_result: Any, error_result: Any) -> None:
    """Register Zoom Phone device management tools on the MCP server."""

    # ── 1. list_devices ─────────────────────────────────────────────────────

    @mcp.tool(
        description=(
            "List Zoom Phone devices (deskphones). "
            "Returns a paginated list of all devices in the account."
        ),
    )
    async def list_devices(
        page_size: int | None = 100,
        next_page_token: str | None = None,
    ) -> str:
        """Retrieve a paginated list of Zoom Phone devices.

        Args:
            page_size: Number of results per page (default 100, max 300).
            next_page_token: Token from a previous response to fetch the next page.

        Returns:
            JSON string with device list and pagination metadata.
        """
        try:
            client = get_client()
            params: dict[str, Any] = {"page_size": page_size}
            if next_page_token:
                params["next_page_token"] = next_page_token
            data = await client.get("/phone/devices", params=params)
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ── 2. get_device ───────────────────────────────────────────────────────

    @mcp.tool(
        description=(
            "Get details of a single Zoom Phone device by its device ID. "
            "Returns MAC address, model, provisioning status, and assigned extension."
        ),
    )
    async def get_device(device_id: str) -> str:
        """Retrieve details for a specific Zoom Phone device.

        Args:
            device_id: The unique identifier of the device.

        Returns:
            JSON string with the device's details.
        """
        try:
            client = get_client()
            data = await client.get(f"/phone/devices/{device_id}")
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ── 3. add_device ───────────────────────────────────────────────────────

    @mcp.tool(
        description=(
            "Add a new deskphone device to the Zoom Phone account. "
            "Requires a MAC address and device model. Optionally specify display_name, "
            "device_type (vendor), site, user/assigned_to, or extension."
        ),
    )
    async def add_device(
        mac_address: str,
        model: str,
        display_name: str | None = None,
        device_type: str | None = None,
        site_id: str | None = None,
        user_id: str | None = None,
        assigned_to: str | None = None,
        extension_id: str | None = None,
        assignee_extension_ids: list[str] | None = None,
        provision_template_id: str | None = None,
    ) -> str:
        """Create a new Zoom Phone device.

        Args:
            mac_address: MAC address of the physical deskphone.
            model: Device model identifier (e.g. "Yealink-T54W" or "T54W").
            display_name: Display name for the deskphone (defaults to "{model}-{mac_address}").
            device_type: Device manufacturer/vendor type (e.g. "Yealink", "Poly", "Cisco").
            site_id: ID of the site to assign the device to.
            user_id: ID or email of the user to assign the device to (alias for assigned_to).
            assigned_to: Extension ID or user ID/email to assign the device to.
            extension_id: ID of the extension to assign the device to.
            assignee_extension_ids: List of extension IDs to assign the device to.
            provision_template_id: Provisioning template ID for the device.

        Returns:
            JSON string with the created device details.
        """
        try:
            client = get_client()
            body: dict[str, Any] = {
                "display_name": display_name or f"{model}-{mac_address}",
                "mac_address": mac_address,
                "model": model,
            }
            if device_type is not None:
                body["type"] = device_type
            if site_id is not None:
                body["site_id"] = site_id
            resolved_assigned_to = assigned_to if assigned_to is not None else user_id
            if resolved_assigned_to is not None:
                body["assigned_to"] = resolved_assigned_to
            if assignee_extension_ids is not None:
                body["assignee_extension_ids"] = assignee_extension_ids
            elif extension_id is not None:
                body["assignee_extension_ids"] = [extension_id]
            if provision_template_id is not None:
                body["provision_template_id"] = provision_template_id
            data = await client.post("/phone/devices", json=body)
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ── 4. update_device ───────────────────────────────────────────────────

    @mcp.tool(
        description=(
            "Update an existing Zoom Phone device's display name, MAC address, or assignment. "
            "Only the provided fields are updated (PATCH semantics)."
        ),
    )
    async def update_device(
        device_id: str,
        mac_address: str | None = None,
        name: str | None = None,
        display_name: str | None = None,
        assigned_to: str | None = None,
        site_id: str | None = None,
        provision_template_id: str | None = None,
    ) -> str:
        """Update a Zoom Phone device's attributes.

        Args:
            device_id: The unique identifier of the device to update.
            mac_address: New MAC address for the device.
            name: Alias for display_name.
            display_name: New display name for the device.
            assigned_to: User ID, email, or extension ID to assign the device to.
            site_id: New site ID for the device.
            provision_template_id: Provisioning template ID.

        Returns:
            JSON string with the updated device details.
        """
        try:
            client = get_client()
            body: dict[str, Any] = {}
            if mac_address is not None:
                body["mac_address"] = mac_address
            resolved_name = display_name if display_name is not None else name
            if resolved_name is not None:
                body["display_name"] = resolved_name
            if assigned_to is not None:
                body["assigned_to"] = assigned_to
            if site_id is not None:
                body["site_id"] = site_id
            if provision_template_id is not None:
                body["provision_template_id"] = provision_template_id
            data = await client.patch(f"/phone/devices/{device_id}", json=body)
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ── 5. delete_device ───────────────────────────────────────────────────

    @mcp.tool(
        description=(
            "Delete a Zoom Phone device by its device ID. "
            "This unassigns and removes the deskphone from the account."
        ),
    )
    async def delete_device(device_id: str) -> str:
        """Delete a Zoom Phone device.

        Args:
            device_id: The unique identifier of the device to delete.

        Returns:
            JSON string confirming deletion (empty on 204).
        """
        try:
            client = get_client()
            data = await client.delete(f"/phone/devices/{device_id}")
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ── 6. reboot_device ───────────────────────────────────────────────────

    @mcp.tool(
        description=(
            "Reboot a Zoom Phone deskphone remotely. "
            "The device will restart and re-provision from the Zoom Phone configuration."
        ),
    )
    async def reboot_device(device_id: str) -> str:
        """Reboot a Zoom Phone device.

        Args:
            device_id: The unique identifier of the device to reboot.

        Returns:
            JSON string confirming the reboot request.
        """
        try:
            client = get_client()
            data = await client.post(f"/phone/devices/{device_id}/reboot")
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ── 7. assign_device_extension ─────────────────────────────────────────

    @mcp.tool(
        description=(
            "Assign an extension to a Zoom Phone device. "
            "This associates the deskphone with a specific phone extension for inbound/outbound calling."
        ),
    )
    async def assign_device_extension(
        device_id: str,
        extension_id: str,
    ) -> str:
        """Assign an extension to a Zoom Phone device.

        Args:
            device_id: The unique identifier of the device.
            extension_id: The ID of the extension to assign.

        Returns:
            JSON string with the assignment result.
        """
        try:
            client = get_client()
            body: dict[str, Any] = {"extension_id": extension_id}
            data = await client.post(
                f"/phone/devices/{device_id}/extensions", json=body
            )
            return json_result(data)
        except Exception as err:
            return error_result(err)

    # ── 8. sync_deskphones ─────────────────────────────────────────────────

    @mcp.tool(
        description=(
            "Trigger a synchronization of all deskphones in the Zoom Phone account. "
            "This pushes configuration updates to all provisioned devices."
        ),
    )
    async def sync_deskphones() -> str:
        """Synchronize all Zoom Phone deskphones.

        Returns:
            JSON string confirming the sync request.
        """
        try:
            client = get_client()
            data = await client.post("/phone/devices/sync")
            return json_result(data)
        except Exception as err:
            return error_result(err)
