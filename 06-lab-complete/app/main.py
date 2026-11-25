"""Production AI agent for Part 6."""

import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from time import perf_counter
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, StringConstraints
from redis.exceptions import RedisError

from utils.mock_llm import ask as llm_ask

from .auth import verify_api_key
from .config import settings
from .cost_guard import check_budget, record_cost
from .rate_limiter import check_rate_limit
from .redis_client import r, redis_healthy

logger = logging.getLogger(__name__)
logger.setLevel(settings.log_level)
logger.propagate = False
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)


def log_event(event: str, **fields) -> None:
    logger.info(json.dumps({
        "ts": datetime.now(timezone.utc).isoformat(),
        "lvl": "INFO",
        "event": event,
        **fields,
    }))


@asynccontextmanager
async def lifespan(_app: FastAPI):
    log_event("startup", environment=settings.environment)
    try:
        yield
    finally:
        r.close()
        log_event("shutdown")


app = FastAPI(title="Production AI Agent", lifespan=lifespan)


class AskRequest(BaseModel):
    question: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


@app.middleware("http")
async def log_request(request: Request, call_next):
    started = perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        route = request.scope.get("route")
        log_event("request", method=request.method, path=route.path if route else "unmatched",
                  status=status, ms=round((perf_counter() - started) * 1000, 2))


@app.exception_handler(RedisError)
async def redis_unavailable(_request: Request, _exc: RedisError):
    return JSONResponse(status_code=503, content={"detail": "Redis unavailable"})


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    if not redis_healthy():
        raise HTTPException(status_code=503, detail="Redis unavailable")
    return {"ready": True}


@app.post("/ask")
def ask(body: AskRequest, key: Annotated[str, Depends(verify_api_key)]):
    check_rate_limit(key)
    budget_key = check_budget()
    answer = llm_ask(body.question)
    # This mock estimates usage at approximately four characters per token.
    input_tokens = max(1, (len(body.question) + 3) // 4)
    output_tokens = max(1, (len(answer) + 3) // 4)
    record_cost(input_tokens, output_tokens, budget_key)
    return {"question": body.question, "answer": answer}
