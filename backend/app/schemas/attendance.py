"""
Pydantic schemas for Attendance
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class AttendanceBase(BaseModel):
    student_id: int
    date: date
    time: datetime
    camera_id: Optional[int] = None
    confidence: Optional[float] = None
    status: str = "present"


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceResponse(AttendanceBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AttendanceWithStudent(AttendanceResponse):
    student_name: str
    student_roll_number: str
    camera_name: Optional[str] = None


class AttendanceStats(BaseModel):
    total_students: int
    present_today: int
    absent_today: int
    attendance_percentage: float
    date: date
