# Phase 1 Design: Data Models & Entity Definitions

**Branch**: `005-phase1-design` | **Date**: 2025-12-09 | **Plan**: [plan.md](./plan.md)

---

## Overview

This document defines all database entities, relationships, and Pydantic models for Phase 1 of the Physical AI & Humanoid Robotics Textbook project. All models conform to the constitution's Technical Excellence principle (full type annotations, validation, Pydantic v2).

**Database**: Neon Postgres
**ORM**: SQLAlchemy 2.x with async session
**Validation**: Pydantic v2
**Versioning**: Initial schema v1.0.0 (see migrations/)

---

## Core Entity Relationships

```
User (1) ──────→ (N) ChapterProgress
User (1) ──────→ (N) ChatMessage
User (1) ──────→ (N) CapstoneSubmission
User (1) ──────→ (1) UserProfile

Module (1) ──────→ (N) Chapter
Chapter (1) ──────→ (N) Embedding
Chapter (1) ──────→ (N) ChapterProgress
Chapter (1) ──────→ (N) Translation

Embedding (N) ──────→ (1) VectorStore (Qdrant)
Translation (N) ──────→ (1) Translator (User)
```

---

## SQLAlchemy Models (backend/src/db/models.py)

### 1. User Model

```python
from sqlalchemy import Column, String, DateTime, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid as uuid_lib

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
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid_lib.uuid4,
        nullable=False
    )

    # Authentication (via better-auth, stored for record)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # User Info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Preferences
    language_preference: Mapped[str] = mapped_column(
        String(5),  # "en" or "ur"
        default="en",
        nullable=False
    )
    theme: Mapped[str] = mapped_column(
        String(10),  # "light" or "dark"
        default="light",
        nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    chapter_progress = relationship("ChapterProgress", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    capstone_submissions = relationship("CapstoneSubmission", back_populates="user", cascade="all, delete-orphan")
    user_profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
```

### 2. UserProfile Model

```python
class UserProfile(Base):
    """Extended user profile information."""
    __tablename__ = "user_profiles"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)

    # Profile Info
    bio: Mapped[str | None] = mapped_column(String(500), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    organization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Preferences (extended)
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    show_progress_publicly: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="user_profile")
```

### 3. Module Model

```python
class Module(Base):
    """Top-level course modules (ROS 2, Digital Twin, Isaac, VLA)."""
    __tablename__ = "modules"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)

    # Identifiers
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)  # "ros2", "digital-twin", etc.
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Metadata
    order: Mapped[int] = mapped_column(Integer, nullable=False)  # Display order
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    chapters = relationship("Chapter", back_populates="module", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Module(slug={self.slug}, title={self.title})>"
```

### 4. Chapter Model

```python
class Chapter(Base):
    """Individual chapters within modules."""
    __tablename__ = "chapters"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    module_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("modules.id"), nullable=False)

    # Identifiers
    slug: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # "ros2-basics", etc.
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # Content
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)  # Full chapter markdown
    estimated_reading_time: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Minutes

    # Metadata
    order: Mapped[int] = mapped_column(Integer, nullable=False)  # Display order within module
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    ready_for_translation: Mapped[bool] = mapped_column(Boolean, default=False)  # Flag for i18n

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    module = relationship("Module", back_populates="chapters")
    embeddings = relationship("Embedding", back_populates="chapter", cascade="all, delete-orphan")
    chapter_progress = relationship("ChapterProgress", back_populates="chapter", cascade="all, delete-orphan")
    translations = relationship("Translation", back_populates="chapter", cascade="all, delete-orphan")

    # Composite Index
    __table_args__ = (UniqueConstraint("module_id", "slug", name="uq_module_chapter_slug"),)

    def __repr__(self) -> str:
        return f"<Chapter(slug={self.slug}, title={self.title})>"
```

### 5. Embedding Model

```python
class Embedding(Base):
    """
    Vector embeddings for RAG chatbot.
    Each chunk of a chapter gets embedded via OpenAI text-embedding-3-small.
    Synced to Qdrant Cloud for vector search.
    """
    __tablename__ = "embeddings"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    chapter_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False, index=True)

    # Content
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)  # Text chunk (max ~512 tokens)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)  # Position in chapter

    # Embedding Metadata
    embedding_model: Mapped[str] = mapped_column(
        String(100),
        default="text-embedding-3-small",
        nullable=False
    )
    vector_dimension: Mapped[int] = mapped_column(Integer, default=1536)  # For text-embedding-3-small

    # Vector ID (for Qdrant reference)
    qdrant_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)  # Last sync to Qdrant

    # Relationships
    chapter = relationship("Chapter", back_populates="embeddings")

    def __repr__(self) -> str:
        return f"<Embedding(chapter_id={self.chapter_id}, chunk_index={self.chunk_index})>"
```

### 6. ChapterProgress Model

```python
class ChapterProgress(Base):
    """User progress per chapter (quizzes, exercises, completion)."""
    __tablename__ = "chapter_progress"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    chapter_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False, index=True)

    # Progress Status
    is_started: Mapped[bool] = mapped_column(Boolean, default=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completion_percentage: Mapped[int] = mapped_column(Integer, default=0)  # 0-100

    # Assessment Results
    quiz_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Percentage (0-100)
    quiz_attempts: Mapped[int] = mapped_column(Integer, default=0)
    exercises_completed: Mapped[int] = mapped_column(Integer, default=0)
    exercises_total: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Timestamps
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_accessed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chapter_progress")
    chapter = relationship("Chapter", back_populates="chapter_progress")

    # Composite Index
    __table_args__ = (UniqueConstraint("user_id", "chapter_id", name="uq_user_chapter_progress"),)

    def __repr__(self) -> str:
        return f"<ChapterProgress(user={self.user_id}, chapter={self.chapter_id}, completed={self.is_completed})>"
```

### 7. ChatMessage Model

```python
class ChatMessage(Base):
    """RAG chatbot conversation history."""
    __tablename__ = "chat_messages"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Message Content
    query: Mapped[str] = mapped_column(Text, nullable=False)  # User question
    response: Mapped[str] = mapped_column(Text, nullable=False)  # Chatbot response
    mode: Mapped[str] = mapped_column(
        String(50),  # "global", "chapter-specific", "highlight"
        nullable=False
    )

    # Context
    chapter_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=True)
    highlighted_text: Mapped[str | None] = mapped_column(Text, nullable=True)  # For highlight mode

    # Source Attribution
    source_citations: Mapped[list[dict]] = mapped_column(
        JSON,
        default=[],
        nullable=False
    )  # [{"chapter_slug": "ros2-basics", "section": "Publishers", "relevance": 0.95}]

    # Quality Metrics
    user_feedback: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5 star rating
    was_helpful: Mapped[bool | None] = mapped_column(Boolean, nullable=True)  # Thumbs up/down

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chat_messages")

    def __repr__(self) -> str:
        return f"<ChatMessage(user={self.user_id}, mode={self.mode}, created={self.created_at})>"
```

### 8. Translation Model

```python
class Translation(Base):
    """Multi-language content translations (English → Urdu)."""
    __tablename__ = "translations"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    chapter_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False, index=True)
    translator_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Language
    language: Mapped[str] = mapped_column(String(5), nullable=False)  # "ur" for Urdu, "en" for English

    # Content
    translated_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    translated_content: Mapped[str] = mapped_column(Text, nullable=False)  # Full translated markdown

    # Status
    status: Mapped[str] = mapped_column(
        String(20),  # "draft", "submitted", "verified", "published"
        default="draft",
        nullable=False
    )
    verified_by: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Composite Index
    __table_args__ = (UniqueConstraint("chapter_id", "language", name="uq_chapter_language_translation"),)

    def __repr__(self) -> str:
        return f"<Translation(chapter={self.chapter_id}, language={self.language}, status={self.status})>"
```

### 9. CapstoneSubmission Model

```python
class CapstoneSubmission(Base):
    """Capstone project submissions (voice command → action graph → video)."""
    __tablename__ = "capstone_submissions"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Submission Content
    voice_command: Mapped[str] = mapped_column(Text, nullable=False)  # Original voice input
    transcribed_text: Mapped[str] = mapped_column(Text, nullable=False)  # Whisper transcription

    # Action Graph (JSON)
    action_graph: Mapped[dict] = mapped_column(
        JSON,
        nullable=False
    )
    # Example: {
    #   "task": "pick_up_object",
    #   "object": "blue_cube",
    #   "location": "table",
    #   "actions": [
    #     {"type": "navigate", "goal": [1.0, 2.0, 0.0]},
    #     {"type": "perceive", "sensor": "camera"},
    #     {"type": "grasp", "object_id": "blue_cube_001"}
    #   ]
    # }

    # Video Submission
    video_url: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Link to video proof

    # Status & Grading
    status: Mapped[str] = mapped_column(
        String(20),  # "submitted", "review", "approved", "rejected"
        default="submitted",
        nullable=False
    )
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)  # Reviewer feedback
    grade: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0-100

    # Timestamps
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    graded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="capstone_submissions")

    def __repr__(self) -> str:
        return f"<CapstoneSubmission(user={self.user_id}, status={self.status})>"
```

---

## Pydantic Schemas (Request/Response)

### User Schemas

```python
# backend/src/schemas/user_schemas.py

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID

class UserCreate(BaseModel):
    """Request: User registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255)
    name: str = Field(..., min_length=1, max_length=255)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "password": "SecurePass123!",
                "name": "Ahmed Ali"
            }
        }

class UserLogin(BaseModel):
    """Request: User login."""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Response: User profile (public data)."""
    id: UUID
    email: EmailStr
    name: str
    language_preference: str = "en"
    theme: str = "light"
    created_at: datetime

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    """Request: Update user profile."""
    bio: str | None = None
    avatar_url: str | None = None
    organization: str | None = None
    language_preference: str | None = None
    theme: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "bio": "Robotics student",
                "language_preference": "ur",
                "theme": "dark"
            }
        }
```

### Chat Schemas

```python
# backend/src/schemas/chat_schemas.py

class ChatQueryRequest(BaseModel):
    """Request: Global or chapter-specific chat query."""
    query: str = Field(..., min_length=1, max_length=2000)
    mode: str = Field("global", pattern="^(global|chapter-specific|highlight)$")
    chapter_id: UUID | None = None
    highlighted_text: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Explain ROS 2 publishers and subscribers",
                "mode": "global",
                "chapter_id": None
            }
        }

class SourceCitation(BaseModel):
    """Citation metadata."""
    chapter_slug: str
    chapter_title: str
    section: str | None = None
    relevance_score: float = Field(..., ge=0.0, le=1.0)

class ChatResponse(BaseModel):
    """Response: RAG chatbot answer."""
    message_id: UUID
    response: str
    sources: list[SourceCitation]
    response_time_ms: int
    model: str = "gpt-4o"

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "message_id": "550e8400-e29b-41d4-a716-446655440000",
                "response": "ROS 2 publishers send messages to topics...",
                "sources": [
                    {
                        "chapter_slug": "ros2-basics",
                        "chapter_title": "ROS 2 Basics",
                        "section": "Publishers & Subscribers",
                        "relevance_score": 0.98
                    }
                ],
                "response_time_ms": 1250,
                "model": "gpt-4o"
            }
        }
```

### Progress Schemas

```python
# backend/src/schemas/progress_schemas.py

class ChapterProgressResponse(BaseModel):
    """Response: User progress for a chapter."""
    chapter_id: UUID
    chapter_slug: str
    title: str
    is_completed: bool
    completion_percentage: int
    quiz_score: int | None
    exercises_completed: int
    exercises_total: int | None
    last_accessed_at: datetime

    class Config:
        from_attributes = True

class DashboardResponse(BaseModel):
    """Response: Full user progress dashboard."""
    user_id: UUID
    user_name: str
    total_completion_percentage: int
    modules: list[dict]  # [{module_slug, title, completion_percentage, chapters: [ChapterProgressResponse]}]

class ProgressUpdateRequest(BaseModel):
    """Request: Update chapter progress."""
    chapter_id: UUID
    is_completed: bool | None = None
    quiz_score: int | None = Field(None, ge=0, le=100)
    exercises_completed: int | None = Field(None, ge=0)
```

### VLA Planning Schemas

```python
# backend/src/schemas/vla_schemas.py

class ActionGraphNode(BaseModel):
    """Single action node in execution graph."""
    type: str  # "navigate", "perceive", "grasp", "move_arm", "release"
    parameters: dict  # Type-specific params
    safety_checks: list[str] = []  # ["collision_check", "grasp_stability"]

class ActionGraphRequest(BaseModel):
    """Request: Generate action graph from transcribed voice."""
    transcribed_text: str
    robot_state: dict | None = None  # Optional: current robot pose, gripper state

class ActionGraphResponse(BaseModel):
    """Response: Generated action graph."""
    action_graph_id: UUID
    task_description: str
    actions: list[ActionGraphNode]
    estimated_duration_seconds: int
    safety_warnings: list[str] = []
    validation_passed: bool
    validation_errors: list[str] = []

class CapstoneSubmissionRequest(BaseModel):
    """Request: Submit capstone project."""
    voice_command: str
    transcribed_text: str
    action_graph: ActionGraphResponse
    video_url: str | None = None
```

---

## Database Initialization (Alembic)

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial schema: users, chapters, embeddings, progress"

# Apply migration to database
alembic upgrade head
```

---

## Indexes & Query Performance

| Table | Index | Reason |
|-------|-------|--------|
| users | email (UNIQUE) | Auth lookups |
| users | created_at | User analytics queries |
| chapters | slug | Content lookups |
| chapters | module_id + order | Module chapter listing |
| embeddings | chapter_id | RAG content sync |
| embeddings | qdrant_id | Vector store sync |
| chapter_progress | user_id, chapter_id (UNIQUE) | User progress queries |
| chapter_progress | last_accessed_at | Dashboard queries |
| chat_messages | user_id, created_at | Chat history retrieval |
| translations | chapter_id, language (UNIQUE) | Translation lookup |
| capstone_submissions | user_id, submitted_at | Submission history |

---

## Migration Strategy

### Phase 1 (Weeks 1-3):
1. Create initial schema with all entities
2. Add indexes for high-traffic queries
3. Implement ORM layer with SQLAlchemy
4. Write migration tests

### Phase 2+ (Weeks 4+):
- Add translations table columns if needed
- Add new fields to CapstoneSubmission (e.g., gazebo_metrics)
- Use Alembic for rolling migrations (zero-downtime updates)

---

## Constraints & Validations

### Data Integrity
- ✅ Foreign key constraints on all relationships
- ✅ Unique constraints on natural keys (user email, chapter slug per module, translation per chapter/language)
- ✅ NOT NULL constraints enforced at DB + Pydantic level
- ✅ Check constraints for status enums (via Python enum validation)

### Application Validations (Pydantic)
- Email validation (EmailStr)
- Password strength (min 8 chars, mixed case recommended in docs)
- UUID validation (all IDs)
- Percentage fields (0-100)
- Timestamps (UTC datetime)
- JSON schema validation for action graphs

---

## Success Criteria (Phase 1 Gate)

- [ ] All 9 SQLAlchemy models created and tested
- [ ] Alembic migration scripts generate without errors
- [ ] Database connection and schema creation verified
- [ ] All Pydantic schemas compile with validation
- [ ] Foreign key constraints verified
- [ ] Unique constraints tested (duplicate email, chapter slug)
- [ ] ORM relationships load without N+1 queries
- [ ] Test database seeding works (fixtures)

---

**Next**: API contracts (`contracts/`) and endpoints implementation
