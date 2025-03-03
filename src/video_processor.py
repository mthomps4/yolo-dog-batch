import cv2
import numpy as np
import os
import tempfile
import logging
from ultralytics import YOLO
import requests
from tqdm import tqdm
import torch
import shutil
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        # Log CUDA availability
        cuda_available = torch.cuda.is_available()
        device = 'cuda' if cuda_available else 'cpu'
        logger.info(f"Using device: {device}")
        if cuda_available:
            logger.info(f"CUDA Device: {torch.cuda.get_device_name(0)}")

        self.model = YOLO('yolov8n.pt')

    def download_video(self, video_path):
        """
        Get video from URL or local path.

        Args:
            video_path (str): URL or local path to video file

        Returns:
            str: Path to local video file
        """
        # Check if it's a URL or local path
        parsed = urlparse(video_path)
        if parsed.scheme in ('http', 'https'):
            # It's a URL, download it
            temp_path = os.path.join(tempfile.gettempdir(), 'input_video.mp4')

            response = requests.get(video_path, stream=True)
            total_size = int(response.headers.get('content-length', 0))

            with open(temp_path, 'wb') as file, tqdm(
                desc='Downloading video',
                total=total_size,
                unit='iB',
                unit_scale=True
            ) as pbar:
                for data in response.iter_content(chunk_size=1024):
                    size = file.write(data)
                    pbar.update(size)

            return temp_path
        else:
            # It's a local path, check if it exists relative to the current directory
            local_path = os.path.join(os.getcwd(), video_path)
            if not os.path.exists(local_path):
                raise ValueError(f"Video file not found at {local_path}")

            # Copy to temp directory to maintain consistent behavior
            temp_path = os.path.join(tempfile.gettempdir(), 'input_video.mp4')
            shutil.copy2(local_path, temp_path)
            return temp_path

    def process_video(self, video_path):
        """Process video with YOLO to detect dogs."""
        # Get video (from URL or local path)
        input_path = self.download_video(video_path)
        output_path = os.path.join(tempfile.gettempdir(), 'processed_video.mp4')

        # Open video
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise ValueError("Could not open video file")

        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        try:
            # Process each frame
            with tqdm(total=total_frames, desc="Processing frames") as pbar:
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    # Run YOLO detection
                    results = self.model(frame)

                    # Filter for dog class (class 16 in COCO dataset)
                    for result in results:
                        boxes = result.boxes
                        for box in boxes:
                            # Check if detection is a dog
                            if int(box.cls) == 16:  # Dog class
                                # Draw bounding box
                                x1, y1, x2, y2 = map(int, box.xyxy[0])
                                conf = float(box.conf[0])

                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                cv2.putText(frame, f'Dog: {conf:.2f}',
                                          (x1, y1 - 10),
                                          cv2.FONT_HERSHEY_SIMPLEX,
                                          0.9, (0, 255, 0), 2)

                    # Write the frame
                    out.write(frame)
                    pbar.update(1)

        finally:
            # Release resources
            cap.release()
            out.release()

            # Clean up input file
            if os.path.exists(input_path):
                os.remove(input_path)

        return output_path