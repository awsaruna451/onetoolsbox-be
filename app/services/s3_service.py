"""
AWS S3 Service

This module provides AWS S3 file upload and download functionality.
"""

import os
import uuid
import time
from pathlib import Path
from typing import Dict, Optional, BinaryIO
from datetime import datetime
import mimetypes

from app.core.config import settings
from app.core.logging_config import logger

# Optional AWS S3 dependencies
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    S3_AVAILABLE = True
except ImportError:
    logger.warning("AWS S3 dependencies not installed")
    logger.warning("Install with: pip install boto3")
    S3_AVAILABLE = False
    boto3 = None


class S3Service:
    """Service for AWS S3 file operations"""
    
    def __init__(self):
        """Initialize S3 service"""
        self.available = S3_AVAILABLE
        self.s3_client = None
        self.bucket_name = settings.AWS_S3_BUCKET_NAME if hasattr(settings, 'AWS_S3_BUCKET_NAME') else None
        
        if not S3_AVAILABLE:
            logger.warning("S3 service not available - boto3 not installed")
            return
        
        if not self.bucket_name:
            logger.warning("AWS_S3_BUCKET_NAME not configured in settings")
            return
        
        # Initialize S3 client with optimized config for speed
        try:
            from botocore.config import Config
            
            # Optimize boto3 config for maximum speed
            boto_config = Config(
                max_pool_connections=50,  # Increase connection pool
                retries={'max_attempts': 2, 'mode': 'standard'},  # Reduce retries
                connect_timeout=5,  # Fast connection timeout
                read_timeout=30,  # Reasonable read timeout
                tcp_keepalive=True  # Keep connections alive
            )
            
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
                aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
                region_name=getattr(settings, 'AWS_REGION', 'us-east-1'),
                config=boto_config
            )
            logger.info(f"S3 service initialized with bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {str(e)}")
            self.available = False
    
    def upload_file(
        self, 
        file_path: str, 
        s3_key: Optional[str] = None,
        folder: str = "voice_samples"
    ) -> Dict:
        """
        Upload a file to S3 (Optimized for speed)
        
        Args:
            file_path (str): Local file path to upload
            s3_key (str): Optional S3 key (path in bucket)
            folder (str): Folder in S3 bucket
            
        Returns:
            Dict: Result with S3 URL and metadata
        """
        if not self.available:
            return {
                "success": False,
                "error": "S3 service not available"
            }
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        try:
            # Generate unique S3 key if not provided
            if s3_key is None:
                file_extension = Path(file_path).suffix
                file_base = Path(file_path).stem
                timestamp_ms = int(time.time() * 1000)
                unique_id = str(uuid.uuid4())[:8]
                s3_key = f"{folder}/{timestamp_ms}_{unique_id}_{file_base}{file_extension}"
            
            # Detect content type
            content_type, _ = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = 'application/octet-stream'
            
            # Ultra-fast transfer config
            from boto3.s3.transfer import TransferConfig
            
            config = TransferConfig(
                multipart_threshold=1024 * 1024 * 5,
                max_concurrency=20,
                multipart_chunksize=1024 * 1024 * 5,
                use_threads=True,
                max_io_queue=1000
            )
            
            logger.info(f"Uploading: {Path(file_path).name}")
            
            # Fast upload
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': content_type},
                Config=config
            )
            
            # Generate S3 URL
            s3_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            file_size = os.path.getsize(file_path)
            
            logger.info(f"Upload complete: {s3_url}")
            
            return {
                "success": True,
                "s3_url": s3_url,
                "s3_key": s3_key,
                "bucket": self.bucket_name,
                "file_size": file_size,
                "content_type": content_type,
                "uploaded_at": datetime.utcnow().isoformat()
            }
            
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            return {
                "success": False,
                "error": "AWS credentials not configured"
            }
        except ClientError as e:
            logger.error(f"AWS S3 error: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to upload to S3: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to upload file: {str(e)}"
            }
    
    def upload_file_object(
        self,
        file_obj: BinaryIO,
        filename: str,
        folder: str = "voice_samples"
    ) -> Dict:
        """
        Upload a file object to S3 (Optimized for speed)
        
        Args:
            file_obj: File-like object
            filename: Original filename
            folder: Folder in S3 bucket
            
        Returns:
            Dict: Result with S3 URL and metadata
        """
        if not self.available:
            return {
                "success": False,
                "error": "S3 service not available"
            }
        
        try:
            # Generate unique S3 key
            file_extension = Path(filename).suffix
            file_base = Path(filename).stem
            timestamp_ms = int(time.time() * 1000)
            unique_id = str(uuid.uuid4())[:8]
            s3_key = f"{folder}/{timestamp_ms}_{unique_id}_{file_base}{file_extension}"
            
            # Detect content type (fast operation)
            content_type, _ = mimetypes.guess_type(filename)
            if content_type is None:
                content_type = 'application/octet-stream'
            
            # Ultra-fast upload configuration
            from boto3.s3.transfer import TransferConfig
            
            # Aggressive optimization for speed
            config = TransferConfig(
                multipart_threshold=1024 * 1024 * 5,  # 5 MB (lower = faster start)
                max_concurrency=20,  # More parallel threads
                multipart_chunksize=1024 * 1024 * 5,  # 5 MB chunks
                use_threads=True,
                max_io_queue=1000  # Larger queue
            )
            
            logger.info(f"Uploading: {filename}")
            
            # Upload with minimal overhead
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': content_type},
                Config=config
            )
            
            # Generate S3 URL
            s3_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            
            logger.info(f"Upload complete: {s3_url}")
            
            return {
                "success": True,
                "s3_url": s3_url,
                "s3_key": s3_key,
                "bucket": self.bucket_name,
                "content_type": content_type,
                "uploaded_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error uploading: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to upload file: {str(e)}"
            }
    
    def download_file(self, s3_key: str, local_path: str) -> Dict:
        """
        Download a file from S3
        
        Args:
            s3_key (str): S3 key (path in bucket)
            local_path (str): Local path to save file
            
        Returns:
            Dict: Result with local file path
        """
        if not self.available:
            return {
                "success": False,
                "error": "S3 service not available"
            }
        
        try:
            logger.info(f"Downloading file from S3: s3://{self.bucket_name}/{s3_key} -> {local_path}")
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Download file
            self.s3_client.download_file(
                self.bucket_name,
                s3_key,
                local_path
            )
            
            logger.info(f"File downloaded successfully to: {local_path}")
            
            return {
                "success": True,
                "local_path": local_path,
                "s3_key": s3_key
            }
            
        except ClientError as e:
            logger.error(f"AWS S3 error: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to download from S3: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to download file: {str(e)}"
            }
    
    def delete_file(self, s3_key: str) -> Dict:
        """
        Delete a file from S3
        
        Args:
            s3_key (str): S3 key (path in bucket)
            
        Returns:
            Dict: Result
        """
        if not self.available:
            return {
                "success": False,
                "error": "S3 service not available"
            }
        
        try:
            logger.info(f"Deleting file from S3: s3://{self.bucket_name}/{s3_key}")
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            logger.info(f"File deleted successfully: {s3_key}")
            
            return {
                "success": True,
                "message": f"File deleted: {s3_key}"
            }
            
        except ClientError as e:
            logger.error(f"AWS S3 error: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to delete from S3: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to delete file: {str(e)}"
            }
    
    def generate_presigned_url(
        self, 
        s3_key: str, 
        expiration: int = 3600
    ) -> Dict:
        """
        Generate a presigned URL for temporary access
        
        Args:
            s3_key (str): S3 key (path in bucket)
            expiration (int): URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Dict: Result with presigned URL
        """
        if not self.available:
            return {
                "success": False,
                "error": "S3 service not available"
            }
        
        try:
            logger.info(f"Generating presigned URL for: s3://{self.bucket_name}/{s3_key}")
            
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            
            logger.info(f"Presigned URL generated (expires in {expiration}s)")
            
            return {
                "success": True,
                "presigned_url": url,
                "expires_in": expiration
            }
            
        except ClientError as e:
            logger.error(f"AWS S3 error: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate presigned URL: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate URL: {str(e)}"
            }
    
    def list_files(self, folder: str = "voice_samples") -> Dict:
        """
        List files in S3 bucket folder
        
        Args:
            folder (str): Folder in S3 bucket
            
        Returns:
            Dict: Result with list of files
        """
        if not self.available:
            return {
                "success": False,
                "error": "S3 service not available"
            }
        
        try:
            logger.info(f"Listing files in s3://{self.bucket_name}/{folder}")
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=folder
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        "key": obj['Key'],
                        "size": obj['Size'],
                        "last_modified": obj['LastModified'].isoformat(),
                        "url": f"https://{self.bucket_name}.s3.amazonaws.com/{obj['Key']}"
                    })
            
            logger.info(f"Found {len(files)} files")
            
            return {
                "success": True,
                "files": files,
                "count": len(files)
            }
            
        except ClientError as e:
            logger.error(f"AWS S3 error: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to list files: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to list files: {str(e)}"
            }


# Singleton instance
s3_service = S3Service()

