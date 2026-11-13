# Zoom Phone MCP Server

A standalone [Model Context Protocol](https://modelcontextprotocol.io/) server for **Zoom Phone**.

## What This Does

Zoom Phone's REST API has 200+ endpoints for managing telephony: auto receptionists, IVR menus, call queues, voicemail, greetings, audio library, call routing, devices, SMS, and more. Zoom's official MCP servers only handle Meetings, Chat, Whiteboard, Tasks, and Canvas — not Phone.

## Features

| Category | Tools | Highlights |
|---|---|---|
| **Auto Receptionists** | 17 | List, create, update, delete, IVR menu tree CRUD, call handling (business/closed/holiday hours), policies, settings, phone number assignment |
| **Call Queues** | 22 | Full CRUD, member management, call handling per hour type, settings (greetings/prompts), policies, recordings, analytics, custom groups |
| **Audio Library** | 6 | List, get, create (TTS), batch create, update, delete greetings/prompts |
| **Phone Users** | 10 | List, get, update, call handling, policies, settings, phone number assignment |
| **Phone Numbers** | 5 | List (assigned/unassigned/all), get, update, unassign, calling plans |
| **Voicemails** | 7 | Account/user voicemails, details, delete, read status, download |
| **Call History** | 6 | Account/user call history, sync, delete entries, client codes |
| **Devices** | 8 | List, get, add, update, delete, reboot deskphones, assign extensions, sync |
| **Sites** | 7 | List, get, create, update, delete, settings per type |
| **Common Areas** | 7 | List, get, create, update, delete, call handling per hour type |
| **Routing Rules** | 5 | List, get, create, update, delete directory backup routing rules |
| **Shared Line Groups** | 8 | Full CRUD, member management, phone number assignment |
| **SMS & Recordings** | 7 | Send SMS, list sessions, get messages, list/download recordings |
| **Reports** | 4 | Call charges, fax charges, operation logs, SMS charges |

**Total: 117 tools** across the Zoom Phone API.

## Quick Start

### Prerequisites

- A Zoom account with a [Server-to-Server OAuth app](https://developers.zoom.us/docs/integrations/oauth/#server-to-server-oauth/) that has Zoom Phone scopes — see [Scope Profiles](#scope-profiles) below for options
- Python 3.11+ or Docker

### Option 1: Docker (recommended)

```bash
git clone https://github.com/fujitsupolycom/zoom-phone-mcp.git
cd zoom-phone-mcp

# Create .env from template
cp .env.example .env
# Edit .env with your Zoom credentials

docker compose up -d
```

Server runs on `http://localhost:8767/mcp`

### Option 2: pip install

```bash
pip install zoom-phone-mcp

export ZOOM_ACCOUNT_ID="your_account_id"
export ZOOM_CLIENT_ID="your_client_id"
export ZOOM_CLIENT_SECRET="your_client_secret"

# Streamable HTTP (default on 0.0.0.0:8767)
zoom-phone-mcp

# Or stdio mode (for local MCP clients)
zoom-phone-mcp --transport stdio

# Or read-only mode (blocks all POST/PATCH/PUT/DELETE requests)
zoom-phone-mcp --read-only
```

### Option 3: Development

```bash
git clone https://github.com/fujitsupolycom/zoom-phone-mcp.git
cd zoom-phone-mcp
pip install -e ".[dev]"
cp .env.example .env  # fill in credentials
python -m zoom_phone_mcp.server
```

## Connecting Your MCP Client

### Claude Desktop / Cursor

Add to your MCP client config:

```json
{
  "mcpServers": {
    "zoom-phone": {
      "url": "http://localhost:8767/mcp"
    }
  }
}
```

### Hermes Agent

```bash
hermes mcp add zoom-phone --url http://localhost:8767/mcp
hermes mcp test zoom-phone
```

## Authentication

This server uses Zoom's **Server-to-Server OAuth** flow (no user interaction needed). You need:

1. A Server-to-Server OAuth app on the [Zoom App Marketplace](https://marketplace.zoom.us/)
2. The app's Account ID, Client ID, and Client Secret
3. Phone scopes assigned to the app (see below)

The server automatically fetches and refreshes access tokens (1-hour expiry).

### Scope Profiles

Zoom supports [granular OAuth scopes](https://developers.zoom.us/docs/integrations/oauth-scopes-granular/) for Phone. Server-to-Server apps use the `:admin` suffix. Choose a profile based on what you need:

#### Full Admin (all tools work)

```
phone:read:admin
phone:write:admin
```

These two legacy scopes grant read/write access to most of the Phone API. However, Zoom requires additional granular scopes for certain call handling and settings sub-resources, even when the legacy admin scopes are present. To ensure **every** tool works, add these granular scopes as well:

<details>
<summary>Additional granular scopes needed for full coverage (click to expand)</summary>

```
phone:read:auto_receptionist_call_handling_setting:admin
phone:read:auto_receptionist_setting:admin
phone:read:call_queue_call_handling_setting:admin
phone:read:call_queue_setting:admin
phone:read:call_queue_policy:admin
phone:read:call_queue_custom_group:admin
phone:read:user_call_handling_setting:admin
phone:read:common_area_call_handling_setting:admin
```

</details>

Without these, list/get calls for auto receptionist settings, call queue settings/policies/custom groups, user call handling, and common area call handling will return `Insicient scope` errors. All other tools work with just the two legacy scopes.

#### Read-Only (all list/get tools, no create/update/delete)

Add only the `phone:read:*:admin` granular scopes for resources you want to query. Full list:

<details>
<summary>All read-only scopes (click to expand)</summary>

```
phone:read:list_auto_receptionists:admin
phone:read:auto_receptionist:admin
phone:read:auto_receptionist_setting:admin
phone:read:auto_receptionist_call_handling_setting:admin
phone:read:auto_receptionist_policy:admin
phone:read:auto_receptionist_ivr:admin
phone:read:list_call_queues:admin
phone:read:call_queue:admin
phone:read:call_queue_setting:admin
phone:read:call_queue_call_handling_setting:admin
phone:read:call_queue_policy:admin
phone:read:list_call_queue_members:admin
phone:read:list_call_queue_recordings:admin
phone:read:call_queue_custom_group:admin
phone:read:list_audios:admin
phone:read:audio:admin
phone:read:list_users:admin
phone:read:user:admin
phone:read:user_call_handling_setting:admin
phone:read:user_policy:admin
phone:read:user_setting:admin
phone:read:list_numbers:admin
phone:read:numbers:admin
phone:read:list_calling_plans:admin
phone:read:list_voicemails:admin
phone:read:voicemail:admin
phone:read:list_call_logs:admin
phone:read:call_log:admin
phone:read:list_devices:admin
phone:read:device:admin
phone:read:list_sites:admin
phone:read:site:admin
phone:read:site_setting:admin
phone:read:common_area:admin
phone:read:list_common_area_settings:admin
phone:read:common_area_call_handling_setting:admin
phone:read:list_routing_rules:admin
phone:read:routing_rule:admin
phone:read:list_shared_line_groups:admin
phone:read:shared_line_group:admin
phone:read:shared_line_group_setting:admin
phone:read:shared_line_group_call_handling_setting:admin
phone:read:shared_line_group_policy:admin
phone:read:list_sms_sessions:admin
phone:read:sms_session:admin
phone:read:sms_message:admin
phone:read:call_charges:admin
phone:read:fax_charges:admin
phone:read:operation_logs:admin
phone:read:sms_charges:admin
```

</details>

#### Call Routing Admin (manage call flow, read-only on users/devices/billing)

Write access to auto receptionists, call queues, audio library, common areas, routing rules, and shared line groups. Read-only on everything else. Useful for a team that manages IVR and call routing but shouldn't touch user provisioning or billing.

<details>
<summary>Scopes for this profile (click to expand)</summary>

```
# Read + write: call routing resources
phone:read:auto_receptionist:admin
phone:write:auto_receptionist:admin
phone:read:auto_receptionist_setting:admin
phone:write:auto_receptionist_setting:admin
phone:delete:auto_receptionist_setting:admin
phone:read:auto_receptionist_call_handling_setting:admin
phone:update:auto_receptionist_call_handling_setting:admin
phone:read:auto_receptionist_policy:admin
phone:write:auto_receptionist_policy:admin
phone:update:auto_receptionist_policy:admin
phone:read:auto_receptionist_ivr:admin
phone:update:auto_receptionist_ivr:admin
phone:write:auto_receptionist_number:admin
phone:delete:auto_receptionist_number:admin
phone:read:list_auto_receptionists:admin

phone:read:list_call_queues:admin
phone:read:call_queue:admin
phone:update:call_queue:admin
phone:write:call_queue:admin
phone:delete:call_queue:admin
phone:read:call_queue_setting:admin
phone:write:call_queue_setting:admin
phone:update:call_queue_setting:admin
phone:delete:call_queue_setting:admin
phone:read:call_queue_call_handling_setting:admin
phone:update:call_queue_call_handling_setting:admin
phone:read:call_queue_policy:admin
phone:write:call_queue_policy:admin
phone:update:call_queue_policy:admin
phone:read:list_call_queue_members:admin
phone:write:call_queue_member:admin
phone:delete:call_queue_member:admin
phone:read:list_call_queue_recordings:admin
phone:read:call_queue_custom_group:admin
phone:write:call_queue_custom_group:admin
phone:update:call_queue_custom_group:admin
phone:delete:call_queue_custom_group:admin
phone:write:call_queue_number:admin
phone:delete:call_queue_number:admin

phone:read:list_audios:admin
phone:read:audio:admin
phone:write:audio:admin
phone:update:audio:admin
phone:delete:audio:admin
phone:write:batch_audios:admin

phone:read:common_area:admin
phone:write:common_area:admin
phone:update:common_area:admin
phone:delete:common_area:admin
phone:read:list_common_area_settings:admin
phone:read:common_area_call_handling_setting:admin
phone:update:common_area_call_handling_setting:admin

phone:read:list_routing_rules:admin
phone:read:routing_rule:admin
phone:write:routing_rule:admin
phone:update:routing_rule:admin
phone:delete:routing_rule:admin

phone:read:list_shared_line_groups:admin
phone:read:shared_line_group:admin
phone:write:shared_line_group:admin
phone:update:shared_line_group:admin
phone:delete:shared_line_group:admin
phone:read:shared_line_group_setting:admin
phone:write:shared_line_group_setting:admin
phone:update:shared_line_group_setting:admin
phone:delete:shared_line_group_setting:admin
phone:read:shared_line_group_call_handling_setting:admin
phone:update:shared_line_group_call_handling_setting:admin
phone:read:shared_line_group_policy:admin
phone:write:shared_line_group_policy:admin
phone:update:shared_line_group_policy:admin
phone:delete:shared_line_group_policy:admin
phone:write:shared_line_member:admin
phone:delete:shared_line_member:admin
phone:write:shared_line_group_number:admin
phone:delete:shared_line_group_number:admin

# Read-only: everything else
phone:read:list_users:admin
phone:read:user:admin
phone:read:user_call_handling_setting:admin
phone:read:user_policy:admin
phone:read:user_setting:admin
phone:read:list_numbers:admin
phone:read:numbers:admin
phone:read:list_calling_plans:admin
phone:read:list_voicemails:admin
phone:read:voicemail:admin
phone:read:list_call_logs:admin
phone:read:call_log:admin
phone:read:list_devices:admin
phone:read:device:admin
phone:read:list_sites:admin
phone:read:site:admin
phone:read:site_setting:admin
phone:read:call_charges:admin
phone:read:fax_charges:admin
phone:read:operation_logs:admin
phone:read:sms_charges:admin
```

</details>

## Tool Examples

### List auto receptionists
```
list_auto_receptionists(page_size=100)
```

### Get IVR menu tree
```
get_auto_receptionist_ivr(auto_receptionist_id="abc123")
```

### Update IVR routing
```
update_auto_receptionist_ivr(
  auto_receptionist_id="abc123",
  ivr_settings={"key_presses": [{"digit": "1", "action_type": "route_to_user", "target": "user@example.com"}]}
)
```

### List call queues
```
list_call_queues()
```

### Update holiday hours routing for a call queue
```
update_queue_call_handling(
  call_queue_id="abc123",
  hour_type="holiday_hours",
  call_handling_settings={"call_handling": [{"action_type": "disconnect"}]}
)
```

### Create a TTS greeting
```
add_audio_item(
  user_id="me@company.com",
  name="Holiday Greeting",
  text="Thank you for calling. We are closed for the holiday.",
  voice_accent="Joanna-Female",
  voice_language="en-US"
)
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Run with hot reload
python -m zoom_phone_mcp.server
```

## Tech Stack

- **[MCP SDK](https://github.com/modelcontextprotocol/python-sdk)** — FastMCP with Streamable HTTP transport
- **[httpx](https://www.python-httpx.org/)** — async HTTP client for Zoom API
- **[uvicorn](https://www.uvicorn.org/)** — ASGI server
- **[Pydantic](https://docs.pydantic.dev/)** — data validation

## License

MIT — see [LICENSE](LICENSE)

## Contributing

PRs welcome.
