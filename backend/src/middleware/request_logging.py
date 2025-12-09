"""
Request/response logging middleware for FastAPI.

Logs all incoming requests and outgoing responses with timing information.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging

from utils.logger import setup_logging

logger = setup_logging(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Log request details, process it, and log response.

        Args:
            request: FastAPI request
            call_next: Next middleware/handler

        Returns:
            Response from the application
        """
        # Get request ID from state (added by main.py)
        request_id = getattr(request.state, "request_id", "unknown")

        # Log request
        logger.info(
            f"[{request_id}] → {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        # Time the request
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            f"[{request_id}] ← {request.method} {request.url.path} "
            f"→ {response.status_code} ({duration:.2f}s)"
        )

        return response
