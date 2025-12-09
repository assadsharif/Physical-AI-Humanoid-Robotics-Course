"""
FastAPI dependencies for injecting authenticated user and database session.

Used across all protected endpoints.
"""

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from services.auth_service import AuthService
from middleware.auth_middleware import JWTAuthMiddleware
from utils.logger import setup_logging

logger = setup_logging(__name__)


async def get_current_user_id(request: Request) -> str:
    """
    Dependency to extract current user ID from JWT token in request.

    Used in protected endpoints like:
        @router.get("/me")
        async def get_me(user_id: str = Depends(get_current_user_id)):
            ...

    Raises:
        HTTPException: 401 if token is missing or invalid
    """
    auth_header = request.headers.get("Authorization")
    token = JWTAuthMiddleware.extract_token(auth_header)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = AuthService.verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """
    Dependency to get the current authenticated user from database.

    Used in endpoints that need full user object:
        @router.get("/profile")
        async def get_profile(user = Depends(get_current_user)):
            ...

    Raises:
        HTTPException: 404 if user not found
    """
    user = await AuthService.get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
