"""
Helper utility functions
"""
from typing import Optional
import re
from urllib.parse import urlparse, parse_qs


def extract_video_id_from_url(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from various URL formats
    
    Args:
        url: YouTube URL
        
    Returns:
        Video ID or None if not found
        
    Examples:
        >>> extract_video_id_from_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_video_id_from_url("https://youtu.be/dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
    """
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # Try parsing as URL
    try:
        parsed_url = urlparse(url)
        if parsed_url.hostname in ['youtu.be']:
            return parsed_url.path[1:]
        elif parsed_url.hostname in ['www.youtube.com', 'youtube.com', 'm.youtube.com']:
            if parsed_url.path == '/watch':
                query_params = parse_qs(parsed_url.query)
                return query_params.get('v', [None])[0]
            elif parsed_url.path.startswith('/embed/'):
                return parsed_url.path.split('/')[2]
    except Exception:
        pass
    
    return None


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
        
    Examples:
        >>> format_duration(125)
        '2m 5s'
        >>> format_duration(3665)
        '1h 1m 5s'
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return ' '.join(parts)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid filename characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = re.sub(r'\s+', '_', filename)
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename or "untitled"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

