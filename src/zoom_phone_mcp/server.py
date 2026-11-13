"""FastMCP server for Zoom Phone — entry point and tool registration."""

from __future__ import annotations

import argparse
from contextlib import asynccontextmanager
import json
import logging
import os
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from . import __version__
from .auth import API_BASE, ZoomAuth, load_dotenv_if_present
from .client import ZoomAPIError, ZoomPhoneClient, is_read_only_env

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Shared state — set during lifespan or lazy-initialized via get_client()
_auth: ZoomAuth | None = None
_client: ZoomPhoneClient | None = None


def get_client() -> ZoomPhoneClient:
    """Return the active ZoomPhoneClient, lazily initializing if needed."""
    global _auth, _client
    if _client is None:
        _auth = ZoomAuth()
        _client = ZoomPhoneClient(_auth)
    return _client


@asynccontextmanager
async def app_lifespan(server: FastMCP):
    """Manage ZoomAuth + ZoomPhoneClient lifecycle."""
    global _auth, _client
    logger.info("Starting Zoom Phone MCP server (v%s)...", __version__)
    _auth = ZoomAuth()
    _client = ZoomPhoneClient(_auth)
    try:
        yield
    finally:
        if _client:
            await _client.close()
            _client = None
        logger.info("Zoom Phone MCP server stopped.")


mcp = FastMCP(
    "zoom-phone",
    lifespan=app_lifespan,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)


# ── Helpers ─────────────────────────────────────────────────────────────────

def _json_result(data: Any) -> str:
    """Serialize API response to JSON string for MCP tool return."""
    return json.dumps(data, indent=2, default=str)


def _error_result(err: Exception) -> str:
    """Format an error as a readable JSON string."""
    if isinstance(err, ZoomAPIError):
        return json.dumps(
            {
                "error": True,
                "status_code": err.status_code,
                "message": err.message,
                "details": err.details,
            },
            indent=2,
            default=str,
        )
    return json.dumps({"error": True, "message": str(err)}, indent=2)


# ── Tool Registration ───────────────────────────────────────────────────────

def register_all_tools() -> None:
    """Import and register all tool modules."""
    from .tools.audio_library import register as _al
    from .tools.auto_receptionists import register as _ar
    from .tools.call_history import register as _ch
    from .tools.call_queues import register as _cq
    from .tools.common_areas import register as _ca
    from .tools.devices import register as _dev
    from .tools.phone_numbers import register as _pn
    from .tools.phone_users import register as _pu
    from .tools.reports import register as _rep
    from .tools.routing_rules import register as _rr
    from .tools.shared_line_groups import register as _slg
    from .tools.sites import register as _st
    from .tools.sms import register as _sms
    from .tools.voicemails import register as _vm

    for mod in [_ar, _cq, _al, _pu, _pn, _vm, _ch, _dev, _st, _ca, _rr, _slg, _sms, _rep]:
        mod(mcp, get_client, _json_result, _error_result)


register_all_tools()


# ── Server Info Tool ────────────────────────────────────────────────────────

@mcp.tool(description="Get Zoom Phone MCP server info, read-only status, and available tool categories.")
async def server_info() -> str:
    """Returns server version, auth status, read-only status, and list of tool categories."""
    info = {
        "server": "zoom-phone-mcp",
        "version": __version__,
        "api_base": API_BASE,
        "read_only": _client.read_only if _client is not None else is_read_only_env(),
        "token_cached": bool(_auth and _auth.is_valid),
        "tool_categories": [
            "auto_receptionists",
            "call_queues",
            "audio_library",
            "phone_users",
            "phone_numbers",
            "voicemails",
            "call_history",
            "devices",
            "sites",
            "common_areas",
            "routing_rules",
            "shared_line_groups",
            "sms",
            "reports",
        ],
    }
    return _json_result(info)


# ── Launch ─────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> None:
    load_dotenv_if_present()
    parser = argparse.ArgumentParser(description="Zoom Phone MCP Server")
    parser.add_argument(
        "--transport",
        choices=["streamable-http", "stdio", "sse"],
        default=os.environ.get("ZOOM_PHONE_MCP_TRANSPORT", "streamable-http"),
        help="MCP transport protocol (default: streamable-http or ZOOM_PHONE_MCP_TRANSPORT)",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("ZOOM_PHONE_MCP_HOST", "0.0.0.0"),
        help="Bind host for HTTP transports (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("ZOOM_PHONE_MCP_PORT", "8767")),
        help="Bind port for HTTP transports (default: 8767)",
    )
    parser.add_argument(
        "--read-only",
        action="store_true",
        default=False,
        help="Block all write/mutate API calls (POST, PATCH, PUT, DELETE)",
    )
    args = parser.parse_args(argv)

    if args.read_only:
        os.environ["ZOOM_PHONE_MCP_READ_ONLY"] = "true"

    if args.transport == "stdio":
        logger.info("Launching Zoom Phone MCP over stdio")
        mcp.run(transport="stdio")
    elif args.transport == "sse":
        import uvicorn

        app = mcp.sse_app()
        logger.info("Launching Zoom Phone MCP (SSE) on %s:%d", args.host, args.port)
        uvicorn.run(app, host=args.host, port=args.port, log_level="info")
    else:
        import uvicorn

        app = mcp.streamable_http_app()
        logger.info("Launching Zoom Phone MCP on %s:%d", args.host, args.port)
        uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()

