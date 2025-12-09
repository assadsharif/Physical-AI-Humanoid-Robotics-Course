"""Common Pydantic schemas used across the API."""

from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, Dict
from datetime import datetime


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(from_attributes=True)  # Allow reading from SQLAlchemy models


class PaginationParams(BaseModel):
    """Pagination parameters."""

    skip: int = 0
    limit: int = 10

    class Config:
        ge = 0
        le = 100


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""

    total: int
    skip: int
    limit: int
    items: list[Any]


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: str
    message: str
    code: int
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    version: str
    environment: str


class MessageResponse(BaseModel):
    """Generic success message response."""

    message: str
    data: Optional[Dict[str, Any]] = None
