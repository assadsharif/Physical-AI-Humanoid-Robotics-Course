# Skill: FastAPI Backend Development

**Description**: Building asynchronous Python web services using FastAPI, Pydantic, and async patterns.

**Scope**:
- RESTful API design
- Async endpoint implementation
- Request/response validation with Pydantic
- Error handling and status codes
- Middleware and CORS
- Dependency injection

**Key Technologies**:
- FastAPI 0.104+
- Pydantic v2
- Python 3.9+
- async/await patterns
- uvicorn (ASGI server)

**Code Standards**:
- All endpoints must be async (no blocking I/O)
- Pydantic models mandatory for all request/response bodies
- Type hints everywhere (mypy strict mode)
- Docstrings with OpenAPI descriptions
- One responsibility per endpoint

**Common Patterns**:
```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

app = FastAPI()

class QueryRequest(BaseModel):
    question: str
    context: str | None = None

@app.post("/api/query")
async def query_endpoint(request: QueryRequest) -> dict:
    # Implementation
    return {"answer": "..."}
```

**Testing**:
- Unit tests with pytest
- Async test fixtures
- Mock external services (Qdrant, OpenAI)
- Integration tests for API contracts

**Performance Targets**:
- Response time < 3 seconds (p95)
- Support 100+ concurrent requests
- Memory footprint < 500MB

**Owner**: RAG Chatbot Agent

**Related**: rag-chatbot-agent.md, authentication-agent.md
