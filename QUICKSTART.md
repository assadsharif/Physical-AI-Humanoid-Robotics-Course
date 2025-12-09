# Quick Start Guide

Get the robotics learning platform up and running in 5 minutes.

## Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Git

## Option 1: Docker (Recommended)

### 1. Start Services

```bash
cd /path/to/hackthon_one

# Development environment
docker-compose up -d

# Or production
docker-compose -f docker-compose.prod.yml up -d
```

### 2. Initialize Database

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Seed test data
docker-compose exec backend python scripts/seed_data.py
```

### 3. Access Application

```bash
# API: http://localhost:8000
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc

# Frontend: http://localhost:3000 (if running web separately)
# PostgreSQL: localhost:5432
# Qdrant: localhost:6333
```

### 4. Create Test User

```bash
# Via API
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "name": "Test User"
  }'
```

## Option 2: Local Development

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database (requires PostgreSQL running)
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/robotics_db"
python -m alembic upgrade head

# Run migrations
python scripts/seed_data.py

# Start server
uvicorn src.main:app --reload
```

### 2. Frontend Setup

```bash
cd web

# Install dependencies
npm install

# Start development server
npm run dev

# Or build for production
npm run build
```

### 3. Database Setup (Local PostgreSQL)

```bash
# Create database
createdb robotics_db

# Connect and initialize
psql robotics_db < /path/to/schema.sql

# Or use Docker for database only
docker run -p 5432:5432 \
  -e POSTGRES_PASSWORD=password \
  postgres:16-alpine
```

## Testing

### Run All Tests

```bash
cd backend
pytest tests/ -v
```

### Run Specific Test

```bash
pytest tests/test_auth.py::TestSignup::test_signup_success -v
```

### With Coverage

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Common Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f postgres
```

### Database Operations

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U robotics_user -d robotics_db

# Run migrations
docker-compose exec backend alembic upgrade head

# Rollback migration
docker-compose exec backend alembic downgrade -1
```

### API Testing

```bash
# Health check
curl http://localhost:8000/health

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Chat query
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."
curl -X POST http://localhost:8000/api/chat/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is robotics?","mode":"learn"}'
```

### Clean Up

```bash
# Stop services
docker-compose down

# Remove volumes (careful!)
docker-compose down -v

# Remove containers and images
docker-compose down --rmi all
```

## Troubleshooting

### Port Already in Use

```bash
# Find process on port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
docker-compose -f docker-compose.yml -p robotics_alt up -d
```

### Database Connection Failed

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Verify connection string
echo $DATABASE_URL
```

### Module Import Errors

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Or clear cache
pip cache purge
```

### Can't Connect to Docker Services

```bash
# Check network
docker network ls
docker network inspect robotics_network

# Restart services
docker-compose restart
```

## Environment Variables

### Development (.env.development)

```bash
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql+asyncpg://robotics_user:robotics_password@postgres:5432/robotics_db
QDRANT_URL=http://qdrant:6333
QDRANT_API_KEY=qdrant-api-key-dev
OPENAI_API_KEY=sk-test
SECRET_KEY=dev-secret-key
```

### Production (.env.production)

```bash
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql+asyncpg://robotics_user:${POSTGRES_PASSWORD}@postgres-prod:5432/robotics_db
QDRANT_URL=https://your-qdrant-instance.com:6333
QDRANT_API_KEY=${QDRANT_API_KEY}
OPENAI_API_KEY=${OPENAI_API_KEY}
SECRET_KEY=${SECRET_KEY}
```

## Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System design
- **[BACKEND.md](./backend/README.md)** - Backend documentation
- **[TESTING.md](./backend/TESTING.md)** - Testing guide
- **[DOCKER.md](./DOCKER.md)** - Docker guide
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Deployment guide
- **[CI-CD.md](./.github/CI-CD.md)** - CI/CD documentation

## Endpoints Cheat Sheet

### Auth
```
POST   /api/auth/signup           # Register
POST   /api/auth/login            # Login
GET    /api/auth/me               # Get user
PATCH  /api/auth/profile          # Update profile
POST   /api/auth/logout           # Logout
```

### Chat
```
POST   /api/chat/query            # Ask question
POST   /api/chat/messages/{id}/rate  # Rate answer
```

### Admin
```
GET    /health                    # Health check
GET    /docs                      # Swagger UI
GET    /redoc                     # ReDoc
```

## Getting Help

### Check Status
```bash
# Service status
docker-compose ps

# Resource usage
docker stats

# Container health
docker inspect --format='{{.State.Health.Status}}' container_name
```

### View Documentation
- API Docs: http://localhost:8000/docs
- Backend README: `backend/README.md`
- Tests: `backend/TESTING.md`

### Common Issues

**Q: Migrations not applied?**
```bash
docker-compose exec backend alembic upgrade head
```

**Q: Tests failing?**
```bash
docker-compose exec backend pytest tests/ -v --tb=short
```

**Q: Need to reset database?**
```bash
docker-compose down -v  # Remove volumes
docker-compose up -d    # Recreate from scratch
```

## Performance Tips

1. **Use Docker for all services** - Consistent environment
2. **Enable caching** - Speeds up builds significantly
3. **Use indexes** - Database queries are optimized
4. **Monitor logs** - Catch issues early
5. **Regular backups** - Protect your data

## Next Steps

1. Read [PHASE1-SUMMARY.md](./PHASE1-SUMMARY.md) for project overview
2. Check [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
3. Review [BACKEND.md](./backend/README.md) for backend details
4. Read [DEPLOYMENT.md](./DEPLOYMENT.md) to deploy to cloud

## Support

For issues:
1. Check existing documentation
2. Review logs: `docker-compose logs -f`
3. Run tests: `pytest tests/ -v`
4. Check GitHub issues

---

**Happy coding! 🚀**
