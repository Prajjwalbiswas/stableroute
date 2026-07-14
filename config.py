"""
StableRoute configuration — the editable data layer.
Kept in sync with ui.html (same chains, ramps, corridors, fallback FX).

TWO KINDS OF DATA:
  1. CHAINS   -> network (gas) cost per stablecoin transfer + on-chain finality.
  2. ONRAMPS / OFFRAMPS -> fiat<->stablecoin fees, rails, and settlement times.

⚠️  RAMP FEE NUMBERS ARE ILLUSTRATIVE PLACEHOLDERS (except the MXN off-ramp,
    which uses Bitso's published exchange fees). Replace with your real Atlas
    corridor research before going live. Every response flags them "estimated".
"""

# ---------------------------------------------------------------------------
# CHAINS
#   typical_transfer_usd : recent all-in cost of one stablecoin transfer (USD)
#   settlement_seconds   : rough on-chain finality (used for "fastest")
#   evm/rpc/gas_units/native_usd : only used by the optional live gas hook
# ---------------------------------------------------------------------------
CHAINS = {
    "Solana":   {"typical_transfer_usd": 0.0006, "settlement_seconds": 8,   "stablecoins": ["USDC", "USDT"], "evm": False},
    "Base":     {"typical_transfer_usd": 0.0040, "settlement_seconds": 6,   "stablecoins": ["USDC", "USDT"], "evm": True,  "rpc": "https://mainnet.base.org",        "gas_units": 55000, "native_usd": 3200.0},
    "Polygon":  {"typical_transfer_usd": 0.0030, "settlement_seconds": 8,   "stablecoins": ["USDC", "USDT"], "evm": True,  "rpc": "https://polygon-rpc.com",          "gas_units": 55000, "native_usd": 0.55},
    "Arbitrum": {"typical_transfer_usd": 0.0200, "settlement_seconds": 5,   "stablecoins": ["USDC", "USDT"], "evm": True,  "rpc": "https://arb1.arbitrum.io/rpc",     "gas_units": 55000, "native_usd": 3200.0},
    "BNB":      {"typical_transfer_usd": 0.1000, "settlement_seconds": 6,   "stablecoins": ["USDT", "USDC"], "evm": True,  "rpc": "https://bsc-dataseed.binance.org", "gas_units": 55000, "native_usd": 620.0},
    "Tron":     {"typical_transfer_usd": 1.2000, "settlement_seconds": 6,   "stablecoins": ["USDT"],         "evm": False},
    "Ethereum": {"typical_transfer_usd": 1.8000, "settlement_seconds": 60,  "stablecoins": ["USDC", "USDT"], "evm": True,  "rpc": "https://eth.llamarpc.com",         "gas_units": 55000, "native_usd": 3200.0},
}

# ---------------------------------------------------------------------------
# ON-RAMPS: fiat -> stablecoin, keyed by send currency.  ⚠️ ILLUSTRATIVE.
# ---------------------------------------------------------------------------
ONRAMPS = {
    "USD": {"provider": "USD->USDC (Circle/business ramp)", "fee_pct": 0.30, "fx_spread_pct": 0.00, "stablecoins": ["USDC", "USDT"], "settlement": "instant"},
    "GBP": {"provider": "GBP on-ramp",                      "fee_pct": 0.90, "fx_spread_pct": 0.50, "stablecoins": ["USDC", "USDT"], "settlement": "minutes"},
    "EUR": {"provider": "EUR on-ramp",                      "fee_pct": 0.80, "fx_spread_pct": 0.45, "stablecoins": ["USDC", "USDT"], "settlement": "minutes"},
}

# ---------------------------------------------------------------------------
# OFF-RAMPS: stablecoin -> fiat, keyed by receive currency.
#   settlement_seconds : representative payout time on that rail (for "fastest")
#   rail               : short label shown in the routes table
# MXN uses Bitso's published USDC-pair taker fee (0.36%); fx_spread is an estimate.
# Others are ILLUSTRATIVE placeholders.
# ---------------------------------------------------------------------------
OFFRAMPS = {
    "USD": {"provider": "USD off-ramp",                  "fee_pct": 0.60, "fx_spread_pct": 0.00, "stablecoins": ["USDC", "USDT"], "settlement": "1-3 business days (ACH)",                  "settlement_seconds": 172800, "rail": "ACH 1-3d"},
    "EUR": {"provider": "EUR off-ramp",                  "fee_pct": 0.90, "fx_spread_pct": 0.45, "stablecoins": ["USDC", "USDT"], "settlement": "~1 day (SEPA; Instant ~10s where supported)", "settlement_seconds": 86400,  "rail": "SEPA ~1d"},
    "MXN": {"provider": "Bitso (USDC->MXN, SPEI)",       "fee_pct": 0.36, "fx_spread_pct": 0.40, "stablecoins": ["USDC", "USDT"], "settlement": "minutes (SPEI, 24/7)",                     "settlement_seconds": 120,    "rail": "SPEI"},
    "NGN": {"provider": "NG off-ramp",                   "fee_pct": 1.50, "fx_spread_pct": 1.20, "stablecoins": ["USDT"],         "settlement": "minutes (local rail)",                     "settlement_seconds": 300,    "rail": "local"},
    "PHP": {"provider": "PH off-ramp",                   "fee_pct": 1.30, "fx_spread_pct": 0.80, "stablecoins": ["USDC", "USDT"], "settlement": "minutes (local rail)",                     "settlement_seconds": 300,    "rail": "local"},
    "GBP": {"provider": "UK off-ramp (Faster Payments)", "fee_pct": 0.60, "fx_spread_pct": 0.30, "stablecoins": ["USDC", "USDT"], "settlement": "same-day (Faster Payments, 24/7)",         "settlement_seconds": 30,     "rail": "Faster Pay"},
    "BRL": {"provider": "BR off-ramp (PIX)",             "fee_pct": 0.90, "fx_spread_pct": 0.70, "stablecoins": ["USDC", "USDT"], "settlement": "instant (PIX, 24/7)",                      "settlement_seconds": 60,     "rail": "PIX"},
    "INR": {"provider": "IN off-ramp (UPI)",             "fee_pct": 1.00, "fx_spread_pct": 0.80, "stablecoins": ["USDC", "USDT"], "settlement": "minutes (UPI)",                            "settlement_seconds": 120,    "rail": "UPI"},
    "ARS": {"provider": "AR off-ramp",                   "fee_pct": 1.50, "fx_spread_pct": 2.50, "stablecoins": ["USDT", "USDC"], "settlement": "minutes (local rail)",                     "settlement_seconds": 600,    "rail": "local"},
    "COP": {"provider": "CO off-ramp",                   "fee_pct": 1.20, "fx_spread_pct": 1.00, "stablecoins": ["USDC", "USDT"], "settlement": "minutes (local rail)",                     "settlement_seconds": 300,    "rail": "local"},
}

# Static fallback FX (units per 1 USD). Used only when the live fetch fails or
# the currency isn't on the ECB feed (ARS, COP, NGN, PHP). Refresh periodically.
FALLBACK_FX_PER_USD = {
    "USD": 1.0, "EUR": 0.92, "GBP": 0.79, "MXN": 18.7, "NGN": 1550.0,
    "PHP": 57.5, "BRL": 5.5, "INR": 85.0, "ARS": 1485.0, "COP": 3249.0,
}

ALL_STABLECOINS = ["USDC", "USDT"]
REMITTANCE_BASELINE_PCT = 5.5  # typical retail remittance fee, for savings framing
