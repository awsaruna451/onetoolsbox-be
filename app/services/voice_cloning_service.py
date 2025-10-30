"""
Voice Cloning Service

This module provides voice cloning and text-to-speech functionality.
"""

import os
import asyncio
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import hashlib
from concurrent.futures import ThreadPoolExecutor

from app.core.config import settings
from app.core.logging_config import logger

# Optional dependencies - graceful degradation if not installed
try:
    import torch
    import librosa
    import soundfile as sf
    import numpy as np
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Voice cloning dependencies not installed: {str(e)}")
    logger.warning("Install with: pip install TTS torch librosa soundfile numpy")
    TTS_AVAILABLE = False
    TTS = None
    torch = None
    librosa = None
    sf = None
    np = None


class VoiceCloningService:
    """Service for voice cloning and text-to-speech operations"""
    
    def __init__(self, model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"):
        """
        Initialize the voice cloning service
        
        Args:
            model_name (str): Name of the TTS model to use
        """
        self.available = TTS_AVAILABLE
        
        if not TTS_AVAILABLE:
            logger.warning("Voice cloning service not available - dependencies not installed")
            return
        
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = None
        
        # Thread pool for async operations
        self._executor = ThreadPoolExecutor(max_workers=2)
        
        # Directories for storing files
        self.voice_samples_dir = Path("data/voice_samples")
        self.generated_speech_dir = Path("data/generated_speech")
        
        # Create directories
        self.voice_samples_dir.mkdir(parents=True, exist_ok=True)
        self.generated_speech_dir.mkdir(parents=True, exist_ok=True)
        
        # Apply PyTorch compatibility fix
        self._apply_torch_compatibility_fix()
        
        logger.info(f"VoiceCloningService initialized on device: {self.device}")
    
    def _apply_torch_compatibility_fix(self):
        """Apply PyTorch 2.6+ compatibility fix for TTS library"""
        try:
            _original_torch_load = torch.load
            
            def patched_torch_load(*args, **kwargs):
                kwargs['weights_only'] = False
                return _original_torch_load(*args, **kwargs)
            
            torch.load = patched_torch_load
            logger.info("Applied torch.load patch for TTS compatibility")
        except Exception as e:
            logger.warning(f"Could not apply torch compatibility fix: {str(e)}")
    
    def _lazy_load_model(self):
        """Lazy load the TTS model only when needed"""
        if self.tts is None:
            try:
                logger.info(f"Loading TTS model: {self.model_name}")
                self.tts = TTS(self.model_name).to(self.device)
                logger.info("TTS model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load TTS model: {str(e)}")
                raise
    
    async def preprocess_audio_async(self, audio_path: str, target_sr: int = 22050) -> str:
        """
        Async version: Preprocess audio file to ensure proper format for voice cloning
        
        Args:
            audio_path (str): Path to the audio file
            target_sr (int): Target sample rate
            
        Returns:
            str: Path to the preprocessed audio file
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._preprocess_audio_sync,
            audio_path,
            target_sr
        )
    
    def _preprocess_audio_sync(self, audio_path: str, target_sr: int = 22050) -> str:
        """
        Synchronous preprocessing implementation (called by async wrapper)
        """
        if not self.available:
            raise ImportError("Voice cloning dependencies not installed")
        
        try:
            # Load audio
            audio, sr = librosa.load(audio_path, sr=None)
            
            # Resample if necessary
            if sr != target_sr:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
            
            # Normalize audio
            audio = audio / np.max(np.abs(audio))
            
            # Remove silence from beginning and end
            audio, _ = librosa.effects.trim(audio, top_db=20)
            
            # Save preprocessed audio
            processed_filename = f"processed_{Path(audio_path).name}"
            processed_path = self.voice_samples_dir / processed_filename
            sf.write(processed_path, audio, target_sr)
            
            logger.info(f"Audio preprocessed: {processed_path}")
            return str(processed_path)
            
        except Exception as e:
            logger.error(f"Error preprocessing audio: {str(e)}")
            raise
    
    def preprocess_audio(self, audio_path: str, target_sr: int = 22050) -> str:
        """
        Synchronous preprocess audio (for backward compatibility)
        
        Args:
            audio_path (str): Path to the audio file
            target_sr (int): Target sample rate
            
        Returns:
            str: Path to the preprocessed audio file
        """
        return self._preprocess_audio_sync(audio_path, target_sr)
    
    def analyze_voice_sample(self, audio_path: str) -> Dict:
        """
        Analyze voice sample characteristics
        
        Args:
            audio_path (str): Path to the audio file
            
        Returns:
            Dict: Analysis results
        """
        if not self.available:
            raise ImportError("Voice cloning dependencies not installed")
        
        try:
            audio, sr = librosa.load(audio_path)
            
            # Calculate features
            duration = len(audio) / sr
            rms_energy = float(np.sqrt(np.mean(audio**2)))
            zero_crossing_rate = float(np.mean(librosa.feature.zero_crossing_rate(audio)))
            
            # Pitch analysis
            pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            avg_pitch = float(np.mean(pitch_values)) if pitch_values else 0.0
            
            analysis = {
                'duration': round(duration, 2),
                'avg_pitch': round(avg_pitch, 2),
                'rms_energy': round(rms_energy, 4),
                'zero_crossing_rate': round(zero_crossing_rate, 4),
                'sample_rate': sr
            }
            
            logger.info(f"Voice sample analysis: {analysis}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing voice sample: {str(e)}")
            raise
    
    async def clone_voice_async(
        self, 
        speaker_wav_path: str, 
        text: str, 
        language: str = "en",
        output_filename: Optional[str] = None
    ) -> Dict:
        """
        Async version: Generate speech using voice cloning from a reference audio
        
        Args:
            speaker_wav_path (str): Path to the speaker's voice sample
            text (str): Text to synthesize
            language (str): Language code (en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, zh-cn, ja)
            output_filename (str): Optional output filename
            
        Returns:
            Dict: Result with generated audio path and metadata
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._clone_voice_sync,
            speaker_wav_path,
            text,
            language,
            output_filename
        )
    
    def clone_voice(
        self, 
        speaker_wav_path: str, 
        text: str, 
        language: str = "en",
        output_filename: Optional[str] = None
    ) -> Dict:
        """
        Synchronous version: Generate speech using voice cloning (for backward compatibility)
        """
        return self._clone_voice_sync(speaker_wav_path, text, language, output_filename)
    
    def _clone_voice_sync(
        self, 
        speaker_wav_path: str, 
        text: str, 
        language: str = "en",
        output_filename: Optional[str] = None
    ) -> Dict:
        """
        Synchronous implementation of voice cloning
        
        Args:
            speaker_wav_path (str): Path to the speaker's voice sample
            text (str): Text to synthesize
            language (str): Language code (en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, zh-cn, ja)
            output_filename (str): Optional output filename
            
        Returns:
            Dict: Result with generated audio path and metadata
        """
        if not self.available:
            return {
                "success": False,
                "error": "Voice cloning service not available. Please install dependencies: pip install TTS torch librosa soundfile numpy"
            }
        
        try:
            # Lazy load model
            self._lazy_load_model()
            
            # Validate input
            if not os.path.exists(speaker_wav_path):
                return {
                    "success": False,
                    "error": f"Speaker audio file not found: {speaker_wav_path}"
                }
            
            if not text or len(text.strip()) == 0:
                return {
                    "success": False,
                    "error": "Text cannot be empty"
                }
            
            # Generate output path
            if output_filename is None:
                # Create unique filename based on text hash
                text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                output_filename = f"cloned_speech_{timestamp}_{text_hash}.wav"
            
            output_path = self.generated_speech_dir / output_filename
            
            logger.info(f"Generating speech with cloned voice...")
            logger.info(f"Text: {text[:100]}..." if len(text) > 100 else f"Text: {text}")
            logger.info(f"Reference audio: {speaker_wav_path}")
            logger.info(f"Language: {language}")
            
            # Generate speech
            start_time = datetime.utcnow()
            self.tts.tts_to_file(
                text=text,
                speaker_wav=speaker_wav_path,
                language=language,
                file_path=str(output_path)
            )
            end_time = datetime.utcnow()
            generation_time = (end_time - start_time).total_seconds()
            
            # Get audio duration
            audio, sr = librosa.load(str(output_path))
            audio_duration = len(audio) / sr
            
            logger.info(f"Generated speech saved to: {output_path}")
            logger.info(f"Generation time: {generation_time:.2f}s")
            
            return {
                "success": True,
                "output_path": str(output_path),
                "output_filename": output_filename,
                "text": text,
                "language": language,
                "audio_duration": round(audio_duration, 2),
                "generation_time": round(generation_time, 2),
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error cloning voice: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to clone voice: {str(e)}"
            }
    
    def get_supported_languages(self) -> Dict:
        """
        Get list of supported languages
        
        Returns:
            Dict: Supported languages
        """
        return {
            "success": True,
            "languages": {
                "en": "English",
                "es": "Spanish",
                "fr": "French",
                "de": "German",
                "it": "Italian",
                "pt": "Portuguese",
                "pl": "Polish",
                "tr": "Turkish",
                "ru": "Russian",
                "nl": "Dutch",
                "cs": "Czech",
                "ar": "Arabic",
                "zh-cn": "Chinese (Simplified)",
                "ja": "Japanese"
            }
        }
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model
        
        Returns:
            Dict: Model information
        """
        return {
            "success": True,
            "model_name": self.model_name,
            "device": self.device,
            "model_loaded": self.tts is not None,
            "voice_samples_dir": str(self.voice_samples_dir),
            "generated_speech_dir": str(self.generated_speech_dir)
        }


# Singleton instance
voice_cloning_service = VoiceCloningService()

