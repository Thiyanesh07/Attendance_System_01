"""
Attendance API routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from app.core.database import get_db
from app.models.attendance import Attendance
from app.models.student import Student
from app.models.camera import Camera
from app.schemas.attendance import AttendanceCreate, AttendanceResponse, AttendanceWithStudent, AttendanceStats
from sqlalchemy import func, and_

router = APIRouter()


@router.get("/", response_model=List[AttendanceWithStudent])
def get_attendance(
    skip: int = 0,
    limit: int = 100,
    date_filter: Optional[date] = None,
    student_id: Optional[int] = None,
    camera_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get attendance records"""
    query = db.query(Attendance).join(Student)
    
    if date_filter:
        query = query.filter(Attendance.date == date_filter)
    if student_id:
        query = query.filter(Attendance.student_id == student_id)
    if camera_id:
        query = query.filter(Attendance.camera_id == camera_id)
    
    records = query.order_by(Attendance.time.desc()).offset(skip).limit(limit).all()
    
    # Format response
    result = []
    for record in records:
        camera_name = None
        if record.camera:
            camera_name = record.camera.name
        
        result.append({
            **record.__dict__,
            'student_name': record.student.name,
            'student_roll_number': record.student.roll_number,
            'camera_name': camera_name
        })
    
    return result


@router.get("/stats", response_model=AttendanceStats)
def get_attendance_stats(
    date_filter: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get attendance statistics"""
    if date_filter is None:
        date_filter = date.today()
    
    # Total active students
    total_students = db.query(func.count(Student.id)).filter(Student.is_active == True).scalar() or 0
    
    # Students present today
    present_today = db.query(func.count(func.distinct(Attendance.student_id))).filter(
        Attendance.date == date_filter
    ).scalar() or 0
    
    absent_today = total_students - present_today
    attendance_percentage = (present_today / total_students * 100) if total_students > 0 else 0.0
    
    return {
        'total_students': total_students,
        'present_today': present_today,
        'absent_today': absent_today,
        'attendance_percentage': round(attendance_percentage, 2),
        'date': date_filter
    }


@router.post("/", response_model=AttendanceResponse)
def mark_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    """Mark attendance for a student"""
    # Check if student exists
    student = db.query(Student).filter(Student.id == attendance.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if already marked for today
    existing = db.query(Attendance).filter(
        and_(
            Attendance.student_id == attendance.student_id,
            Attendance.date == attendance.date
        )
    ).first()
    
    if existing:
        # Update existing record
        existing.time = attendance.time
        existing.camera_id = attendance.camera_id
        existing.confidence = attendance.confidence
        existing.status = attendance.status
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new attendance record
    db_attendance = Attendance(**attendance.dict())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance


@router.get("/today", response_model=List[AttendanceWithStudent])
def get_today_attendance(db: Session = Depends(get_db)):
    """Get today's attendance records"""
    today = date.today()
    return get_attendance(date_filter=today, db=db)


@router.delete("/{attendance_id}")
def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    """Delete attendance record"""
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    db.delete(attendance)
    db.commit()
    return {"message": "Attendance record deleted successfully"}
