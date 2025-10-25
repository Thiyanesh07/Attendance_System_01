"""
Video capture and processing service
"""

import cv2
import numpy as np
from typing import List, Generator, Optional
import base64
from io import BytesIO
from PIL import Image


class VideoCapture:
    """
    Video capture service for camera streams
    """
    
    def __init__(self, source: str, fps: int = 30):
        """
        Initialize video capture
        
        Args:
            source: Video source (camera index, IP address, or file path)
            fps: Frames per second to capture
        """
        self.source = source
        self.fps = fps
        self.cap = None
        self.is_opened = False
    
    def open(self) -> bool:
        """Open video capture"""
        try:
            # Try to parse as integer (camera index)
            try:
                source_int = int(self.source)
                self.cap = cv2.VideoCapture(source_int)
            except ValueError:
                # Use as string (IP address or file path)
                self.cap = cv2.VideoCapture(self.source)
            
            if self.cap.isOpened():
                self.is_opened = True
                # Set FPS
                self.cap.set(cv2.CAP_PROP_FPS, self.fps)
                return True
            return False
        except Exception as e:
            print(f"Error opening video source {self.source}: {e}")
            return False
    
    def close(self):
        """Close video capture"""
        if self.cap is not None:
            self.cap.release()
            self.is_opened = False
    
    def read(self) -> Optional[np.ndarray]:
        """
        Read a single frame
        
        Returns:
            Frame as numpy array or None if failed
        """
        if not self.is_opened:
            return None
        
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
    
    def read_frames(self, num_frames: int) -> List[np.ndarray]:
        """
        Read multiple frames
        
        Args:
            num_frames: Number of frames to read
            
        Returns:
            List of frames
        """
        frames = []
        for _ in range(num_frames):
            frame = self.read()
            if frame is not None:
                frames.append(frame)
        return frames
    
    def stream_frames(self) -> Generator[np.ndarray, None, None]:
        """
        Stream frames as generator
        
        Yields:
            Video frames
        """
        while self.is_opened:
            frame = self.read()
            if frame is not None:
                yield frame
            else:
                break
    
    def get_frame_count(self) -> int:
        """Get total frame count (for video files)"""
        if self.cap is not None:
            return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return 0
    
    def get_fps(self) -> float:
        """Get actual FPS"""
        if self.cap is not None:
            return self.cap.get(cv2.CAP_PROP_FPS)
        return 0.0
    
    def __enter__(self):
        """Context manager entry"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


def frame_to_base64(frame: np.ndarray, format: str = 'JPEG') -> str:
    """
    Convert frame to base64 string
    
    Args:
        frame: Image frame (BGR)
        format: Image format (JPEG, PNG)
        
    Returns:
        Base64 encoded string
    """
    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Convert to PIL Image
    pil_img = Image.fromarray(rgb_frame)
    
    # Save to bytes buffer
    buffer = BytesIO()
    pil_img.save(buffer, format=format)
    buffer.seek(0)
    
    # Encode to base64
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    
    return img_base64


def base64_to_frame(base64_str: str) -> np.ndarray:
    """
    Convert base64 string to frame
    
    Args:
        base64_str: Base64 encoded image
        
    Returns:
        Image frame (BGR)
    """
    try:
        # Remove data URI prefix if present (e.g., "data:image/jpeg;base64,")
        if ',' in base64_str and base64_str.startswith('data:'):
            base64_str = base64_str.split(',', 1)[1]
        
        # Decode base64
        img_bytes = base64.b64decode(base64_str)
        
        # Convert to PIL Image
        pil_img = Image.open(BytesIO(img_bytes))
        
        # Convert to numpy array
        rgb_frame = np.array(pil_img)
        
        # Convert RGB to BGR
        bgr_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
        
        return bgr_frame
    except Exception as e:
        raise ValueError(f"Failed to decode base64 image: {str(e)}")


def extract_frames_from_video(
    video_source: str,
    num_frames: int = 50,
    skip_frames: int = 5
) -> List[np.ndarray]:
    """
    Extract frames from video source
    
    Args:
        video_source: Video file path or camera source
        num_frames: Number of frames to extract
        skip_frames: Number of frames to skip between extractions
        
    Returns:
        List of extracted frames
    """
    frames = []
    
    with VideoCapture(video_source) as cap:
        if not cap.is_opened:
            raise ValueError(f"Could not open video source: {video_source}")
        
        frame_count = 0
        while len(frames) < num_frames:
            frame = cap.read()
            if frame is None:
                break
            
            if frame_count % (skip_frames + 1) == 0:
                frames.append(frame)
            
            frame_count += 1
    
    return frames
