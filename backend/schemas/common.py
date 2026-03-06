"""
Shared API response envelope models used across v1 endpoints.
"""

from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Dict, Generic, Optional, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseMeta(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    processing_time_ms: int = 0


class APIResponse(BaseModel, Generic[T]):
    status: str
    data: T
    meta: ResponseMeta


def build_response(
    data: T,
    *,
    status: str = "success",
    request_id: Optional[str] = None,
    started_at: Optional[float] = None,
) -> APIResponse[T]:
    """
    Build a consistent API response envelope with timing metadata.
    """
    elapsed_ms = 0
    if started_at is not None:
        elapsed_ms = int((perf_counter() - started_at) * 1000)

    meta = ResponseMeta(
        request_id=request_id or str(uuid4()),
        processing_time_ms=elapsed_ms,
    )
    return APIResponse[T](status=status, data=data, meta=meta)


class ErrorData(BaseModel):
    error_code: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
