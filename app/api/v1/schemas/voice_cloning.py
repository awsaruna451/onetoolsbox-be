"""
Voice Cloning API schemas
"""

from typing import Optional, Dict
from pydantic import BaseModel, Field


class VoiceCloneRequest(BaseModel):
    """Request schema for voice cloning"""
    text: str = Field(
        ...,
        description="Text to convert to speech",
        min_length=1,
        max_length=5000,
        example="Please subscribe and like to support me in creating more free content like this."
    )
    speaker_wav_path: str = Field(
        ...,
        description="Path to the speaker's voice sample audio file (local path or S3 URL)",
        example="https://your-bucket.s3.amazonaws.com/voice_samples/my_voice.wav"
    )
    language: str = Field(
        default="en",
        description="Language code (en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, zh-cn, ja)",
        example="en"
    )
    output_filename: Optional[str] = Field(
        default=None,
        description="Optional custom output filename (without path)",
        example="my_speech.wav"
    )
    preprocess: bool = Field(
        default=True,
        description="Whether to preprocess the speaker audio (recommended)",
        example=True
    )
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Hello! This is my cloned voice speaking.",
                "speaker_wav_path": "https://your-bucket.s3.amazonaws.com/voice_samples/my_voice.wav",
                "language": "en",
                "preprocess": True
            }
        }


class VoiceCloneResponse(BaseModel):
    """Response schema for voice cloning"""
    success: bool = Field(..., description="Whether the operation was successful")
    output_path: Optional[str] = Field(None, description="Path to the generated audio file")
    output_filename: Optional[str] = Field(None, description="Filename of the generated audio")
    text: Optional[str] = Field(None, description="Text that was synthesized")
    language: Optional[str] = Field(None, description="Language used")
    audio_duration: Optional[float] = Field(None, description="Duration of generated audio in seconds")
    generation_time: Optional[float] = Field(None, description="Time taken to generate audio in seconds")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    s3_url: Optional[str] = Field(None, description="S3 URL of the uploaded generated audio")
    s3_key: Optional[str] = Field(None, description="S3 key (path) of the uploaded audio")
    s3_bucket: Optional[str] = Field(None, description="S3 bucket name")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "output_path": "data/generated_speech/cloned_speech_20251026_120000_abc123.wav",
                "output_filename": "cloned_speech_20251026_120000_abc123.wav",
                "text": "Hello! This is my cloned voice speaking.",
                "language": "en",
                "audio_duration": 3.5,
                "generation_time": 2.1,
                "created_at": "2025-10-26T12:00:00",
                "s3_url": "https://video-processor-bucket-dev.s3.amazonaws.com/generated_speech/cloned_speech_20251026_120000_abc123.wav",
                "s3_key": "generated_speech/cloned_speech_20251026_120000_abc123.wav",
                "s3_bucket": "video-processor-bucket-dev"
            }
        }


class AnalyzeVoiceRequest(BaseModel):
    """Request schema for voice sample analysis"""
    audio_path: str = Field(
        ...,
        description="Path to the audio file to analyze",
        example="data/voice_samples/my_voice.wav"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "audio_path": "data/voice_samples/my_voice.wav"
            }
        }


class AnalyzeVoiceResponse(BaseModel):
    """Response schema for voice sample analysis"""
    success: bool = Field(..., description="Whether the operation was successful")
    duration: Optional[float] = Field(None, description="Duration in seconds")
    avg_pitch: Optional[float] = Field(None, description="Average pitch in Hz")
    rms_energy: Optional[float] = Field(None, description="RMS energy level")
    zero_crossing_rate: Optional[float] = Field(None, description="Zero crossing rate")
    sample_rate: Optional[int] = Field(None, description="Sample rate in Hz")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "duration": 10.5,
                "avg_pitch": 180.5,
                "rms_energy": 0.0523,
                "zero_crossing_rate": 0.0812,
                "sample_rate": 22050
            }
        }


class PreprocessAudioRequest(BaseModel):
    """Request schema for audio preprocessing"""
    audio_path: str = Field(
        ...,
        description="Path to the audio file to preprocess",
        example="data/voice_samples/raw_voice.wav"
    )
    target_sr: int = Field(
        default=22050,
        description="Target sample rate",
        example=22050
    )
    
    class Config:
        schema_extra = {
            "example": {
                "audio_path": "data/voice_samples/raw_voice.wav",
                "target_sr": 22050
            }
        }


class PreprocessAudioResponse(BaseModel):
    """Response schema for audio preprocessing"""
    success: bool = Field(..., description="Whether the operation was successful")
    processed_path: Optional[str] = Field(None, description="Path to the preprocessed audio file")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "processed_path": "data/voice_samples/processed_raw_voice.wav"
            }
        }


class SupportedLanguagesResponse(BaseModel):
    """Response schema for supported languages"""
    success: bool = Field(..., description="Whether the operation was successful")
    languages: Optional[Dict[str, str]] = Field(None, description="Dictionary of language codes and names")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "languages": {
                    "en": "English",
                    "es": "Spanish",
                    "fr": "French"
                }
            }
        }


class ModelInfoResponse(BaseModel):
    """Response schema for model information"""
    success: bool = Field(..., description="Whether the operation was successful")
    model_name: Optional[str] = Field(None, description="Name of the TTS model")
    device: Optional[str] = Field(None, description="Device being used (cpu/cuda)")
    model_loaded: Optional[bool] = Field(None, description="Whether model is loaded")
    voice_samples_dir: Optional[str] = Field(None, description="Directory for voice samples")
    generated_speech_dir: Optional[str] = Field(None, description="Directory for generated speech")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "model_name": "tts_models/multilingual/multi-dataset/xtts_v2",
                "device": "cuda",
                "model_loaded": True,
                "voice_samples_dir": "data/voice_samples",
                "generated_speech_dir": "data/generated_speech"
            }
        }

