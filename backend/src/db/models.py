"""
SQLAlchemy database models for the application.

Core entities:
- User: Student/educator account
- UserProfile: Extended profile information
- Module: Course modules
- Chapter: Lessons within modules
- Embedding: Vector embeddings for vector search
- ChapterProgress: Student progress tracking
- ChatMessage: Conversation history
- Translation: Multi-language support
- CapstoneSubmission: Student capstone projects (Phase 2)
"""

from sqlalchemy import (
    Column, String, Text, DateTime, Boolean, Integer, Float, ForeignKey, Index, Enum,
    JSON
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
import uuid as uuid_lib
from typing import Optional, List

from db.base import Base


class User(Base):
    """
    Core user entity for authentication and profile management.

    Relationships:
    - chapter_progress: One-to-many with ChapterProgress
    - chat_messages: One-to-many with ChatMessage
    - capstone_submissions: One-to-many with CapstoneSubmission
    - user_profile: One-to-one with UserProfile
    """
    __tablename__ = "users"

    # Primary Key
    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=lambda: str(uuid_lib.uuid4()),
    )

    # Authentication
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Account status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Preferences
    language_preference: Mapped[str] = mapped_column(String(5), default="en", nullable=False)  # "en", "ur"
    theme: Mapped[str] = mapped_column(String(10), default="light", nullable=False)  # "light", "dark"

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    chapter_progress = relationship("ChapterProgress", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    capstone_submissions = relationship("CapstoneSubmission", back_populates="user", cascade="all, delete-orphan")
    user_profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_user_email", email),
        Index("idx_user_active", is_active),
    )


class UserProfile(Base):
    """Extended user profile information."""
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid_lib.uuid4()))
    user_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)

    # Profile Info
    bio: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    organization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Preferences
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    show_progress_publicly: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="user_profile")


class Module(Base):
    """Top-level course modules (ROS 2, Digital Twin, Isaac, VLA)."""
    __tablename__ = "modules"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid_lib.uuid4()))

    # Identifiers
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)  # "ros2", "digital-twin"
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Metadata
    order: Mapped[int] = mapped_column(Integer, nullable=False)  # Display order
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    chapters = relationship("Chapter", back_populates="module", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_module_slug", slug),
        Index("idx_module_published", is_published),
    )


class Chapter(Base):
    """Individual chapters within a module."""
    __tablename__ = "chapters"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid_lib.uuid4()))

    # Foreign Keys
    module_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("modules.id"), nullable=False, index=True)

    # Identifiers
    slug: Mapped[str] = mapped_column(String(100), nullable=False)  # Unique within module: "2.1", "2.2", etc.
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Metadata
    order: Mapped[int] = mapped_column(Integer, nullable=False)  # Display order within module
    difficulty_level: Mapped[str] = mapped_column(String(20), default="intermediate")  # "beginner", "intermediate", "advanced"
    estimated_duration_minutes: Mapped[int] = mapped_column(Integer, default=60)

    # Content
    content_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Rich HTML content
    learning_objectives: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of objectives

    # Publishing
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    module = relationship("Module", back_populates="chapters")
    embeddings = relationship("Embedding", back_populates="chapter", cascade="all, delete-orphan")
    chapter_progress = relationship("ChapterProgress", back_populates="chapter", cascade="all, delete-orphan")
    translations = relationship("Translation", back_populates="chapter", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_chapter_module_slug", module_id, slug),
        Index("idx_chapter_published", is_published),
        Index("idx_chapter_difficulty", difficulty_level),
    )


class Embedding(Base):
    """Vector embeddings for semantic search (stored locally, vectorized in Qdrant)."""
    __tablename__ = "embeddings"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid_lib.uuid4()))

    # Foreign Keys
    chapter_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False, index=True)

    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)  # Text segment to be embedded
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)  # Order within chapter

    # Embedding metadata
    embedding_model: Mapped[str] = mapped_column(String(100), default="text-embedding-3-small")
    qdrant_point_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Reference to Qdrant

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    chapter = relationship("Chapter", back_populates="embeddings")

    __table_args__ = (
        Index("idx_embedding_chapter", chapter_id),
    )


class ChapterProgress(Base):
    """Track student progress through chapters."""
    __tablename__ = "chapter_progress"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid_lib.uuid4()))

    # Foreign Keys
    user_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    chapter_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False, index=True)

    # Progress Tracking
    status: Mapped[str] = mapped_column(String(20), default="not_started")  # "not_started", "in_progress", "completed"
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0)
    quiz_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-100
    quiz_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    exercise_passed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chapter_progress")
    chapter = relationship("Chapter", back_populates="chapter_progress")

    __table_args__ = (
        Index("idx_progress_user", user_id),
        Index("idx_progress_chapter", chapter_id),
        Index("idx_progress_user_chapter", user_id, chapter_id),
        Index("idx_progress_status", status),
    )


class ChatMessage(Base):
    """Conversation history with RAG chatbot."""
    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid_lib.uuid4()))

    # Foreign Keys
    user_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Message Content
    query: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)

    # Context (Phase 1+)
    conversation_session_id: Mapped[Optional[str]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)  # For multi-turn
    parent_message_id: Mapped[Optional[str]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chat_messages.id"), nullable=True)  # For follow-ups
    intent: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # "explain", "code_example", "debug", etc.
    context_chapter_id: Mapped[Optional[str]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    context_module_slug: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    user_difficulty_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    clarification_depth: Mapped[int] = mapped_column(Integer, default=0)
    was_follow_up: Mapped[bool] = mapped_column(Boolean, default=False)

    # Sources used in response (JSON array)
    sources: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of chapter/embedding references

    # Quality metrics (Phase 2)
    user_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5 stars
    helpful_count: Mapped[int] = mapped_column(Integer, default=0)
    unhelpful_count: Mapped[int] = mapped_column(Integer, default=0)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # -1.0 to 1.0

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chat_messages")

    __table_args__ = (
        Index("idx_message_user", user_id),
        Index("idx_message_created", created_at),
        Index("idx_message_session", conversation_session_id),
    )


class Translation(Base):
    """Multi-language translations of chapters (for i18n)."""
    __tablename__ = "translations"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid_lib.uuid4()))

    # Foreign Keys
    chapter_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False, index=True)

    # Language
    language_code: Mapped[str] = mapped_column(String(5), nullable=False)  # "en", "ur", etc.

    # Translated Content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    content_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    chapter = relationship("Chapter", back_populates="translations")

    __table_args__ = (
        Index("idx_translation_chapter_lang", chapter_id, language_code),
    )


class CapstoneSubmission(Base):
    """Student capstone project submissions (Phase 2+)."""
    __tablename__ = "capstone_submissions"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid_lib.uuid4()))

    # Foreign Keys
    user_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Submission
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source_code_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    demo_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Evaluation (Phase 2+)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # "pending", "reviewing", "approved", "rejected"
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-100
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewer_id: Mapped[Optional[str]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    # Timestamps
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="capstone_submissions")

    __table_args__ = (
        Index("idx_capstone_user", user_id),
        Index("idx_capstone_status", status),
    )
