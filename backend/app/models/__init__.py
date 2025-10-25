"""
Models package initialization
"""

from app.models.student import Student
from app.models.attendance import Attendance
from app.models.camera import Camera
from app.models.admin import Admin

__all__ = ["Student", "Attendance", "Camera", "Admin"]
