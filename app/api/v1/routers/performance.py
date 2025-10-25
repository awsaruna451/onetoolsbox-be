"""
Performance monitoring endpoints
"""
from fastapi import APIRouter
from datetime import datetime
from app.core.logging_config import logger
from app.services.youtube_caption_service import YouTubeCaptionService


router = APIRouter(prefix="/performance", tags=["Performance"])


@router.get(
    "/cache/stats",
    summary="Get cache statistics",
    description="Get current cache statistics and performance metrics"
)
async def get_cache_stats():
    """
    Get cache statistics
    
    Returns cache hit/miss ratios and current cache size.
    """
    cache_size = len(YouTubeCaptionService._cache)
    cache_ttl = YouTubeCaptionService._cache_ttl
    
    return {
        "cache_size": cache_size,
        "cache_ttl_seconds": cache_ttl,
        "cache_ttl_hours": cache_ttl / 3600,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post(
    "/cache/clear",
    summary="Clear cache",
    description="Clear all cached caption data"
)
async def clear_cache():
    """
    Clear all cached data
    
    Useful for testing or when you want to force fresh data.
    """
    cache_size_before = len(YouTubeCaptionService._cache)
    YouTubeCaptionService._cache.clear()
    
    logger.info(f"Cache cleared. Removed {cache_size_before} entries.")
    
    return {
        "success": True,
        "entries_cleared": cache_size_before,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    "/health/detailed",
    summary="Detailed health check",
    description="Get detailed system health information"
)
async def detailed_health():
    """
    Get detailed health information
    
    Returns system status, cache info, and performance metrics.
    """
    cache_size = len(YouTubeCaptionService._cache)
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "cache": {
            "size": cache_size,
            "ttl_seconds": YouTubeCaptionService._cache_ttl
        },
        "performance": {
            "cache_enabled": True,
            "optimizations": [
                "Reduced timeouts",
                "Parallel downloads", 
                "HTTP connection reuse",
                "In-memory caching"
            ]
        }
    }
