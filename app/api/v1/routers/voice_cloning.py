"""
Voice Cloning API Router

This module provides API endpoints for voice cloning and text-to-speech operations.
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from typing import Dict
import os
from pathlib import Path

from app.api.v1.schemas.voice_cloning import (
    VoiceCloneRequest,
    VoiceCloneResponse,
    AnalyzeVoiceRequest,
    AnalyzeVoiceResponse,
    PreprocessAudioRequest,
    PreprocessAudioResponse,
    SupportedLanguagesResponse,
    ModelInfoResponse
)
from app.services.voice_cloning_service import voice_cloning_service
from app.core.logging_config import logger
import requests
import tempfile

router = APIRouter(prefix="/voice-cloning", tags=["Voice Cloning"])


@router.post(
    "/clone",
    response_model=VoiceCloneResponse,
    summary="Clone voice and generate speech",
    description="Generate speech from text using a cloned voice from a reference audio file"
)
async def clone_voice(request: VoiceCloneRequest) -> Dict:
    """
    Clone voice and generate speech from text
    
    - **text**: The text to convert to speech (required)
    - **speaker_wav_path**: Path to the speaker's voice sample audio file (required)
    - **language**: Language code (default: 'en')
    - **output_filename**: Optional custom output filename
    - **preprocess**: Whether to preprocess the speaker audio (default: True)
    
    Returns the generated audio file path and metadata
    """
    try:
        # Check if voice cloning service is available
        if not voice_cloning_service.available:
            raise HTTPException(
                status_code=503,
                detail="Voice cloning service not available. TTS library requires Python 3.9-3.11. Your Python version is 3.13. Please create a new virtual environment with Python 3.11 and install: pip install TTS torch librosa soundfile numpy"
            )
        
        logger.info(f"Voice cloning request received")
        logger.info(f"Text length: {len(request.text)} characters")
        logger.info(f"Speaker audio: {request.speaker_wav_path}")
        
        speaker_path = request.speaker_wav_path
        temp_file = None
        
        # Check if speaker_wav_path is a URL (S3 or HTTP)
        if request.speaker_wav_path.startswith(('http://', 'https://')):
            logger.info(f"Downloading audio from URL: {request.speaker_wav_path}")
            
            try:
                # Download file from URL
                response = requests.get(request.speaker_wav_path, timeout=30)
                response.raise_for_status()
                
                # Save to temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                temp_file.write(response.content)
                temp_file.close()
                
                speaker_path = temp_file.name
                logger.info(f"Downloaded audio to: {speaker_path}")
                
            except requests.exceptions.RequestException as e:
                if temp_file and os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to download audio from URL: {str(e)}"
                )
        else:
            # Check if local file exists
            if not os.path.exists(request.speaker_wav_path):
                raise HTTPException(
                    status_code=404,
                    detail=f"Speaker audio file not found: {request.speaker_wav_path}"
                )
        
        try:
            # Preprocess audio if requested (async)
            processed_path = speaker_path
            if request.preprocess:
                try:
                    processed_path = await voice_cloning_service.preprocess_audio_async(speaker_path)
                    logger.info(f"Audio preprocessed: {processed_path}")
                except Exception as e:
                    logger.warning(f"Preprocessing failed, using original audio: {str(e)}")
                    processed_path = speaker_path
            
            # Clone voice (async)
            result = await voice_cloning_service.clone_voice_async(
                speaker_wav_path=processed_path,
                text=request.text,
                language=request.language,
                output_filename=request.output_filename
            )
            
            if not result.get("success"):
                raise HTTPException(status_code=400, detail=result.get("error"))
            
            # Upload generated audio to S3 (async)
            s3_url = None
            s3_key = None
            if result.get("output_path"):
                try:
                    from app.services.s3_service import s3_service
                    import asyncio
                    from concurrent.futures import ThreadPoolExecutor
                    
                    logger.info(f"Uploading generated audio to S3: {result['output_path']}")
                    
                    # Upload to S3 asynchronously
                    loop = asyncio.get_event_loop()
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        s3_result = await loop.run_in_executor(
                            executor,
                            lambda: s3_service.upload_file(
                                file_path=result["output_path"],
                                folder="generated_speech"
                            )
                        )
                    
                    if s3_result.get("success"):
                        s3_url = s3_result.get("s3_url")
                        s3_key = s3_result.get("s3_key")
                        logger.info(f"Generated audio uploaded to S3: {s3_url}")
                        
                        # Add S3 info to result
                        result["s3_url"] = s3_url
                        result["s3_key"] = s3_key
                        result["s3_bucket"] = s3_result.get("bucket")
                        
                        # Delete local generated file after successful upload
                        try:
                            local_output = result.get("output_path")
                            if local_output and os.path.exists(local_output):
                                os.remove(local_output)
                                logger.info(f"Deleted local generated file: {local_output}")
                                # Reflect deletion in response
                                result["output_path"] = None
                        except Exception as del_err:
                            logger.warning(f"Failed to delete local generated file: {str(del_err)}")
                    else:
                        logger.warning(f"Failed to upload to S3: {s3_result.get('error')}")
                        
                except Exception as e:
                    logger.warning(f"S3 upload failed (non-critical): {str(e)}")
            
            return result
            
        finally:
            # Clean up temporary file if it was created
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                    logger.info(f"Cleaned up temp file: {temp_file.name}")
                except Exception as e:
                    logger.warning(f"Failed to delete temp file: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in clone_voice endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clone voice: {str(e)}"
        )


@router.post(
    "/analyze",
    response_model=AnalyzeVoiceResponse,
    summary="Analyze voice sample",
    description="Analyze voice sample characteristics including pitch, energy, and duration"
)
async def analyze_voice(request: AnalyzeVoiceRequest) -> Dict:
    """
    Analyze voice sample characteristics
    
    - **audio_path**: Path to the audio file to analyze (required)
    
    Returns analysis results including duration, pitch, energy, etc.
    """
    try:
        # Check if voice cloning service is available
        if not voice_cloning_service.available:
            raise HTTPException(
                status_code=503,
                detail="Voice cloning service not available. TTS library requires Python 3.9-3.11. Your Python version is 3.13. Please create a new virtual environment with Python 3.11 and install: pip install TTS torch librosa soundfile numpy"
            )
        
        logger.info(f"Voice analysis request for: {request.audio_path}")
        
        # Check if audio file exists
        if not os.path.exists(request.audio_path):
            raise HTTPException(
                status_code=404,
                detail=f"Audio file not found: {request.audio_path}"
            )
        
        # Analyze voice sample
        analysis = voice_cloning_service.analyze_voice_sample(request.audio_path)
        
        return {
            "success": True,
            **analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_voice endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze voice: {str(e)}"
        )


@router.post(
    "/preprocess",
    response_model=PreprocessAudioResponse,
    summary="Preprocess audio file",
    description="Preprocess audio file for optimal voice cloning (resample, normalize, trim silence)"
)
async def preprocess_audio(request: PreprocessAudioRequest) -> Dict:
    """
    Preprocess audio file
    
    - **audio_path**: Path to the audio file to preprocess (required)
    - **target_sr**: Target sample rate (default: 22050)
    
    Returns the path to the preprocessed audio file
    """
    try:
        # Check if voice cloning service is available
        if not voice_cloning_service.available:
            raise HTTPException(
                status_code=503,
                detail="Voice cloning service not available. TTS library requires Python 3.9-3.11. Your Python version is 3.13. Please create a new virtual environment with Python 3.11 and install: pip install TTS torch librosa soundfile numpy"
            )
        
        logger.info(f"Audio preprocessing request for: {request.audio_path}")
        
        # Check if audio file exists
        if not os.path.exists(request.audio_path):
            raise HTTPException(
                status_code=404,
                detail=f"Audio file not found: {request.audio_path}"
            )
        
        # Preprocess audio
        processed_path = voice_cloning_service.preprocess_audio(
            request.audio_path,
            target_sr=request.target_sr
        )
        
        return {
            "success": True,
            "processed_path": processed_path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in preprocess_audio endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to preprocess audio: {str(e)}"
        )


@router.post(
    "/upload-voice-sample",
    summary="Upload voice sample",
    description="Upload a voice sample audio file for voice cloning"
)
async def upload_voice_sample(file: UploadFile = File(...)) -> Dict:
    """
    Upload a voice sample audio file
    
    Accepts audio files in formats: .wav, .mp3, .flac, .ogg, .m4a
    """
    try:
        # Validate file extension
        allowed_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file
        voice_samples_dir = Path("data/voice_samples")
        voice_samples_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = voice_samples_dir / file.filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"Voice sample uploaded: {file_path}")
        
        # Analyze the uploaded file
        try:
            analysis = voice_cloning_service.analyze_voice_sample(str(file_path))
        except Exception as e:
            logger.warning(f"Could not analyze uploaded file: {str(e)}")
            analysis = {}
        
        return {
            "success": True,
            "filename": file.filename,
            "file_path": str(file_path),
            "size_bytes": len(content),
            "analysis": analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading voice sample: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload voice sample: {str(e)}"
        )


@router.get(
    "/download/{filename}",
    summary="Download generated speech",
    description="Download a generated speech audio file"
)
async def download_generated_speech(filename: str):
    """
    Download a generated speech audio file
    
    - **filename**: Name of the generated audio file
    """
    try:
        file_path = Path("data/generated_speech") / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {filename}"
            )
        
        return FileResponse(
            path=str(file_path),
            media_type="audio/wav",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download file: {str(e)}"
        )


@router.get(
    "/languages",
    response_model=SupportedLanguagesResponse,
    summary="Get supported languages",
    description="Get list of supported languages for voice cloning"
)
async def get_supported_languages() -> Dict:
    """
    Get list of supported languages
    
    Returns a dictionary of language codes and their names
    """
    try:
        # Check if voice cloning service is available
        if not voice_cloning_service.available:
            raise HTTPException(
                status_code=503,
                detail="Voice cloning service not available. TTS library requires Python 3.9-3.11. Your Python version is 3.13. Please create a new virtual environment with Python 3.11 and install: pip install TTS torch librosa soundfile numpy"
            )
        
        return voice_cloning_service.get_supported_languages()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting supported languages: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get supported languages: {str(e)}"
        )


@router.get(
    "/model-info",
    response_model=ModelInfoResponse,
    summary="Get model information",
    description="Get information about the loaded TTS model"
)
async def get_model_info() -> Dict:
    """
    Get information about the loaded TTS model
    
    Returns model name, device, and status information
    """
    try:
        # Check if voice cloning service is available
        if not voice_cloning_service.available:
            raise HTTPException(
                status_code=503,
                detail="Voice cloning service not available. TTS library requires Python 3.9-3.11. Your Python version is 3.13. Please create a new virtual environment with Python 3.11 and install: pip install TTS torch librosa soundfile numpy"
            )
        
        return voice_cloning_service.get_model_info()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get model info: {str(e)}"
        )

