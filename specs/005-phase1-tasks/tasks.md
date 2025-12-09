# Phase 1: Sprint-Ready Task Breakdown

**Branch**: `005-phase1-design` → `006-phase1-implementation` | **Duration**: 2-3 weeks | **Spec**: [Plan](../004-plan-architecture/plan.md) | **Design**: [Data Models](../004-plan-architecture/data-model.md) | [API Contracts](../004-plan-architecture/contracts/API-CONTRACTS.md)

---

## Executive Summary

Phase 1 delivers the **Core Infrastructure & RAG Foundation** - the MVP that enables students to learn with an AI-powered chatbot. This sprint contains **42 actionable tasks** across 5 agent teams:

| Team | Agent | Task Count | Focus |
|------|-------|-----------|-------|
| Backend | RAG Chatbot | 12 | FastAPI, Qdrant, OpenAI |
| Backend | Authentication | 8 | better-auth, JWT, user mgmt |
| Frontend | Docusaurus | 10 | Sidebar, components, embedding |
| Data | Embeddings & Sync | 8 | Vector prep, Qdrant sync |
| Infra | DevOps & Testing | 4 | Docker, migrations, CI/CD |

**Definition of Done (Phase 1 Gate)**:
- [ ] 42 tasks completed and merged to main
- [ ] 95%+ test coverage on critical paths
- [ ] All success criteria met (see plan.md)
- [ ] Feature merged to main via PR

---

## Task Categories

### Group 1: Backend Infrastructure (20 tasks)

#### 1.1 FastAPI Setup & Core (4 tasks)

**T1.1.1** - Initialize FastAPI project structure
- **Status**: Ready
- **Owner**: RAG Chatbot Agent
- **Story**: As a developer, I need a FastAPI project scaffold with proper folder structure, so that all components integrate cleanly
- **Acceptance**:
  - [ ] `backend/src/main.py` created with FastAPI app
  - [ ] Folder structure matches `plan.md` (models, schemas, api, services, db, utils, middleware)
  - [ ] CORS middleware configured
  - [ ] Request ID middleware for tracing
  - [ ] Startup/shutdown event handlers implemented
  - [ ] Health check endpoint returns 200 OK with service status
- **Dependencies**: None
- **Effort**: 2 hours
- **Files to create**: `backend/src/main.py`, `backend/src/config.py`
- **Tests**: `tests/unit/test_main.py::test_app_startup`, `test_health_check`

**T1.1.2** - Set up Pydantic models & schemas
- **Status**: Ready
- **Owner**: RAG Chatbot Agent
- **Story**: As a developer, I need Pydantic v2 models for type safety and validation
- **Acceptance**:
  - [ ] All 6 Pydantic models created (User, UserProfile, Chapter, Embedding, ChatMessage, Translation)
  - [ ] Request/response schemas for all endpoints
  - [ ] Validation rules: email (EmailStr), password (min 8), UUID, ranges (0-100)
  - [ ] JSON schema examples in docstrings
  - [ ] All models pass Pydantic v2 validation
- **Dependencies**: None
- **Effort**: 3 hours
- **Files to create**: `backend/src/models/`, `backend/src/schemas/`
- **Tests**: `tests/unit/test_models.py` with 100% coverage

**T1.1.3** - Configure environment & secrets management
- **Status**: Ready
- **Owner**: RAG Chatbot Agent
- **Story**: As an operator, I need secure environment variable management for local, staging, and production
- **Acceptance**:
  - [ ] `.env.example` with all required variables
  - [ ] `config.py` using pydantic-settings for type-safe config
  - [ ] Support 3 environments (dev, staging, prod)
  - [ ] Secrets never logged or exposed
  - [ ] .env.* added to .gitignore
  - [ ] Documentation on required keys
- **Dependencies**: None
- **Effort**: 1 hour
- **Files to create**: `backend/.env.example`, `backend/src/config.py`
- **Tests**: `tests/unit/test_config.py::test_env_validation`

**T1.1.4** - Set up logging & error handling
- **Status**: Ready
- **Owner**: RAG Chatbot Agent
- **Story**: As a developer, I need structured logging and consistent error responses for debugging
- **Acceptance**:
  - [ ] Structured logging with Python logging module
  - [ ] Request/response logging middleware
  - [ ] Error handler for FastAPI exceptions
  - [ ] Custom exceptions defined (ValidationError, NotFoundError, ServiceUnavailableError)
  - [ ] All errors return standard JSON format (error, message, code, details)
  - [ ] Sensitive data not logged
- **Dependencies**: T1.1.1
- **Effort**: 2 hours
- **Files to create**: `backend/src/utils/logger.py`, `backend/src/utils/errors.py`, `backend/src/middleware/error_handler.py`
- **Tests**: `tests/unit/test_error_handler.py`

#### 1.2 Database Layer (4 tasks)

**T1.2.1** - Set up SQLAlchemy ORM & async session management
- **Status**: Ready
- **Owner**: RAG Chatbot Agent
- **Story**: As a developer, I need async-safe database connections to support high concurrency
- **Acceptance**:
  - [ ] SQLAlchemy 2.x with async engine
  - [ ] Neon Postgres connection pooling (asyncpg)
  - [ ] Session factory with dependency injection
  - [ ] Connection pooling configured (pool_size=10, max_overflow=20)
  - [ ] Automatic session cleanup on request end
  - [ ] All models use UUID primary keys
  - [ ] Timestamps (created_at, updated_at) on all entities
- **Dependencies**: T1.1.3
- **Effort**: 3 hours
- **Files to create**: `backend/src/db/session.py`, `backend/src/db/base.py`
- **Tests**: `tests/integration/test_db_session.py` with connection pooling tests

**T1.2.2** - Create SQLAlchemy models (9 entities)
- **Status**: Ready
- **Owner**: RAG Chatbot Agent
- **Story**: As a developer, I need all database models implemented per data-model.md specification
- **Acceptance**:
  - [ ] User model with authentication fields
  - [ ] UserProfile model (1-to-1 relationship)
  - [ ] Module, Chapter, Embedding models (with relationships)
  - [ ] ChapterProgress tracking model
  - [ ] ChatMessage history model
  - [ ] Translation model (for i18n)
  - [ ] CapstoneSubmission model (ready for Phase 2)
  - [ ] All foreign keys with cascade rules
  - [ ] Unique constraints on natural keys (email, chapter slug per module, etc.)
  - [ ] Composite indexes for common queries
- **Dependencies**: T1.2.1
- **Effort**: 4 hours
- **Files to create**: `backend/src/db/models.py` (700+ lines)
- **Tests**: `tests/unit/test_models.py::test_user_creation`, `test_chapter_progress_unique_constraint`, etc.

**T1.2.3** - Set up Alembic migrations framework
- **Status**: Ready
- **Owner**: RAG Chatbot Agent
- **Story**: As an operator, I need schema versioning and zero-downtime deployments
- **Acceptance**:
  - [ ] Alembic initialized and configured
  - [ ] Initial migration generated from models (autogenerate)
  - [ ] Migration naming convention: `<timestamp>_<description>.py`
  - [ ] Migration can be applied forward and backward
  - [ ] Version tracking in database (_alembic_version table)
  - [ ] Migration script for seed data (Phase 1 test data)
  - [ ] README documenting migration process
- **Dependencies**: T1.2.2
- **Effort**: 2 hours
- **Files to create**: `backend/migrations/` directory, initial migration script
- **Tests**: `tests/integration/test_migrations.py::test_initial_migration_creates_tables`

**T1.2.4** - Create database seed script for testing
- **Status**: Ready
- **Owner**: RAG Chatbot Agent
- **Story**: As a developer, I need test data to verify the system end-to-end
- **Acceptance**:
  - [ ] Seed script creates 3 test users
  - [ ] 2 test modules (ROS 2, Digital Twin) with 5 chapters each
  - [ ] 10 test embeddings per chapter (for vector search)
  - [ ] 5 sample chat messages per user
  - [ ] 1 capstone submission (ready for Phase 2)
  - [ ] Script runnable with: `python scripts/seed_data.py`
  - [ ] Idempotent (can be run multiple times)
- **Dependencies**: T1.2.3
- **Effort**: 2 hours
- **Files to create**: `backend/scripts/seed_data.py`
- **Tests**: `tests/integration/test_seed_data.py`

#### 1.3 Authentication & User Management (8 tasks)

**T1.3.1** - Integrate better-auth backend
- **Status**: Ready
- **Owner**: Authentication Agent
- **Story**: As a developer, I need production-grade authentication without managing password hashing
- **Acceptance**:
  - [ ] better-auth library integrated
  - [ ] User sign-up endpoint: POST /api/auth/signup
  - [ ] Login endpoint: POST /api/auth/login
  - [ ] JWT token generation (24-hour expiry)
  - [ ] Password hashing via better-auth
  - [ ] Email validation
  - [ ] Duplicate email rejection (409 Conflict)
  - [ ] better-auth database tables created (users, sessions, tokens)
- **Dependencies**: T1.2.1, T1.2.2, T1.1.3
- **Effort**: 3 hours
- **Files to create**: `backend/src/services/auth_service.py`, `backend/src/api/auth.py`
- **Tests**: `tests/integration/test_auth_api.py::test_signup`, `test_login`, `test_duplicate_email`

**T1.3.2** - Implement JWT token validation middleware
- **Status**: Ready
- **Owner**: Authentication Agent
- **Story**: As a developer, I need protected endpoints that validate JWT tokens
- **Acceptance**:
  - [ ] JWT middleware extracts token from Authorization header
  - [ ] Token signature validation
  - [ ] Token expiration check
  - [ ] User context injected into requests (current_user dependency)
  - [ ] Expired token returns 401 Unauthorized
  - [ ] Missing token returns 401 Unauthorized
  - [ ] Invalid token returns 401 Unauthorized
  - [ ] Health check endpoint skips auth
- **Dependencies**: T1.3.1, T1.1.1
- **Effort**: 2 hours
- **Files to create**: `backend/src/middleware/auth_middleware.py`, `backend/src/api/dependencies.py`
- **Tests**: `tests/unit/test_auth_middleware.py`, `test_invalid_token`, `test_expired_token`

**T1.3.3** - Implement password reset flow
- **Status**: Ready
- **Owner**: Authentication Agent
- **Story**: As a user, I can reset my password via email link
- **Acceptance**:
  - [ ] POST /api/auth/password-reset endpoint
  - [ ] Generates secure reset token (valid 1 hour)
  - [ ] Sends email with reset link (mock for dev)
  - [ ] Token stored in database with expiry
  - [ ] Reset endpoint validates token and updates password
  - [ ] Token consumed after use (one-time)
  - [ ] Security: Always return 200 OK (even if email not found)
- **Dependencies**: T1.3.1, T1.2.1
- **Effort**: 3 hours
- **Files to create**: `backend/src/services/password_reset_service.py`
- **Tests**: `tests/integration/test_password_reset.py`

**T1.3.4** - User profile management endpoints
- **Status**: Ready
- **Owner**: Authentication Agent
- **Story**: As a user, I can view and update my profile and preferences
- **Acceptance**:
  - [ ] GET /api/auth/me (view current user)
  - [ ] PATCH /api/auth/profile (update profile, preferences)
  - [ ] Language preference persists (en/ur)
  - [ ] Theme preference persists (light/dark)
  - [ ] Bio, avatar_url, organization fields
  - [ ] Email notifications toggle
  - [ ] All endpoints require auth
  - [ ] Profile updates trigger updated_at timestamp
- **Dependencies**: T1.3.2
- **Effort**: 2 hours
- **Files to create**: `backend/src/api/auth.py` (extend with profile routes)
- **Tests**: `tests/integration/test_profile.py`

**T1.3.5** - Set up logout & session management
- **Status**: Ready
- **Owner**: Authentication Agent
- **Story**: As a user, I can log out and my session is invalidated
- **Acceptance**:
  - [ ] POST /api/auth/logout endpoint
  - [ ] Session marked as revoked in database
  - [ ] Token no longer valid after logout
  - [ ] Multiple devices: logout affects only current session (optional for Phase 1, can skip)
  - [ ] Returns 200 OK on successful logout
- **Dependencies**: T1.3.1, T1.3.2
- **Effort**: 1 hour
- **Files to create**: Extend `backend/src/services/auth_service.py`
- **Tests**: `tests/integration/test_logout.py`

**T1.3.6** - User profile creation in UserProfile table
- **Status**: Ready
- **Owner**: Authentication Agent
- **Story**: As a user, I have extended profile data (bio, avatar, organization)
- **Acceptance**:
  - [ ] UserProfile created automatically on user sign-up
  - [ ] UserProfile linked to User (1-to-1)
  - [ ] Cascade delete when user deleted
  - [ ] All profile fields optional on creation
  - [ ] Profile accessible via GET /api/auth/me
- **Dependencies**: T1.3.1, T1.2.2
- **Effort**: 1 hour
- **Files to create**: Extend migration, auth_service
- **Tests**: `tests/unit/test_user_profile_creation.py`

**T1.3.7** - API endpoint: POST /api/auth/signup tests
- **Status**: Ready
- **Owner**: Authentication Agent
- **Story**: As a tester, I need comprehensive tests for sign-up edge cases
- **Acceptance**:
  - [ ] Valid sign-up returns 201 Created
  - [ ] Invalid email format returns 400
  - [ ] Password too short returns 400
  - [ ] Duplicate email returns 409
  - [ ] Missing fields returns 400
  - [ ] Response includes user_id, access_token, expires_in
  - [ ] Token can be used immediately for protected endpoints
- **Dependencies**: T1.3.1
- **Effort**: 1.5 hours
- **Files**: `tests/integration/test_auth_api.py`
- **Tests**: 8+ test cases

**T1.3.8** - API endpoint: POST /api/auth/login tests
- **Status**: Ready
- **Owner**: Authentication Agent
- **Story**: As a tester, I need to verify login flow security
- **Acceptance**:
  - [ ] Valid credentials return token
  - [ ] Invalid password returns 401
  - [ ] User not found returns 401
  - [ ] Token valid for protected endpoints
  - [ ] Multiple logins work (new token each time)
  - [ ] Response matches contract
- **Dependencies**: T1.3.1
- **Effort**: 1 hour
- **Files**: `tests/integration/test_auth_api.py`
- **Tests**: 6+ test cases

#### 1.4 Chat Service & RAG Integration (8 tasks)

**T1.4.1** - Integrate Qdrant Cloud vector database
- **Status**: Ready
- **Owner**: RAG Chatbot Agent
- **Story**: As a developer, I need vector search for semantic retrieval of chapters
- **Acceptance**:
  - [ ] Qdrant SDK installed and configured
  - [ ] Connection to Qdrant Cloud verified
  - [ ] Collection schema defined (matching embeddings structure)
  - [ ] Collection auto-created if not exists
  - [ ] Qdrant service class: QdrantService
  - [ ] Methods: search(query_vector, limit=5), insert_vector(), delete_vector()
  - [ ] Connection pooling and retry logic
  - [ ] Error handling for Qdrant unavailability
- **Dependencies**: T1.1.3, T1.2.1
- **Effort**: 3 hours
- **Files to create**: `backend/src/services/qdrant_service.py`
- **Tests**: `tests/integration/test_qdrant_service.py`

**T1.4.2** - Integrate OpenAI API for embeddings & completions
- **Status**: Ready
- **Owner**: RAG Chatbot Agent
- **Story**: As a developer, I need LLM integration for generating embeddings and chat responses
- **Acceptance**:
  - [ ] OpenAI SDK installed
  - [ ] LLM service class: LLMService
  - [ ] Methods: embed_text(), chat_completion()
  - [ ] Embeddings model: text-embedding-3-small
  - [ ] Chat model: gpt-4o
  - [ ] API key from environment
  - [ ] Retry logic (exponential backoff) for rate limits
  - [ ] Timeout: 30 seconds for embeddings, 60 for chat
  - [ ] Error handling for quota exceeded, invalid key, timeout
- **Dependencies**: T1.1.3, T1.1.4
- **Effort**: 2 hours
- **Files to create**: `backend/src/services/llm_service.py`
- **Tests**: `tests/unit/test_llm_service.py` (mock OpenAI)

**T1.4.3** - Build RAG pipeline: query → embed → search → prompt → response
- **Status**: Ready
- **Owner**: RAG Chatbot Agent
- **Story**: As a student, I ask questions and get answers citing source chapters
- **Acceptance**:
  - [ ] ChatService orchestrates: embed query → search Qdrant → build prompt → call LLM
  - [ ] Retrieved chunks ranked by relevance
  - [ ] System prompt includes: "Only answer questions about this course" + retrieved context
  - [ ] Response includes source citations (chapter_slug, section, relevance_score)
  - [ ] Handles three modes: global, chapter-specific, highlight
  - [ ] Response time < 3 seconds (p95)
  - [ ] Response length < 2000 characters
- **Dependencies**: T1.4.1, T1.4.2, T1.2.1
- **Effort**: 3 hours
- **Files to create**: `backend/src/services/chat_service.py`
- **Tests**: `tests/integration/test_rag_pipeline.py`

**T1.4.4** - Implement chat API endpoints (POST /api/chat/query, GET /api/chat/history)
- **Status**: Ready
- **Owner**: RAG Chatbot Agent
- **Story**: As a frontend developer, I have chat endpoints to call
- **Acceptance**:
  - [ ] POST /api/chat/query (requires auth)
  - [ ] GET /api/chat/history (paginated, requires auth)
  - [ ] Query validation: 1-2000 chars, valid mode
  - [ ] Response matches contract (message_id, response, sources, response_time_ms)
  - [ ] All errors return proper HTTP codes
  - [ ] Rate limiting: 30 requests per minute per user
  - [ ] Message stored in chat_messages table
  - [ ] Supports filtering by chapter_id or mode
- **Dependencies**: T1.4.3, T1.3.2, T1.2.1
- **Effort**: 2 hours
- **Files to create**: `backend/src/api/chat.py`
- **Tests**: `tests/integration/test_chat_api.py`

**T1.4.5** - Implement feedback endpoint (POST /api/chat/feedback)
- **Status**: Ready
- **Owner**: RAG Chatbot Agent
- **Story**: As a student, I can rate responses to improve quality
- **Acceptance**:
  - [ ] POST /api/chat/feedback (1-5 star rating, helpful/not helpful)
  - [ ] Updates ChatMessage.user_feedback and was_helpful
  - [ ] Feedback data used for analytics
  - [ ] Returns 200 OK
- **Dependencies**: T1.4.4, T1.2.1
- **Effort**: 1 hour
- **Files to create**: Extend `backend/src/api/chat.py`
- **Tests**: `tests/integration/test_chat_feedback.py`

**T1.4.6** - Chat service error handling & fallback
- **Status**: Ready
- **Owner**: RAG Chatbot Agent
- **Story**: As a user, the system gracefully handles failures (Qdrant down, OpenAI timeout, etc.)
- **Acceptance**:
  - [ ] Qdrant down: Return error "Vector database temporarily unavailable"
  - [ ] OpenAI timeout: Return error "LLM service timed out, please try again"
  - [ ] Empty results: Return "I couldn't find relevant content. Try a different query."
  - [ ] All errors logged with context
  - [ ] Partial failures: Still return best-effort response if possible
  - [ ] No cascade failures (one service down doesn't crash whole API)
- **Dependencies**: T1.4.3, T1.1.4
- **Effort**: 1.5 hours
- **Files**: Extend chat_service.py, add exception handling
- **Tests**: `tests/integration/test_chat_error_handling.py`

**T1.4.7** - Integration tests: end-to-end chat query
- **Status**: Ready
- **Owner**: RAG Chatbot Agent
- **Story**: As a QA engineer, I verify the full chat flow
- **Acceptance**:
  - [ ] User authenticates
  - [ ] User submits query (global mode)
  - [ ] Chat service retrieves chapters
  - [ ] LLM generates response
  - [ ] Response stored in database
  - [ ] Frontend receives response with sources
  - [ ] User can see chat history
  - [ ] Feedback recorded
  - [ ] All assertions pass
- **Dependencies**: T1.4.4, T1.4.5, T1.3.2
- **Effort**: 2 hours
- **Files**: `tests/integration/test_chat_full_flow.py`
- **Tests**: 3+ comprehensive end-to-end tests

**T1.4.8** - Performance optimization: response time < 3 seconds (p95)
- **Status**: Ready
- **Owner**: RAG Chatbot Agent
- **Story**: As a student, the chatbot responds quickly even under load
- **Acceptance**:
  - [ ] Profile RAG pipeline: identify bottlenecks
  - [ ] Qdrant search optimized (parallel requests if multiple chunks)
  - [ ] Connection pooling active for all services
  - [ ] Caching (optional): LRU cache for repeated queries
  - [ ] Load test: 10 concurrent requests, measure p95
  - [ ] Target: p95 < 3 seconds
  - [ ] Document optimization decisions
- **Dependencies**: T1.4.3
- **Effort**: 2 hours
- **Files**: Performance tests, optimization code
- **Tests**: `tests/integration/test_chat_performance.py`

### Group 2: Data Preparation & Sync (8 tasks)

#### 2.1 Embedding Generation & Sync (8 tasks)

**T2.1.1** - Create content chunking strategy
- **Status**: Ready
- **Owner**: Data Team
- **Story**: As a data engineer, I need to split chapters into optimal chunks for vector search
- **Acceptance**:
  - [ ] Chunking strategy: 256-512 tokens per chunk
  - [ ] Overlap: 50 tokens between chunks
  - [ ] Chunk metadata includes: chapter_id, chunk_index, source_section
  - [ ] Tokenizer: OpenAI tiktoken library
  - [ ] Chunks don't split mid-sentence (sentence boundaries)
  - [ ] Script: `scripts/chunk_content.py`
  - [ ] Runnable with: `python scripts/chunk_content.py <chapter_file>`
- **Effort**: 2 hours
- **Files to create**: `backend/scripts/chunk_content.py`, `backend/src/utils/chunking.py`
- **Tests**: `tests/unit/test_chunking.py::test_chunk_boundaries`, `test_metadata_attached`

**T2.1.2** - Generate embeddings for sample chapters
- **Status**: Ready
- **Owner**: Data Team
- **Story**: As a developer, sample chapters have embeddings for RAG testing
- **Acceptance**:
  - [ ] Embedding generation script created
  - [ ] Uses OpenAI text-embedding-3-small model
  - [ ] Generates embeddings for 2 sample modules (10 chapters, 10 chunks each = 100 embeddings)
  - [ ] Stores embeddings in embeddings table
  - [ ] Embeddings indexed by chapter_id and chunk_index
  - [ ] Batch processing: 1000 tokens batches to save API cost
  - [ ] Script: `python scripts/generate_embeddings.py --module ros2`
- **Effort**: 2 hours
- **Files to create**: `backend/scripts/generate_embeddings.py`
- **Tests**: `tests/integration/test_embedding_generation.py`

**T2.1.3** - Sync embeddings to Qdrant Cloud
- **Status**: Ready
- **Owner**: Data Team
- **Story**: As a data engineer, embeddings are synced to Qdrant for vector search
- **Acceptance**:
  - [ ] Qdrant sync script created
  - [ ] Reads embeddings from Neon Postgres
  - [ ] Creates Qdrant collection (if not exists)
  - [ ] Inserts embeddings as points with metadata
  - [ ] Metadata includes: chapter_id, chunk_index, chunk_text
  - [ ] Batch insert: 100 points per request
  - [ ] Synced_at timestamp updated in embeddings table
  - [ ] Idempotent: can be run multiple times
  - [ ] Script: `python scripts/sync_to_qdrant.py`
- **Effort**: 2 hours
- **Files to create**: `backend/scripts/sync_to_qdrant.py`
- **Tests**: `tests/integration/test_qdrant_sync.py`

**T2.1.4** - Verify Qdrant search quality
- **Status**: Ready
- **Owner**: Data Team
- **Story**: As a QA engineer, I verify that vector search returns relevant results
- **Acceptance**:
  - [ ] Test queries: "ROS 2 publishers", "Gazebo simulation", etc.
  - [ ] For each query: retrieve top-5 results
  - [ ] Manually verify: top-3 results are relevant (≥0.8 relevance score)
  - [ ] Document search quality: 10/10 queries returned relevant results
  - [ ] No false positives (retrieving unrelated chapters)
  - [ ] Response time per query < 100ms
- **Effort**: 2 hours
- **Files**: Manual QA checklist, test queries
- **Tests**: `tests/integration/test_qdrant_search_quality.py`

**T2.1.5** - Create embeddings update pipeline
- **Status**: Ready
- **Owner**: Data Team
- **Story**: As a content author, when I update a chapter, embeddings are regenerated
- **Acceptance**:
  - [ ] Monitor chapters table for updated_at changes
  - [ ] On chapter update: regenerate embeddings (delete old, create new)
  - [ ] Sync updated embeddings to Qdrant
  - [ ] Update synced_at timestamp
  - [ ] Pipeline runnable: `python scripts/update_chapter_embeddings.py <chapter_id>`
  - [ ] Or: via API endpoint POST /api/admin/chapters/{id}/sync-embeddings
  - [ ] Idempotent
- **Effort**: 2 hours
- **Files**: `backend/scripts/update_chapter_embeddings.py`
- **Tests**: `tests/integration/test_embedding_update.py`

**T2.1.6** - Batch embedding generation for all chapters
- **Status**: Blocked (waiting for content)
- **Owner**: Data Team
- **Story**: As a content team, once chapters are written, embeddings are generated at scale
- **Acceptance**:
  - [ ] Batch script processes all chapters in parallel
  - [ ] Rate-limited to avoid OpenAI quota
  - [ ] Progress reporting: X/Y chapters processed
  - [ ] Error handling: skip failed chapters, log errors
  - [ ] Runnable: `python scripts/batch_embeddings.py --all`
  - [ ] Cost estimation: ~$0.02 per 1M tokens (for 20-30 chapters)
- **Effort**: 2 hours (after content ready)
- **Dependencies**: T2.1.2, Content authors write chapters
- **Files**: `backend/scripts/batch_embeddings.py`

**T2.1.7** - Test data setup: seed embeddings
- **Status**: Ready
- **Owner**: Data Team
- **Story**: As a developer, I can run tests without hitting OpenAI API
- **Acceptance**:
  - [ ] Seed script includes 100 sample embeddings
  - [ ] 10 chapters × 10 chunks each
  - [ ] Embeddings pre-generated and stored
  - [ ] Qdrant collection pre-populated via migration
  - [ ] Tests use seeded data (no API calls)
  - [ ] Script: `python scripts/seed_embeddings.py`
- **Effort**: 1 hour
- **Files**: Extend `backend/scripts/seed_data.py`
- **Tests**: `tests/integration/test_embedding_seed.py`

**T2.1.8** - Documentation: embedding strategy & cost analysis
- **Status**: Ready
- **Owner**: Data Team
- **Story**: As a team, we understand embedding costs and refresh strategy
- **Acceptance**:
  - [ ] Document created: `backend/EMBEDDINGS.md`
  - [ ] Covers: chunking strategy, model choice, cost per chapter
  - [ ] Refresh strategy: when/how often to regenerate
  - [ ] Qdrant storage requirements (1536 dims × 100 embeddings = ~600KB)
  - [ ] Scaling plan: 100 chapters → 1000 chapters
- **Effort**: 1 hour
- **Files to create**: `backend/EMBEDDINGS.md`

### Group 3: Frontend & UI Components (10 tasks)

#### 3.1 Docusaurus Setup & Content Structure (6 tasks)

**T3.1.1** - Initialize Docusaurus v3 project
- **Status**: Ready
- **Owner**: Docusaurus Content Agent
- **Story**: As a frontend developer, I have a Docusaurus site scaffold
- **Acceptance**:
  - [ ] Docusaurus v3 initialized: `docusaurus.config.js`
  - [ ] Sidebar configuration: `sidebars.js`
  - [ ] Docs folder structure created (01-intro through 06-capstone)
  - [ ] Static assets folder setup
  - [ ] README with build/run instructions
  - [ ] Builds without errors: `npm run build`
  - [ ] Starts dev server: `npm start`
- **Effort**: 1 hour
- **Files to create**: `frontend/docusaurus.config.js`, `frontend/sidebars.js`
- **Tests**: `npm run build` succeeds, `npm run lint` passes

**T3.1.2** - Create module structure (4 modules, 6 chapters)
- **Status**: Ready
- **Owner**: Docusaurus Content Agent
- **Story**: As a student, I see the full course structure (ROS 2, Digital Twin, Isaac, VLA)
- **Acceptance**:
  - [ ] docs/01-intro/ (Course intro, 1 chapter)
  - [ ] docs/02-ros2/ (ROS 2 Fundamentals, 5 chapters)
  - [ ] docs/03-gazebo/ (Gazebo & Simulation, 5 chapters - renamed from Digital Twin)
  - [ ] docs/04-isaac/ (NVIDIA Isaac, 4 chapters)
  - [ ] docs/05-vla/ (Vision-Language-Action, 4 chapters)
  - [ ] docs/06-capstone/ (Capstone Project, 2-3 chapters)
  - [ ] index.md at module roots
  - [ ] Sidebar auto-generates from structure
- **Effort**: 2 hours
- **Files to create**: 20+ markdown files (chapter stubs)
- **Tests**: Sidebar renders all modules correctly

**T3.1.3** - Create chapter templates with section structure
- **Status**: Ready
- **Owner**: Docusaurus Content Agent
- **Story**: As a content author, I have chapter templates for consistency
- **Acceptance**:
  - [ ] Template structure: Learning Objectives → Concepts → Examples → Code Samples → Exercises → Quiz → Advanced Topics
  - [ ] Section headers with consistent formatting
  - [ ] Code block syntax: ```python, ```ros2
  - [ ] Quiz section template with sample questions
  - [ ] Learning outcomes at start
  - [ ] References/further reading section
  - [ ] Apply to all 20 chapters
  - [ ] Content authors fill in for Phase 1: 2-3 chapters as examples
- **Effort**: 2 hours
- **Files**: Template in `frontend/docs/CHAPTER_TEMPLATE.md`, apply to chapters
- **Tests**: All chapters follow template structure

**T3.1.4** - Set up MDX support for interactive components
- **Status**: Ready
- **Owner**: Docusaurus Content Agent
- **Story**: As a content author, I can embed React components in markdown (future quizzes, visualizations)
- **Acceptance**:
  - [ ] Docusaurus MDX plugin configured
  - [ ] Test component created: `frontend/src/components/TestComponent.tsx`
  - [ ] Embedded in a chapter and renders correctly
  - [ ] Supports props from markdown frontmatter
  - [ ] No build errors
- **Effort**: 1.5 hours
- **Files**: `frontend/docusaurus.config.js` (update), test component
- **Tests**: MDX component renders in browser

**T3.1.5** - Configure theme & styling
- **Status**: Ready
- **Owner**: Docusaurus Content Agent
- **Story**: As a user, the site has a clean, accessible theme
- **Acceptance**:
  - [ ] Theme: Docusaurus classic theme (light/dark mode)
  - [ ] Color palette: Professional robotics theme (not default)
  - [ ] Typography: Clear, readable fonts
  - [ ] Responsive: Mobile, tablet, desktop layouts
  - [ ] Accessibility: WCAG AA baseline (alt text, contrast)
  - [ ] CSS customization: `src/css/custom.css`
  - [ ] Light/dark mode toggle working
- **Effort**: 2 hours
- **Files**: `frontend/docusaurus.config.js`, `src/css/custom.css`
- **Tests**: Visual regression test or screenshot comparison

**T3.1.6** - Set up navigation & sidebar
- **Status**: Ready
- **Owner**: Docusaurus Content Agent
- **Story**: As a student, I easily navigate between modules and chapters
- **Acceptance**:
  - [ ] Sidebar shows all 4 modules + chapters
  - [ ] Active chapter highlighted
  - [ ] Collapsible modules (optional)
  - [ ] Next/Previous chapter links
  - [ ] Search bar functional (Docusaurus algolia or local)
  - [ ] Mobile-friendly hamburger menu
  - [ ] Breadcrumb navigation
- **Effort**: 1 hour
- **Files**: `frontend/sidebars.js`, update docusaurus.config.js
- **Tests**: All navigation links work, sidebar loads correctly

#### 3.2 React Components & Chatbot Widget (4 tasks)

**T3.2.1** - Create ChatbotWidget React component
- **Status**: Ready
- **Owner**: Docusaurus Content Agent
- **Story**: As a student, I see a chatbot widget in the right sidebar of every page
- **Acceptance**:
  - [ ] Component: `frontend/src/components/Chatbot/ChatbotWidget.tsx`
  - [ ] Floating chat bubble in bottom-right corner
  - [ ] Expandable chat window (300px width, 400px height)
  - [ ] Chat message list (scrollable)
  - [ ] Input field with send button
  - [ ] Loading indicator while awaiting response
  - [ ] Keyboard shortcut: Cmd+K to focus (optional)
  - [ ] Remembers expand/collapse state (localStorage)
- **Effort**: 3 hours
- **Files to create**: `frontend/src/components/Chatbot/ChatbotWidget.tsx`, `ChatMessage.tsx`, `InputBox.tsx`, `styles.css`
- **Tests**: `tests/components/Chatbot.test.tsx` with 5+ test cases

**T3.2.2** - Integrate ChatbotWidget into Docusaurus layout
- **Status**: Ready
- **Owner**: Docusaurus Content Agent
- **Story**: As a student, the chatbot appears on every page automatically
- **Acceptance**:
  - [ ] Widget wrapped in context provider (AuthContext, ChatContext)
  - [ ] Embedded in root layout via Docusaurus theme
  - [ ] Appears on all doc pages
  - [ ] Doesn't interfere with existing UI
  - [ ] Mobile-friendly positioning
  - [ ] No console errors
- **Effort**: 1.5 hours
- **Files**: `frontend/src/theme/DocLayout.tsx` (create wrapper)
- **Tests**: Widget renders on multiple page types

**T3.2.3** - Create chat API service (frontend)
- **Status**: Ready
- **Owner**: Docusaurus Content Agent
- **Story**: As a frontend developer, I have clean API calls to chat endpoints
- **Acceptance**:
  - [ ] Service: `frontend/src/services/chatService.ts`
  - [ ] Functions: submitQuery(query, mode, chapterId), getChatHistory(), submitFeedback()
  - [ ] Axios instance configured with baseURL
  - [ ] JWT token auto-injected in requests
  - [ ] Error handling & retry logic
  - [ ] Response parsing & validation
  - [ ] Type-safe (TypeScript)
- **Effort**: 1.5 hours
- **Files to create**: `frontend/src/services/chatService.ts`, `frontend/src/services/api.ts`
- **Tests**: `tests/services/chatService.test.ts` with mocked HTTP

**T3.2.4** - Create auth flow UI (sign-up, login, profile)
- **Status**: Ready
- **Owner**: Docusaurus Content Agent
- **Story**: As a student, I can sign up, log in, and manage my profile
- **Acceptance**:
  - [ ] Components: `LoginForm.tsx`, `SignupForm.tsx`, `ProfilePage.tsx`
  - [ ] Sign-up: email, password, name fields + validation
  - [ ] Login: email, password fields
  - [ ] Forgot password: email input, recovery link
  - [ ] Profile page: name, bio, organization, language, theme toggles
  - [ ] Error messages displayed clearly
  - [ ] Success redirects or confirmations
  - [ ] Form validation before submission
  - [ ] Mobile responsive
- **Effort**: 3 hours
- **Files to create**: `frontend/src/components/Auth/`, `frontend/src/pages/LoginPage.tsx`, etc.
- **Tests**: `tests/components/Auth.test.tsx` with form validation tests

### Group 4: Infrastructure & DevOps (4 tasks)

#### 4.1 Docker & Deployment (4 tasks)

**T4.1.1** - Create Dockerfile & docker-compose for local development
- **Status**: Ready
- **Owner**: DevOps Team
- **Story**: As a developer, I can run the entire stack with one command
- **Acceptance**:
  - [ ] Dockerfile for backend (Python 3.9, FastAPI)
  - [ ] docker-compose.yml with services: backend, frontend, postgres, qdrant
  - [ ] Postgres service with Neon-compatible setup (port 5432)
  - [ ] Qdrant service (port 6333)
  - [ ] Backend service (port 8000)
  - [ ] Frontend service (port 3000)
  - [ ] Volumes for development (code reload)
  - [ ] Environment variables passed via .env
  - [ ] `docker-compose up` starts all services
  - [ ] README with troubleshooting
- **Effort**: 2 hours
- **Files to create**: `Dockerfile`, `docker-compose.yml`
- **Tests**: `docker-compose up` succeeds, all containers healthy

**T4.1.2** - Set up GitHub Actions CI/CD pipeline
- **Status**: Ready
- **Owner**: DevOps Team
- **Story**: As a developer, my code is tested automatically on push
- **Acceptance**:
  - [ ] Workflow file: `.github/workflows/test.yml`
  - [ ] Triggers on push to main and PRs
  - [ ] Steps: checkout → install deps → lint → test → coverage
  - [ ] Backend tests: pytest with coverage report
  - [ ] Frontend tests: npm test
  - [ ] Lint: flake8 (backend), eslint (frontend)
  - [ ] Notify on failure (comment on PR)
  - [ ] Coverage badge in README (optional)
- **Effort**: 2 hours
- **Files to create**: `.github/workflows/test.yml`
- **Tests**: Trigger workflow, verify checks pass

**T4.1.3** - Database migration deployment strategy
- **Status**: Ready
- **Owner**: DevOps Team
- **Story**: As an operator, I can deploy schema changes safely
- **Acceptance**:
  - [ ] Migration script: `scripts/deploy.sh`
  - [ ] Steps: backup DB → apply migrations → health check
  - [ ] Rollback script if health check fails
  - [ ] Migrations are versioned and idempotent
  - [ ] Dry-run mode: show what will run without applying
  - [ ] Documentation in `DEPLOYMENT.md`
- **Effort**: 1.5 hours
- **Files to create**: `scripts/deploy.sh`, `DEPLOYMENT.md`
- **Tests**: Dry-run mode works, rollback tested

**T4.1.4** - Health check & monitoring setup
- **Status**: Ready
- **Owner**: DevOps Team
- **Story**: As an operator, I know when services are down
- **Acceptance**:
  - [ ] Health check endpoint: GET /api/health
  - [ ] Response includes status of each service (db, qdrant, openai, ros2)
  - [ ] Liveness probe: service is running
  - [ ] Readiness probe: service can handle requests
  - [ ] Kubernetes-compatible probe format (optional for Phase 1)
  - [ ] Response time < 100ms
  - [ ] Metrics: response_time_ms, services status
- **Effort**: 1 hour
- **Files**: Extend `backend/src/api/health.py`
- **Tests**: `tests/integration/test_health_check.py`

---

## Task Dependencies Map

```
T1.1.1 (FastAPI setup)
  └─ T1.1.2 (Pydantic models)
  └─ T1.1.3 (Config)
       └─ T1.1.4 (Logging)
           └─ T1.3.1-T1.3.8 (Auth)
           └─ T1.4.1-T1.4.8 (Chat)
               └─ T2.1.1-T2.1.8 (Embeddings)

T1.2.1 (SQLAlchemy setup)
  └─ T1.2.2 (Models)
       └─ T1.2.3 (Alembic)
           └─ T1.2.4 (Seed data)
               └─ T3.1.1-T3.1.6 (Frontend)
                   └─ T3.2.1-T3.2.4 (UI Components)

T4.1.1 (Docker setup)
T4.1.2 (CI/CD)
T4.1.3 (Deployment)
T4.1.4 (Health)
```

---

## Daily Standup Template

**Format**: Brief update on blockers and progress

```
## Standup: [DATE]

**Team**: RAG Chatbot Agent
**Status**: On track

**Completed Today**:
- T1.4.1: Qdrant integration (✅ Done)
- T1.4.2: OpenAI API integration (✅ Done, tested with mocks)

**In Progress**:
- T1.4.3: RAG pipeline orchestration (ETA: EOD)

**Blockers**:
- Waiting for OpenAI API key from ops team (needed for T1.4.7)

**Next**:
- Complete T1.4.3 and start T1.4.4
- Run integration tests for full chat flow
```

---

## Definition of Done (per task)

Each task is complete when:

1. **Code written** and committed to feature branch
2. **Tests written** with > 80% coverage (unit) or comprehensive (integration)
3. **Code reviewed** and approved (at least 1 reviewer)
4. **Tests passing**: `pytest` (backend), `npm test` (frontend)
5. **Documentation** updated: docstrings, README, API docs
6. **No console errors** or warnings
7. **Performance** meets targets (if applicable)
8. **Merged** to main via PR

---

## Success Metrics (Phase 1 Gate)

- [ ] 42/42 tasks completed
- [ ] 95%+ test coverage (critical paths)
- [ ] All 9 success criteria from plan.md met:
  - [ ] FastAPI server starts without errors
  - [ ] Neon Postgres connection test passes
  - [ ] Qdrant vector search returns results < 100ms
  - [ ] OpenAI API calls successful
  - [ ] Docusaurus builds successfully
  - [ ] better-auth sign-up/login flows work
  - [ ] 0 authentication errors on deployment
  - [ ] Chatbot widget renders in Docusaurus
  - [ ] API contract tests pass
- [ ] Phase 1 merged to main via PR
- [ ] Team confidence: ✅ Ready for Phase 2

---

**Phase 1 Status**: Ready to begin

**Estimated Duration**: 2-3 weeks with 3-5 developers in parallel

**Next**: Create feature branch `006-phase1-implementation` and start Task T1.1.1
