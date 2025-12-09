# How to Run Your Project Locally in Chrome

Follow these steps to run your AI-powered robotics learning platform on your local machine.

## Prerequisites

Make sure you have installed:
- Docker & Docker Compose
- Git
- (Node.js 18+ and Python 3.11+ are included in Docker)

## Step 1: Clone Your Repository

```bash
cd ~/Projects  # or your preferred directory
git clone https://github.com/assadsharif/Physical-AI-Humanoid-Robotics-Course.git
cd Physical-AI-Humanoid-Robotics-Course
```

## Step 2: Start the Project with Docker Compose

```bash
# Start all services (PostgreSQL, Qdrant, FastAPI backend)
docker-compose up -d

# Verify services are running
docker-compose ps
```

You should see:
```
NAME                COMMAND                  STATUS
robotics_backend    uvicorn src.main:app...  Up
robotics_postgres   postgres...              Up
robotics_qdrant     qdrant...                Up
```

## Step 3: Open in Chrome

**API Documentation (Swagger UI):**
```
http://localhost:8000/docs
```

**Alternative API Docs (ReDoc):**
```
http://localhost:8000/redoc
```

**Frontend (if running separately):**
```
http://localhost:3000
```

## Step 4: Test the API in Chrome

### 1. Create a User (Sign Up)

Open Chrome and go to: `http://localhost:8000/docs`

1. Click on the **POST /api/auth/signup** endpoint
2. Click "Try it out"
3. Enter the following JSON in the Request body:

```json
{
  "email": "test@example.com",
  "password": "TestPass123",
  "name": "Test User"
}
```

4. Click "Execute"
5. You should see a 201 Created response with a token

### 2. Copy the Token

From the response, copy the `access_token` value (it looks like: `eyJ0eXAiOiJKV1QiLCJhbGc...`)

### 3. Test Chat Endpoint

1. Scroll down to find **POST /api/chat/query** endpoint
2. Click "Try it out"
3. Click the lock icon next to the endpoint and paste your token
4. Enter the following JSON:

```json
{
  "query": "What is robotics?",
  "mode": "learn"
}
```

5. Click "Execute"
6. You should get a response with AI-generated content

## Step 5: View Logs

```bash
# View backend logs
docker-compose logs -f backend

# View database logs
docker-compose logs -f postgres

# View Qdrant logs
docker-compose logs -f qdrant
```

## Step 6: Stop the Project

```bash
docker-compose down
```

## Common Commands

```bash
# Restart services
docker-compose restart

# Rebuild images
docker-compose build

# Remove all volumes (careful - deletes data)
docker-compose down -v

# Run tests
docker-compose exec backend pytest tests/ -v

# Access database
docker-compose exec postgres psql -U robotics_user -d robotics_db

# View specific service logs
docker-compose logs backend -f --tail=100
```

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 8000
lsof -i :8000
kill -9 <PID>

# Or use different port
docker-compose -f docker-compose.yml -p myproject up -d
```

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Restart Docker
docker restart

# Clean up and restart
docker-compose down -v
docker-compose up -d
```

### Database Connection Error

```bash
# Wait for PostgreSQL to be ready
docker-compose exec backend sleep 10

# Run migrations
docker-compose exec backend alembic upgrade head
```

## API Endpoints Available

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user (requires auth)
- `PATCH /api/auth/profile` - Update profile (requires auth)
- `POST /api/auth/logout` - Logout (requires auth)

### Chat (RAG Chatbot)
- `POST /api/chat/query` - Ask a question (requires auth)
- `POST /api/chat/messages/{id}/rate` - Rate a response (requires auth)

### Health
- `GET /health` - Check service health

## Next Steps

1. ✅ Services running in Docker
2. ✅ API working in Chrome (http://localhost:8000/docs)
3. 📖 Read QUICKSTART.md for more options
4. 🚀 Deploy to production (see DEPLOYMENT.md)
5. 📈 Add Phase 1+ features

## Frontend (Optional)

If you want to run the Docusaurus frontend separately:

```bash
# Terminal 1: Keep backend running
docker-compose up

# Terminal 2: Start frontend
cd web
npm install
npm run dev
```

Then open: `http://localhost:3000`

## Need Help?

1. Check logs: `docker-compose logs -f`
2. Read QUICKSTART.md
3. Read DEPLOYMENT.md
4. Check GitHub issues

---

**Your project is ready to run! 🚀**

Start with: `docker-compose up -d`
Then visit: `http://localhost:8000/docs`
