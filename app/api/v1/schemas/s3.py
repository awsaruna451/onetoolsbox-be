"""
S3 API schemas
"""

from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class UploadToS3Response(BaseModel):
    """Response schema for S3 upload"""
    success: bool = Field(..., description="Whether the operation was successful")
    s3_url: Optional[str] = Field(None, description="S3 URL of the uploaded file")
    s3_key: Optional[str] = Field(None, description="S3 key (path in bucket)")
    bucket: Optional[str] = Field(None, description="S3 bucket name")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    content_type: Optional[str] = Field(None, description="File content type")
    uploaded_at: Optional[str] = Field(None, description="Upload timestamp")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "s3_url": "https://my-bucket.s3.amazonaws.com/voice_samples/20251028_120000_voice.wav",
                "s3_key": "voice_samples/20251028_120000_voice.wav",
                "bucket": "my-bucket",
                "file_size": 441000,
                "content_type": "audio/wav",
                "uploaded_at": "2025-10-28T12:00:00"
            }
        }


class DownloadFromS3Request(BaseModel):
    """Request schema for S3 download"""
    s3_key: str = Field(
        ...,
        description="S3 key (path in bucket)",
        example="voice_samples/20251028_120000_voice.wav"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "s3_key": "voice_samples/20251028_120000_voice.wav"
            }
        }


class DownloadFromS3Response(BaseModel):
    """Response schema for S3 download"""
    success: bool = Field(..., description="Whether the operation was successful")
    local_path: Optional[str] = Field(None, description="Local file path")
    s3_key: Optional[str] = Field(None, description="S3 key")
    error: Optional[str] = Field(None, description="Error message if failed")


class DeleteFromS3Request(BaseModel):
    """Request schema for S3 delete"""
    s3_key: str = Field(
        ...,
        description="S3 key (path in bucket)",
        example="voice_samples/20251028_120000_voice.wav"
    )


class DeleteFromS3Response(BaseModel):
    """Response schema for S3 delete"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: Optional[str] = Field(None, description="Success message")
    error: Optional[str] = Field(None, description="Error message if failed")


class PresignedUrlRequest(BaseModel):
    """Request schema for generating presigned URL"""
    s3_key: str = Field(
        ...,
        description="S3 key (path in bucket)",
        example="voice_samples/20251028_120000_voice.wav"
    )
    expiration: int = Field(
        default=3600,
        description="URL expiration time in seconds (default: 1 hour)",
        example=3600
    )


class PresignedUrlResponse(BaseModel):
    """Response schema for presigned URL"""
    success: bool = Field(..., description="Whether the operation was successful")
    presigned_url: Optional[str] = Field(None, description="Presigned URL")
    expires_in: Optional[int] = Field(None, description="Expiration time in seconds")
    error: Optional[str] = Field(None, description="Error message if failed")


class S3File(BaseModel):
    """Schema for an S3 file"""
    key: str = Field(..., description="S3 key")
    size: int = Field(..., description="File size in bytes")
    last_modified: str = Field(..., description="Last modified timestamp")
    url: str = Field(..., description="S3 URL")


class ListS3FilesResponse(BaseModel):
    """Response schema for listing S3 files"""
    success: bool = Field(..., description="Whether the operation was successful")
    files: Optional[List[S3File]] = Field(None, description="List of files")
    count: Optional[int] = Field(None, description="Number of files")
    error: Optional[str] = Field(None, description="Error message if failed")

