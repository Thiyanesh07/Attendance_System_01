"""
SCRFD Face Detection Service using ONNX Runtime
"""

import cv2
import numpy as np
import onnxruntime as ort
from typing import List, Tuple, Optional
from app.core.config import settings
import os


class SCRFDDetector:
    """
    SCRFD (Sample and Computation Redistribution for Efficient Face Detection)
    Face detector using ONNX runtime
    """
    
    def __init__(self, model_path: str = None, threshold: float = None):
        self.model_path = model_path or settings.SCRFD_MODEL_PATH
        self.threshold = threshold or settings.FACE_DETECTION_THRESHOLD
        
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"SCRFD model not found at {self.model_path}. "
                f"Please download the model from: "
                f"https://github.com/deepinsight/insightface/tree/master/detection/scrfd"
            )
        
        # Initialize ONNX Runtime session with CPU only
        # Use CPUExecutionProvider to avoid CUDA errors
        self.session = ort.InferenceSession(
            self.model_path,
            providers=['CPUExecutionProvider']
        )
        
        # Get input details
        self.input_name = self.session.get_inputs()[0].name
        self.input_shape = self.session.get_inputs()[0].shape
        
        # Handle dynamic shapes - convert to int, use default if string/None
        try:
            self.input_height = int(self.input_shape[2]) if isinstance(self.input_shape[2], (int, float)) else 640
            self.input_width = int(self.input_shape[3]) if isinstance(self.input_shape[3], (int, float)) else 640
        except (ValueError, TypeError):
            # Default to 640x640 if shape parsing fails
            self.input_height = 640
            self.input_width = 640
        
        print(f"SCRFD Detector initialized with input size: {self.input_width}x{self.input_height}")
        
    def preprocess(self, image: np.ndarray) -> Tuple[np.ndarray, float, Tuple[int, int]]:
        """
        Preprocess image for SCRFD model
        
        Args:
            image: Input BGR image
            
        Returns:
            Preprocessed image, scale factor, and padding
        """
        # Get original dimensions
        img_h, img_w = image.shape[:2]
        
        # Calculate scale to fit model input
        scale = min(self.input_height / img_h, self.input_width / img_w)
        
        # Resize image
        new_h, new_w = int(img_h * scale), int(img_w * scale)
        resized = cv2.resize(image, (new_w, new_h))
        
        # Create padded image
        padded = np.zeros((self.input_height, self.input_width, 3), dtype=np.uint8)
        padded[:new_h, :new_w] = resized
        
        # Convert to RGB and normalize
        rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
        normalized = rgb.astype(np.float32)
        normalized = (normalized - 127.5) / 128.0
        
        # Transpose to NCHW format
        transposed = np.transpose(normalized, (2, 0, 1))
        blob = np.expand_dims(transposed, axis=0)
        
        return blob, scale, (img_w, img_h)
    
    def postprocess(self, outputs, scale: float, orig_size: Tuple[int, int]) -> List[dict]:
        """
        Post-process SCRFD model outputs
        
        Args:
            outputs: Raw model outputs
            scale: Scale factor used in preprocessing
            orig_size: Original image size (width, height)
            
        Returns:
            List of detected faces with bounding boxes and landmarks
        """
        faces = []
        
        # SCRFD outputs structure: 
        # Outputs 0,1,2: scores for different scales (12800, 3200, 800)
        # Outputs 3,4,5: bboxes for different scales (12800, 3200, 800) 
        # Outputs 6,7,8: keypoints for different scales (12800, 3200, 800)
        try:
            # Combine all scales
            all_scores = []
            all_bboxes = []
            all_keypoints = []
            
            # Process each scale
            for scale_idx in range(3):
                scores = outputs[scale_idx]  # Shape: (N, 1)
                bboxes = outputs[scale_idx + 3]  # Shape: (N, 4)
                keypoints = outputs[scale_idx + 6]  # Shape: (N, 10) - 5 points x 2 coords
                
                all_scores.extend(scores.flatten())
                all_bboxes.extend(bboxes)
                all_keypoints.extend(keypoints)
            
            # Convert to numpy arrays
            all_scores = np.array(all_scores)
            all_bboxes = np.array(all_bboxes)
            all_keypoints = np.array(all_keypoints)
            
            # Filter by threshold
            valid_indices = all_scores > self.threshold
            
            for i in range(len(all_scores)):
                if valid_indices[i]:
                    score = all_scores[i]
                    bbox = all_bboxes[i]
                    kps = all_keypoints[i]
                    
                    # Scale back to original image size
                    x1 = int(bbox[0] / scale)
                    y1 = int(bbox[1] / scale)
                    x2 = int(bbox[2] / scale)
                    y2 = int(bbox[3] / scale)
                    
                    # Clip to image boundaries
                    x1 = max(0, min(x1, orig_size[0]))
                    y1 = max(0, min(y1, orig_size[1]))
                    x2 = max(0, min(x2, orig_size[0]))
                    y2 = max(0, min(y2, orig_size[1]))
                    
                    # Skip invalid bounding boxes
                    if x2 <= x1 or y2 <= y1:
                        continue
                    
                    face_dict = {
                        'bbox': [x1, y1, x2, y2],
                        'score': float(score),
                        'landmarks': None
                    }
                    
                    # Add landmarks if available (reshape to 5 points x 2 coords)
                    if len(kps) >= 10:
                        landmarks = kps[:10].reshape(-1, 2)
                        landmarks[:, 0] = landmarks[:, 0] / scale
                        landmarks[:, 1] = landmarks[:, 1] / scale
                        face_dict['landmarks'] = landmarks.tolist()
                    
                    faces.append(face_dict)
            
            # Sort by confidence score (highest first)
            faces.sort(key=lambda x: x['score'], reverse=True)
            
        except Exception as e:
            print(f"Error in postprocessing: {e}")
            import traceback
            traceback.print_exc()
        
        return faces
    
    def detect(self, image: np.ndarray) -> List[dict]:
        """
        Detect faces in an image
        
        Args:
            image: Input BGR image
            
        Returns:
            List of detected faces with bounding boxes and landmarks
        """
        # Preprocess
        blob, scale, orig_size = self.preprocess(image)
        
        # Run inference
        outputs = self.session.run(None, {self.input_name: blob})
        
        # Postprocess
        faces = self.postprocess(outputs, scale, orig_size)
        
        return faces
    
    def draw_faces(self, image: np.ndarray, faces: List[dict]) -> np.ndarray:
        """
        Draw detected faces on image
        
        Args:
            image: Input image
            faces: List of detected faces
            
        Returns:
            Image with drawn faces
        """
        img_copy = image.copy()
        
        for face in faces:
            bbox = face['bbox']
            score = face['score']
            
            # Draw bounding box
            cv2.rectangle(
                img_copy,
                (bbox[0], bbox[1]),
                (bbox[2], bbox[3]),
                (0, 255, 0),
                2
            )
            
            # Draw score
            cv2.putText(
                img_copy,
                f"{score:.2f}",
                (bbox[0], bbox[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )
            
            # Draw landmarks if available
            if face['landmarks']:
                for landmark in face['landmarks']:
                    cv2.circle(img_copy, tuple(map(int, landmark)), 2, (0, 0, 255), -1)
        
        return img_copy


# Global detector instance
_detector_instance: Optional[SCRFDDetector] = None


def get_detector() -> SCRFDDetector:
    """Get or create global detector instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = SCRFDDetector()
    return _detector_instance
