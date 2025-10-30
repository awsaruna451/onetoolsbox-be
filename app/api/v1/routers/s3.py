"""
S3 API Router

This module provides API endpoints for AWS S3 file operations.
"""

from fastapi import APIRouter, HTTPException, File, UploadFile, Query
from typing import Dict
import io
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.api.v1.schemas.s3 import (
    UploadToS3Response,
    DownloadFromS3Request,
    DownloadFromS3Response,
    DeleteFromS3Request,
    DeleteFromS3Response,
    PresignedUrlRequest,
    PresignedUrlResponse,
    ListS3FilesResponse
)
from app.services.s3_service import s3_service
from app.core.logging_config import logger
from app.core.config import settings

router = APIRouter(prefix="/s3", tags=["AWS S3"])


@router.post(
    "/upload",
    response_model=UploadToS3Response,
    summary="Upload file to S3",
    description="Upload a file to AWS S3 bucket (voice_samples folder)"
)
async def upload_to_s3(
    file: UploadFile = File(...)
) -> Dict:
    """
    Upload a file to AWS S3 (Optimized for speed)
    
    - **file**: File to upload (required)
    
    Files are automatically uploaded to the 'voice_samples' folder.
    Returns the S3 URL and metadata
    """
    try:
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        logger.info(f"Upload: {file.filename}")
        
        # Read file content
        content = await file.read()
        file_obj = io.BytesIO(content)
        
        # Run S3 upload in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=1) as executor:
            result = await loop.run_in_executor(
                executor,
                lambda: s3_service.upload_file_object(
                    file_obj=file_obj,
                    filename=file.filename,
                    folder=settings.AWS_S3_FOLDER
                )
            )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_to_s3 endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload to S3: {str(e)}"
        )


@router.post(
    "/upload-voice-and-clone",
    summary="Upload voice sample to S3 and clone voice",
    description="Upload voice sample to S3, then use it for voice cloning"
)
async def upload_voice_and_clone(
    file: UploadFile = File(...),
    text: str = Query(..., description="Text to convert to speech"),
    language: str = Query(default="en", description="Language code")
) -> Dict:
    """
    Upload voice sample to S3 and use it for voice cloning
    
    - **file**: Voice sample file (required)
    - **text**: Text to synthesize (required)
    - **language**: Language code (default: 'en')
    
    Files are automatically uploaded to the 'voice_samples' folder.
    Returns both S3 URL and cloned voice result
    """
    try:
        from app.services.voice_cloning_service import voice_cloning_service
        import tempfile
        import os
        
        logger.info(f"Upload and clone request for: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Run S3 upload and local file save in parallel
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Upload to S3 (async)
            file_obj = io.BytesIO(content)
            s3_upload_future = loop.run_in_executor(
                executor,
                lambda: s3_service.upload_file_object(
                    file_obj=file_obj,
                    filename=file.filename,
                    folder=settings.AWS_S3_FOLDER
                )
            )
            
            # Save locally for voice cloning (async)
            temp_dir = tempfile.mkdtemp()
            local_voice_path = os.path.join(temp_dir, file.filename)
            
            def save_locally():
                with open(local_voice_path, 'wb') as f:
                    f.write(content)
                return local_voice_path
            
            local_save_future = loop.run_in_executor(executor, save_locally)
            
            # Wait for both operations to complete
            s3_result, _ = await asyncio.gather(s3_upload_future, local_save_future)
        
        if not s3_result.get("success"):
            raise HTTPException(status_code=400, detail=s3_result.get("error"))
        
        # Clone voice (async)
        clone_result = await voice_cloning_service.clone_voice_async(
            speaker_wav_path=local_voice_path,
            text=text,
            language=language
        )
        
        # Clean up temp file
        try:
            os.remove(local_voice_path)
            os.rmdir(temp_dir)
        except:
            pass
        
        # Upload generated speech to S3 if cloning succeeded (async)
        generated_s3_result = None
        if clone_result.get("success") and clone_result.get("output_path"):
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=1) as executor:
                generated_s3_result = await loop.run_in_executor(
                    executor,
                    lambda: s3_service.upload_file(
                        file_path=clone_result["output_path"],
                        folder="generated_speech"
                    )
                )
            
            # Delete local generated file after successful upload
            try:
                if generated_s3_result and generated_s3_result.get("success"):
                    local_generated = clone_result.get("output_path")
                    if local_generated and os.path.exists(local_generated):
                        os.remove(local_generated)
                        logger.info(f"Deleted local generated file: {local_generated}")
                        clone_result["output_path"] = None
            except Exception as del_err:
                logger.warning(f"Failed to delete local generated file: {str(del_err)}")
        
        return {
            "success": True,
            "voice_sample_s3": s3_result,
            "clone_result": clone_result,
            "generated_speech_s3": generated_s3_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_voice_and_clone endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload and clone: {str(e)}"
        )


@router.post(
    "/download",
    response_model=DownloadFromS3Response,
    summary="Download file from S3",
    description="Download a file from AWS S3 bucket to local storage"
)
async def download_from_s3(request: DownloadFromS3Request) -> Dict:
    """
    Download a file from AWS S3
    
    - **s3_key**: S3 key (path in bucket) (required)
    
    Returns the local file path
    """
    try:
        logger.info(f"S3 download request for: {request.s3_key}")
        
        # Generate local path
        from pathlib import Path
        filename = Path(request.s3_key).name
        local_path = f"data/downloaded/{filename}"
        
        # Download from S3
        result = s3_service.download_file(
            s3_key=request.s3_key,
            local_path=local_path
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in download_from_s3 endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download from S3: {str(e)}"
        )


@router.delete(
    "/delete",
    response_model=DeleteFromS3Response,
    summary="Delete file from S3",
    description="Delete a file from AWS S3 bucket"
)
async def delete_from_s3(request: DeleteFromS3Request) -> Dict:
    """
    Delete a file from AWS S3
    
    - **s3_key**: S3 key (path in bucket) (required)
    
    Returns confirmation of deletion
    """
    try:
        logger.info(f"S3 delete request for: {request.s3_key}")
        
        # Delete from S3
        result = s3_service.delete_file(s3_key=request.s3_key)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_from_s3 endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete from S3: {str(e)}"
        )


@router.post(
    "/presigned-url",
    response_model=PresignedUrlResponse,
    summary="Generate presigned URL",
    description="Generate a temporary presigned URL for S3 file access"
)
async def generate_presigned_url(request: PresignedUrlRequest) -> Dict:
    """
    Generate a presigned URL for temporary S3 file access
    
    - **s3_key**: S3 key (path in bucket) (required)
    - **expiration**: URL expiration time in seconds (default: 3600 = 1 hour)
    
    Returns the presigned URL
    """
    try:
        logger.info(f"Presigned URL request for: {request.s3_key}")
        
        # Generate presigned URL
        result = s3_service.generate_presigned_url(
            s3_key=request.s3_key,
            expiration=request.expiration
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_presigned_url endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate presigned URL: {str(e)}"
        )


@router.get(
    "/list",
    response_model=ListS3FilesResponse,
    summary="List files in S3",
    description="List all files in the voice_samples folder"
)
async def list_s3_files() -> Dict:
    """
    List files in AWS S3 bucket (voice_samples folder)
    
    Returns list of files with metadata
    """
    try:
        logger.info(f"S3 list request for folder: {settings.AWS_S3_FOLDER}")
        
        # List files (folder from settings)
        result = s3_service.list_files(folder=settings.AWS_S3_FOLDER)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in list_s3_files endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list S3 files: {str(e)}"
        )

