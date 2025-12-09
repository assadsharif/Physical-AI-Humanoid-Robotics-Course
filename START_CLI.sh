#!/bin/bash

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     AI Robotics Learning Platform - CLI Setup       ║${NC}"
echo -e "${BLUE}╚═════════════════════════════════════════════════════╝${NC}"
echo ""

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Check Python
echo -e "${YELLOW}1. Checking Python environment...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $(python3 --version | cut -d' ' -f2) found${NC}"

# Check npm
echo -e "${YELLOW}2. Checking Node.js environment...${NC}"
if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm $(npm --version) found${NC}"

# Setup Backend
echo ""
echo -e "${YELLOW}3. Setting up Backend...${NC}"
cd "$PROJECT_DIR/backend"

if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv || { echo -e "${RED}Failed to create venv${NC}"; exit 1; }
fi

source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

echo "   Installing dependencies..."
pip install -q -r requirements.txt 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠ Some dependencies failed (might be Python 3.12 compatibility)${NC}"
    echo "   Continuing with available packages..."
fi

# Setup Frontend
echo ""
echo -e "${YELLOW}4. Setting up Frontend...${NC}"
cd "$PROJECT_DIR/web"

if [ ! -d "node_modules" ]; then
    echo "   Installing npm packages..."
    npm install --quiet 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ npm packages installed${NC}"
    else
        echo -e "${YELLOW}⚠ npm install failed${NC}"
    fi
else
    echo -e "${GREEN}✓ node_modules already exist${NC}"
fi

# Create .env file for backend
echo ""
echo -e "${YELLOW}5. Setting up Environment Variables...${NC}"
cd "$PROJECT_DIR/backend"

if [ ! -f ".env" ]; then
    echo "   Creating .env file..."
    cat > .env << 'EOF'
# Application Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=info
SECRET_KEY=dev-secret-key-change-in-production

# Database (SQLite for CLI)
DATABASE_URL=sqlite:///./robotics.db

# Qdrant Vector Store (can be mocked)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=dev-api-key

# OpenAI (mock key for testing)
OPENAI_API_KEY=sk-mock-key-for-testing

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Features
ENABLE_ANALYTICS=true
ENABLE_CODE_SANDBOX=false
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Create startup menu
echo ""
echo -e "${BLUE}╔═════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Setup Complete! Choose what to run:          ║${NC}"
echo -e "${BLUE}╚═════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}1. Start Backend (FastAPI) on http://localhost:8000${NC}"
echo -e "${YELLOW}2. Start Frontend (Docusaurus) on http://localhost:3000${NC}"
echo -e "${YELLOW}3. Run Backend Tests${NC}"
echo -e "${YELLOW}4. Start Both Backend and Frontend${NC}"
echo -e "${YELLOW}5. Show API Documentation${NC}"
echo -e "${YELLOW}0. Exit${NC}"
echo ""
read -p "Enter choice (0-5): " choice

case $choice in
    1)
        echo -e "${GREEN}Starting Backend...${NC}"
        cd "$PROJECT_DIR/backend"
        source venv/bin/activate
        echo -e "${YELLOW}Backend will start on: http://localhost:8000${NC}"
        echo -e "${YELLOW}API Docs (Swagger): http://localhost:8000/docs${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
        echo ""
        uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
        ;;
    2)
        echo -e "${GREEN}Starting Frontend...${NC}"
        cd "$PROJECT_DIR/web"
        echo -e "${YELLOW}Frontend will start on: http://localhost:3000${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
        echo ""
        npm run dev
        ;;
    3)
        echo -e "${GREEN}Running Tests...${NC}"
        cd "$PROJECT_DIR/backend"
        source venv/bin/activate
        pytest tests/ -v --tb=short
        ;;
    4)
        echo -e "${GREEN}Starting Both Backend and Frontend...${NC}"
        echo -e "${YELLOW}Backend: http://localhost:8000${NC}"
        echo -e "${YELLOW}Frontend: http://localhost:3000${NC}"
        echo -e "${YELLOW}API Docs: http://localhost:8000/docs${NC}"
        echo ""
        echo -e "${YELLOW}Starting backend in background...${NC}"

        cd "$PROJECT_DIR/backend"
        source venv/bin/activate
        uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
        BACKEND_PID=$!
        echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"

        sleep 2

        echo -e "${YELLOW}Starting frontend...${NC}"
        cd "$PROJECT_DIR/web"
        npm run dev

        # Cleanup on exit
        kill $BACKEND_PID 2>/dev/null
        ;;
    5)
        echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}API Documentation${NC}"
        echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
        echo ""
        echo -e "Swagger UI:  ${YELLOW}http://localhost:8000/docs${NC}"
        echo -e "ReDoc:       ${YELLOW}http://localhost:8000/redoc${NC}"
        echo -e "OpenAPI JSON: ${YELLOW}http://localhost:8000/openapi.json${NC}"
        echo ""
        echo -e "${BLUE}Key Endpoints:${NC}"
        echo "  Authentication:"
        echo "    POST   /api/auth/signup      - Register new user"
        echo "    POST   /api/auth/login       - Login user"
        echo "    GET    /api/auth/me          - Get current user"
        echo "    PATCH  /api/auth/profile     - Update profile"
        echo "    POST   /api/auth/logout      - Logout"
        echo ""
        echo "  Chat:"
        echo "    POST   /api/chat/query       - Ask a question"
        echo "    POST   /api/chat/messages/{id}/rate - Rate response"
        echo ""
        echo "  Health:"
        echo "    GET    /health               - Service health"
        echo ""
        echo -e "${YELLOW}To use these endpoints, start the backend with option 1 or 4${NC}"
        ;;
    0)
        echo -e "${GREEN}Goodbye!${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac
