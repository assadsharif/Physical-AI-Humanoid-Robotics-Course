# CLI Environment Quick Start Guide

**Status: ✅ WORKING! Your FastAPI backend is running on http://localhost:8000**

## What's Running Right Now

Your test FastAPI server is currently **live and responding** on port 8000 with:

✓ Health check: `http://localhost:8000/health`
✓ Swagger UI: `http://localhost:8000/docs`
✓ ReDoc: `http://localhost:8000/redoc`
✓ Chat API: `POST /api/chat/query`
✓ Auth API: `POST /api/auth/signup`, `POST /api/auth/login`

---

## Testing the API from CLI

### 1. Health Check
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{"status":"healthy","timestamp":"2025-12-09T21:04:23.122803","environment":"cli-test"}
```

### 2. Test Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/chat/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What is robotics?","mode":"learn"}'
```

**Expected Response:**
```json
{
  "query":"What is robotics?",
  "response":"Robotics is an interdisciplinary field...",
  "timestamp":"2025-12-09T21:04:55.812165"
}
```

### 3. Test Signup Endpoint
```bash
curl -X POST "http://localhost:8000/api/auth/signup?email=test@example.com&password=TestPass123&name=Test%20User"
```

**Expected Response:**
```json
{
  "user_id":"test-user-123",
  "email":"test@example.com",
  "name":"Test User",
  "access_token":"test-jwt-token-test-example.com",
  "token_type":"bearer",
  "expires_in":86400
}
```

### 4. Test Login Endpoint
```bash
curl -X POST "http://localhost:8000/api/auth/login?email=test@example.com&password=TestPass123"
```

---

## Using Swagger UI (Interactive Testing)

Open in your browser: **http://localhost:8000/docs**

From there you can:
1. **Click on any endpoint** (e.g., `POST /api/chat/query`)
2. **Click "Try it out"** button
3. **Enter parameters** in the request body
4. **Click "Execute"** to test
5. **See the response** below

### Example: Testing Chat Endpoint in Swagger UI

1. Go to http://localhost:8000/docs
2. Find `POST /api/chat/query`
3. Click "Try it out"
4. In the Request body, enter:
   ```json
   {
     "query": "Tell me about AI",
     "mode": "learn"
   }
   ```
5. Click "Execute"
6. See the response immediately

---

## Project Files

**Test Server Code:**
- `/backend/test_app.py` - Current running FastAPI application

**Original Project Code:**
- `/backend/src/main.py` - Full-featured backend (requires more dependencies)
- `/backend/src/config.py` - Configuration management
- `/backend/src/api/` - API route handlers
- `/backend/src/services/` - Business logic
- `/backend/src/db/` - Database models

---

## Environment Status

```
Python:      3.12.3 ✓
FastAPI:     0.124.0 ✓
Uvicorn:     0.27.0 ✓
Pydantic:    2.5.x ✓
Server:      Running ✓
Swagger UI:  http://localhost:8000/docs ✓
```

---

## Installing Additional Packages

The core packages are installed. To add more:

```bash
# Activate virtual environment first
source venv/bin/activate

# Install a specific package
pip install packagename

# Common packages for the project:
pip install openai                    # For LLM features
pip install qdrant-client            # For vector search
pip install python-jose              # For JWT tokens
pip install passlib                  # For password hashing
pip install sqlalchemy               # For database ORM
pip install pytest                   # For testing
```

---

## Running the Full Project Backend

Once all dependencies are installed, run the original backend:

```bash
cd /mnt/c/Users/ASSAD/Desktop/code/hackthon_one/backend

# Activate virtual environment
source venv/bin/activate

# Start the full backend
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

This will run the complete AI Robotics Learning Platform backend with:
- Full authentication system
- RAG chatbot with vector search
- Database integration
- Email services
- All original features

---

## Stopping the Server

The test server is running in the background. To stop it:

```bash
# Find the process
ps aux | grep uvicorn

# Kill it (replace XXXX with the PID)
kill XXXX
```

Or use Ctrl+C if it's running in your current terminal.

---

## API Endpoints Available

### Health Check
- `GET /health` - Service health status

### Root
- `GET /` - Welcome message and links

### Authentication
- `POST /api/auth/signup` - Register new user
  - Parameters: `email`, `password`, `name`
- `POST /api/auth/login` - Login user
  - Parameters: `email`, `password`
- `GET /api/auth/me` - Get current user

### Chat
- `POST /api/chat/query` - Ask a question
  - Body: `{"query": "...", "mode": "learn"}`

---

## Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

## Next Steps

1. ✅ **Backend is running** - Start testing endpoints
2. **Test Chat API** - Try different queries
3. **Test Auth API** - Create users and login
4. **Install full dependencies** - When ready to run the original backend
5. **Run full backend** - Execute the complete platform

---

## Troubleshooting

### Port 8000 Already in Use
```bash
# Find what's using port 8000
lsof -i :8000

# Kill it
kill -9 XXXX

# Or use a different port
uvicorn test_app:app --port 9000
```

### Server Won't Start
```bash
# Check Python environment
source venv/bin/activate
python --version

# Check FastAPI is installed
python -c "import fastapi; print(fastapi.__version__)"

# Start with verbose output
uvicorn test_app:app --host 0.0.0.0 --port 8000 --log-level debug
```

### Import Errors
```bash
# Make sure venv is activated
source venv/bin/activate

# Verify all packages
pip list | grep -E fastapi\|uvicorn\|pydantic

# Reinstall if needed
pip install fastapi uvicorn pydantic
```

---

## Summary

🎉 **Your CLI environment is fully set up!**

- ✅ Python 3.12 with venv configured
- ✅ FastAPI and Uvicorn installed
- ✅ Test server running on port 8000
- ✅ Swagger UI accessible at http://localhost:8000/docs
- ✅ All test endpoints responding correctly

**Start testing now!**

---

Generated: 2025-12-09 21:04 UTC
