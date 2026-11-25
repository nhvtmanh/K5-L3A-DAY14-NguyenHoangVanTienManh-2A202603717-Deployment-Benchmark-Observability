"""Require the configured API key on authenticated routes."""

from secrets import compare_digest
from typing import Annotated

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from .config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(key: Annotated[str | None, Security(api_key_header)]) -> str:
    expected = settings.agent_api_key
    if not expected or not key or not compare_digest(key.encode(), expected.encode()):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return key
