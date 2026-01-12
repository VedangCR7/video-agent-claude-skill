"""
File utility functions for FAL Image-to-Video.
"""

import os
import time
import requests
import fal_client
from pathlib import Path
from typing import Optional


def ensure_output_directory(output_dir: Optional[str] = None) -> Path:
    """
    Ensure output directory exists.

    Args:
        output_dir: Custom output directory path

    Returns:
        Path object for the output directory
    """
    if output_dir is None:
        output_dir = "output"

    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def download_video(
    video_url: str,
    output_dir: Path,
    model_key: str,
    filename: Optional[str] = None
) -> Optional[str]:
    """
    Download video from URL to local folder.

    Args:
        video_url: URL of the video to download
        output_dir: Output directory path
        model_key: Model identifier for filename
        filename: Optional custom filename

    Returns:
        Local path of the downloaded video or None if failed
    """
    try:
        if filename is None:
            timestamp = int(time.time())
            filename = f"{model_key}_video_{timestamp}.mp4"

        print(f"📥 Downloading video...")
        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        local_path = output_dir / filename
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        absolute_path = str(local_path.absolute())
        print(f"✅ Video saved: {absolute_path}")
        return absolute_path

    except Exception as e:
        print(f"❌ Error downloading video: {e}")
        return None


def upload_image(image_path: str) -> Optional[str]:
    """
    Upload a local image file to FAL AI.

    Args:
        image_path: Path to the local image file

    Returns:
        URL of the uploaded image or None if failed
    """
    try:
        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            return None

        print(f"📤 Uploading image: {image_path}")
        url = fal_client.upload_file(image_path)
        print(f"✅ Image uploaded: {url[:50]}...")
        return url

    except Exception as e:
        print(f"❌ Error uploading image: {e}")
        return None
