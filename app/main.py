"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging_config import logger
from app.api.v1.routers import captions, health, performance


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    YouTube Caption Extractor API - Extract and process captions from YouTube videos.
    
    ## Features
    
    * Extract captions from YouTube videos
    * Support for multiple caption formats (VTT, SRV, JSON3)
    * Clean and deduplicate caption text
    * Get detailed captions with timestamps
    * Production-ready with proper logging and error handling
    
    ## Usage
    
    1. Send a POST request to `/api/v1/captions/extract` with a YouTube URL
    2. Receive cleaned and deduplicated caption text
    3. Optionally use `/api/v1/captions/extract/detailed` for timestamped segments
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(",") if settings.ALLOWED_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": {
                "success": False,
                "error": "Validation error",
                "details": exc.errors()
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": {
                "success": False,
                "error": "Internal server error",
                "details": "An unexpected error occurred"
            }
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info(f"Shutting down {settings.APP_NAME}")


# Include routers
app.include_router(health.router)
app.include_router(
    captions.router,
    prefix=settings.API_V1_PREFIX
)
app.include_router(
    performance.router,
    prefix=settings.API_V1_PREFIX
)


# Health check at root
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs_url": "/docs",
        "health_check_url": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

