"""
Application configuration management
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "YouTube Caption Extractor API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS
    ALLOWED_ORIGINS: str = "*"
    
    # URL Shortener Settings
    BASE_URL: str = "http://localhost:8000/s/"  # Base URL for shortened links
    
    # AWS S3 Settings
    AWS_S3_BUCKET_NAME: str = ""  # S3 bucket name for file storage
    AWS_S3_FOLDER: str = "voice_samples"  # S3 folder for voice samples
    AWS_ACCESS_KEY_ID: str = ""  # AWS access key ID
    AWS_SECRET_ACCESS_KEY: str = ""  # AWS secret access key
    AWS_REGION: str = "us-east-1"  # AWS region
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or console
    
    # YouTube Settings
    MAX_VIDEO_DURATION: int = 7200  # 2 hours in seconds
    DEFAULT_CAPTION_FORMAT: str = "txt"
    SUPPORTED_CAPTION_FORMATS: List[str] = ["txt", "srt", "json"]
    
    # Performance Settings
    CACHE_TTL: int = 3600  # Cache time-to-live in seconds (1 hour)
    REQUEST_TIMEOUT: int = 15  # Request timeout in seconds
    MAX_CONCURRENT_DOWNLOADS: int = 3  # Max concurrent downloads
    
    # Rate Limiting (optional for future implementation)
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_PER_MINUTE: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

