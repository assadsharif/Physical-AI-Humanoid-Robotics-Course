"""
Health check endpoint for service monitoring.
"""

from fastapi import APIRouter
from typing import Dict, Any

from config import settings
from utils.logger import setup_logging

logger = setup_logging(__name__)

router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint - returns 200 OK with service status.

    Returns:
        Service status information
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


@router.get("/health/ready", tags=["health"])
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check - indicates if service is ready to receive traffic.

    Returns:
        Readiness status
    """
    # In production, this would check database connectivity, etc.
    return {
        "ready": True,
        "service": settings.APP_NAME,
    }


@router.get("/health/live", tags=["health"])
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check - indicates if service is running.

    Returns:
        Liveness status
    """
    return {
        "alive": True,
        "service": settings.APP_NAME,
    }
