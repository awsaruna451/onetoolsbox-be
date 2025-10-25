"""
Pydantic models for request/response schemas
"""
from pydantic import BaseModel, HttpUrl, Field, validator
from typing import Optional, List, Dict
from enum import Enum


class CaptionFormat(str, Enum):
    """Supported caption output formats"""
    TXT = "txt"
    SRT = "srt"
    JSON = "json"


class CaptionRequest(BaseModel):
    """Request model for caption extraction"""
    youtube_url: HttpUrl = Field(
        ...,
        description="YouTube video URL",
        example="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    )
    format: CaptionFormat = Field(
        default=CaptionFormat.TXT,
        description="Output format for captions"
    )
    
    @validator('youtube_url')
    def validate_youtube_url(cls, v):
        """Validate that the URL is a YouTube URL"""
        url_str = str(v)
        valid_domains = ['youtube.com', 'youtu.be', 'www.youtube.com', 'm.youtube.com']
        
        if not any(domain in url_str for domain in valid_domains):
            raise ValueError('URL must be a valid YouTube URL')
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "format": "txt"
            }
        }


class CaptionSegment(BaseModel):
    """Individual caption segment"""
    start_time: float = Field(..., description="Start time in seconds")
    end_time: float = Field(..., description="End time in seconds")
    duration: float = Field(..., description="Duration in seconds")
    text: str = Field(..., description="Caption text")


class CaptionResponse(BaseModel):
    """Response model for caption extraction"""
    success: bool = Field(..., description="Indicates if the operation was successful")
    video_title: str = Field(..., description="Title of the YouTube video")
    video_id: str = Field(..., description="YouTube video ID")
    caption_format: str = Field(..., description="Format of the extracted captions")
    clean_text: str = Field(..., description="Cleaned and deduplicated caption text")
    content_length: int = Field(..., description="Length of the clean text")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "video_title": "Sample Video Title",
                "video_id": "dQw4w9WgXcQ",
                "caption_format": "vtt",
                "clean_text": "This is the cleaned caption text...",
                "content_length": 1250
            }
        }


class CaptionDetailedResponse(BaseModel):
    """Detailed response with individual caption segments"""
    success: bool
    video_title: str
    video_id: str
    video_duration: float
    total_captions: int
    format: str
    captions: List[CaptionSegment]


class ErrorDetail(BaseModel):
    """Error detail model"""
    success: bool = False
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Detailed error information")


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: ErrorDetail
    
    class Config:
        schema_extra = {
            "example": {
                "detail": {
                    "success": False,
                    "error": "Failed to extract captions",
                    "details": "No English captions available for this video"
                }
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: str

