import logging
import uuid
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from app.core.s3_config import s3_settings

# Set up logging
logger = logging.getLogger("s3_service")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class S3Service:
    """Service for handling AWS S3 operations"""

    def __init__(self):
        self.aws_access_key_id = s3_settings.aws_access_key_id
        self.aws_secret_access_key = s3_settings.aws_secret_access_key
        self.region_name = s3_settings.region_name
        self.bucket_name = s3_settings.bucket_name
        self.presigned_url_expiration = s3_settings.presigned_url_expiration
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name
        )
        
    async def upload_file(self, file: UploadFile, folder: str = "products") -> Tuple[bool, str, Optional[str]]:
        """Upload a file to S3
        
        Args:
            file: The file to upload
            folder: The folder in the S3 bucket to upload to
            
        Returns:
            Tuple containing:
            - success: Boolean indicating if upload was successful
            - message: Message describing the result
            - file_url: URL of the uploaded file if successful, None otherwise
        """
        try:
            # Generate a unique filename
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}" if file_extension else f"{uuid.uuid4().hex}"
            s3_path = f"{folder}/{unique_filename}"
            
            # Read file content
            file_content = await file.read()
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_path,
                Body=file_content,
                ContentType=file.content_type
            )
            
            # Generate URL
            file_url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{s3_path}"
            
            logger.info(f"Successfully uploaded file to {file_url}")
            return True, "File uploaded successfully", file_url
            
        except Exception as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            return False, f"Error uploading file: {str(e)}", None
            
    def generate_presigned_url(self, object_key: str) -> Optional[str]:
        """Generate a presigned URL for an S3 object
        
        Args:
            object_key: The key of the object in S3
            
        Returns:
            Presigned URL if successful, None otherwise
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key
                },
                ExpiresIn=self.presigned_url_expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            return None
            
    def delete_file(self, object_key: str) -> Tuple[bool, str]:
        """Delete a file from S3
        
        Args:
            object_key: The key of the object in S3
            
        Returns:
            Tuple containing:
            - success: Boolean indicating if deletion was successful
            - message: Message describing the result
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            logger.info(f"Successfully deleted file {object_key} from S3")
            return True, "File deleted successfully"
        except ClientError as e:
            logger.error(f"Error deleting file from S3: {str(e)}")
            return False, f"Error deleting file: {str(e)}"
            
    def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """List files in the S3 bucket
        
        Args:
            prefix: The prefix to filter files by
            
        Returns:
            List of file information dictionaries
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            files = []
            if 'Contents' in response:
                for item in response['Contents']:
                    files.append({
                        'key': item['Key'],
                        'size': item['Size'],
                        'last_modified': item['LastModified'].isoformat(),
                        'url': f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{item['Key']}"
                    })
            
            return files
        except ClientError as e:
            logger.error(f"Error listing files in S3: {str(e)}")
            return []


# Create a singleton instance
s3_service = S3Service()
