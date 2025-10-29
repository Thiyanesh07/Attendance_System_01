"""
Configuration settings for the application
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Project Info
    PROJECT_NAME: str = "Face Recognition Attendance System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/attendance_db"
    
    # Paths
    MODELS_PATH: str = "models"
    UPLOADS_PATH: str = "uploads"
    FAISS_INDEX_PATH: str = "models/faiss_index.bin"
    FACE_EMBEDDINGS_PATH: str = "models/face_embeddings.pkl"
    
    # Face Recognition Settings
    SCRFD_MODEL_PATH: str = "models/scrfd_10g_bnkps.onnx"
    ARCFACE_MODEL_PATH: str = "models/w600k_r50.onnx"
    FACE_DETECTION_THRESHOLD: float = 0.3  # Lower for better recall, quality filtering applied later
    FACE_RECOGNITION_THRESHOLD: float = 0.55  # Optimized threshold for cosine similarity (higher = stricter)
    
    # FAISS Settings
    FAISS_DIMENSION: int = 512  # ArcFace embedding dimension
    FAISS_INDEX_TYPE: str = "COSINE"  # Use cosine similarity for better accuracy
    FAISS_K_NEIGHBORS: int = 5  # Check top-5 matches for verification
    
    # Camera Settings
    DEFAULT_CAMERA_FPS: int = 30
    FRAME_WIDTH: int = 640
    FRAME_HEIGHT: int = 480
    
    # Training Settings
    FRAMES_PER_STUDENT: int = 50  # Number of frames to capture per student
    TRAINING_BATCH_SIZE: int = 32
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Create necessary directories
os.makedirs(settings.MODELS_PATH, exist_ok=True)
os.makedirs(settings.UPLOADS_PATH, exist_ok=True)
