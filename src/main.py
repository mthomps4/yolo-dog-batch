import argparse
import os
import logging
from dotenv import load_dotenv
from video_processor import VideoProcessor
from s3_handler import S3Handler
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def parse_args():
    parser = argparse.ArgumentParser(description='Process video for dog detection using YOLO')
    parser.add_argument('--video_url', required=True, help='URL of the video to process')
    parser.add_argument('--callback_url', required=True, help='Callback URL for job completion notification')
    return parser.parse_args()

def main():
    try:
        # Parse command line arguments
        args = parse_args()

        # Initialize handlers
        s3_handler = S3Handler(
            bucket_name=os.getenv('S3_BUCKET'),
            aws_region=os.getenv('AWS_REGION')
        )

        video_processor = VideoProcessor()

        # Download and process video
        logger.info(f"Processing video from: {args.video_url}")
        processed_video_path = video_processor.process_video(args.video_url)

        # Upload to S3
        logger.info("Uploading processed video to S3")
        s3_url = s3_handler.upload_file(processed_video_path)

        # Send callback
        if args.callback_url:
            response = {
                'status': 'success',
                'processed_video_url': s3_url
            }
            requests.post(args.callback_url, json=response)
            logger.info(f"Callback sent to: {args.callback_url}")

        # Cleanup
        if os.path.exists(processed_video_path):
            os.remove(processed_video_path)

        logger.info("Processing completed successfully")
        print(s3_url)  # Print URL for AWS Batch job output

    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        if args.callback_url:
            error_response = {
                'status': 'error',
                'error': str(e)
            }
            requests.post(args.callback_url, json=error_response)
        raise

if __name__ == '__main__':
    main()