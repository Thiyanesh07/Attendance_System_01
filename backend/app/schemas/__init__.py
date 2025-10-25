"""
Schemas package initialization
"""

from app.schemas.student import (
    StudentBase, StudentCreate, StudentUpdate, 
    StudentResponse, StudentWithAttendance
)
from app.schemas.attendance import (
    AttendanceBase, AttendanceCreate, AttendanceResponse,
    AttendanceWithStudent, AttendanceStats
)
from app.schemas.camera import (
    CameraBase, CameraCreate, CameraUpdate, CameraResponse
)

__all__ = [
    "StudentBase", "StudentCreate", "StudentUpdate", "StudentResponse", "StudentWithAttendance",
    "AttendanceBase", "AttendanceCreate", "AttendanceResponse", "AttendanceWithStudent", "AttendanceStats",
    "CameraBase", "CameraCreate", "CameraUpdate", "CameraResponse"
]
