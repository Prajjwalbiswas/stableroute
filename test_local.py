"""
Local smoke test — no external services required (falls back cleanly offline).
Run: python test_local.py
"""
import json
from cost_model import compare_routes


def show(title, r):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)
    if "error" in r:
        print("ERROR:", r["error"]); print(json.dumps(r, indent=2)); return
    print(f"as_of {r['as_of']} | FX {r['fx_source']}"
          + (f" (ref {r['fx_reference_date']})" if r['fx_reference_date'] else "")
          + f" | 1 {r['query']['send_currency']} = {r['fx_mid_rate']} {r['query']['receive_currency']}")
    print("Reco:", r["recommendation"])
    if r["savings_vs_remittance_usd"]:
        print(f"Savings vs {r['remittance_baseline_pct']}% remittance: ${r['savings_vs_remittance_usd']}")
    print(f"\n{'#':<3}{'Chain':<10}{'Coin':<14}{'Net fee':<10}{'Settle':<11}{'Total':<11}{'vs #1':<10}{'Received'}")
    for x in r["routes"]:
        vs = "—" if x["rank"] == 1 else (("+" if x["delta_vs_best_usd"] >= 0 else "−") + f"${abs(x['delta_vs_best_usd'])}")
        settle = x["settlement"].split(" on-chain")[0] + " +" + x["rail"]
        print(f"{x['rank']:<3}{x['chain']:<10}{x['stablecoin_label']:<14}"
              f"${x['network_fee_usd']:<9}{settle:<11}${x['total_cost_usd']:<10}{vs:<10}"
              f"{x['amount_received']} {x['receive_currency']}")


if __name__ == "__main__":
    show("$10,000 US -> MX (cheapest)", compare_routes(10000, "USD", "MXN", "US", "MX"))
    show("$10,000 US -> BR, fastest",   compare_routes(10000, "USD", "BRL", priority="fastest"))
    show("$10,000 US -> AR (exotic)",   compare_routes(10000, "USD", "ARS"))
    show("£5,000 GB -> IN, USDT only",  compare_routes(5000, "GBP", "INR", preferred_stablecoins=["USDT"]))
    show("Unsupported corridor",        compare_routes(100, "JPY", "MXN"))

    json.dumps(compare_routes(10000, "USD", "MXN"))  # serialisation check
    print("\nJSON serialisation: OK")
