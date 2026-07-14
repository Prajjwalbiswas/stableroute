"""
FastAPI HTTP service — the plain REST layer.
Run:  uvicorn app:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel, Field
from cost_model import compare_routes
from config import ONRAMPS, OFFRAMPS, CHAINS

app = FastAPI(
    title="StableRoute",
    description="Cheapest stablecoin route for a cross-border transfer.",
    version="0.1.0",
)


class CompareRequest(BaseModel):
    amount: float = Field(..., gt=0, examples=[5000])
    send_currency: str = Field(..., examples=["GBP"])
    receive_currency: str = Field(..., examples=["MXN"])
    send_country: str = ""
    receive_country: str = ""
    preferred_stablecoins: list[str] | None = None
    priority: str = Field("cheapest", pattern="^(cheapest|fastest)$")
    live_gas: bool = False


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/corridors")
def corridors():
    return {
        "send_currencies": sorted(ONRAMPS),
        "receive_currencies": sorted(OFFRAMPS),
        "chains": sorted(CHAINS),
    }


@app.post("/compare")
def compare(req: CompareRequest):
    return compare_routes(**req.model_dump())
