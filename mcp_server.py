"""
FastMCP wrapper — this is what OKX.AI (and any MCP client) calls.

Run over HTTP (front it with HTTPS + a domain per the OKX A2MCP guide):
    python mcp_server.py
which serves streamable-http on 0.0.0.0:8000/mcp

Local stdio debugging:
    fastmcp run mcp_server.py:mcp
"""
from __future__ import annotations
import os
from fastmcp import FastMCP
from starlette.responses import HTMLResponse, JSONResponse
from cost_model import compare_routes as _compare
from config import ONRAMPS, OFFRAMPS, CHAINS

mcp = FastMCP("StableRoute")


@mcp.tool
def compare_routes(
    amount: float,
    send_currency: str,
    receive_currency: str,
    send_country: str = "",
    receive_country: str = "",
    preferred_stablecoins: list[str] | None = None,
    priority: str = "cheapest",
) -> dict:
    """Compare stablecoin routes for a cross-border transfer and return them
    ranked by total landed cost (or settlement time if priority='fastest').

    Args:
        amount: Amount to send, in send_currency.
        send_currency: ISO code of the funding currency, e.g. "GBP".
        receive_currency: ISO code the recipient is paid in, e.g. "MXN".
        send_country: Optional ISO-2 country of the sender.
        receive_country: Optional ISO-2 country of the recipient.
        preferred_stablecoins: Optional filter, e.g. ["USDC"].
        priority: "cheapest" (default) or "fastest".

    Returns:
        Ranked routes with per-leg cost breakdown, amount received, total cost
        (absolute + %), estimated settlement, and a data_basis flag per route
        indicating whether each figure is live or estimated.
    """
    live_gas = os.getenv("STABLEROUTE_LIVE_GAS", "0") == "1"
    return _compare(
        amount=amount,
        send_currency=send_currency,
        receive_currency=receive_currency,
        send_country=send_country,
        receive_country=receive_country,
        preferred_stablecoins=preferred_stablecoins,
        priority=priority,
        live_gas=live_gas,
    )


@mcp.tool
def list_corridors() -> dict:
    """List the currencies and chains StableRoute currently supports."""
    return {
        "send_currencies": sorted(ONRAMPS),
        "receive_currencies": sorted(OFFRAMPS),
        "chains": sorted(CHAINS),
    }


@mcp.custom_route("/", methods=["GET"])
async def landing(request):
    return HTMLResponse(
        """<!DOCTYPE html><html><head><meta charset="utf-8">
        <title>StableRoute ASP</title>
        <style>body{font-family:system-ui,sans-serif;background:#0b1f3a;color:#f6f2e9;
        display:flex;min-height:100vh;margin:0;align-items:center;justify-content:center;text-align:center}
        .c{max-width:520px;padding:32px}h1{color:#2e63ff;margin:0 0 8px}code{background:#12294a;
        padding:2px 8px;border-radius:6px;color:#d9a441}a{color:#2e63ff}</style></head>
        <body><div class="c">
        <h1>StableRoute</h1>
        <p>Cheapest stablecoin route for a cross-border transfer. This service is <b>live</b>.</p>
        <p>It's an OKX.AI Agent Service Provider — the machine-readable MCP endpoint is at
        <code>/mcp</code>, not this page. Point an MCP client there.</p>
        <p>Tools: <code>compare_routes</code> · <code>list_corridors</code></p>
        <p style="opacity:.6;font-size:13px">Health check: <a href="/health">/health</a></p>
        </div></body></html>"""
    )


@mcp.custom_route("/health", methods=["GET"])
async def health(request):
    return JSONResponse({"status": "ok", "service": "StableRoute", "mcp_endpoint": "/mcp",
                         "tools": ["compare_routes", "list_corridors"]})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    mcp.run(transport="http", host="0.0.0.0", port=port)