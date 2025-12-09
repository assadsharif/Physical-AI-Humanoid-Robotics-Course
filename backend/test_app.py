#!/usr/bin/env python
"""
Minimal test FastAPI app to verify backend setup in CLI environment
Run with: uvicorn test_app:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(
    title="Robotics Learning Platform - Test Server",
    description="Minimal test server to verify CLI setup",
    version="1.0.0"
)

# Models
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    environment: str = "cli-test"

class QueryRequest(BaseModel):
    query: str
    mode: str = "learn"

class QueryResponse(BaseModel):
    query: str
    response: str
    timestamp: str

# Routes
@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint"""
    return {
        "message": "AI Robotics Learning Platform - CLI Test Server",
        "docs": "http://localhost:8000/docs",
        "redoc": "http://localhost:8000/redoc",
        "health": "http://localhost:8000/health"
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        environment="cli-test"
    )

@app.post("/api/chat/query", tags=["Chat"], response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    """
    Test chat query endpoint

    Example:
    ```json
    {
      "query": "What is robotics?",
      "mode": "learn"
    }
    ```
    """
    responses = {
        "What is robotics?": "Robotics is an interdisciplinary field that combines mechanical engineering, electrical engineering, and computer science to design, build, and control robots.",
        "Tell me about AI": "Artificial Intelligence (AI) involves machines that can learn from experience and perform tasks that typically require human intelligence.",
        "Default": f"You asked: {request.query}. This is a test response from the CLI test server."
    }

    response_text = responses.get(request.query, responses["Default"])

    return QueryResponse(
        query=request.query,
        response=response_text,
        timestamp=datetime.utcnow().isoformat()
    )

@app.post("/api/auth/signup", tags=["Auth"])
def signup(email: str, password: str, name: str):
    """Test signup endpoint"""
    return {
        "user_id": "test-user-123",
        "email": email,
        "name": name,
        "access_token": "test-jwt-token-" + email.replace("@", "-"),
        "token_type": "bearer",
        "expires_in": 86400
    }

@app.post("/api/auth/login", tags=["Auth"])
def login(email: str, password: str):
    """Test login endpoint"""
    return {
        "user_id": "test-user-123",
        "email": email,
        "access_token": "test-jwt-token-" + email.replace("@", "-"),
        "token_type": "bearer",
        "expires_in": 86400
    }

@app.get("/api/auth/me", tags=["Auth"])
def get_me():
    """Get current user (test)"""
    return {
        "user_id": "test-user-123",
        "email": "test@example.com",
        "name": "Test User"
    }

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting test FastAPI server...")
    print("📚 API Docs: http://localhost:8000/docs")
    print("📖 ReDoc: http://localhost:8000/redoc")
    print("❤️  Health: http://localhost:8000/health\n")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
