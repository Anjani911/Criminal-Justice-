"""
Lightweight in-memory rate limiting middleware.

This is intentionally simple and suitable for development or a single-process
deployment. It can be swapped with Redis-backed rate limiting later without
changing API behavior.
"""
from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self._requests: Dict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc") or request.url.path.startswith("/openapi"):
            return await call_next(request)

        client_host = request.client.host if request.client else "unknown"
        now = time.time()
        window = settings.RATE_LIMIT_WINDOW_SECONDS
        limit = settings.RATE_LIMIT_REQUESTS

        bucket = self._requests[client_host]
        while bucket and now - bucket[0] > window:
            bucket.popleft()

        if len(bucket) >= limit:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded.",
                    "limit": limit,
                    "window_seconds": window,
                },
            )

        bucket.append(now)
        return await call_next(request)
