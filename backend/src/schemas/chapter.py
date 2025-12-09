"""Pydantic schemas for chapter-related endpoints."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from schemas.common import BaseSchema


class ModuleResponse(BaseSchema):
    """Schema for module response."""

    id: str
    slug: str
    title: str
    description: str
    order: int
    is_published: bool
    published_at: Optional[datetime] = None


class ChapterResponse(BaseSchema):
    """Schema for chapter response."""

    id: str
    module_id: str
    slug: str
    title: str
    description: str
    order: int
    difficulty_level: str
    estimated_duration_minutes: int
    is_published: bool
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ChapterDetailResponse(ChapterResponse):
    """Full chapter response with content."""

    content_html: Optional[str] = None
    learning_objectives: Optional[str] = None  # JSON array
    module: Optional[ModuleResponse] = None


class ChapterProgressResponse(BaseSchema):
    """Schema for chapter progress."""

    id: str
    user_id: str
    chapter_id: str
    status: str
    progress_percentage: int
    time_spent_seconds: int
    quiz_score: Optional[float] = None
    quiz_passed: bool
    exercise_passed: bool
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TranslationResponse(BaseSchema):
    """Schema for chapter translation."""

    id: str
    chapter_id: str
    language_code: str
    title: str
    description: str
    is_published: bool
    published_at: Optional[datetime] = None
