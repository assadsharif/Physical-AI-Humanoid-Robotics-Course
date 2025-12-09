"""Pydantic schemas for request/response validation."""

from .common import (
    BaseSchema,
    PaginationParams,
    PaginatedResponse,
    ErrorResponse,
    HealthResponse,
    MessageResponse,
)
from .user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserProfileUpdate,
    UserProfileResponse,
    UserDetailResponse,
    TokenResponse,
    AuthResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from .chapter import (
    ModuleResponse,
    ChapterResponse,
    ChapterDetailResponse,
    ChapterProgressResponse,
    TranslationResponse,
)
from .chat import (
    ChatQueryRequest,
    ChatSourceResponse,
    ConversationContextResponse,
    ChatMessageResponse,
    ChatQueryResponse,
    ConversationSessionResponse,
    ChatRatingRequest,
)

__all__ = [
    # Common
    "BaseSchema",
    "PaginationParams",
    "PaginatedResponse",
    "ErrorResponse",
    "HealthResponse",
    "MessageResponse",
    # User
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserProfileUpdate",
    "UserProfileResponse",
    "UserDetailResponse",
    "TokenResponse",
    "AuthResponse",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    # Chapter
    "ModuleResponse",
    "ChapterResponse",
    "ChapterDetailResponse",
    "ChapterProgressResponse",
    "TranslationResponse",
    # Chat
    "ChatQueryRequest",
    "ChatSourceResponse",
    "ConversationContextResponse",
    "ChatMessageResponse",
    "ChatQueryResponse",
    "ConversationSessionResponse",
    "ChatRatingRequest",
]
