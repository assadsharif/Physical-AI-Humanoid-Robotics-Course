"""
Error handling middleware and exception handlers for FastAPI.

Catches all exceptions and returns standardized JSON error responses.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from utils.errors import AppException
from utils.logger import setup_logging

logger = setup_logging(__name__)


async def error_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for all unhandled exceptions.

    Args:
        request: FastAPI request
        exc: Exception raised

    Returns:
        JSONResponse with error details
    """
    # Log the error
    logger.error(
        f"Unhandled exception in {request.method} {request.url.path}",
        exc_info=exc,
    )

    # If it's our custom exception, use its format
    if isinstance(exc, AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
        )

    # Generic error response for unexpected exceptions
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "code": 500,
            "details": {},
        },
    )


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware to catch and handle exceptions."""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except AppException as exc:
            logger.warning(f"Application exception: {exc.message}")
            return JSONResponse(
                status_code=exc.status_code,
                content=exc.to_dict(),
            )
        except Exception as exc:
            logger.error(f"Unexpected error: {exc}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "code": 500,
                    "details": {},
                },
            )
