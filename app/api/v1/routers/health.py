"""
Health check endpoints
"""
from fastapi import APIRouter
from datetime import datetime
from app.models.schemas import HealthResponse
from app.core.config import settings


router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check endpoint",
    description="Check if the API is running and healthy"
)
async def health_check():
    """
    Health check endpoint
    
    Returns the current status of the API.
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    "/",
    summary="Root endpoint",
    description="API information"
)
async def root():
    """
    Root endpoint
    
    Returns basic API information.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "health_url": "/health"
    }

