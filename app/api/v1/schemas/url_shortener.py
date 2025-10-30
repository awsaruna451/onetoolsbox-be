"""
URL Shortener API schemas
"""

from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl


class ShortenURLRequest(BaseModel):
    """Request schema for shortening a URL"""
    long_url: str = Field(
        ...,
        description="The long URL to shorten",
        example="https://www.example.com/very/long/url/path?param1=value1&param2=value2"
    )
    method: str = Field(
        default="hash",
        description="Method to generate short code: 'hash' or 'random'",
        example="hash"
    )
    custom_code: Optional[str] = Field(
        default=None,
        description="Optional custom short code (3-20 characters)",
        example="mycode"
    )
    custom_domain: Optional[str] = Field(
        default=None,
        description="Optional custom domain for the shortened URL (e.g., 'https://yourdomain.com' or 'https://short.link')",
        example="https://short.link"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "long_url": "https://www.example.com/very/long/url",
                "method": "hash",
                "custom_domain": "https://short.link"
            }
        }


class ShortenURLResponse(BaseModel):
    """Response schema for shortened URL"""
    success: bool = Field(..., description="Whether the operation was successful")
    short_url: Optional[str] = Field(None, description="The shortened URL")
    short_code: Optional[str] = Field(None, description="The short code")
    long_url: Optional[str] = Field(None, description="The original long URL")
    method: Optional[str] = Field(None, description="Method used to generate the code")
    custom_domain: Optional[str] = Field(None, description="Custom domain used (if provided)")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    message: Optional[str] = Field(None, description="Additional message")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "short_url": "https://short.link/s/abc123",
                "short_code": "abc123",
                "long_url": "https://www.example.com/very/long/url",
                "method": "hash",
                "custom_domain": "https://short.link",
                "created_at": "2025-10-25T10:30:00"
            }
        }


class ExpandURLResponse(BaseModel):
    """Response schema for expanded URL"""
    success: bool = Field(..., description="Whether the operation was successful")
    long_url: Optional[str] = Field(None, description="The original long URL")
    short_code: Optional[str] = Field(None, description="The short code")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    clicks: Optional[int] = Field(None, description="Number of times accessed")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "long_url": "https://www.example.com/very/long/url",
                "short_code": "abc123",
                "created_at": "2025-10-25T10:30:00",
                "clicks": 42
            }
        }


class URLMapping(BaseModel):
    """Schema for a single URL mapping"""
    short_code: str = Field(..., description="The short code")
    long_url: str = Field(..., description="The long URL")
    short_url: str = Field(..., description="The full short URL")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    method: Optional[str] = Field(None, description="Generation method")
    clicks: Optional[int] = Field(None, description="Number of clicks")


class AllMappingsResponse(BaseModel):
    """Response schema for all URL mappings"""
    success: bool = Field(..., description="Whether the operation was successful")
    total: Optional[int] = Field(None, description="Total number of mappings")
    mappings: Optional[List[URLMapping]] = Field(None, description="List of all mappings")
    error: Optional[str] = Field(None, description="Error message if failed")


class DeleteMappingResponse(BaseModel):
    """Response schema for deleting a mapping"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: Optional[str] = Field(None, description="Success message")
    error: Optional[str] = Field(None, description="Error message if failed")


class StatsResponse(BaseModel):
    """Response schema for statistics"""
    success: bool = Field(..., description="Whether the operation was successful")
    total_urls: Optional[int] = Field(None, description="Total number of URLs")
    total_clicks: Optional[int] = Field(None, description="Total number of clicks")
    storage_file: Optional[str] = Field(None, description="Storage file path")
    base_url: Optional[str] = Field(None, description="Base URL for short links")
    error: Optional[str] = Field(None, description="Error message if failed")

