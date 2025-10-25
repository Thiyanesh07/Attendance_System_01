"""
Student API routes
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from app.core.database import get_db
from app.models.student import Student
from app.models.attendance import Attendance
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse, StudentWithAttendance
from app.schemas.attendance import AttendanceResponse
from sqlalchemy import func

router = APIRouter()


@router.get("/", response_model=List[StudentResponse])
def get_students(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all students"""
    query = db.query(Student)
    
    if is_active is not None:
        query = query.filter(Student.is_active == is_active)
    
    students = query.offset(skip).limit(limit).all()
    return students


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    """Get student by ID"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.get("/roll/{roll_number}", response_model=StudentWithAttendance)
def get_student_by_roll(roll_number: str, db: Session = Depends(get_db)):
    """Get student by roll number with attendance stats"""
    student = db.query(Student).filter(Student.roll_number == roll_number).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Calculate attendance stats
    total_days = db.query(func.count(func.distinct(Attendance.date))).scalar() or 0
    present_days = db.query(func.count(func.distinct(Attendance.date))).filter(
        Attendance.student_id == student.id
    ).scalar() or 0
    
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0.0
    
    student_dict = {
        **student.__dict__,
        'attendance_percentage': round(attendance_percentage, 2),
        'total_days': total_days,
        'present_days': present_days
    }
    
    return student_dict


@router.post("/", response_model=StudentResponse)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Create new student"""
    # Check if roll number already exists
    existing = db.query(Student).filter(Student.roll_number == student.roll_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Roll number already exists")
    
    # Check if email already exists
    if student.email:
        existing_email = db.query(Student).filter(Student.email == student.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student_update: StudentUpdate,
    db: Session = Depends(get_db)
):
    """Update student"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Update fields
    update_data = student_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)
    
    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Delete student"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Delete from FAISS
    from app.services.training_service import get_trainer
    trainer = get_trainer()
    trainer.remove_student_data(student_id)
    
    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}


@router.get("/{student_id}/attendance", response_model=List[AttendanceResponse])
def get_student_attendance(
    student_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get student attendance records"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    query = db.query(Attendance).filter(Attendance.student_id == student_id)
    
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    
    attendance_records = query.order_by(Attendance.date.desc(), Attendance.time.desc()).all()
    return attendance_records
