"""
Shared API dependencies for v1 routes.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from uuid import uuid4

from fastapi import Request


@dataclass
class RequestContext:
    request_id: str
    started_at: float


def get_request_context(request: Request) -> RequestContext:
    """
    Derive request context used for standard response metadata.
    """
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    return RequestContext(request_id=request_id, started_at=perf_counter())

