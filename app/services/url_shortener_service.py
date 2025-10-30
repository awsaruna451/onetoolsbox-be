"""
URL Shortener Service

This module provides URL shortening functionality with multiple generation methods.
"""

import hashlib
import string
import random
import json
import os
from typing import Dict, Optional
from datetime import datetime

from app.core.config import settings
from app.core.logging_config import logger


class URLShortenerService:
    """Service for URL shortening operations"""
    
    def __init__(self, storage_file: str = 'data/url_mappings.json'):
        """
        Initialize URL Shortener with local storage
        
        Args:
            storage_file (str): File to store URL mappings
        """
        self.storage_file = storage_file
        self.url_map = self.load_mappings()
        self.base_url = settings.BASE_URL
        self.short_length = 6
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
        
    def load_mappings(self) -> Dict:
        """Load URL mappings from file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data)} URL mappings from storage")
                    return data
            except Exception as e:
                logger.error(f"Error loading mappings: {str(e)}")
                return {}
        return {}
    
    def save_mappings(self) -> None:
        """Save URL mappings to file"""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.url_map, f, indent=2)
            logger.info(f"Saved {len(self.url_map)} URL mappings to storage")
        except Exception as e:
            logger.error(f"Error saving mappings: {str(e)}")
            raise
    
    def generate_short_code_hash(self, long_url: str) -> str:
        """
        Generate short code using hash of the URL
        This ensures same URL always gets same short code
        
        Args:
            long_url (str): The URL to hash
            
        Returns:
            str: Short code
        """
        hash_object = hashlib.md5(long_url.encode())
        hash_hex = hash_object.hexdigest()
        return hash_hex[:self.short_length]
    
    def generate_short_code_random(self) -> str:
        """
        Generate random short code
        
        Returns:
            str: Random short code
        """
        characters = string.ascii_letters + string.digits
        max_attempts = 100
        attempts = 0
        
        while attempts < max_attempts:
            short_code = ''.join(random.choices(characters, k=self.short_length))
            if short_code not in self.url_map:
                return short_code
            attempts += 1
        
        raise Exception("Unable to generate unique short code")
    
    def validate_url(self, url: str) -> bool:
        """
        Validate URL format
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if valid
        """
        return url.startswith(('http://', 'https://'))
    
    def normalize_custom_domain(self, custom_domain: str) -> str:
        """
        Normalize custom domain to proper format
        
        Args:
            custom_domain (str): Custom domain to normalize
            
        Returns:
            str: Normalized domain with /s/ path
        """
        # Remove trailing slash
        domain = custom_domain.rstrip('/')
        
        # Ensure it starts with http:// or https://
        if not domain.startswith(('http://', 'https://')):
            domain = 'https://' + domain
        
        # Add /s/ path if not present
        if not domain.endswith('/s'):
            domain = domain + '/s/'
        else:
            domain = domain + '/'
            
        return domain
    
    def shorten_url(
        self, 
        long_url: str, 
        method: str = 'hash', 
        custom_code: Optional[str] = None,
        custom_domain: Optional[str] = None
    ) -> Dict:
        """
        Shorten a URL
        
        Args:
            long_url (str): The URL to shorten
            method (str): 'hash' or 'random' for code generation
            custom_code (str): Optional custom short code
            custom_domain (str): Optional custom domain for the shortened URL
            
        Returns:
            Dict: Result with shortened URL and metadata
        """
        try:
            # Validate URL
            if not self.validate_url(long_url):
                return {
                    "success": False,
                    "error": "Invalid URL format. URL must start with http:// or https://"
                }
            
            # Determine the base URL to use
            base_url_to_use = self.base_url
            if custom_domain:
                try:
                    base_url_to_use = self.normalize_custom_domain(custom_domain)
                    logger.info(f"Using custom domain: {base_url_to_use}")
                except Exception as e:
                    logger.warning(f"Failed to normalize custom domain '{custom_domain}': {str(e)}")
                    return {
                        "success": False,
                        "error": f"Invalid custom domain format: {str(e)}"
                    }
            
            # Check if URL already exists
            for code, data in self.url_map.items():
                url = data if isinstance(data, str) else data.get('url')
                if url == long_url:
                    logger.info(f"URL already exists with code: {code}")
                    return {
                        "success": True,
                        "short_url": base_url_to_use + code,
                        "short_code": code,
                        "long_url": long_url,
                        "method": "existing",
                        "custom_domain": custom_domain,
                        "message": "URL was already shortened"
                    }
            
            # Generate short code
            if custom_code:
                if custom_code in self.url_map:
                    return {
                        "success": False,
                        "error": f"Custom code '{custom_code}' already exists"
                    }
                if len(custom_code) < 3 or len(custom_code) > 20:
                    return {
                        "success": False,
                        "error": "Custom code must be between 3 and 20 characters"
                    }
                short_code = custom_code
            elif method == 'hash':
                short_code = self.generate_short_code_hash(long_url)
                # Handle collision for hash method
                if short_code in self.url_map:
                    existing_url = self.url_map[short_code]
                    existing_url_str = existing_url if isinstance(existing_url, str) else existing_url.get('url')
                    if existing_url_str != long_url:
                        # Hash collision - use random method instead
                        logger.warning(f"Hash collision for code {short_code}, using random method")
                        short_code = self.generate_short_code_random()
            else:
                short_code = self.generate_short_code_random()
            
            # Store mapping with metadata
            self.url_map[short_code] = {
                'url': long_url,
                'created_at': datetime.utcnow().isoformat(),
                'method': custom_code and 'custom' or method,
                'clicks': 0
            }
            self.save_mappings()
            
            logger.info(f"Created short URL: {short_code} -> {long_url}" + 
                       (f" with custom domain: {custom_domain}" if custom_domain else ""))
            
            return {
                "success": True,
                "short_url": base_url_to_use + short_code,
                "short_code": short_code,
                "long_url": long_url,
                "method": custom_code and 'custom' or method,
                "custom_domain": custom_domain,
                "created_at": self.url_map[short_code]['created_at']
            }
            
        except Exception as e:
            logger.error(f"Error shortening URL: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to shorten URL: {str(e)}"
            }
    
    def expand_url(self, short_code: str) -> Dict:
        """
        Get original URL from short code
        
        Args:
            short_code (str): The short code
            
        Returns:
            Dict: Result with original URL
        """
        try:
            if short_code in self.url_map:
                data = self.url_map[short_code]
                
                # Handle both old format (string) and new format (dict)
                if isinstance(data, str):
                    long_url = data
                    created_at = None
                    clicks = 0
                else:
                    long_url = data.get('url')
                    created_at = data.get('created_at')
                    clicks = data.get('clicks', 0)
                    
                    # Increment click counter
                    data['clicks'] = clicks + 1
                    self.save_mappings()
                
                logger.info(f"Expanded short code: {short_code} -> {long_url}")
                
                return {
                    "success": True,
                    "long_url": long_url,
                    "short_code": short_code,
                    "created_at": created_at,
                    "clicks": clicks + 1
                }
            else:
                return {
                    "success": False,
                    "error": "Short code not found"
                }
                
        except Exception as e:
            logger.error(f"Error expanding URL: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to expand URL: {str(e)}"
            }
    
    def get_all_mappings(self) -> Dict:
        """
        Get all URL mappings
        
        Returns:
            Dict: All mappings
        """
        try:
            mappings = []
            for code, data in self.url_map.items():
                if isinstance(data, str):
                    mappings.append({
                        "short_code": code,
                        "long_url": data,
                        "short_url": self.base_url + code
                    })
                else:
                    mappings.append({
                        "short_code": code,
                        "long_url": data.get('url'),
                        "short_url": self.base_url + code,
                        "created_at": data.get('created_at'),
                        "method": data.get('method'),
                        "clicks": data.get('clicks', 0)
                    })
            
            return {
                "success": True,
                "total": len(mappings),
                "mappings": mappings
            }
            
        except Exception as e:
            logger.error(f"Error getting mappings: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get mappings: {str(e)}"
            }
    
    def delete_mapping(self, short_code: str) -> Dict:
        """
        Delete a URL mapping
        
        Args:
            short_code (str): The short code to delete
            
        Returns:
            Dict: Result
        """
        try:
            if short_code in self.url_map:
                del self.url_map[short_code]
                self.save_mappings()
                logger.info(f"Deleted short code: {short_code}")
                return {
                    "success": True,
                    "message": f"Short code '{short_code}' deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Short code not found"
                }
                
        except Exception as e:
            logger.error(f"Error deleting mapping: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to delete mapping: {str(e)}"
            }
    
    def get_stats(self) -> Dict:
        """
        Get statistics
        
        Returns:
            Dict: Statistics
        """
        try:
            total_clicks = 0
            for data in self.url_map.values():
                if isinstance(data, dict):
                    total_clicks += data.get('clicks', 0)
            
            return {
                "success": True,
                "total_urls": len(self.url_map),
                "total_clicks": total_clicks,
                "storage_file": self.storage_file,
                "base_url": self.base_url
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get stats: {str(e)}"
            }


# Singleton instance
url_shortener_service = URLShortenerService()

