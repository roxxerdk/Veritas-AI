import os
import shutil
import logging
from typing import BinaryIO
from app.config.settings import settings

logger = logging.getLogger("veritas-ai.storage")

class StorageService:
    def __init__(self):
        self.bucket = settings.AWS_S3_BUCKET
        self.use_s3 = bool(self.bucket and settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY)
        
        if self.use_s3:
            try:
                import boto3
                self.s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION
                )
                logger.info(f"S3 Storage service initialized. Target Bucket: {self.bucket}")
            except Exception as e:
                logger.error(f"Failed to initialize S3 storage client (falling back to local): {str(e)}")
                self.use_s3 = False
                self.setup_local_storage()
        else:
            self.setup_local_storage()

    def setup_local_storage(self):
        self.local_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "uploads"))
        os.makedirs(self.local_dir, exist_ok=True)
        logger.info(f"Local disk storage initialized at: {self.local_dir}")

    def save_file(self, file_content: bytes, destination_name: str) -> str:
        """Saves a file to local storage or S3 bucket, returning the target path/URI."""
        if self.use_s3:
            try:
                self.s3_client.put_object(
                    Bucket=self.bucket,
                    Key=destination_name,
                    Body=file_content
                )
                s3_uri = f"s3://{self.bucket}/{destination_name}"
                logger.info(f"File uploaded successfully to S3: {s3_uri}")
                return s3_uri
            except Exception as e:
                logger.error(f"S3 upload failed: {str(e)}. Falling back to local disk storage.")
                self.setup_local_storage()

        # Local disk fallback
        local_path = os.path.join(self.local_dir, destination_name)
        with open(local_path, "wb") as f:
            f.write(file_content)
        logger.info(f"File saved successfully to local storage: {local_path}")
        return local_path

    def delete_file(self, storage_path: str):
        """Deletes a file from either S3 bucket or local disk."""
        if storage_path.startswith("s3://") and self.use_s3:
            try:
                key = storage_path.replace(f"s3://{self.bucket}/", "")
                self.s3_client.delete_object(Bucket=self.bucket, Key=key)
                logger.info(f"File deleted successfully from S3: {storage_path}")
                return
            except Exception as e:
                logger.error(f"Failed to delete file from S3: {str(e)}")
                return

        # Local file deletion
        if os.path.exists(storage_path):
            try:
                os.remove(storage_path)
                logger.info(f"File deleted successfully from local storage: {storage_path}")
            except Exception as e:
                logger.error(f"Failed to delete local file: {str(e)}")
