"""
JWT authentication middleware for protecting endpoints.

Extracts and validates JWT tokens from Authorization header.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Callable, Optional

from services.auth_service import AuthService
from utils.logger import setup_logging

logger = setup_logging(__name__)


class JWTAuthMiddleware:
    """Middleware to validate JWT tokens on protected endpoints."""

    # Endpoints that don't require authentication
    EXCLUDED_PATHS = {
        "/api/health",
        "/api/health/ready",
        "/api/health/live",
        "/api/auth/signup",
        "/api/auth/login",
        "/api/auth/password-reset",
        "/docs",
        "/redoc",
        "/openapi.json",
    }

    @staticmethod
    def extract_token(authorization_header: Optional[str]) -> Optional[str]:
        """
        Extract JWT token from Authorization header.

        Expected format: "Bearer <token>"

        Args:
            authorization_header: Value of Authorization header

        Returns:
            Token string if valid format, None otherwise
        """
        if not authorization_header:
            return None

        parts = authorization_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        return parts[1]

    @staticmethod
    async def get_current_user(request: Request) -> Optional[str]:
        """
        Extract and verify JWT token from request.

        Used as FastAPI dependency to inject user_id into endpoints.

        Args:
            request: FastAPI request

        Returns:
            User ID if token is valid, None otherwise
        """
        # Check if path is excluded
        path = request.url.path
        for excluded in JWTAuthMiddleware.EXCLUDED_PATHS:
            if path.startswith(excluded):
                return None

        # Extract token from header
        auth_header = request.headers.get("Authorization")
        token = JWTAuthMiddleware.extract_token(auth_header)

        if not token:
            return None

        # Verify token
        user_id = AuthService.verify_token(token)
        if not user_id:
            return None

        return user_id


async def jwt_auth_middleware(request: Request, call_next: Callable):
    """
    Middleware to enforce JWT authentication on protected endpoints.

    Checks token validity and injects user_id into request state.
    """
    path = request.url.path

    # Skip auth for excluded paths
    excluded_paths = {
        "/api/health",
        "/api/health/ready",
        "/api/health/live",
        "/api/auth/signup",
        "/api/auth/login",
        "/api/auth/password-reset",
        "/docs",
        "/redoc",
        "/openapi.json",
    }

    is_excluded = any(path.startswith(ep) for ep in excluded_paths)

    if not is_excluded:
        # Extract and verify token
        auth_header = request.headers.get("Authorization")
        token = JWTAuthMiddleware.extract_token(auth_header)

        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "AUTHENTICATION_ERROR",
                    "message": "Missing authentication token",
                    "code": 401,
                    "details": {},
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = AuthService.verify_token(token)
        if not user_id:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "AUTHENTICATION_ERROR",
                    "message": "Invalid or expired token",
                    "code": 401,
                    "details": {},
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Inject user_id into request state
        request.state.user_id = user_id

    response = await call_next(request)
    return response
