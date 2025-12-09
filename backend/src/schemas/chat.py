"""Pydantic schemas for chat/RAG endpoints."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from schemas.common import BaseSchema


class ChatQueryRequest(BaseSchema):
    """Schema for chat query request."""

    query: str = Field(..., min_length=1, max_length=5000)
    mode: str = Field(default="global")  # "global", "chapter", "module"
    chapter_id: Optional[str] = None
    conversation_session_id: Optional[str] = None
    parent_message_id: Optional[str] = None
    intent: Optional[str] = None  # "explain", "code_example", "debug", etc.
    user_difficulty: Optional[str] = None


class ChatSourceResponse(BaseSchema):
    """Schema for source citation."""

    chapter_id: str
    chapter_title: str
    module_slug: str
    excerpt: str
    relevance_score: float


class ConversationContextResponse(BaseSchema):
    """Schema for conversation context."""

    session_id: Optional[str] = None
    topics: List[str] = []
    next_suggestions: List[str] = []


class ChatMessageResponse(BaseSchema):
    """Schema for single chat message in conversation history."""

    message_id: str
    query: str
    response: str
    intent: Optional[str] = None
    created_at: datetime


class ChatQueryResponse(BaseSchema):
    """Schema for chat query response."""

    message_id: str
    response: str
    sources: List[ChatSourceResponse] = []
    conversation_context: Optional[ConversationContextResponse] = None
    follow_up_options: List[str] = []
    created_at: datetime


class ConversationSessionResponse(BaseSchema):
    """Schema for conversation session."""

    session_id: str
    user_id: str
    created_at: datetime
    current_chapter: Optional[Dict[str, Any]] = None
    conversation_history: List[ChatMessageResponse] = []
    topics_discussed: List[str] = []
    session_insights: Optional[Dict[str, Any]] = None


class ChatRatingRequest(BaseModel):
    """Schema for rating a chat response."""

    message_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=500)
