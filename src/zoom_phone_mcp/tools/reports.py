"""Reports — Zoom Phone usage reports (call charges, fax, operation logs, SMS charges)."""

from typing import Any

def register(mcp: Any, get_client, json_result, error_result):
    client = get_client

    @mcp.tool(description="Get Zoom Phone call charges usage report.")
    async def get_call_charges(from_date: str | None = None, to_date: str | None = None, page_size: int | None = 100, next_page_token: str | None = None) -> str:
        """Get call charges report. Dates in YYYY-MM-DD format."""
        try:
            params: dict[str, Any] = {"page_size": page_size}
            if from_date:
                params["from"] = from_date
            if to_date:
                params["to"] = to_date
            if next_page_token:
                params["next_page_token"] = next_page_token
            data = await client().get("/phone/reports/call_charges", params=params)
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Get Zoom Phone fax charges usage report.")
    async def get_fax_charges(from_date: str | None = None, to_date: str | None = None, page_size: int | None = 100, next_page_token: str | None = None) -> str:
        """Get fax charges report. Dates in YYYY-MM-DD format."""
        try:
            params: dict[str, Any] = {"page_size": page_size}
            if from_date:
                params["from"] = from_date
            if to_date:
                params["to"] = to_date
            if next_page_token:
                params["next_page_token"] = next_page_token
            data = await client().get("/phone/reports/fax_charges", params=params)
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Get Zoom Phone operation logs report.")
    async def get_operation_logs(from_date: str | None = None, to_date: str | None = None, page_size: int | None = 100, next_page_token: str | None = None) -> str:
        """Get operation logs report. Dates in YYYY-MM-DD format."""
        try:
            params: dict[str, Any] = {"page_size": page_size}
            if from_date:
                params["from"] = from_date
            if to_date:
                params["to"] = to_date
            if next_page_token:
                params["next_page_token"] = next_page_token
            data = await client().get("/phone/reports/operationlogs", params=params)
            return json_result(data)
        except Exception as e:
            return error_result(e)

    @mcp.tool(description="Get Zoom Phone SMS/MMS charges usage report.")
    async def get_sms_charges(from_date: str | None = None, to_date: str | None = None, page_size: int | None = 100, next_page_token: str | None = None) -> str:
        """Get SMS/MMS charges report. Dates in YYYY-MM-DD format."""
        try:
            params: dict[str, Any] = {"page_size": page_size}
            if from_date:
                params["from"] = from_date
            if to_date:
                params["to"] = to_date
            if next_page_token:
                params["next_page_token"] = next_page_token
            data = await client().get("/phone/reports/sms_charges", params=params)
            return json_result(data)
        except Exception as e:
            return error_result(e)
