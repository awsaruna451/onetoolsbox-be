"""
URL Shortener API Router

This module provides API endpoints for URL shortening operations.
"""

from fastapi import APIRouter, HTTPException, Path
from typing import Dict

from app.api.v1.schemas.url_shortener import (
    ShortenURLRequest,
    ShortenURLResponse,
    ExpandURLResponse,
    AllMappingsResponse,
    DeleteMappingResponse,
    StatsResponse
)
from app.services.url_shortener_service import url_shortener_service
from app.core.logging_config import logger

router = APIRouter(prefix="/url-shortener", tags=["URL Shortener"])


@router.post(
    "/shorten",
    response_model=ShortenURLResponse,
    summary="Shorten a URL",
    description="Create a shortened version of a long URL"
)
async def shorten_url(request: ShortenURLRequest) -> Dict:
    """
    Shorten a long URL
    
    - **long_url**: The URL to shorten (required)
    - **method**: Generation method - 'hash' (deterministic) or 'random' (default: 'hash')
    - **custom_code**: Optional custom short code (3-20 characters)
    - **custom_domain**: Optional custom domain for the shortened URL (e.g., 'https://yourdomain.com')
    
    Returns the shortened URL with metadata
    """
    try:
        logger.info(f"Shortening URL: {request.long_url}" + 
                   (f" with custom domain: {request.custom_domain}" if request.custom_domain else ""))
        
        result = url_shortener_service.shorten_url(
            long_url=request.long_url,
            method=request.method,
            custom_code=request.custom_code,
            custom_domain=request.custom_domain
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in shorten_url endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to shorten URL: {str(e)}"
        )


@router.get(
    "/expand/{short_code}",
    response_model=ExpandURLResponse,
    summary="Expand a short code",
    description="Get the original URL from a short code"
)
async def expand_url(
    short_code: str = Path(..., description="The short code to expand")
) -> Dict:
    """
    Expand a short code to get the original URL
    
    - **short_code**: The short code from the shortened URL
    
    Returns the original long URL with metadata
    """
    try:
        logger.info(f"Expanding short code: {short_code}")
        
        result = url_shortener_service.expand_url(short_code)
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in expand_url endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to expand URL: {str(e)}"
        )


@router.get(
    "/mappings",
    response_model=AllMappingsResponse,
    summary="Get all URL mappings",
    description="Retrieve all shortened URLs and their mappings"
)
async def get_all_mappings() -> Dict:
    """
    Get all URL mappings
    
    Returns a list of all shortened URLs with their original URLs and metadata
    """
    try:
        logger.info("Getting all URL mappings")
        
        result = url_shortener_service.get_all_mappings()
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_all_mappings endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get mappings: {str(e)}"
        )


@router.delete(
    "/mappings/{short_code}",
    response_model=DeleteMappingResponse,
    summary="Delete a URL mapping",
    description="Delete a shortened URL mapping"
)
async def delete_mapping(
    short_code: str = Path(..., description="The short code to delete")
) -> Dict:
    """
    Delete a URL mapping
    
    - **short_code**: The short code to delete
    
    Returns success confirmation
    """
    try:
        logger.info(f"Deleting mapping for short code: {short_code}")
        
        result = url_shortener_service.delete_mapping(short_code)
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_mapping endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete mapping: {str(e)}"
        )


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Get statistics",
    description="Get URL shortener statistics"
)
async def get_stats() -> Dict:
    """
    Get URL shortener statistics
    
    Returns statistics including total URLs, clicks, and storage info
    """
    try:
        logger.info("Getting URL shortener statistics")
        
        result = url_shortener_service.get_stats()
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_stats endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats: {str(e)}"
        )



