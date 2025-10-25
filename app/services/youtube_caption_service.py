"""
YouTube caption extraction service
"""
import re
import yt_dlp
import json
import requests
import xml.etree.ElementTree as ET
import hashlib
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.core.logging_config import logger
from app.core.config import settings


class YouTubeCaptionService:
    """Service for extracting and processing YouTube captions"""
    
    # Simple in-memory cache (for production, use Redis)
    _cache = {}
    _cache_ttl = 3600  # 1 hour cache TTL
    
    @staticmethod
    def extract_video_info(url: str) -> Dict:
        """
        Extract video information from YouTube URL
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dictionary with video information
            
        Raises:
            Exception: If video information cannot be extracted
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            
            video_info = {
                'title': info.get('title', 'Unknown'),
                'video_id': info.get('id', ''),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown')
            }
            
            # Validate video duration
            if video_info['duration'] > settings.MAX_VIDEO_DURATION:
                raise Exception(
                    f"Video duration ({video_info['duration']}s) exceeds maximum "
                    f"allowed duration ({settings.MAX_VIDEO_DURATION}s)"
                )
            
            return video_info
            
        except Exception as e:
            logger.error(f"Failed to extract video info: {str(e)}")
            raise Exception(f"Failed to extract video information: {str(e)}")
    
    @staticmethod
    def _get_cache_key(url: str, output_format: str) -> str:
        """Generate cache key for URL and format"""
        return hashlib.md5(f"{url}:{output_format}".encode()).hexdigest()
    
    @staticmethod
    def _is_cache_valid(timestamp: float) -> bool:
        """Check if cache entry is still valid"""
        return time.time() - timestamp < YouTubeCaptionService._cache_ttl
    
    @staticmethod
    def extract_captions(url: str, output_format: str = "txt") -> Dict:
        """
        Extract captions from YouTube video
        
        Args:
            url: YouTube video URL
            output_format: Output format (txt, srt, json)
            
        Returns:
            Dictionary with extracted caption data
            
        Raises:
            Exception: If captions cannot be extracted
        """
        logger.info(f"Extracting captions from: {url}")
        
        # Check cache first
        cache_key = YouTubeCaptionService._get_cache_key(url, output_format)
        if cache_key in YouTubeCaptionService._cache:
            cached_data, timestamp = YouTubeCaptionService._cache[cache_key]
            if YouTubeCaptionService._is_cache_valid(timestamp):
                logger.info(f"Returning cached captions for: {url}")
                return cached_data
            else:
                # Remove expired cache entry
                del YouTubeCaptionService._cache[cache_key]
        
        try:
            # Get video info
            video_info = YouTubeCaptionService.extract_video_info(url)
            logger.info(f"Video: {video_info['title']} (Duration: {video_info['duration']}s)")
            
            # Configure yt-dlp for subtitle extraction with performance optimizations
            ydl_opts = {
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en'],
                'skip_download': True,
                'quiet': True,
                'no_warnings': True,
                # Performance optimizations
                'socket_timeout': 10,  # Reduce timeout
                'retries': 2,  # Reduce retries
                'fragment_retries': 2,
                'extractor_retries': 2,
                'http_chunk_size': 10485760,  # 10MB chunks
                'concurrent_fragment_downloads': 3,  # Parallel downloads
            }
            
            # Extract subtitles
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Try to get subtitles
                subtitles = info.get('subtitles', {})
                automatic_captions = info.get('automatic_captions', {})
                
                # Prefer manual subtitles over automatic
                all_subs = subtitles if subtitles else automatic_captions
                
                if not all_subs or 'en' not in all_subs:
                    raise Exception("No English captions available for this video")
                
                # Get the subtitle data
                en_subs = all_subs['en']
                
                # Find the best format (prefer vtt, then srv3, then others)
                subtitle_data = None
                file_ext = None
                
                for sub in en_subs:
                    if sub.get('ext') in ['vtt', 'srv3', 'srv1', 'json3']:
                        # Download the subtitle content with optimized settings
                        response = requests.get(
                            sub['url'], 
                            timeout=15,  # Reduced timeout
                            stream=True,
                            headers={
                                'User-Agent': 'Mozilla/5.0 (compatible; CaptionExtractor/1.0)',
                                'Accept': 'text/plain,application/json,*/*',
                                'Accept-Encoding': 'gzip, deflate',
                                'Connection': 'keep-alive'
                            }
                        )
                        response.raise_for_status()
                        subtitle_data = response.text
                        file_ext = sub.get('ext')
                        logger.info(f"Downloaded captions in {file_ext} format")
                        break
                
                if not subtitle_data:
                    raise Exception("Could not download subtitle data")
            
            # Parse the captions based on format
            if file_ext == 'vtt':
                parsed_captions = YouTubeCaptionService._parse_vtt_captions(subtitle_data)
            elif file_ext in ['srv3', 'srv1']:
                parsed_captions = YouTubeCaptionService._parse_srv_captions(subtitle_data)
            elif file_ext == 'json3':
                parsed_captions = YouTubeCaptionService._parse_json3_captions(subtitle_data)
            else:
                raise Exception(f"Unsupported subtitle format: {file_ext}")
            
            # Format output data
            output_data = {
                'video_title': video_info['title'],
                'video_id': video_info['video_id'],
                'video_duration': video_info['duration'],
                'total_captions': len(parsed_captions),
                'format': file_ext,
                'captions': parsed_captions
            }
            
            logger.info(f"Successfully extracted {len(parsed_captions)} caption segments")
            
            # Cache the result
            YouTubeCaptionService._cache[cache_key] = (output_data, time.time())
            
            return output_data
            
        except requests.RequestException as e:
            logger.error(f"Network error while downloading captions: {str(e)}")
            raise Exception(f"Failed to download captions: {str(e)}")
        except Exception as e:
            logger.error(f"Caption extraction failed: {str(e)}")
            raise
    
    @staticmethod
    def _parse_vtt_captions(vtt_content: str) -> List[Dict]:
        """
        Parse VTT format captions
        
        Args:
            vtt_content: VTT format caption content
            
        Returns:
            List of caption dictionaries
        """
        captions = []
        lines = vtt_content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for timestamp line
            if '-->' in line:
                # Parse timestamps
                parts = line.split('-->')
                if len(parts) == 2:
                    start_time = YouTubeCaptionService._vtt_time_to_seconds(parts[0].strip())
                    end_time = YouTubeCaptionService._vtt_time_to_seconds(parts[1].strip().split()[0])
                    
                    # Get caption text (next non-empty lines)
                    text_lines = []
                    i += 1
                    while i < len(lines) and lines[i].strip() and '-->' not in lines[i]:
                        text_lines.append(lines[i].strip())
                        i += 1
                    
                    text = ' '.join(text_lines)
                    
                    if text:
                        captions.append({
                            'start_time': start_time,
                            'end_time': end_time,
                            'duration': end_time - start_time,
                            'text': text
                        })
            
            i += 1
        
        logger.debug(f"Parsed {len(captions)} VTT captions")
        return captions
    
    @staticmethod
    def _parse_srv_captions(srv_content: str) -> List[Dict]:
        """
        Parse SRV format captions (XML-based)
        
        Args:
            srv_content: SRV format caption content
            
        Returns:
            List of caption dictionaries
        """
        captions = []
        try:
            root = ET.fromstring(srv_content)
            for text_elem in root.findall('.//text'):
                start_time = float(text_elem.get('start', 0))
                duration = float(text_elem.get('dur', 0))
                end_time = start_time + duration
                text = text_elem.text or ''
                
                if text:
                    captions.append({
                        'start_time': start_time,
                        'end_time': end_time,
                        'duration': duration,
                        'text': text
                    })
            
            logger.debug(f"Parsed {len(captions)} SRV captions")
            
        except ET.ParseError as e:
            logger.error(f"Error parsing XML captions: {e}")
            raise Exception(f"Failed to parse SRV captions: {str(e)}")
        
        return captions
    
    @staticmethod
    def _parse_json3_captions(json_content: str) -> List[Dict]:
        """
        Parse JSON3 format captions
        
        Args:
            json_content: JSON3 format caption content
            
        Returns:
            List of caption dictionaries
        """
        captions = []
        try:
            data = json.loads(json_content)
            events = data.get('events', [])
            
            for event in events:
                if 'segs' in event:
                    start_time = event.get('tStartMs', 0) / 1000
                    duration = event.get('dDurationMs', 0) / 1000
                    end_time = start_time + duration
                    
                    text = ''.join(seg.get('utf8', '') for seg in event['segs'])
                    
                    if text:
                        captions.append({
                            'start_time': start_time,
                            'end_time': end_time,
                            'duration': duration,
                            'text': text
                        })
            
            logger.debug(f"Parsed {len(captions)} JSON3 captions")
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON captions: {e}")
            raise Exception(f"Failed to parse JSON3 captions: {str(e)}")
        
        return captions
    
    @staticmethod
    def _vtt_time_to_seconds(time_str: str) -> float:
        """
        Convert VTT time format to seconds
        
        Args:
            time_str: Time string in VTT format
            
        Returns:
            Time in seconds
        """
        time_str = time_str.replace(',', '.')
        parts = time_str.split(':')
        
        if len(parts) == 3:
            hours, minutes, seconds = parts
            return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
        elif len(parts) == 2:
            minutes, seconds = parts
            return float(minutes) * 60 + float(seconds)
        else:
            return float(parts[0])
    
    @staticmethod
    def clean_captions(captions: List[Dict]) -> str:
        """
        Clean and deduplicate captions
        
        Args:
            captions: List of caption dictionaries
            
        Returns:
            Cleaned and deduplicated caption text
        """
        clean_sentences = []
        seen_sentences = set()
        
        for caption in captions:
            text = caption['text'].strip()
            if not text:
                continue
            
            # Remove HTML-like tags and timestamps
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'\[\d+\.\d+s\s*-\s*\d+\.\d+s\]', '', text)
            text = re.sub(r'<00:\d+:\d+\.\d+>', '', text)
            text = re.sub(r'<c>', '', text)
            text = re.sub(r'</c>', '', text)
            
            # Clean up the text
            text = re.sub(r'\s+', ' ', text).strip()
            
            if text and len(text) > 10:  # Only keep substantial sentences
                # Remove duplicates
                if text not in seen_sentences:
                    clean_sentences.append(text)
                    seen_sentences.add(text)
        
        # Join all sentences into one continuous text
        final_text = ' '.join(clean_sentences)
        
        logger.debug(f"Cleaned text length: {len(final_text)} characters")
        
        return final_text