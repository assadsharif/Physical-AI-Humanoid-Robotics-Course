# Phase 1 Quickstart: Local Development Setup

**Branch**: `005-phase1-design` | **Date**: 2025-12-09 | **Target**: Get full stack running in < 30 minutes

---

## Overview

This quickstart guide enables developers to set up the entire Physical AI & Humanoid Robotics Textbook system locally. By the end, you'll have:

- ✅ FastAPI backend running on `http://localhost:8000`
- ✅ Docusaurus frontend on `http://localhost:3000`
- ✅ PostgreSQL database with migrations applied
- ✅ Qdrant vector DB for RAG
- ✅ Sample data loaded
- ✅ All tests passing

**Prerequisites**:
- Python 3.9+ (use `python3 --version`)
- Node.js 18+ (use `node --version`)
- Docker & Docker Compose (optional but recommended)
- Git
- 8GB RAM minimum

---

## Option 1: Docker Compose (Recommended - 10 minutes)

### Step 1: Clone & Navigate

```bash
git clone https://github.com/assadsharif/Physical-AI-Humanoid-Robotics-Course.git
cd Physical-AI-Humanoid-Robotics-Course
```

### Step 2: Configure Environment

```bash
# Copy example env files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit backend/.env (fill in API keys if available, or use mock defaults)
# Required (or use mock for testing):
# - OPENAI_API_KEY=sk-...
# - QDRANT_API_KEY=...
# - DATABASE_URL=postgresql://postgres:postgres@db:5432/textbook_dev
# - JWT_SECRET=your-secret-key-here (generate: python -c "import secrets; print(secrets.token_urlsafe(32))")
```

### Step 3: Start Full Stack

```bash
# From repo root, start all services (backend, frontend, postgres, qdrant)
docker-compose up --build

# In new terminal, wait for services and run migrations
docker-compose exec backend alembic upgrade head

# Optional: Load sample data
docker-compose exec backend python -m scripts.seed_data
```

### Step 4: Verify

```bash
# Backend health check
curl http://localhost:8000/api/health

# Frontend
open http://localhost:3000  # or browser to localhost:3000

# OpenAPI docs
open http://localhost:8000/docs
```

**Done!** Skip to [Testing](#testing) section.

---

## Option 2: Manual Local Setup (20 minutes)

### Backend Setup

#### Step 1: Create Python Virtual Environment

```bash
cd backend

# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

#### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 3: Configure Environment

```bash
# Create .env from template
cp .env.example .env

# Edit .env with your configuration
# Required variables:
# - DATABASE_URL=postgresql://postgres:password@localhost:5432/textbook_dev
# - QDRANT_URL=http://localhost:6333
# - QDRANT_API_KEY=your-key (optional for local)
# - OPENAI_API_KEY=sk-... (required for chat features)
# - JWT_SECRET=generated-secret-key

# Generate JWT secret:
python -c "import secrets; print(secrets.token_urlsafe(32))" > jwt_secret.txt
# Then copy the output to .env JWT_SECRET value
```

#### Step 4: Database Setup

**Option A: Use Docker for PostgreSQL only**
```bash
docker run -d \
  --name textbook_postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=textbook_dev \
  -p 5432:5432 \
  postgres:15-alpine

# Wait 5 seconds for DB to start
sleep 5

# Run migrations
alembic upgrade head
```

**Option B: Local PostgreSQL**
```bash
# Install PostgreSQL locally (brew on Mac, apt on Linux, etc.)
# Create database
createdb textbook_dev

# Update DATABASE_URL in .env to: postgresql://username:password@localhost:5432/textbook_dev
# Apply migrations
alembic upgrade head
```

#### Step 5: Set Up Qdrant (Local)

```bash
# Option A: Docker
docker run -d \
  --name textbook_qdrant \
  -p 6333:6333 \
  qdrant/qdrant

# Option B: Use Qdrant Cloud
# Sign up at https://cloud.qdrant.io
# Create cluster, add URL + API key to .env QDRANT_URL and QDRANT_API_KEY
```

#### Step 6: Run Backend

```bash
# From backend/ directory with venv activated
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

Test it:
```bash
curl http://localhost:8000/api/health
# Should return: {"status": "healthy", ...}
```

---

### Frontend Setup

#### Step 1: Navigate & Install

```bash
cd frontend

# Install dependencies
npm install
```

#### Step 2: Configure Environment

```bash
# Create .env.local from template
cp .env.example .env.local

# Edit .env.local
# REACT_APP_API_URL=http://localhost:8000/api
# REACT_APP_ENV=development
```

#### Step 3: Start Development Server

```bash
npm run start

# Expected output:
# > Compiled successfully!
# Ready in 2.05s.
# http://localhost:3000
```

Open http://localhost:3000 in browser.

---

## Testing Everything Works

### Test 1: Health Check

```bash
# Backend health
curl http://localhost:8000/api/health

# Expected: {"status": "healthy", "services": {...}}
```

### Test 2: Database Connection

```bash
# From backend/ with venv activated
python -c "from src.db.session import get_async_session; print('DB connection OK')"

# Expected: DB connection OK
```

### Test 3: Create User (Auth)

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "name": "Test User"
  }'

# Expected response: {user_id, email, access_token, ...}
```

### Test 4: Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# Save the access_token for next requests
ACCESS_TOKEN="your-token-here"
```

### Test 5: Get User Profile

```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Expected: User profile with ID, email, name, preferences
```

### Test 6: Frontend Access

Open http://localhost:3000 in browser. You should see:
- Docusaurus sidebar with modules
- Chatbot widget (right side)
- Login/signup forms
- Dashboard skeleton

### Test 7: Run Backend Tests

```bash
cd backend

# Run pytest
pytest tests/ -v

# Expected: All tests pass
# tests/unit/test_auth_service.py::test_signup PASSED
# tests/integration/test_auth_api.py::test_login_flow PASSED
# ...
```

### Test 8: Run Frontend Tests

```bash
cd frontend

npm test -- --passWithNoTests

# Expected: All tests pass or skip gracefully
```

---

## Database Schema Verification

```bash
# Connect to local PostgreSQL
psql -U postgres -d textbook_dev -c "\dt"

# Expected tables:
# users
# user_profiles
# modules
# chapters
# embeddings
# chapter_progress
# chat_messages
# translations
# capstone_submissions
```

---

## API Documentation

Once backend is running, visit:

**OpenAPI (Swagger UI)**: http://localhost:8000/docs
- Interactive API explorer
- Try all endpoints
- See request/response schemas

**ReDoc**: http://localhost:8000/redoc
- Alternative API documentation

---

## Useful Development Commands

### Backend

```bash
cd backend
source venv/bin/activate

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Lint code
flake8 src/
black src/  # Format code
isort src/  # Sort imports

# Create new migration
alembic revision --autogenerate -m "Add new field to users"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Frontend

```bash
cd frontend

# Run tests
npm test

# Build for production
npm run build

# Lint & format
npm run lint
npm run format

# Check TypeScript errors
npm run type-check
```

### Docker

```bash
# Stop all services
docker-compose down

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Rebuild and restart
docker-compose down && docker-compose up --build

# Clean up volumes (WARNING: deletes data)
docker-compose down -v
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process (replace PID)
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows
```

### Database Connection Error

```bash
# Check PostgreSQL is running
docker ps | grep postgres  # or your local psql process

# Check connection string in .env
# Format: postgresql://user:password@host:port/database

# Test connection
psql -U postgres -h localhost -d textbook_dev -c "SELECT 1"
```

### Qdrant Connection Error

```bash
# Check Qdrant is running
curl http://localhost:6333/health

# If using cloud, verify URL and API key in .env
# Format: https://your-cluster-id.qdrant.io
```

### OpenAI API Error

```bash
# Verify API key is valid
echo $OPENAI_API_KEY  # Should not be empty

# Test API call
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Node_modules Issues

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Python Package Issues

```bash
cd backend
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Next Steps

1. **Start Coding**: Open `backend/src/api/` and `frontend/src/` to explore
2. **Read Data Model**: See `specs/004-plan-architecture/data-model.md`
3. **Review API Contracts**: See `specs/004-plan-architecture/contracts/API-CONTRACTS.md`
4. **Write Features**: Follow the feature branches workflow (create branch, commit, PR)
5. **Run Tests**: Before every commit, run `pytest` and `npm test`
6. **Check Status**: Run `/sp.tasks` to see sprint-ready breakdown of Phase 1 work

---

## Architecture Overview (Local Stack)

```
┌─────────────────┐
│  Frontend       │  http://localhost:3000
│  (Docusaurus)   │  npm run start
└────────┬────────┘
         │ API calls (http://localhost:8000/api)
┌────────▼────────┐
│  Backend        │  http://localhost:8000
│  (FastAPI)      │  uvicorn main.py
└────────┬────────┘
         │
    ┌────┼────┬────────┬──────────┐
    │    │    │        │          │
┌───▼──┐ │ ┌──▼───┐ ┌──▼───────┐│
│ Neon │ │ │Qdrant│ │ OpenAI   ││
│ PG   │ │ │Cloud │ │ API      ││
└──────┘ │ └──────┘ └──────────┘│
    ┌────┴────────────────────────┐
    │    ROS 2 + Gazebo (Optional)│  Local or Docker
    │    http://localhost:11311   │
    └─────────────────────────────┘
```

---

## Success Checklist

- [ ] Backend starts without errors
- [ ] Frontend loads at localhost:3000
- [ ] Can sign up new user via API
- [ ] Can log in and get JWT token
- [ ] Can fetch user profile
- [ ] Can view OpenAPI docs at /docs
- [ ] Database tables created and populated
- [ ] All backend tests pass
- [ ] All frontend tests pass
- [ ] Can make chat query (with API keys configured)
- [ ] Health check returns healthy status

---

**Status**: Phase 1 Quickstart Complete ✅

**Next**: Run `/sp.tasks` to generate sprint breakdown of all Phase 1 work items.
