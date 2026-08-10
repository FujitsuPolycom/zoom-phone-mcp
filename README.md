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

- A Zoom account with a [Server-to-Server OAuth app](https://developers.zoom.us/docs/integrations/oauth/#server-to-server-oauth/) that has Zoom Phone scopes (`phone:read:admin`, `phone:write:admin`)
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

python -m zoom_phone_mcp.server
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
2. Scopes: `phone:read:admin` and `phone:write:admin` (add granular scopes as needed)
3. The app's Account ID, Client ID, and Client Secret

The server automatically fetches and refreshes access tokens (1-hour expiry).

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
