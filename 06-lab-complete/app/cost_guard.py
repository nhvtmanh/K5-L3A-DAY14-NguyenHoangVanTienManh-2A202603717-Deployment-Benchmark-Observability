"""Daily token spend shared across workers and instances."""

from datetime import datetime, timezone

from fastapi import HTTPException

from .config import settings
from .redis_client import r

PRICE_INPUT_PER_1K = 0.00015
PRICE_OUTPUT_PER_1K = 0.0006


def check_budget() -> str:
    budget_key = f"agent:cost:{datetime.now(timezone.utc).date().isoformat()}"
    spent = float(r.get(budget_key) or 0)
    if spent >= settings.daily_budget_usd:
        raise HTTPException(status_code=402, detail="Daily budget exhausted")
    return budget_key


def record_cost(input_tokens: int, output_tokens: int, budget_key: str) -> float:
    cost = (input_tokens * PRICE_INPUT_PER_1K + output_tokens * PRICE_OUTPUT_PER_1K) / 1000
    with r.pipeline() as batch:
        batch.incrbyfloat(budget_key, cost)
        batch.expire(budget_key, 2 * 86400)
        batch.execute()
    return cost
