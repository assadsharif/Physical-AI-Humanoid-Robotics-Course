# CLI Environment Setup Status

## Current Progress

Your AI Robotics Learning Platform is being set up for CLI-based development and testing.

### ✓ Completed
- Python 3.12.3 environment verified
- npm 11.6.4 verified
- Node.js v24.11.1 verified
- Python virtual environment created at `backend/venv`
- `.env` configuration file ready (with SQLite support)
- `START_CLI.sh` startup script created
- Multiple requirements files prepared

### ⏳ In Progress (Running in Background)
- Python dependencies installation
  - `requirements-cli.txt`: Optimized for Python 3.12 (recommended)
  - `requirements-minimal.txt`: Bare minimum dependencies (fastest)
  - `requirements.txt`: Full feature set (may have compatibility issues)
- npm packages installation (for frontend)

---

## How to Use Once Setup Completes

### Step 1: Wait for Background Installations
The installation processes are running. You can check their progress:

```bash
cd /mnt/c/Users/ASSAD/Desktop/code/hackthon_one/backend

# Check if Python dependencies installed successfully
source venv/bin/activate
python -c "import fastapi; print('FastAPI installed ✓')"
```

### Step 2: Start the Backend Server

Once the backend dependencies are installed:

```bash
cd /mnt/c/Users/ASSAD/Desktop/code/hackthon_one/backend

# Activate virtual environment
source venv/bin/activate

# Start the FastAPI server
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will be available at: **http://localhost:8000**

### Step 3: Access API Documentation

Once the server is running, open in your browser:

**Swagger UI:** http://localhost:8000/docs
**ReDoc:** http://localhost:8000/redoc

### Step 4: Test the API

In Swagger UI (http://localhost:8000/docs), you can:

1. **Create a User (Sign Up)**
   - Find: `POST /api/auth/signup`
   - Click "Try it out"
   - Enter:
     ```json
     {
       "email": "test@example.com",
       "password": "TestPass123",
       "name": "Test User"
     }
     ```
   - Click "Execute"

2. **Test Chat Endpoint**
   - Find: `POST /api/chat/query`
   - Click "Try it out"
   - Enter:
     ```json
     {
       "query": "What is robotics?",
       "mode": "learn"
     }
     ```
   - Click "Execute"

### Step 5: Run Tests

Once dependencies are installed:

```bash
cd /mnt/c/Users/ASSAD/Desktop/code/hackthon_one/backend

# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

---

## Using START_CLI.sh (Interactive Menu)

Once all installations complete, you can use the automated setup script:

```bash
cd /mnt/c/Users/ASSAD/Desktop/code/hackthon_one
bash START_CLI.sh
```

This script provides an interactive menu:
- **1**: Start Backend (FastAPI) on port 8000
- **2**: Start Frontend (Docusaurus) on port 3000
- **3**: Run Backend Tests
- **4**: Start Both Backend and Frontend
- **5**: Show API Documentation
- **0**: Exit

---

## Project Structure

```
/mnt/c/Users/ASSAD/Desktop/code/hackthon_one/
├── backend/                    # Python FastAPI application
│   ├── src/
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── models/            # Database models
│   │   ├── routes/            # API endpoints
│   │   └── schemas/           # Pydantic schemas
│   ├── tests/                 # Test suite
│   ├── venv/                  # Python virtual environment
│   ├── requirements.txt       # Full dependencies
│   ├── requirements-cli.txt   # Optimized for CLI
│   └── requirements-minimal.txt # Minimal dependencies
├── web/                        # Docusaurus frontend
│   ├── src/                   # React components
│   ├── package.json           # npm dependencies
│   └── node_modules/          # npm packages (after install)
├── START_CLI.sh               # Interactive startup script
├── RUN_LOCALLY.md             # Docker setup guide
└── SETUP_STATUS.md            # This file
```

---

## Troubleshooting

### Installation Timeout

If pip install times out, the installation may still be running. You can:

1. **Wait longer** - Large package downloads can take 5-15 minutes
2. **Check process** - Use `ps aux | grep pip` to see if it's still running
3. **Retry install** - Stop the current process and run:
   ```bash
   source venv/bin/activate
   pip install -r requirements-minimal.txt --default-timeout=1000
   ```

### Import Errors

If you see import errors when running the backend:

```bash
# Reinstall minimal dependencies
source venv/bin/activate
pip install -r requirements-minimal.txt --force-reinstall

# Then add only what you need as errors appear
pip install openai qdrant-client python-jose passlib
```

### FastAPI Won't Start

If `uvicorn src.main:app` fails:

1. Verify FastAPI is installed:
   ```bash
   python -c "import fastapi; print(fastapi.__version__)"
   ```

2. Check if `src/main.py` exists:
   ```bash
   ls -la src/main.py
   ```

3. Try with verbose output:
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --log-level debug
   ```

### Port Already in Use

If port 8000 is already in use:

```bash
# Kill the process using port 8000
lsof -i :8000  # Find the PID
kill -9 <PID>

# Or use a different port
uvicorn src.main:app --host 0.0.0.0 --port 9000
```

---

## Key URLs Once Running

| Service | URL | Purpose |
|---------|-----|---------|
| FastAPI Backend | http://localhost:8000 | Main API |
| Swagger UI | http://localhost:8000/docs | API Interactive Docs |
| ReDoc | http://localhost:8000/redoc | API Documentation |
| Health Check | http://localhost:8000/health | Service Status |
| Frontend | http://localhost:3000 | Docusaurus Site (after npm install) |

---

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

---

## Next Steps

1. **Wait for installations to complete**
2. **Test basic endpoint** - `curl http://localhost:8000/health`
3. **Sign up a test user** - Use Swagger UI
4. **Test chat endpoint** - Ask a question
5. **Run test suite** - `pytest tests/ -v`

---

## Notes

- **Database**: Using SQLite (`robotics.db`) for CLI environment - no external database needed
- **Vector Store**: Qdrant client included but will work in mock mode without running Qdrant service
- **OpenAI**: Uses mock key for testing - replace with real key to enable LLM features
- **Authentication**: JWT tokens with 24-hour expiry
- **CORS**: Configured for `localhost:3000` and `localhost:8000`

---

**Your project is ready to test once installations complete! 🚀**

Check back in a few minutes for installation status.
