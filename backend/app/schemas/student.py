"""
Pydantic schemas for Student
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class StudentBase(BaseModel):
    roll_number: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    department: Optional[str] = None
    year: Optional[int] = None
    section: Optional[str] = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    year: Optional[int] = None
    section: Optional[str] = None
    is_active: Optional[bool] = None


class StudentResponse(StudentBase):
    id: int
    is_active: bool
    face_encoding_id: Optional[int] = None
    photo_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class StudentWithAttendance(StudentResponse):
    attendance_percentage: float
    total_days: int
    present_days: int
