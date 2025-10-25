"""
YouTube Caption extraction API endpoints
"""
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    CaptionRequest,
    CaptionResponse,
    CaptionDetailedResponse,
    ErrorResponse
)
from app.services.youtube_caption_service import YouTubeCaptionService
from app.core.logging_config import logger


router = APIRouter(prefix="/captions", tags=["Captions"])


@router.post(
    "/extract",
    response_model=CaptionResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Extract captions from YouTube video",
    description="Extract and clean captions from a YouTube video URL",
    status_code=status.HTTP_200_OK
)
async def extract_captions(request: CaptionRequest):
    """
    Extract captions from YouTube video
    
    - **youtube_url**: YouTube video URL (required)
    - **format**: Output format (txt, srt, json) - default: txt
    
    Returns cleaned and deduplicated caption text.
    """
    try:
        logger.info(f"Received caption extraction request for: {request.youtube_url}")
        
        # Extract captions
        caption_data = YouTubeCaptionService.extract_captions(
            str(request.youtube_url),
            request.format.value
        )
        
        # Clean captions
        clean_text = YouTubeCaptionService.clean_captions(caption_data['captions'])
        
        response = {
            "success": True,
            "video_title": caption_data['video_title'],
            "video_id": caption_data['video_id'],
            "caption_format": caption_data['format'],
            "clean_text": clean_text,
            "content_length": len(clean_text)
        }
        
        logger.info(f"Successfully processed captions for video: {caption_data['video_id']}")
        
        return response
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "Invalid request",
                "details": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Caption extraction failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "Failed to extract captions",
                "details": str(e)
            }
        )


@router.post(
    "/extract/detailed",
    response_model=CaptionDetailedResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Extract detailed captions with timestamps",
    description="Extract captions with individual segments and timestamps",
    status_code=status.HTTP_200_OK
)
async def extract_detailed_captions(request: CaptionRequest):
    """
    Extract detailed captions with timestamps
    
    - **youtube_url**: YouTube video URL (required)
    - **format**: Output format (txt, srt, json) - default: txt
    
    Returns captions with individual segments and timing information.
    """
    try:
        logger.info(f"Received detailed caption extraction request for: {request.youtube_url}")
        
        # Extract captions
        caption_data = YouTubeCaptionService.extract_captions(
            str(request.youtube_url),
            request.format.value
        )
        
        response = {
            "success": True,
            "video_title": caption_data['video_title'],
            "video_id": caption_data['video_id'],
            "video_duration": caption_data['video_duration'],
            "total_captions": caption_data['total_captions'],
            "format": caption_data['format'],
            "captions": caption_data['captions']
        }
        
        logger.info(f"Successfully processed detailed captions for video: {caption_data['video_id']}")
        
        return response
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "Invalid request",
                "details": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Detailed caption extraction failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "Failed to extract detailed captions",
                "details": str(e)
            }
        )

