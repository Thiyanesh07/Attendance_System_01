"""
Training API routes
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Body
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import numpy as np
import cv2
import os
import tempfile
import shutil
from datetime import datetime
from PIL import Image
from io import BytesIO

from app.core.database import get_db
from app.models.student import Student
from app.services.training_service import get_trainer
from app.services.video_service import extract_frames_from_video, base64_to_frame
from app.core.config import settings

router = APIRouter()


class TrainingFramesRequest(BaseModel):
    """Schema for training frames request"""
    frames_base64: List[str]


@router.post("/train-student/{student_id}")
async def train_student(
    student_id: int,
    video: UploadFile = File(...),
    num_frames: int = Form(50),
    db: Session = Depends(get_db)
):
    """
    Train face recognition model for a student using uploaded video
    
    Args:
        student_id: Student ID
        video: Video file
        num_frames: Number of frames to extract
    """
    # Check if student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    try:
        # Save video temporarily
        temp_dir = tempfile.mkdtemp()
        video_path = os.path.join(temp_dir, f"temp_video_{student_id}.mp4")
        
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        
        # Extract frames
        frames = extract_frames_from_video(video_path, num_frames=num_frames)
        
        if len(frames) == 0:
            raise HTTPException(status_code=400, detail="No frames could be extracted from video")
        
        # Train model
        trainer = get_trainer()
        result = trainer.process_student_frames(frames, student_id)
        
        # Clean up
        shutil.rmtree(temp_dir)
        
        if result['success']:
            # Update student record
            student.face_encoding_id = student_id
            db.commit()
            
            return {
                'success': True,
                'message': result['message'],
                'embeddings_count': result['embeddings_count'],
                'student_id': student_id,
                'student_name': student.name
            }
        else:
            return {
                'success': False,
                'message': result['message'],
                'embeddings_count': result.get('embeddings_count', 0)
            }
    
    except Exception as e:
        # Clean up on error
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")


@router.post("/train-student-frames/{student_id}")
async def train_student_frames(
    student_id: int,
    request: TrainingFramesRequest,
    db: Session = Depends(get_db)
):
    """
    Train face recognition model for a student using base64 encoded frames
    
    Args:
        student_id: Student ID
        request: Training frames request with base64 encoded frames
    """
    # Check if student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    try:
        # Decode frames
        frames = []
        for i, frame_str in enumerate(request.frames_base64):
            try:
                frame = base64_to_frame(frame_str)
                frames.append(frame)
            except Exception as decode_error:
                print(f"Error decoding frame {i}: {str(decode_error)}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to decode frame {i}: {str(decode_error)}"
                )
        
        if len(frames) == 0:
            raise HTTPException(status_code=400, detail="No frames provided")
        
        print(f"Training student {student_id} with {len(frames)} frames...")
        
        # Train model
        trainer = get_trainer()
        result = trainer.process_student_frames(frames, student_id)
        
        print(f"Training result: {result}")
        
        if result['success']:
            # Update student record
            student.face_encoding_id = student_id
            db.commit()
            
            return {
                'success': True,
                'message': result['message'],
                'embeddings_count': result['embeddings_count'],
                'student_id': student_id,
                'student_name': student.name
            }
        else:
            return {
                'success': False,
                'message': result['message'],
                'embeddings_count': result.get('embeddings_count', 0)
            }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")


@router.post("/train-student-photos/{student_id}")
async def train_student_photos(
    student_id: int,
    photos: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Train face recognition model for a student using uploaded photos
    
    Args:
        student_id: Student ID
        photos: List of photo files
    """
    # Check if student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if not photos or len(photos) == 0:
        raise HTTPException(status_code=400, detail="No photos provided")
    
    try:
        print(f"Training student {student_id} with {len(photos)} photos...")
        
        # Create student photos directory
        student_photos_dir = os.path.join(settings.UPLOADS_PATH, f"student_{student_id}")
        os.makedirs(student_photos_dir, exist_ok=True)
        
        # Process each photo
        frames = []
        saved_photo_paths = []
        
        for i, photo in enumerate(photos):
            try:
                # Read photo
                contents = await photo.read()
                nparr = np.frombuffer(contents, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if img is None:
                    print(f"Photo {i}: Could not decode image")
                    continue
                
                # Save original photo
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                photo_filename = f"photo_{i}_{timestamp}.jpg"
                photo_path = os.path.join(student_photos_dir, photo_filename)
                cv2.imwrite(photo_path, img)
                saved_photo_paths.append(photo_path)
                
                # Add to frames for training
                frames.append(img)
                print(f"Photo {i}: Processed successfully, shape={img.shape}")
                
            except Exception as e:
                print(f"Photo {i}: Error processing: {e}")
                continue
        
        if len(frames) == 0:
            raise HTTPException(status_code=400, detail="No valid photos could be processed")
        
        print(f"Successfully processed {len(frames)} photos, starting training...")
        
        # Train model
        trainer = get_trainer()
        result = trainer.process_student_frames(frames, student_id, min_faces=5)  # Lower threshold for photos
        
        print(f"Training result: {result}")
        
        if result['success']:
            # Update student record with first photo path
            if saved_photo_paths:
                student.photo_path = saved_photo_paths[0]
            student.face_encoding_id = student_id
            db.commit()
            
            return {
                'success': True,
                'message': result['message'],
                'embeddings_count': result['embeddings_count'],
                'photos_processed': len(frames),
                'photos_saved': len(saved_photo_paths),
                'student_id': student_id,
                'student_name': student.name
            }
        else:
            # Clean up photos if training failed
            for path in saved_photo_paths:
                if os.path.exists(path):
                    os.remove(path)
            
            return {
                'success': False,
                'message': result['message'],
                'embeddings_count': result.get('embeddings_count', 0),
                'photos_processed': len(frames)
            }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")


@router.delete("/remove-student/{student_id}")
def remove_student_training(student_id: int, db: Session = Depends(get_db)):
    """Remove student training data from model"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    try:
        trainer = get_trainer()
        trainer.remove_student_data(student_id)
        
        # Update student record
        student.face_encoding_id = None
        db.commit()
        
        return {
            'success': True,
            'message': f'Training data removed for student {student.name}'
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing training data: {str(e)}")


@router.post("/retrain-all")
async def retrain_all_students(db: Session = Depends(get_db)):
    """Retrain model with all students (requires video files for each student)"""
    # This is a placeholder - implement based on your storage strategy
    raise HTTPException(status_code=501, detail="Retrain all not implemented yet")


@router.get("/model-stats")
def get_model_stats():
    """Get model statistics"""
    trainer = get_trainer()
    return trainer.get_model_stats()


@router.post("/export-model")
def export_model():
    """Export model as pickle file"""
    try:
        trainer = get_trainer()
        output_path = trainer.export_model_pickle()
        return {
            'success': True,
            'message': 'Model exported successfully',
            'path': output_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")


@router.post("/save-model")
def save_model():
    """Save current model to disk"""
    try:
        trainer = get_trainer()
        trainer.save_model()
        return {
            'success': True,
            'message': 'Model saved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save error: {str(e)}")
