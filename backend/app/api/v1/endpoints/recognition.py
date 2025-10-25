"""
Recognition API routes
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List
import numpy as np
import cv2
from datetime import date, datetime
import base64

from app.core.database import get_db
from app.models.student import Student
from app.models.attendance import Attendance
from app.schemas.attendance import AttendanceCreate
from app.services.training_service import get_trainer
from app.services.video_service import base64_to_frame, frame_to_base64

router = APIRouter()


@router.post("/recognize-frame")
async def recognize_frame(
    frame_base64: str = Form(...),
    camera_id: int = Form(None),
    mark_attendance: bool = Form(True),
    db: Session = Depends(get_db)
):
    """
    Recognize faces in a frame and optionally mark attendance
    
    Args:
        frame_base64: Base64 encoded image frame
        camera_id: Camera ID
        mark_attendance: Whether to mark attendance
    """
    try:
        print(f"Recognition request received, mark_attendance={mark_attendance}, camera_id={camera_id}")
        
        # Decode frame
        frame = base64_to_frame(frame_base64)
        print(f"Frame decoded: shape={frame.shape}, dtype={frame.dtype}")
        
        # Get trainer
        trainer = get_trainer()
        
        # Recognize faces
        results = trainer.recognize_face(frame)
        print(f"Recognition results: {len(results)} faces detected")
        for i, result in enumerate(results):
            conf = result.get('confidence')
            conf_str = f"{conf:.3f}" if conf is not None else "N/A"
            print(f"Face {i}: student_id={result.get('student_id')}, confidence={conf_str}")
        
        # Mark attendance if requested
        attendance_records = []
        if mark_attendance:
            today = date.today()
            now = datetime.now()
            
            for result in results:
                if result['student_id']:
                    # Check if already marked today
                    existing = db.query(Attendance).filter(
                        Attendance.student_id == result['student_id'],
                        Attendance.date == today
                    ).first()
                    
                    if not existing:
                        # Mark attendance
                        attendance = Attendance(
                            student_id=result['student_id'],
                            date=today,
                            time=now,
                            camera_id=camera_id,
                            confidence=result['confidence'],
                            status='present'
                        )
                        db.add(attendance)
                        db.commit()
                        db.refresh(attendance)
                        attendance_records.append(attendance.id)
                        print(f"Attendance marked for student {result['student_id']}")
        
        # Get student details for recognized faces
        recognized_students = []
        all_faces = []  # Include all detected faces for bounding boxes
        
        for result in results:
            face_data = {
                'bbox': result['bbox'],
                'detection_score': result.get('detection_score', 0.0),
                'student_id': result.get('student_id'),
                'confidence': result.get('confidence', 0.0)
            }
            
            if result['student_id']:
                student = db.query(Student).filter(Student.id == result['student_id']).first()
                if student:
                    face_data.update({
                        'roll_number': student.roll_number,
                        'name': student.name,
                        'recognized': True
                    })
                    recognized_students.append(face_data)
            else:
                face_data['recognized'] = False
            
            all_faces.append(face_data)
        
        print(f"Returning {len(recognized_students)} recognized students, {len(all_faces)} total faces")
        
        return {
            'success': True,
            'recognized_count': len(recognized_students),
            'students': recognized_students,
            'all_faces': all_faces,  # Include all detected faces for drawing boxes
            'attendance_marked': attendance_records
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Recognition error: {str(e)}")


@router.post("/recognize-file")
async def recognize_file(
    file: UploadFile = File(...),
    camera_id: int = Form(None),
    mark_attendance: bool = Form(True),
    db: Session = Depends(get_db)
):
    """
    Recognize faces in an uploaded image file
    """
    try:
        # Read file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Convert frame to base64
        frame_base64 = frame_to_base64(frame)
        
        # Use recognize_frame logic
        return await recognize_frame(frame_base64, camera_id, mark_attendance, db)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recognition error: {str(e)}")


@router.get("/stats")
def get_recognition_stats():
    """Get recognition model statistics"""
    trainer = get_trainer()
    return trainer.get_model_stats()
