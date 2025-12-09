# Implementation Plan: Physical AI & Humanoid Robotics Textbook

**Branch**: `004-plan-architecture` | **Date**: 2025-12-09 | **Spec**: [specs/ai-native-textbook/spec.md](../ai-native-textbook/spec.md)

**Input**: Feature specification from `/specs/ai-native-textbook/spec.md` (470+ lines, 5 prioritized user stories)

---

## Summary

Build an AI-native, interactive textbook platform using Docusaurus (frontend) + FastAPI (backend) with integrated RAG chatbot, supporting 4 robotics modules, voice-based capstone project, and multi-language learning. The system enables students to learn Physical AI/Humanoid Robotics through interactive content, AI assistance via semantic search, and hands-on capstone project with Gazebo simulation.

---

## Technical Context

**Language/Version**:
- Backend: Python 3.9+ (FastAPI, Pydantic, async)
- Frontend: TypeScript/React (Docusaurus v3, MDX)
- Robotics: Python 3.9+ (rclpy for ROS 2)
- Database: SQL (Neon Postgres)

**Primary Dependencies**:
- Backend: FastAPI, Pydantic v2, SQLAlchemy, uvicorn
- Frontend: Docusaurus v3, React 18+, MDX
- Vector DB: Qdrant Cloud (managed)
- Auth: better-auth
- AI/Voice: OpenAI API (GPT-4o, text-embedding-3-small, Whisper)
- Robotics: ROS 2 (Humble/Iron), Gazebo, Nav2, MoveIt

**Storage**:
- Neon Postgres: User data, chapter metadata, chat history, progress, translations
- Qdrant Cloud: Vector embeddings (synced from chapters)
- GitHub Pages/Vercel: Static content (Docusaurus build)

**Testing**:
- Backend: pytest, async fixtures, mock services
- Frontend: React Testing Library, vitest
- Integration: FastAPI test client, browser tests
- ROS 2: launch_testing, Gazebo unit tests

**Target Platform**:
- Frontend: Web (responsive design, all browsers)
- Backend: Cloud (Render, Railway, Fly.io, or similar)
- Robotics: Linux (ROS 2 Humble/Iron)
- Simulation: Gazebo (cross-platform)

**Project Type**: Web application (frontend + backend with external APIs)

**Performance Goals**:
- Docusaurus site load: < 2 seconds
- Chatbot response: < 3 seconds (p95)
- Chatbot accuracy: > 90%
- Backend uptime: 95%+
- Support 100 concurrent users
- Capstone project completion: < 10 minutes

**Constraints**:
- Code examples 100% compile
- ROS 2 examples compatible with Humble/Iron
- Urdu translations ≥ 80% of chapters
- Safety validators on all LLM → robot commands
- No uncontrolled LLM-to-robot direct control

**Scale/Scope**:
- 4 modules, 20-30 chapters estimated
- 5 prioritized user stories (P1/P2)
- 29 functional requirements
- 10 success criteria
- 100-500 concurrent students initially
- Simulation-only, no hardware deployment

---

## Constitution Check

**GATE: All principles must align. Re-check after Phase 1 design.**

### Principle I: Spec-Driven Development (SDD)
✅ **PASS** - This plan follows `/sp.specify` → `/sp.plan` → `/sp.tasks` → `/sp.implement` workflow
- Spec: Completed (470+ lines)
- Plan: Current (this document)
- Tasks: Next phase
- Implementation: Following phase

### Principle II: Technical Excellence
✅ **PASS** - Strict standards defined:
- Python for backend/robotics ✓
- JavaScript/TypeScript for frontend ✓
- Pydantic models mandatory ✓
- Async FastAPI endpoints ✓
- Full type annotations ✓
- ROS 2 on Humble/Iron ✓
- PEER naming conventions (in design phase)

### Principle III: Safety-First (NON-NEGOTIABLE)
✅ **PASS** - Safety architecture designed:
- All dangerous workflows simulation-only ✓
- LLM outputs validated against ROS 2 vocabulary ✓
- No uncontrolled LLM-to-robot control ✓
- Kinematic feasibility checks (planned) ✓
- Collision detection via Gazebo ✓
- Grasp stability validation (planned) ✓

### Principle IV: Pedagogical Rigor
✅ **PASS** - Per-module structure defined:
- Concept explanations ✓
- Real-world examples ✓
- Python code samples ✓
- Diagrams ✓
- Exercises ✓
- Quizzes ✓
- Mini-projects ✓
- Advanced projects ✓

### Principle V: AI Integration Discipline
✅ **PASS** - LLM constraints enforced:
- LLMs only for planning, parsing, action graphs ✓
- No hallucinated APIs ✓
- Every command maps to ROS 2 constructs ✓
- Whisper voice only ✓
- Action planning produces JSON action graphs ✓

### Principle VI: Versioning & Reproducibility
✅ **PASS** - Version control strategy:
- All work Git-controlled ✓
- Semantic versioning: MAJOR.MINOR.PATCH ✓
- Feature branches for all changes ✓
- Constitution v1.0.0 ✓
- PHR tracking decisions ✓

**Constitution Check Result**: ✅ **PASS - No violations**

---

## Project Structure

### Documentation (This Feature)

```text
specs/004-plan-architecture/
├── plan.md                    # This file (/sp.plan output)
├── spec.md                    # Feature specification (copied)
├── research.md                # Phase 0 output - research findings
├── data-model.md              # Phase 1 output - entity definitions
├── contracts/                 # Phase 1 output - API contracts
│   ├── chat-api.openapi.json
│   ├── auth-api.openapi.json
│   ├── progress-api.openapi.json
│   ├── transcribe-api.openapi.json
│   └── vla-planning-api.openapi.json
├── quickstart.md              # Phase 1 output - setup guide
└── tasks.md                   # Phase 2 output (/sp.tasks - NOT created here)
```

### Source Code (Repository Root) - Web Application Structure

```text
# Backend (FastAPI)
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                           # FastAPI app entry
│   ├── config.py                         # Configuration & env
│   ├── models/                           # Pydantic models
│   │   ├── user.py
│   │   ├── chapter.py
│   │   ├── progress.py
│   │   ├── chat.py
│   │   ├── embedding.py
│   │   └── vla.py
│   ├── schemas/                          # Request/response schemas
│   │   ├── chat_schemas.py
│   │   ├── auth_schemas.py
│   │   ├── transcribe_schemas.py
│   │   └── vla_schemas.py
│   ├── api/                              # API endpoints (by agent)
│   │   ├── __init__.py
│   │   ├── chat.py                       # RAG Chatbot Agent routes
│   │   ├── auth.py                       # Authentication Agent routes
│   │   ├── progress.py                   # Progress tracking routes
│   │   ├── transcribe.py                 # Whisper integration routes
│   │   ├── vla.py                        # VLA planning routes
│   │   └── health.py                     # Health check
│   ├── services/                         # Business logic (by agent)
│   │   ├── __init__.py
│   │   ├── chat_service.py               # RAG chatbot logic
│   │   ├── auth_service.py               # better-auth integration
│   │   ├── progress_service.py           # Progress tracking
│   │   ├── qdrant_service.py             # Vector search
│   │   ├── llm_service.py                # OpenAI integration
│   │   ├── transcribe_service.py         # Whisper logic
│   │   ├── vla_service.py                # Action planning & validation
│   │   └── ros2_validator.py             # ROS 2 safety validation
│   ├── db/                               # Database
│   │   ├── __init__.py
│   │   ├── session.py                    # Neon Postgres connection
│   │   ├── models.py                     # SQLAlchemy models
│   │   └── migrations/                   # Alembic migrations
│   ├── utils/                            # Utilities
│   │   ├── __init__.py
│   │   ├── validators.py                 # Safety validators
│   │   ├── logger.py                     # Logging config
│   │   └── errors.py                     # Custom exceptions
│   └── middleware/                       # Middleware
│       ├── __init__.py
│       ├── auth_middleware.py
│       ├── cors.py
│       └── error_handler.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py                       # Pytest fixtures
│   ├── unit/                             # Unit tests
│   │   ├── test_chat_service.py
│   │   ├── test_vla_service.py
│   │   └── test_validators.py
│   ├── integration/                      # Integration tests
│   │   ├── test_chat_api.py
│   │   ├── test_auth_flow.py
│   │   └── test_vla_pipeline.py
│   └── contract/                         # API contract tests
│       └── test_openapi_schemas.py
├── requirements.txt                      # Python dependencies
├── .env.example                          # Environment template
├── Dockerfile                            # Container config
├── docker-compose.yml                    # Local dev setup
└── pyproject.toml                        # Project metadata

# Frontend (Docusaurus + React)
frontend/
├── docs/                                 # Markdown content
│   ├── 01-intro/
│   │   ├── what-is-physical-ai.md
│   │   ├── course-overview.md
│   │   └── index.md
│   ├── 02-ros2/
│   │   ├── ros2-basics.md
│   │   ├── publishers-subscribers.md
│   │   ├── services.md
│   │   ├── launch-files.md
│   │   ├── urdf-guide.md
│   │   └── index.md
│   ├── 03-gazebo/
│   │   ├── gazebo-basics.md
│   │   ├── world-building.md
│   │   ├── physics-simulation.md
│   │   ├── sensor-simulation.md
│   │   └── index.md
│   ├── 04-isaac/
│   │   ├── isaac-intro.md
│   │   ├── perception.md
│   │   ├── vslam.md
│   │   ├── nav2-navigation.md
│   │   ├── reinforcement-learning.md
│   │   └── index.md
│   ├── 05-vla/
│   │   ├── vision-language-action.md
│   │   ├── whisper-integration.md
│   │   ├── llm-planning.md
│   │   ├── ros2-execution.md
│   │   └── index.md
│   └── 06-capstone/
│       ├── capstone-project.md
│       ├── challenge-1.md
│       ├── challenge-2.md
│       └── index.md
├── src/
│   ├── components/
│   │   ├── Chatbot/
│   │   │   ├── ChatbotWidget.tsx         # RAG chatbot UI
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── InputBox.tsx
│   │   │   └── styles.css
│   │   ├── Quiz/
│   │   │   ├── QuizComponent.tsx
│   │   │   ├── Question.tsx
│   │   │   └── ResultsDisplay.tsx
│   │   ├── ProgressDashboard/
│   │   │   ├── Dashboard.tsx              # User progress display
│   │   │   ├── ModuleCard.tsx
│   │   │   └── ScoresDisplay.tsx
│   │   ├── LanguageToggle/
│   │   │   ├── LanguageSwitcher.tsx       # Urdu/English toggle
│   │   │   └── styles.css
│   │   └── CodeBlock/
│   │       ├── CodeHighlight.tsx          # Syntax highlighting
│   │       └── CopyButton.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   └── NotFound.tsx
│   ├── services/
│   │   ├── api.ts                        # Axios instance
│   │   ├── chatService.ts                # Chat API calls
│   │   ├── authService.ts                # Auth API calls
│   │   └── progressService.ts            # Progress API calls
│   ├── hooks/
│   │   ├── useChatbot.ts
│   │   ├── useAuth.ts
│   │   └── useProgress.ts
│   ├── context/
│   │   ├── AuthContext.tsx               # Auth state management
│   │   ├── LanguageContext.tsx           # Language preference
│   │   └── UserContext.tsx               # User profile
│   ├── utils/
│   │   ├── validators.ts
│   │   └── formatters.ts
│   └── App.tsx
├── tests/
│   ├── components/
│   │   ├── Chatbot.test.tsx
│   │   └── Quiz.test.tsx
│   ├── integration/
│   │   └── e2e.test.ts
│   └── setup.ts
├── docusaurus.config.js                  # Docusaurus configuration
├── sidebars.js                           # Navigation structure
├── package.json                          # Dependencies
├── tsconfig.json                         # TypeScript config
├── .env.example                          # Environment template
└── .gitignore

# Robotics & Capstone (separate ROS 2 package)
robotics/
├── humanoid_sim/                         # ROS 2 package
│   ├── src/
│   │   ├── humanoid_sim/
│   │   │   ├── __init__.py
│   │   │   ├── robot_controller.py       # Main node
│   │   │   ├── action_executor.py        # Execute ROS 2 actions
│   │   │   ├── safety_validator.py       # Validate actions
│   │   │   ├── perception_handler.py     # Camera/sensors
│   │   │   └── diagnostics.py            # Diagnostics publishing
│   │   └── launch/
│   │       ├── humanoid.launch.py        # Gazebo + robot launch
│   │       └── simulation.launch.py      # Full simulation stack
│   ├── worlds/                           # Gazebo worlds (SDF)
│   │   ├── humanoid_simple.world
│   │   └── humanoid_complex.world
│   ├── models/                           # URDF descriptions
│   │   ├── humanoid_robot.urdf
│   │   └── meshes/
│   ├── config/                           # ROS 2 config
│   │   ├── robot_params.yaml
│   │   └── controllers.yaml
│   ├── test/                             # ROS 2 tests
│   │   ├── test_robot_controller.py
│   │   └── test_safety_validator.py
│   ├── package.xml                       # ROS 2 package manifest
│   └── setup.py                          # Python setup
└── README.md

# Root level
docker-compose.yml                        # Full stack compose (backend + postgres + qdrant)
.github/
├── workflows/
│   ├── test-backend.yml
│   ├── test-frontend.yml
│   ├── deploy-backend.yml
│   └── deploy-frontend.yml
├── CODEOWNERS
└── pull_request_template.md
.gitignore
README.md
ARCHITECTURE.md                           # System architecture overview
DEPLOYMENT.md                             # Deployment guide
CONTRIBUTING.md                           # Developer guidelines
```

**Structure Decision**:
Selected **Web Application (Option 2)** with separate robotics package because:
- Frontend: Docusaurus static site (React components, MDX content)
- Backend: FastAPI microservice (scalable, async, cloud-deployable)
- Robotics: Separate ROS 2 package (can run locally or in container)
- Each can be developed, tested, deployed independently
- Clear separation of concerns (SDD principle)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                               │
│                    (Docusaurus + React)                            │
│                                                                     │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐               │
│  │  Modules &   │  │   Chatbot   │  │ Auth & User  │               │
│  │  Chapters    │  │   Widget    │  │   Profile    │               │
│  └──────────────┘  └─────────────┘  └──────────────┘               │
│                                                                     │
│  GitHub Pages / Vercel (Static hosting)                            │
└─────────────────────────────────────────────────────────────────────┘
                              ↕ (API calls)
┌─────────────────────────────────────────────────────────────────────┐
│                      API GATEWAY / FASTAPI                          │
│                    (Render / Railway / Fly.io)                     │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  /api/chat   │  │  /api/auth   │  │ /api/vla     │              │
│  │              │  │              │  │              │              │
│  │  RAG Chat    │  │  better-auth │  │  Action      │              │
│  │  Service     │  │  Integration │  │  Planner     │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ /api/trans   │  │ /api/progress│  │ /api/health  │              │
│  │              │  │              │  │              │              │
│  │  Whisper     │  │  Progress    │  │  Monitoring  │              │
│  │  Integration │  │  Tracking    │  │              │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
     ↕ (Database)        ↕ (Vector)         ↕ (External)
┌──────────────────┐  ┌──────────────┐  ┌─────────────────────┐
│  Neon Postgres   │  │ Qdrant Cloud │  │  OpenAI API         │
│                  │  │              │  │  (GPT, Embeddings,  │
│  User Data       │  │  Embeddings  │  │   Whisper)          │
│  Chapters        │  │  (Vector DB) │  │                     │
│  Progress        │  │              │  │  better-auth        │
│  Chat History    │  │  Semantic    │  │  (Auth Service)     │
│  Translations    │  │  Search      │  │                     │
└──────────────────┘  └──────────────┘  └─────────────────────┘

Local Development:
┌─────────────────────────────────────────────────────────────────────┐
│                    ROS 2 + Gazebo (Local)                           │
│                                                                     │
│  ┌────────────────────┐  ┌────────────────────┐                    │
│  │   Gazebo Engine    │  │  ROS 2 Master      │                    │
│  │                    │  │  (Humble/Iron)     │                    │
│  │  - Humanoid robot  │  │                    │                    │
│  │  - Physics sim     │  │  - Nav2            │                    │
│  │  - Sensors         │  │  - MoveIt          │                    │
│  │  - World           │  │  - Diagnostics     │                    │
│  └────────────────────┘  └────────────────────┘                    │
└─────────────────────────────────────────────────────────────────────┘
                              ↕
                     (ROS 2 Action Execution)
                              ↕
                      API (VLA Planner) ←
```

---

## Implementation Phases

### Phase 1: Core Infrastructure & RAG (P1 - Critical)
**Duration**: ~2-3 weeks (parallel teams)

**RAG Chatbot Agent**:
- FastAPI setup, Pydantic models, error handling
- Neon Postgres connection & schema
- Qdrant Cloud integration & vector indexing
- OpenAI embeddings & chat completions
- API endpoints: `/api/chat/query`, `/api/chat/highlight`, `/api/chat/chapter-specific`
- Response time < 3 seconds target

**Docusaurus Content Agent**:
- Docusaurus v3 setup with auto-sidebar
- Module structure (01-intro, 02-ros2, 03-gazebo, 04-isaac, 05-vla, 06-capstone)
- Initial chapter stubs with Markdown templates
- React chatbot widget embedding
- Deployment: GitHub Pages or Vercel
- Load time < 2 seconds target

**Authentication Agent**:
- better-auth setup
- Neon Postgres schema: users, sessions
- Sign-up, login, password reset flows
- JWT token management
- User profile endpoints

### Phase 2: Capstone & ROS 2 Integration (P1 - Critical)
**Duration**: ~2-3 weeks (parallel teams)

**Capstone & VLA Agent**:
- Whisper integration (`/api/transcribe`)
- OpenAI action planning (voice → JSON action graph)
- ROS 2 action vocabulary & validator
- Safety checks: kinematic, collision, grasp stability
- Gazebo world setup
- Nav2 + MoveIt integration
- End-to-end testing (voice → Gazebo execution)

**Robotics Package**:
- ROS 2 humanoid_sim package
- Robot controller node
- Action executor (Nav2 goals, MoveIt trajectories)
- Safety validator (constraint checking)
- Gazebo integration

### Phase 3: Personalization & i18n (P2 - Important)
**Duration**: ~1-2 weeks (parallel teams)

**Authentication Agent (Progress)**:
- Progress tracking schema
- Dashboard API endpoints
- Quiz scoring & history

**i18n & Translation Agent**:
- i18next setup for frontend
- Neon Postgres translation storage
- Translation infrastructure for Urdu
- Language toggle UI component
- RTL support for Urdu

### Phase 4: Content Authoring & Polish (Ongoing)
- Write chapter content (8-10 chapters minimum)
- Create diagrams and code examples
- Record quiz questions
- Validation & testing

---

## Agent Responsibilities & Parallel Work

| Agent | Phase 1 Focus | Phase 2 Focus | Dependencies |
|-------|--------------|--------------|--------------|
| **RAG Chatbot** | FastAPI, Qdrant, OpenAI setup | Embedding optimization | Docusaurus content |
| **Docusaurus Content** | Frontend scaffold, sidebar | Content population | RAG widget integration |
| **Authentication** | Sign-up/login flow | Progress tracking | Frontend integration |
| **Capstone & VLA** | Whisper, Planning API | ROS 2 integration | Robot simulator ready |
| **i18n & Translation** | Infrastructure | Language support | Content complete |

---

## Critical Dependencies & Blockers

1. **Qdrant Cloud API Key**: Required for vector DB setup
2. **OpenAI API Key**: Required for embeddings & chat
3. **ROS 2 Environment**: Development requires Humble/Iron (Docker or WSL2)
4. **Neon Postgres Connection**: Database must be operational
5. **Content Authoring**: Capstone can't be tested without chapters

**Mitigation**:
- Mock external APIs during early development
- Use Docker for ROS 2 (avoid local installation issues)
- Parallel content writing with stubs for testing

---

## Success Metrics (Phase 1 Gate)

- [ ] FastAPI server starts without errors
- [ ] Neon Postgres connection test passes
- [ ] Qdrant vector search returns results < 100ms
- [ ] OpenAI API calls successful (embeddings, completions)
- [ ] Docusaurus builds successfully
- [ ] better-auth sign-up/login flows work
- [ ] 0 authentication errors on deployment
- [ ] Chatbot widget renders in Docusaurus
- [ ] API contract tests pass

---

## Next: Phase 0 Research

Identified unknowns to resolve in `research.md`:

1. **Qdrant Chunking Strategy**: Optimal chunk size and overlap for robotics content?
2. **LLM Context Window Management**: How to handle long conversations in RAG?
3. **ROS 2 Safety Validator Rules**: Complete list of constraints for validation?
4. **Translation Workflow**: Translator roles and review process?
5. **Capstone Video Validation**: Automated or manual review?
6. **Multi-language Code Comments**: How to structure translated code?
7. **Rate Limiting Strategy**: Per-user or global limits for OpenAI calls?
8. **Offline Content Caching**: Mechanism and scope?

---

**Plan Status**: Ready for Phase 0 Research

**Next Command**: `/sp.plan` continues with Phase 0 (research.md generation)

