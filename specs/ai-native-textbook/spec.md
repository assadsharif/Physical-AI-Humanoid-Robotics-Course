# Feature Specification: AI-Native Interactive Textbook - Physical AI & Humanoid Robotics

**Feature Branch**: `001-ai-native-textbook`
**Created**: 2025-12-09
**Status**: Draft
**Input**: User description: Build an AI-native, interactive textbook titled "Physical AI & Humanoid Robotics" with Docusaurus, 4 modules, RAG chatbot, and user features.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Student Learns ROS 2 Fundamentals (Priority: P1)

A student opens the ROS 2 module, reads concept explanations with diagrams, views Python code examples using rclpy, and completes a hands-on exercise in a simulated ROS 2 environment. The student then uses the RAG chatbot to clarify a concept by highlighting text and asking "Explain this."

**Why this priority**: ROS 2 is foundational; without this, roboticists cannot progress. This is the MVP core.

**Independent Test**: Can be fully tested by: (1) Loading ROS 2 module on Docusaurus, (2) Reading chapter content, (3) Running chatbot highlight-to-answer on selected text. Delivers: Working module with RAG integration.

**Acceptance Scenarios**:

1. **Given** student is on ROS 2 chapter, **When** student highlights text and asks chatbot "Explain nodes," **Then** chatbot returns accurate explanation from ROS 2 content only
2. **Given** ROS 2 module page loads, **When** student scrolls, **Then** all diagrams, code examples, and exercises render correctly
3. **Given** student completes ROS 2 quiz, **When** student submits, **Then** quiz is scored and feedback is provided

---

### User Story 2 - Student Uses RAG Chatbot for Global Q&A (Priority: P1)

A student opens the chatbot sidebar and asks "What is a digital twin?" The chatbot searches across all 4 modules using vector search (Qdrant), retrieves relevant content, and provides a comprehensive answer with citations.

**Why this priority**: RAG chatbot is core differentiator (AI-native); without it, textbook is static. Essential for hackathon demo.

**Independent Test**: Can be fully tested by: (1) Opening chatbot interface, (2) Submitting global query, (3) Validating response accuracy and citations. Delivers: Working RAG backend + frontend integration.

**Acceptance Scenarios**:

1. **Given** student is on any page, **When** student opens chatbot and asks "Explain Vision-Language-Action," **Then** chatbot returns relevant content from VLA module with metadata
2. **Given** chatbot receives query, **When** Qdrant vector search finds multiple chapters, **Then** chatbot ranks results and provides best answer first
3. **Given** student asks out-of-scope question (e.g., "What's the weather?"), **When** chatbot processes query, **Then** chatbot responds "I can only answer questions about this course"

---

### User Story 3 - Student Authenticates and Tracks Progress (Priority: P2)

A student signs up using better-auth, logs in, and starts the course. As the student completes chapters and quizzes, progress is saved in Neon Postgres. On returning, the student sees personalized progress dashboard showing completed modules and recommendations.

**Why this priority**: Authentication enables personalization and analytics; important for engagement but can be MVP'd with basic auth.

**Independent Test**: Can be fully tested by: (1) Sign-up/login flow, (2) Progress persistence across sessions, (3) Dashboard rendering. Delivers: Authentication + persistence layer.

**Acceptance Scenarios**:

1. **Given** user is new, **When** user signs up with email, **Then** account is created and user is logged in
2. **Given** authenticated user completes a quiz, **When** user navigates away and returns, **Then** progress is persisted and visible on dashboard
3. **Given** user is logged in, **When** user views dashboard, **Then** personalized progress for each module is displayed

---

### User Story 4 - Student Reads Content in Urdu (Priority: P2)

A student navigates to chapter settings and selects "Urdu" translation. The chapter content (explanations, diagrams labels, code comments) is displayed in Urdu. The student can toggle back to English.

**Why this priority**: Expands accessibility; important for global audience but can be phased post-launch.

**Independent Test**: Can be fully tested by: (1) Language toggle button, (2) Content rendering in Urdu, (3) Toggle back to English. Delivers: Multi-language support infrastructure.

**Acceptance Scenarios**:

1. **Given** student is on a chapter, **When** student clicks language selector and chooses Urdu, **Then** content is displayed in Urdu
2. **Given** content is in Urdu, **When** student clicks English, **Then** content switches back to English
3. **Given** user has Urdu selected, **When** user returns to page, **Then** Urdu language preference is remembered

---

### User Story 5 - Student Completes Capstone Project (Priority: P1)

A student reaches the capstone module. The student receives a voice prompt: "Pick up the blue cube from the table." The student's system (running locally or simulated):
1. Processes voice input (Whisper)
2. Plans robot actions (LLM + action graph)
3. Executes ROS 2 commands (Nav2 for navigation, MoveIt for manipulation)
4. Simulated humanoid robot navigates, identifies object, grasps, and manipulates

The student submits video proof of execution. System validates against success criteria.

**Why this priority**: Capstone is showcase feature (90-second hackathon video); demonstrates full stack integration.

**Independent Test**: Can be fully tested by: (1) Voice input → action planning → ROS 2 execution in Gazebo, (2) Video validation, (3) Project submission. Delivers: Complete VLA + sim integration.

**Acceptance Scenarios**:

1. **Given** student starts capstone, **When** student provides voice command, **Then** Whisper correctly transcribes command
2. **Given** command is transcribed, **When** LLM planner processes it, **Then** executable action graph is generated for robot
3. **Given** action graph exists, **When** ROS 2 executes sequence in Gazebo, **Then** humanoid robot performs expected movements
4. **Given** robot completes task, **When** student submits video, **Then** system validates completion and awards capstone badge

---

### Edge Cases

- What happens if student is offline? → Cached content loads; chatbot queues offline and syncs on reconnect
- How does system handle concurrent chatbot requests? → Queue with max 3 concurrent per user; others get "Please wait"
- What if Qdrant is down? → Chatbot returns "Service unavailable; try again later"
- What if Whisper transcription fails? → User can retry or manually enter command text
- What if LLM planning times out (>5sec)? → Return timeout error; suggest simplifying command
- What if user deletes account? → Anonymize user data; retain aggregate analytics (GDPR compliance)

## Requirements *(mandatory)*

### Functional Requirements

**Docusaurus & Content**
- **FR-001**: System MUST display 4 modules (ROS 2, Digital Twin, NVIDIA Isaac, VLA) as top-level navigation in Docusaurus sidebar
- **FR-002**: System MUST render each module with chapters containing: concept explanation, real-world examples, Python code samples, diagrams, exercises, quizzes, mini-projects
- **FR-003**: System MUST support code syntax highlighting for Python and ROS 2 launch files
- **FR-004**: System MUST display diagrams (SVG/PNG) with alt-text for accessibility

**RAG Chatbot (Embedded in Docusaurus)**
- **FR-005**: System MUST embed chatbot UI in right sidebar of all pages
- **FR-006**: Chatbot MUST support 3 interaction modes:
  - **Global chat**: Ask questions about any module (Qdrant searches all content)
  - **Highlight-to-answer**: User highlights text, chatbot contextualizes answer
  - **Chapter-specific**: Chatbot answers only from current chapter (toggle option)
- **FR-007**: Chatbot MUST call FastAPI backend for all LLM completions; frontend is stateless chat UI only
- **FR-008**: Chatbot responses MUST include source citations (e.g., "Source: ROS 2 Chapter 2, Section 3")
- **FR-009**: Chatbot MUST handle concurrent user queries without blocking; max queue 100

**Authentication & User Management**
- **FR-010**: System MUST support sign-up with email using better-auth
- **FR-011**: System MUST store user profile (name, email, preferences) in Neon Postgres
- **FR-012**: System MUST support password reset via email link
- **FR-013**: System MUST support logout and session expiry (24 hours)

**Personalization & Progress**
- **FR-014**: System MUST track completed chapters, quizzes, exercises per user
- **FR-015**: System MUST display personalized dashboard showing module progress (e.g., "ROS 2: 70% complete")
- **FR-016**: System MUST persist user preferences (language, theme, chapter position) across sessions

**Multi-Language Support**
- **FR-017**: System MUST support English (default) and Urdu translations
- **FR-018**: System MUST store translations in Neon Postgres with versioning
- **FR-019**: System MUST allow content creators to flag chapters as "ready for translation"
- **FR-020**: Language preference MUST persist in user profile

**Capstone Project Integration**
- **FR-021**: System MUST provide capstone module with voice-based challenge
- **FR-022**: Capstone module MUST integrate Whisper for voice transcription
- **FR-023**: System MUST call LLM planning endpoint to generate action graphs from voice commands
- **FR-024**: System MUST provide example ROS 2 launch files for Gazebo humanoid simulation
- **FR-025**: System MUST accept video submission and validate capstone completion

**Deployment & Infrastructure**
- **FR-026**: System MUST deploy Docusaurus on GitHub Pages or Vercel
- **FR-027**: FastAPI backend MUST deploy on cloud (Render, Railway, Fly.io, or AWS)
- **FR-028**: System MUST use Neon Postgres for all user data
- **FR-029**: System MUST use Qdrant Cloud for vector embeddings

### Key Entities

- **User**: id, email, password_hash, name, language_preference (EN/UR), theme, created_at, last_login
- **Module**: id, slug (ros2, digital-twin, isaac, vla), title, description, order, published_at
- **Chapter**: id, module_id, slug, title, content_markdown, order, created_at, updated_at
- **ChapterProgress**: user_id, chapter_id, completed_at, quiz_score, exercises_completed
- **Embedding**: id, chapter_id, chunk_text, vector (Qdrant), embedding_model ("OpenAI text-embedding-3-small")
- **Translation**: id, chapter_id, language (EN/UR), translated_content, translator_id, verified_at
- **CapstoneSubmission**: id, user_id, voice_command, action_graph (JSON), video_url, status (pending/approved/rejected), submitted_at

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Docusaurus site loads with all 4 modules visible in < 2 seconds on 4G connection
- **SC-002**: RAG chatbot responds to queries in < 3 seconds (p95) with > 90% accuracy
- **SC-003**: Authentication (sign-up → login) completes in < 30 seconds
- **SC-004**: 100% of code examples compile and run on Python 3.9+
- **SC-005**: ROS 2 examples run without errors on ROS 2 Humble/Iron
- **SC-006**: Capstone project can be completed end-to-end in < 10 minutes
- **SC-007**: 95% uptime for FastAPI backend
- **SC-008**: Support for 100 concurrent users on chatbot
- **SC-009**: All chapters have Urdu translations within 2 weeks of English publication
- **SC-010**: 90% of students successfully complete at least one full module quiz

## Constraints & Non-Goals

### In Scope
- Docusaurus frontend (static site generation with React)
- FastAPI backend for RAG + LLM
- Qdrant vector search for content retrieval
- Neon Postgres for metadata + user data
- better-auth for authentication
- 4 modules + capstone (MVP content structure)
- English + Urdu translation infrastructure
- Whisper integration for voice (capstone)
- GitHub Pages / Vercel deployment

### Out of Scope
- Real humanoid robot deployment (simulation only)
- Advanced LLM fine-tuning (use OpenAI API only)
- Video hosting (use external platform like YouTube or Vimeo)
- Payment/billing system
- Advanced analytics (basic user engagement tracking only)
- Mobile app (responsive web only)
- Advanced accessibility features (WCAG AA baseline)

### Technical Constraints
- Code examples MUST use Python 3.9+ (backward compatible)
- ROS 2 examples MUST target Humble or Iron
- Gazebo used for simulation (not hardware deployment)
- LLM responses MUST be deterministic and reproducible (seed=0 in OpenAI API)
- Vector embeddings MUST use OpenAI text-embedding-3-small (for consistency)
- Authentication MUST use better-auth (not custom auth)
- Database MUST be Neon Postgres (not MySQL/SQLite)

## Open Questions & Clarifications Needed

- **Q1**: Should chatbot support follow-up context (e.g., multi-turn conversation)? Or stateless per query?
  - **Current assumption**: Stateless per query (simpler MVP)
  - **Suggest**: Confirm with user

- **Q2**: Capstone video submission: Should system validate video content (e.g., check for robot motion)? Or manual review only?
  - **Current assumption**: Manual review by instructor
  - **Suggest**: Clarify grading workflow

- **Q3**: Translation scope: Should translations include code comments and diagrams? Or only explanatory text?
  - **Current assumption**: All text including code comments; diagrams with Urdu labels
  - **Suggest**: Confirm budget for translation

- **Q4**: Offline mode: Should cached content update periodically? Or only on manual refresh?
  - **Current assumption**: Manual refresh only
  - **Suggest**: Clarify UX requirement

- **Q5**: LLM planning for capstone: Should action graphs be pre-defined templates? Or fully generated by LLM?
  - **Current assumption**: LLM generates from Whisper transcription, validated against ROS 2 action vocabulary
  - **Suggest**: Confirm safety validation approach

## Acceptance Checklist

- [ ] All 4 modules (ROS 2, Digital Twin, NVIDIA Isaac, VLA) deployed on Docusaurus
- [ ] RAG chatbot embedded and functional (global + highlight + chapter-specific modes)
- [ ] Authentication (sign-up/login/logout) working with better-auth
- [ ] User progress tracking and personalized dashboard functional
- [ ] Urdu translation support for at least 1 chapter
- [ ] Capstone project runnable end-to-end (voice → planning → ROS 2 execution in Gazebo)
- [ ] All code examples compile and run without errors
- [ ] Deployed on GitHub Pages/Vercel (frontend) and Render/Railway (backend)
- [ ] README with setup instructions and demo video link
- [ ] FastAPI backend deployed and responding < 3sec on all endpoints
- [ ] Neon Postgres and Qdrant Cloud instances running and accessible
- [ ] 90-second hackathon demo ready (recorded or live)

## Next Steps

1. **Plan Phase** (`/sp.plan`): Define architecture, data models, API contracts, VLA action graph schema
2. **Task Breakdown** (`/sp.tasks`): Generate sprint-ready tasks for Docusaurus, RAG, auth, capstone
3. **Implementation** (`/sp.implement`): Execute tasks in priority order (P1 first)
4. **ADR Suggestions**: Consider ADRs for:
   - RAG chatbot architecture (context window management, fallback strategies)
   - Capstone safety validation (LLM → ROS 2 action mapping)
   - Multi-language content versioning strategy
