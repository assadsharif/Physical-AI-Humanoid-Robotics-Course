"""
Authentication endpoints.

Handles user registration, login, password reset, and profile management.
"""

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from db import get_db
from schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserDetailResponse,
    AuthResponse,
    UserProfileUpdate,
)
from services.auth_service import AuthService
from api.dependencies import get_current_user_id, get_current_user
from utils.logger import setup_logging
from utils.errors import (
    ConflictError,
    ValidationError,
    AuthenticationError,
    AppException,
)

logger = setup_logging(__name__)

router = APIRouter()


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    tags=["authentication"],
)
async def signup(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """
    Register a new user account.

    Args:
        user_data: Email, password, and name

    Returns:
        User info and access token

    Raises:
        409: Email already registered
        400: Validation error
    """
    try:
        user, access_token, expires_in = await AuthService.register_user(
            user_data, session
        )

        return AuthResponse(
            user=UserResponse.model_validate(user),
            access_token=access_token,
            expires_in=expires_in,
        )
    except (ConflictError, ValidationError, AppException) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="User login",
    tags=["authentication"],
)
async def login(
    credentials: UserLogin,
    session: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """
    Authenticate a user and return access token.

    Args:
        credentials: Email and password

    Returns:
        User info and access token

    Raises:
        401: Invalid credentials
    """
    try:
        user, access_token, expires_in = await AuthService.login_user(
            credentials.email, credentials.password, session
        )

        return AuthResponse(
            user=UserResponse.model_validate(user),
            access_token=access_token,
            expires_in=expires_in,
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=e.message)


@router.get(
    "/me",
    response_model=UserDetailResponse,
    summary="Get current user profile",
    tags=["authentication"],
)
async def get_me(
    user = Depends(get_current_user),
) -> UserDetailResponse:
    """
    Get the current authenticated user's profile.

    Returns:
        Full user details including profile
    """
    return UserDetailResponse.model_validate(user)


@router.patch(
    "/profile",
    response_model=UserDetailResponse,
    summary="Update user profile",
    tags=["authentication"],
)
async def update_profile(
    profile_update: UserProfileUpdate,
    user = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> UserDetailResponse:
    """
    Update current user's profile and preferences.

    Args:
        profile_update: Fields to update (all optional)

    Returns:
        Updated user details
    """
    # Update user preferences
    if profile_update.language_preference:
        user.language_preference = profile_update.language_preference
    if profile_update.theme:
        user.theme = profile_update.theme

    # Update user profile if it exists
    if user.user_profile:
        if profile_update.bio is not None:
            user.user_profile.bio = profile_update.bio
        if profile_update.avatar_url is not None:
            user.user_profile.avatar_url = profile_update.avatar_url
        if profile_update.organization is not None:
            user.user_profile.organization = profile_update.organization
        if profile_update.country is not None:
            user.user_profile.country = profile_update.country
        if profile_update.email_notifications is not None:
            user.user_profile.email_notifications = profile_update.email_notifications
        if profile_update.show_progress_publicly is not None:
            user.user_profile.show_progress_publicly = (
                profile_update.show_progress_publicly
            )

    from datetime import datetime

    user.updated_at = datetime.utcnow()
    await session.commit()

    return UserDetailResponse.model_validate(user)


@router.post(
    "/logout",
    summary="User logout",
    tags=["authentication"],
)
async def logout(
    user_id: str = Depends(get_current_user_id),
) -> Dict[str, str]:
    """
    Logout the current user.

    Note: JWT tokens cannot be revoked server-side. The client should
    delete the token from storage. For production, implement a token
    blacklist or use short-lived tokens with refresh tokens.

    Returns:
        Success message
    """
    logger.info(f"User logout: {user_id}")
    return {"message": "Successfully logged out"}
