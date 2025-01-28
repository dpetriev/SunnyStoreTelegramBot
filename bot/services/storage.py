import logging
from functools import wraps
from typing import Any, Callable
import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from bot.config import (
    AWS_ACCESS_KEY,
    AWS_SECRET_KEY,
    AWS_REGION,
    S3_BUCKET_NAME,
    AWS_TIMEOUT,
    AWS_MAX_RETRIES
)

logger = logging.getLogger(__name__)

def with_s3_retry(max_retries: int = AWS_MAX_RETRIES) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (BotoCoreError, ClientError) as e:
                    last_error = e
                    logger.warning(f"S3 operation failed (attempt {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        continue
            raise last_error
        return wrapper
    return decorator

class StorageService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StorageService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        try:
            config = Config(
                region_name=AWS_REGION,
                connect_timeout=AWS_TIMEOUT,
                read_timeout=AWS_TIMEOUT,
                retries={'max_attempts': AWS_MAX_RETRIES}
            )
            
            self.s3 = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_KEY,
                config=config
            )
            self.bucket_name = S3_BUCKET_NAME
            
            # Test connection by listing buckets
            self.s3.list_buckets()
            logger.info("Successfully connected to AWS S3")
        except Exception as e:
            logger.error(f"Failed to initialize S3 connection: {e}")
            raise

    @with_s3_retry()
    def upload_file(self, file_path, file_key):
        try:
            self.s3.upload_file(file_path, self.bucket_name, file_key)
            logger.info(f"Successfully uploaded file {file_key}")
        except Exception as e:
            logger.error(f"Error uploading file {file_key}: {e}")
            raise

    @with_s3_retry()
    def get_file(self, file_key):
        try:
            return self.s3.get_object(Bucket=self.bucket_name, Key=file_key)
        except Exception as e:
            logger.error(f"Error getting file {file_key}: {e}")
            raise

    @with_s3_retry()
    def delete_file(self, file_key):
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=file_key)
            logger.info(f"Successfully deleted file {file_key}")
        except Exception as e:
            logger.error(f"Error deleting file {file_key}: {e}")
            raise