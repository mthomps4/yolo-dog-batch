# YOLO Dog Detection with AWS Batch

This project processes videos to detect dogs using the YOLO (You Only Look Once) model and AWS Batch. It takes a video input, processes it to detect dogs, and uploads the processed video to S3.

## Features

- Video processing using YOLOv5 for dog detection
- AWS Batch integration for scalable processing
- S3 storage for processed videos
- Webhook callback support
- Support for both local video files and URLs

## Prerequisites

- Python 3.8+
- AWS Account with access to:
  - AWS Batch
  - S3
  - ECR (Elastic Container Registry)
- Docker
- Docker Compose

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure AWS credentials:

```bash
aws configure
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your actual values
```

5. Add your video files:

```bash
# Place your video files in the videos directory
cp your-video.mp4 videos/
```

## Project Structure

```
YoloBatch/
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── README.md
├── requirements.txt
├── videos/           # Directory for local video files
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── video_processor.py
│   ├── s3_handler.py
│   └── yolo_detector.py
└── tests/
    └── __init__.py
```

## Environment Variables

Required AWS credentials and configuration:

- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_REGION`: AWS region
- `S3_BUCKET`: Target S3 bucket for processed videos

## Usage

### Local Development with Docker Compose

1. Set up your environment variables:

```bash
cp .env.example .env
# Edit .env with your actual values
```

2. Add your video files to the videos directory:

```bash
cp your-video.mp4 videos/
```

3. Run with docker-compose:

```bash
docker-compose up
```

You can process videos in two ways:

1. Local video file (recommended for development):

```bash
# Using a video from the videos directory
VIDEO_URL=videos/your-video.mp4 docker-compose up
```

2. Remote video URL:

```bash
# Using a video from the internet
VIDEO_URL=https://example.com/my-video.mp4 docker-compose up
```

### AWS Batch Deployment

1. Build the Docker image:
Note: platform required in both the Dockerfile and build command when running from an Apple Silicon or similar.

```bash
docker build --platform linux/amd64 -t yolo-dog-detector .
```

2. Push to ECR:

```bash
aws ecr get-login-password --region YOUR_REGION | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com
docker tag yolo-dog-detector:latest YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/yolo-dog-detector:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/yolo-dog-detector:latest
```

3. Submit job to AWS Batch:

```bash
aws batch submit-job \
    --job-name dog-detection-job \
    --job-queue YoloDogDetectionGPUQueue \
    --job-definition yolo-dog-detection-gpu-job \
    --container-overrides '{"command": ["python", "src/main.py", "--video_url", "YOUR_VIDEO_URL", "--callback_url", "YOUR_CALLBACK_URL"]}'
```

### Manual Docker Run

If you need to run the container directly:

```bash
docker run -e AWS_ACCESS_KEY_ID=your_key \
          -e AWS_SECRET_ACCESS_KEY=your_secret \
          -e AWS_REGION=your_region \
          -e S3_BUCKET=your_bucket \
          -v $(pwd)/videos:/app/videos \
          yolo-dog-detector \
          --video_url="videos/your-video.mp4" \
          --callback_url="https://your-callback-url"
```

## License

MIT

### Notes for usage

`CMD for Job Definition`
["python3","src/main.py","--video_url","Ref::video_url","--callback_url","Ref::callback_url"]

aws batch submit-job \
    --job-name test-dog-detection \
    --job-queue YoloDogDetectionGPUQueue \
    --job-definition yolo-dog-detection-gpu-job \
    --parameters video_url="SIGNED_AWS_URL or PUBLIC HOSTED LINK",callback_url="<https://d31e23cab59b.ngrok.app>"
