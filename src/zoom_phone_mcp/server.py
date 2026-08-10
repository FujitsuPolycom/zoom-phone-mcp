"""FastMCP server for Zoom Phone — entry point and tool registration."""

import json
import logging
import os
from contextlib import asynccontextmanager
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from .auth import ZoomAuth
from .client import ZoomPhoneClient, ZoomAPIError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Shared state — set during lifespan
_auth: ZoomAuth | None = None
_client: ZoomPhoneClient | None = None


def get_client() -> ZoomPhoneClient:
    if _client is None:
        raise RuntimeError("Server not initialized — lifespan didn't start client")
    return _client


@asynccontextmanager
async def app_lifespan(server: FastMCP):
    """Manage ZoomAuth + ZoomPhoneClient lifecycle."""
    global _auth, _client
    logger.info("Starting Zoom Phone MCP server...")
    _auth = ZoomAuth()
    _client = ZoomPhoneClient(_auth)
    try:
        yield
    finally:
        if _client:
            await _client.__aexit__(None, None, None)
        logger.info("Zoom Phone MCP server stopped.")


mcp = FastMCP(
    "zoom-phone",
    lifespan=app_lifespan,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)


# ── Helper ──────────────────────────────────────────────────────────────────

def _json_result(data: Any) -> str:
    """Serialize API response to JSON string for MCP tool return."""
    return json.dumps(data, indent=2, default=str)


def _error_result(err: Exception) -> str:
    """Format an error as a readable JSON string."""
    if isinstance(err, ZoomAPIError):
        return json.dumps({
            "error": True,
            "status_code": err.status_code,
            "message": err.message,
            "details": err.details,
        }, indent=2, default=str)
    return json.dumps({"error": True, "message": str(err)}, indent=2)


# ── Tool Registration ───────────────────────────────────────────────────────

def register_all_tools():
    """Import and register all tool modules."""
    from .tools.auto_receptionists import register as _ar
    from .tools.call_queues import register as _cq
    from .tools.audio_library import register as _al
    from .tools.phone_users import register as _pu
    from .tools.phone_numbers import register as _pn
    from .tools.voicemails import register as _vm
    from .tools.call_history import register as _ch
    from .tools.devices import register as _dev
    from .tools.sites import register as _st
    from .tools.common_areas import register as _ca
    from .tools.routing_rules import register as _rr
    from .tools.shared_line_groups import register as _slg
    from .tools.sms import register as _sms
    from .tools.reports import register as _rep

    for mod in [_ar, _cq, _al, _pu, _pn, _vm, _ch, _dev, _st, _ca, _rr, _slg, _sms, _rep]:
        mod(mcp, get_client, _json_result, _error_result)


register_all_tools()


# ── Server Info Tool ────────────────────────────────────────────────────────

@mcp.tool(description="Get Zoom Phone MCP server info and available tool categories.")
async def server_info() -> str:
    """Returns server version, auth status, and list of tool categories."""
    info = {
        "server": "zoom-phone-mcp",
        "version": "0.1.0",
        "api_base": "https://api.zoom.us/v2",
        "tool_categories": [
            "auto_receptionists", "call_queues", "audio_library",
            "phone_users", "phone_numbers", "voicemails",
            "call_history", "devices", "sites", "common_areas",
            "routing_rules", "shared_line_groups", "sms", "reports",
        ],
    }
    return _json_result(info)


# ── Launch ─────────────────────────────────────────────────────────────────

def main():
    import uvicorn
    host = os.environ.get("ZOOM_PHONE_MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("ZOOM_PHONE_MCP_PORT", "8767"))
    app = mcp.streamable_http_app()
    logger.info("Launching Zoom Phone MCP on %s:%d", host, port)
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
