# StableRoute

**Cheapest way to move money across borders with stablecoins.** An OKX.AI
Agent Service Provider (A2MCP) that takes a corridor query and returns
stablecoin routes ranked by total landed cost.

Ask it: *"£5,000 GB → MX, cheapest?"* → it returns each viable
stablecoin × chain route with a full cost breakdown (on-ramp, network/gas,
off-ramp, FX spread), the amount the recipient receives, total cost in USD and
%, and estimated settlement time.

---

## What's real vs. estimated

A money tool must not fake precision. Every response carries a `data_basis`
flag per route:

- **Network (gas) cost** — recent per-chain figures in `config.py`; optionally
  refined live from EVM gas price (set `STABLEROUTE_LIVE_GAS=1`).
- **FX rate** — fetched live from Frankfurter, with a static fallback. The
  response shows `"fx_source": "live"` or `"cached"`.
- **Ramp fees** — the on/off-ramp numbers in `config.py` are **illustrative
  placeholders**. Replace them with your real corridor research before
  going live. They're always flagged `"ramps": "estimated"`.

---

## Run locally

```bash
python -m venv venv && ./venv/bin/pip install -r requirements.txt

# smoke test (works offline, falls back cleanly)
./venv/bin/python test_local.py

# plain REST API
./venv/bin/uvicorn app:app --port 8000
# -> POST http://localhost:8000/compare

# MCP server (what OKX.AI calls)
./venv/bin/python mcp_server.py
# -> streamable-http on http://0.0.0.0:8000/mcp
```

Debug the MCP tools interactively with the official inspector:

```bash
npx @modelcontextprotocol/inspector
# point it at http://localhost:8000/mcp and call compare_routes
```

## Deploy (public HTTPS, per the OKX A2MCP guide)

1. Put this on any public server (a Singapore/Tokyo node or a serverless edge
   platform both work) or a container host.
2. Point a domain at it and terminate HTTPS (Caddy/Nginx reverse proxy, or the
   platform's built-in TLS). MCP requires an HTTPS URL tied to a domain.
3. Your public endpoint becomes `https://your-domain/mcp`.
4. Verify with MCP Inspector against the HTTPS URL before registering.

## List on OKX.AI (A2MCP)

In your agent (Claude Code / Codex / etc.) with Onchain OS installed:

```
npx skills add okx/onchainos-skills --yes -g          # once
Log in to Agentic Wallet on Onchain OS with my email
Help me register an A2MCP ASP on OKX.AI using OKX Agent Identity from Onchain OS
Help me list my ASP on OKX.AI using Onchain OS
```

Give it your `https://your-domain/mcp` endpoint. **Ship free first** (no x402
needed — a free endpoint just returns the result), which removes the biggest
go-live risk. Add x402 paid pricing (~0.05–0.1 USDT/call via the OKX Payment
SDK) only once it's live and reviewed. Review is ~24h, emailed to your Agentic
Wallet address.

## Files

| File | Purpose |
|------|---------|
| `config.py` | Chains, stablecoin support, ramp fees, FX fallback — **edit this** |
| `providers.py` | Live FX + optional EVM gas, with fallbacks |
| `cost_model.py` | Landed-cost calculation and ranking |
| `app.py` | FastAPI REST layer (`/compare`, `/corridors`, `/health`) |
| `mcp_server.py` | FastMCP wrapper exposing `compare_routes` + `list_corridors` |
| `test_local.py` | Offline smoke test |

## Extending

- **Real corridors:** replace `ONRAMPS` / `OFFRAMPS` in `config.py` with your
  Atlas fee data; the `"estimated"` flag becomes accurate as you wire live
  ramp-quote APIs.
- **Bridging:** the model reserves a `bridge_fee_usd` hook (currently 0) for
  cross-chain routes where on-ramp and off-ramp chains differ.
- **More chains/currencies:** add entries to `CHAINS`, `ONRAMPS`, `OFFRAMPS`.
