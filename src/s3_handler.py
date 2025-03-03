import boto3
import os
import logging
from botocore.exceptions import ClientError
from datetime import datetime

logger = logging.getLogger(__name__)

class S3Handler:
    def __init__(self, bucket_name, aws_region=None):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3', region_name=aws_region)

    def upload_file(self, file_path):
        """
        Upload a file to S3 bucket and return its URL

        Args:
            file_path (str): Path to the file to upload

        Returns:
            str: The URL of the uploaded file in S3
        """
        try:
            # Generate a unique key for the file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.basename(file_path)
            s3_key = f'processed_videos/{timestamp}_{filename}'

            # Upload the file without ACL
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                s3_key
            )

            # Generate the URL
            url = f'https://{self.bucket_name}.s3.amazonaws.com/{s3_key}'
            logger.info(f"File uploaded successfully to {url}")

            return url

        except ClientError as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            raise