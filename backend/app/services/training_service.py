"""
Training service for face recognition model
"""

import numpy as np
import pickle
from typing import List, Dict
from app.services.face_detection import get_detector
from app.services.face_recognition import get_recognizer
from app.services.faiss_service import get_faiss_db
from app.core.config import settings
import os


class FaceRecognitionTrainer:
    """
    Service for training face recognition model
    """
    
    def __init__(self):
        self.detector = get_detector()
        self.recognizer = get_recognizer()
        self.faiss_db = get_faiss_db()
    
    def process_student_frames(
        self,
        frames: List[np.ndarray],
        student_id: int,
        min_faces: int = 10
    ) -> Dict:
        """
        Process frames for a student and extract embeddings
        
        Args:
            frames: List of video frames
            student_id: Student ID
            min_faces: Minimum number of valid faces required
            
        Returns:
            Dictionary with processing results
        """
        embeddings = []
        valid_frames = 0
        
        print(f"Processing {len(frames)} frames for student {student_id}")
        
        for i, frame in enumerate(frames):
            try:
                # Detect faces
                faces = self.detector.detect(frame)
                
                if len(faces) == 0:
                    print(f"Frame {i}: No faces detected")
                    continue
                
                # Use the face with highest confidence
                best_face = max(faces, key=lambda x: x['score'])
                print(f"Frame {i}: Detected face with score {best_face['score']:.3f}")
                
                # Extract face region
                face_img = self.recognizer.extract_face_from_bbox(
                    frame, 
                    best_face['bbox']
                )
                
                if face_img is None:
                    print(f"Frame {i}: Could not extract face region")
                    continue
                
                # Get embedding
                try:
                    embedding = self.recognizer.get_embedding(face_img)
                    embeddings.append(embedding)
                    valid_frames += 1
                    print(f"Frame {i}: Successfully extracted embedding")
                except Exception as e:
                    print(f"Frame {i}: Error getting embedding: {e}")
                    continue
            except Exception as e:
                print(f"Frame {i}: Error processing frame: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Check if we have enough valid faces
        if len(embeddings) < min_faces:
            return {
                'success': False,
                'message': f'Not enough valid faces detected. Found {len(embeddings)}, need at least {min_faces}',
                'embeddings_count': len(embeddings)
            }
        
        # Add embeddings to FAISS
        try:
            self.faiss_db.add_multiple_embeddings(
                embeddings,
                student_id,
                metadata={'num_embeddings': len(embeddings)}
            )
            
            return {
                'success': True,
                'message': f'Successfully processed {len(embeddings)} embeddings',
                'embeddings_count': len(embeddings),
                'valid_frames': valid_frames
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error adding embeddings to database: {str(e)}',
                'embeddings_count': len(embeddings)
            }
    
    def recognize_face(self, frame: np.ndarray) -> List[Dict]:
        """
        Recognize faces in a frame
        
        Args:
            frame: Video frame
            
        Returns:
            List of recognized faces with student IDs and confidence
        """
        results = []
        
        print(f"[RECOGNITION] Starting face recognition on frame shape: {frame.shape}")
        
        # Detect faces
        try:
            faces = self.detector.detect(frame)
            print(f"[RECOGNITION] Detected {len(faces)} faces")
        except Exception as e:
            print(f"[RECOGNITION] Error detecting faces: {e}")
            import traceback
            traceback.print_exc()
            return results
        
        for i, face in enumerate(faces):
            print(f"[RECOGNITION] Processing face {i+1}/{len(faces)}, bbox={face['bbox']}, score={face['score']:.3f}")
            
            # Extract face region
            face_img = self.recognizer.extract_face_from_bbox(
                frame,
                face['bbox']
            )
            
            if face_img is None:
                print(f"[RECOGNITION] Face {i+1}: Could not extract face region")
                continue
            
            print(f"[RECOGNITION] Face {i+1}: Extracted face region, shape={face_img.shape}")
            
            # Get embedding
            try:
                embedding = self.recognizer.get_embedding(face_img)
                print(f"[RECOGNITION] Face {i+1}: Got embedding, shape={embedding.shape}")
                
                # Search in FAISS
                matches = self.faiss_db.search(embedding, k=1)
                print(f"[RECOGNITION] Face {i+1}: FAISS search returned {len(matches) if matches else 0} matches")
                
                if matches:
                    student_id, confidence = matches[0]
                    print(f"[RECOGNITION] Face {i+1}: Matched student_id={student_id}, confidence={confidence:.3f}")
                    results.append({
                        'bbox': face['bbox'],
                        'student_id': student_id,
                        'confidence': confidence,
                        'detection_score': face['score']
                    })
                else:
                    print(f"[RECOGNITION] Face {i+1}: No match found (unknown face)")
                    results.append({
                        'bbox': face['bbox'],
                        'student_id': None,
                        'confidence': 0.0,
                        'detection_score': face['score']
                    })
            except Exception as e:
                print(f"[RECOGNITION] Face {i+1}: Error recognizing face: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"[RECOGNITION] Completed recognition, returning {len(results)} results")
        return results
    
    def remove_student_data(self, student_id: int):
        """
        Remove student data from the model
        
        Args:
            student_id: Student ID to remove
        """
        self.faiss_db.remove_student_embeddings(student_id)
    
    def get_model_stats(self) -> Dict:
        """
        Get statistics about the trained model
        
        Returns:
            Dictionary with model statistics
        """
        return {
            'total_embeddings': self.faiss_db.get_total_embeddings(),
            'unique_students': len(set(self.faiss_db.student_ids)),
            'model_path': settings.FAISS_INDEX_PATH,
            'dimension': self.faiss_db.dimension
        }
    
    def save_model(self):
        """Save the model to disk"""
        self.faiss_db.save_index()
    
    def export_model_pickle(self, output_path: str = None):
        """
        Export model as pickle file
        
        Args:
            output_path: Path to save pickle file
        """
        if output_path is None:
            output_path = os.path.join(settings.MODELS_PATH, 'face_recognition_model.pkl')
        
        model_data = {
            'faiss_index_path': self.faiss_db.index_path,
            'embeddings_path': self.faiss_db.embeddings_path,
            'student_ids': self.faiss_db.student_ids,
            'embeddings_data': self.faiss_db.embeddings_data,
            'dimension': self.faiss_db.dimension,
            'config': {
                'detection_threshold': settings.FACE_DETECTION_THRESHOLD,
                'recognition_threshold': settings.FACE_RECOGNITION_THRESHOLD,
                'scrfd_model': settings.SCRFD_MODEL_PATH,
                'arcface_model': settings.ARCFACE_MODEL_PATH
            }
        }
        
        with open(output_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model exported to {output_path}")
        return output_path


# Global trainer instance
_trainer_instance = None


def get_trainer() -> FaceRecognitionTrainer:
    """Get or create global trainer instance"""
    global _trainer_instance
    if _trainer_instance is None:
        _trainer_instance = FaceRecognitionTrainer()
    return _trainer_instance
