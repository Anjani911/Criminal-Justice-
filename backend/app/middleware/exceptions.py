"""
Central exception handling utilities.
"""
from __future__ import annotations

import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status

logger = logging.getLogger(__name__)


async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning("Validation error for %s: %s", request.url.path, exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation failed.",
            "errors": exc.errors(),
            "path": str(request.url.path),
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception for %s", request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error.",
            "path": str(request.url.path),
        },
    )
