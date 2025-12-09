# FastAPI Backend - Physical AI & Humanoid Robotics Textbook

RAG-powered learning platform with AI chatbot, vector search, and interactive course content.

## Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL (Neon) with SQLAlchemy 2.x async ORM
- **Vector Store**: Qdrant Cloud for semantic search
- **LLM**: OpenAI (GPT-4o for generation, text-embedding-3-small for embeddings)
- **Authentication**: better-auth + JWT
- **Testing**: pytest with async support
- **Deployment**: Docker + docker-compose

## Project Structure

```
backend/
├── src/
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Environment configuration
│   ├── api/
│   │   ├── health.py           # Health check endpoints
│   │   ├── auth.py             # Authentication endpoints (signup, login, etc.)
│   │   └── chat.py             # RAG chat endpoints
│   ├── services/
│   │   ├── auth_service.py     # Authentication logic
│   │   ├── chat_service.py     # RAG chatbot logic
│   │   └── embedding_service.py # Embedding generation
│   ├── db/
│   │   ├── session.py          # Database session management
│   │   ├── base.py             # Base model for SQLAlchemy
│   │   └── models.py           # All database models
│   ├── schemas/
│   │   ├── user.py             # Pydantic schemas for users
│   │   ├── chat.py             # Pydantic schemas for chat
│   │   └── common.py           # Common schemas
│   ├── middleware/
│   │   ├── error_handler.py    # Global error handling
│   │   └── request_logging.py  # Request/response logging
│   └── utils/
│       ├── logger.py           # Logging configuration
│       └── errors.py           # Custom exceptions
├── migrations/                 # Alembic migrations (generated)
├── tests/
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── conftest.py             # pytest configuration
├── scripts/
│   └── seed_data.py            # Database seeding
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional, but recommended)
- PostgreSQL (if not using Docker)
- Qdrant (if not using Docker)

### Setup with Docker (Recommended)

1. **Copy environment file**:
   ```bash
   cp backend/.env.example backend/.env
   # Edit .env with your API keys
   ```

2. **Start services**:
   ```bash
   docker-compose up -d
   ```

3. **Check health**:
   ```bash
   curl http://localhost:8000/api/health
   ```

4. **View API docs**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Setup Without Docker

1. **Create virtual environment**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings and API keys
   ```

4. **Set up database**:
   - Ensure PostgreSQL is running
   - Create database: `createdb robotics_db`
   - Run migrations: `alembic upgrade head`

5. **Seed test data** (optional):
   ```bash
   python scripts/seed_data.py
   ```

6. **Start server**:
   ```bash
   uvicorn src.main:app --reload
   ```

## Environment Variables

Create a `.env` file (copy from `.env.example`):

```env
# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/robotics_db

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-api-key
```

See `.env.example` for all available options.

## API Endpoints

### Health Check
- `GET /api/health` - Service health status
- `GET /api/health/ready` - Readiness probe
- `GET /api/health/live` - Liveness probe

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/password-reset` - Request password reset
- `GET /api/auth/me` - Get current user profile
- `PATCH /api/auth/profile` - Update user profile

### Chat (RAG)
- `POST /api/chat/query` - Ask a question
- `GET /api/chat/sessions/{session_id}` - Get conversation history (Phase 1+)
- `POST /api/chat/sessions` - Create new session (Phase 1+)
- `POST /api/chat/messages/{id}/rate` - Rate response (Phase 2)

See [API-CONTRACTS.md](../specs/004-plan-architecture/contracts/API-CONTRACTS.md) for full details.

## Database Models

Core entities:
- **User** - Student/educator account
- **UserProfile** - Extended profile information
- **Module** - Course modules (ROS 2, Digital Twin, etc.)
- **Chapter** - Chapter within a module
- **Embedding** - Vector embeddings for chapters
- **ChapterProgress** - Student progress tracking
- **ChatMessage** - Conversation history
- **Translation** - Multi-language support (i18n)

See [data-model.md](../specs/004-plan-architecture/data-model.md) for full schema.

## Testing

### Run all tests:
```bash
pytest
```

### Run specific test file:
```bash
pytest tests/unit/test_main.py -v
```

### Run with coverage:
```bash
pytest --cov=src tests/
```

### Run only integration tests:
```bash
pytest tests/integration/ -v
```

## Development

### Code Style
- **Formatter**: Black
- **Linter**: Flake8
- **Type Checking**: mypy

Format code:
```bash
black src/ tests/
```

Check types:
```bash
mypy src/
```

### Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

## Database Migrations

All schema changes go through Alembic. Never modify SQLAlchemy models without creating a migration.

1. Make model changes in `src/db/models.py`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Review the generated migration file
4. Apply: `alembic upgrade head`
5. Commit both model and migration changes

## Deployment

### Using Docker

```bash
docker build -t robotics-api:latest .
docker run -p 8000:8000 --env-file .env robotics-api:latest
```

### Using Docker Compose (Development)

```bash
docker-compose up -d
docker-compose logs -f backend
```

### To Production

1. Set `ENVIRONMENT=production` in `.env`
2. Update `SECRET_KEY`, `DATABASE_URL`, API keys
3. Use Gunicorn in production (included in requirements.txt)

```bash
gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker src.main:app
```

## Troubleshooting

### Database connection errors
- Check `DATABASE_URL` in `.env`
- Ensure PostgreSQL is running
- Verify network connectivity to database

### Qdrant connection errors
- Check `QDRANT_URL` and `QDRANT_API_KEY`
- Ensure Qdrant is running and accessible

### OpenAI API errors
- Verify `OPENAI_API_KEY` is set and valid
- Check API quota and billing

### Port already in use
- Change `PORT` in config or `.env`
- Or kill process: `lsof -ti:8000 | xargs kill -9`

## Phase 1 Task Status

- [x] T1.1.1 - FastAPI project structure
- [x] T1.1.2 - Pydantic models & schemas
- [x] T1.1.3 - Environment & secrets management
- [x] T1.1.4 - Logging & error handling
- [ ] T1.2.1 - SQLAlchemy ORM setup
- [ ] T1.2.2 - Database models
- [ ] T1.2.3 - Alembic migrations
- [ ] T1.2.4 - Seed data script
- [ ] T1.3.* - Authentication system
- [ ] T2.1.* - Chat service
- [ ] ... (other tasks)

## Contributing

1. Create a feature branch
2. Make changes following code style
3. Write tests for new functionality
4. Run full test suite
5. Create pull request

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/20/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
- [Qdrant Vector Store](https://qdrant.tech/documentation/)

## License

Part of the Physical AI & Humanoid Robotics Textbook project.
