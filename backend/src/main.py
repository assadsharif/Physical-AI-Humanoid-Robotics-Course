"""
FastAPI application entry point and configuration.

This module initializes the FastAPI application with middleware,
event handlers, and route registration.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from uuid import uuid4
import logging
from typing import Callable

from config import settings
from middleware.error_handler import error_exception_handler
from middleware.request_logging import RequestLoggingMiddleware
from utils.logger import setup_logging
from api import health, auth, chat

# Setup logging
logger = setup_logging(__name__)


# Event handlers
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown events.

    Startup: Initialize database connections, services
    Shutdown: Close connections, cleanup resources
    """
    logger.info("🚀 Application starting up")

    # Startup
    try:
        # Initialize vector store connection if needed
        logger.info("✅ Application ready")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Application shutting down")
    try:
        # Cleanup database connections, etc.
        logger.info("✅ Shutdown complete")
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")


# Create FastAPI app
app = FastAPI(
    title="Physical AI & Humanoid Robotics Textbook API",
    description="RAG-powered learning platform with vector search and AI chatbot",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request ID middleware (for tracing)
@app.middleware("http")
async def add_request_id(request: Request, call_next: Callable):
    """Add unique request ID to each request for tracing."""
    request.state.request_id = str(uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Register error handlers
app.add_exception_handler(Exception, error_exception_handler)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API status."""
    return {
        "name": "Physical AI & Humanoid Robotics Textbook API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
