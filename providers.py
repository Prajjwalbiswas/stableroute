"""
Live data providers with graceful fallbacks.

A money tool must never silently invent precision. Every fetch reports its
`source` ("live" | "cached") and, for FX, the reference date — surfaced in the
API response so the caller knows what they're trusting.
"""
from __future__ import annotations
import requests
from config import CHAINS, FALLBACK_FX_PER_USD

FX_TIMEOUT = 4
GAS_TIMEOUT = 4


def get_fx_rates(currencies: list[str]) -> tuple[dict[str, float], str, str | None]:
    """Return ({currency: units_per_USD}, source, fx_date).

    source is "live" (Frankfurter/ECB) or "cached" (static fallback).
    fx_date is the ECB reference date when live, else None.
    """
    wanted = [c for c in currencies if c != "USD"]
    try:
        resp = requests.get(
            "https://api.frankfurter.dev/v1/latest",
            params={"base": "USD", "symbols": ",".join(wanted)},
            timeout=FX_TIMEOUT,
        )
        resp.raise_for_status()
        body = resp.json()
        rates = body.get("rates", {})
        rates["USD"] = 1.0
        if all(rates.get(c) for c in currencies):
            return rates, "live", body.get("date")
    except Exception:
        pass
    rates = {c: FALLBACK_FX_PER_USD.get(c) for c in currencies}
    rates["USD"] = 1.0
    return rates, "cached", None


def _live_evm_transfer_usd(chain: str) -> float | None:
    """Refine an EVM chain's transfer cost from live gas price. None on failure."""
    cfg = CHAINS.get(chain, {})
    if not cfg.get("evm") or not cfg.get("rpc"):
        return None
    try:
        resp = requests.post(
            cfg["rpc"],
            json={"jsonrpc": "2.0", "id": 1, "method": "eth_gasPrice", "params": []},
            timeout=GAS_TIMEOUT,
        )
        resp.raise_for_status()
        wei = int(resp.json()["result"], 16)
        return (wei / 1e18) * cfg["gas_units"] * cfg["native_usd"]
    except Exception:
        return None


def get_network_cost_usd(chain: str, live_gas: bool = False) -> tuple[float, str]:
    """Return (transfer_cost_usd, source). Config value unless live_gas succeeds."""
    cfg = CHAINS[chain]
    if live_gas:
        live = _live_evm_transfer_usd(chain)
        if live is not None:
            return round(live, 6), "live"
    return cfg["typical_transfer_usd"], "estimated"
