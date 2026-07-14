"""
Core landed-cost model. Mirrors ui.html exactly.

Flow per route (one row per chain; USDC/USDT price identically so they share a row):

    send_amount (send_ccy)
      -> value at mid in USD  = amount / fx[send]
      -> on-ramp fee + spread -> stablecoin bought
      -> network (gas) cost   -> stablecoin after transfer
      -> off-ramp fee + spread-> USD delivered
      -> convert at mid       -> amount received

    total_cost_usd = mid_usd - usd_delivered
    delta_usd      = total_cost_usd - cheapest_total   (why one route beats another)
    settlement_seconds = chain finality + off-ramp rail time
"""
from __future__ import annotations
from datetime import datetime, timezone
from config import CHAINS, ONRAMPS, OFFRAMPS, ALL_STABLECOINS, REMITTANCE_BASELINE_PCT
from providers import get_fx_rates, get_network_cost_usd

DISCLAIMER = "Estimates for comparison only — not a quote or financial advice."


def _human_time(seconds: int) -> str:
    if seconds < 60:
        return f"~{seconds}s"
    if seconds < 3600:
        return f"~{round(seconds/60)} min"
    if seconds < 86400:
        return f"~{round(seconds/3600)} h"
    return f"~{round(seconds/86400)} day" + ("s" if seconds >= 172800 else "")


def compare_routes(
    amount: float,
    send_currency: str,
    receive_currency: str,
    send_country: str = "",
    receive_country: str = "",
    preferred_stablecoins: list[str] | None = None,
    priority: str = "cheapest",
    live_gas: bool = False,
) -> dict:
    send_ccy = send_currency.upper()
    recv_ccy = receive_currency.upper()
    preferred = [c.upper() for c in preferred_stablecoins] if preferred_stablecoins else None

    if send_ccy not in ONRAMPS:
        return {"error": f"No on-ramp configured for {send_ccy}.",
                "supported_send_currencies": sorted(ONRAMPS)}
    if recv_ccy not in OFFRAMPS:
        return {"error": f"No off-ramp configured for {recv_ccy}.",
                "supported_receive_currencies": sorted(OFFRAMPS)}

    fx, fx_source, fx_date = get_fx_rates([send_ccy, recv_ccy])
    mid_usd = amount / fx[send_ccy]

    on, off = ONRAMPS[send_ccy], OFFRAMPS[recv_ccy]
    on_take, off_take = on["fee_pct"] + on["fx_spread_pct"], off["fee_pct"] + off["fx_spread_pct"]
    allowed = preferred or ALL_STABLECOINS

    routes = []
    for chain, c in CHAINS.items():
        coins = [x for x in allowed
                 if x in c["stablecoins"] and x in on["stablecoins"] and x in off["stablecoins"]]
        if not coins:
            continue
        net, net_source = get_network_cost_usd(chain, live_gas=live_gas)
        stable_bought = mid_usd * (1 - on_take / 100)
        usd_delivered = (stable_bought - net) * (1 - off_take / 100)
        received = usd_delivered * fx[recv_ccy]
        total_usd = mid_usd - usd_delivered
        on_cost = mid_usd * on_take / 100
        off_cost = max(total_usd - on_cost - net, 0)
        secs = c["settlement_seconds"] + off["settlement_seconds"]
        routes.append({
            "chain": chain,
            "stablecoins": coins,
            "stablecoin_label": " or ".join(coins),
            "network_fee_usd": round(net, 6),
            "settlement_seconds": secs,
            "settlement": f"{_human_time(c['settlement_seconds'])} on-chain + {off['settlement']} off-ramp",
            "rail": off["rail"],
            "amount_received": round(received, 2),
            "receive_currency": recv_ccy,
            "total_cost_usd": round(total_usd, 4),
            "total_cost_pct": round(total_usd / mid_usd * 100, 3) if mid_usd else 0.0,
            "cost_breakdown": {"onramp_usd": round(on_cost, 4),
                               "network_usd": round(net, 6),
                               "offramp_and_fx_usd": round(off_cost, 4)},
            "data_basis": {"network": net_source, "fx": fx_source, "ramps": "estimated"},
            "_secs": secs, "_total": total_usd,
        })

    if not routes:
        return {"error": "No viable stablecoin route for that corridor and preference.",
                "hint": "Try USDC or USDT, or drop preferred_stablecoins."}

    routes.sort(key=lambda r: (r["_secs"], r["_total"]) if priority == "fastest"
                else (r["_total"], r["_secs"]))
    best_total = routes[0]["_total"]
    for i, r in enumerate(routes, 1):
        r["rank"] = i
        r["delta_vs_best_usd"] = round(r["_total"] - best_total, 4)
        r.pop("_secs", None); r.pop("_total", None)

    best = routes[0]
    savings = mid_usd * REMITTANCE_BASELINE_PCT / 100 - best["total_cost_usd"]
    recommendation = (
        f"{best['chain']} with {best['stablecoin_label']} is "
        f"{'fastest' if priority == 'fastest' else 'cheapest'}: ~{best['total_cost_pct']}% all-in "
        f"({best['total_cost_usd']} USD on {amount} {send_ccy}); recipient gets "
        f"~{best['amount_received']} {recv_ccy}, settling {best['settlement']}."
    )

    return {
        "query": {"amount": amount, "send_currency": send_ccy, "receive_currency": recv_ccy,
                  "send_country": send_country, "receive_country": receive_country,
                  "preferred_stablecoins": preferred, "priority": priority},
        "as_of": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fx_source": fx_source,
        "fx_reference_date": fx_date,
        "fx_mid_rate": round(fx[recv_ccy] / fx[send_ccy], 6),
        "routes": routes,
        "recommendation": recommendation,
        "savings_vs_remittance_usd": round(savings, 2) if savings > 0 else 0,
        "remittance_baseline_pct": REMITTANCE_BASELINE_PCT,
        "disclaimer": DISCLAIMER,
    }
