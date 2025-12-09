"""Pydantic schemas for user-related endpoints."""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from schemas.common import BaseSchema


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255)
    name: str = Field(..., min_length=2, max_length=255)


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str = Field(..., min_length=8)


class UserResponse(BaseSchema):
    """Schema for user response."""

    id: str
    email: str
    name: str
    is_active: bool
    language_preference: str
    theme: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None


class UserProfileUpdate(BaseSchema):
    """Schema for updating user profile."""

    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=255)
    organization: Optional[str] = Field(None, max_length=255)
    country: Optional[str] = Field(None, max_length=100)
    email_notifications: Optional[bool] = None
    show_progress_publicly: Optional[bool] = None
    language_preference: Optional[str] = Field(None, min_length=2, max_length=5)
    theme: Optional[str] = Field(None, max_length=10)


class UserProfileResponse(BaseSchema):
    """Schema for user profile response."""

    id: str
    user_id: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    organization: Optional[str] = None
    country: Optional[str] = None
    email_notifications: bool
    show_progress_publicly: bool
    created_at: datetime
    updated_at: datetime


class UserDetailResponse(UserResponse):
    """Full user response with profile."""

    user_profile: Optional[UserProfileResponse] = None


class TokenResponse(BaseModel):
    """Schema for authentication token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class AuthResponse(BaseModel):
    """Schema for auth endpoint response."""

    user: UserResponse
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for confirming password reset."""

    token: str
    new_password: str = Field(..., min_length=8, max_length=255)
