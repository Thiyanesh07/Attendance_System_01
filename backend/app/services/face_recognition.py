"""
ArcFace Face Recognition Service using ONNX Runtime
"""

import cv2
import numpy as np
import onnxruntime as ort
from typing import Optional
from app.core.config import settings
import os


class ArcFaceRecognizer:
    """
    ArcFace face recognition model using ONNX runtime
    Generates 512-dimensional embeddings for face recognition
    """
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path or settings.ARCFACE_MODEL_PATH
        
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"ArcFace model not found at {self.model_path}. "
                f"Please download the model from: "
                f"https://github.com/deepinsight/insightface/tree/master/model_zoo"
            )
        
        # Initialize ONNX Runtime session with GPU acceleration
        # Try CUDA first, fallback to CPU if not available
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        
        # Try to create session with GPU, fallback to CPU if fails
        try:
            self.session = ort.InferenceSession(
                self.model_path,
                providers=providers
            )
        except Exception as e:
            print(f"⚠️ Failed to initialize with CUDA: {e}")
            print("⚠️ Falling back to CPU execution")
            self.session = ort.InferenceSession(
                self.model_path,
                providers=['CPUExecutionProvider']
            )
        
        # Log which provider is being used
        available_providers = self.session.get_providers()
        print(f"ONNX Runtime providers available: {available_providers}")
        if 'CUDAExecutionProvider' in available_providers:
            print("✅ GPU acceleration ENABLED (CUDA)")
        else:
            print("⚠️  Running on CPU (CUDA not available)")
        
        # Get input details
        self.input_name = self.session.get_inputs()[0].name
        self.input_shape = self.session.get_inputs()[0].shape
        
        # Handle dynamic shapes - convert to int, use default if string/None
        try:
            self.input_height = int(self.input_shape[2]) if isinstance(self.input_shape[2], (int, float)) else 112
            self.input_width = int(self.input_shape[3]) if isinstance(self.input_shape[3], (int, float)) else 112
        except (ValueError, TypeError):
            # Default to 112x112 for ArcFace if shape parsing fails
            self.input_height = 112
            self.input_width = 112
        
        # Get output details
        self.output_name = self.session.get_outputs()[0].name
        
        print(f"ArcFace Recognizer initialized with input size: {self.input_width}x{self.input_height}")
    
    def preprocess(self, face_img: np.ndarray) -> np.ndarray:
        """
        Preprocess face image for ArcFace model
        
        Args:
            face_img: Cropped face image (BGR)
            
        Returns:
            Preprocessed image tensor
        """
        # Resize to model input size
        resized = cv2.resize(face_img, (self.input_width, self.input_height))
        
        # Convert BGR to RGB
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # Normalize
        normalized = rgb.astype(np.float32)
        normalized = (normalized - 127.5) / 128.0
        
        # Transpose to NCHW format
        transposed = np.transpose(normalized, (2, 0, 1))
        blob = np.expand_dims(transposed, axis=0)
        
        return blob
    
    def get_embedding(self, face_img: np.ndarray) -> np.ndarray:
        """
        Get face embedding from face image
        
        Args:
            face_img: Cropped face image (BGR)
            
        Returns:
            512-dimensional embedding vector
        """
        # Preprocess
        blob = self.preprocess(face_img)
        
        # Run inference
        embedding = self.session.run([self.output_name], {self.input_name: blob})[0]
        
        # Normalize embedding
        embedding = embedding.flatten()
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    def extract_face_from_bbox(self, image: np.ndarray, bbox: list, margin: float = 0.2) -> Optional[np.ndarray]:
        """
        Extract face region from image using bounding box
        
        Args:
            image: Full image
            bbox: Bounding box [x1, y1, x2, y2]
            margin: Margin to add around face (default 20%)
            
        Returns:
            Cropped face image or None if invalid
        """
        x1, y1, x2, y2 = bbox
        
        # Add margin
        width = x2 - x1
        height = y2 - y1
        margin_x = int(width * margin)
        margin_y = int(height * margin)
        
        x1 = max(0, x1 - margin_x)
        y1 = max(0, y1 - margin_y)
        x2 = min(image.shape[1], x2 + margin_x)
        y2 = min(image.shape[0], y2 + margin_y)
        
        # Crop face
        face_img = image[y1:y2, x1:x2]
        
        if face_img.size == 0:
            return None
        
        return face_img
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Similarity score (0 to 1)
        """
        # Cosine similarity
        similarity = np.dot(embedding1, embedding2)
        return float(similarity)
    
    def align_face(self, image: np.ndarray, landmarks: list = None) -> np.ndarray:
        """
        Align face using facial landmarks (if available)
        
        Args:
            image: Face image
            landmarks: Facial landmarks (5 points: left_eye, right_eye, nose, left_mouth, right_mouth)
            
        Returns:
            Aligned face image
        """
        # Simple alignment - just return original if no landmarks
        # For production, implement proper alignment using landmarks
        if landmarks is None or len(landmarks) < 5:
            return image
        
        # TODO: Implement proper face alignment
        # This would involve calculating rotation and scaling based on eye positions
        
        return image


# Global recognizer instance
_recognizer_instance: Optional[ArcFaceRecognizer] = None


def get_recognizer() -> ArcFaceRecognizer:
    """Get or create global recognizer instance"""
    global _recognizer_instance
    if _recognizer_instance is None:
        _recognizer_instance = ArcFaceRecognizer()
    return _recognizer_instance
