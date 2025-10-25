"""
Attendance database model
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    time = Column(DateTime(timezone=True), nullable=False)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=True)
    confidence = Column(Float)  # Recognition confidence score
    status = Column(String, default="present")  # present, absent, late
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    camera = relationship("Camera", back_populates="attendance_records")
    
    def __repr__(self):
        return f"<Attendance {self.student_id} on {self.date} at {self.time}>"
