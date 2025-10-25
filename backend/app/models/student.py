"""
Student database model
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    roll_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    department = Column(String)
    year = Column(Integer)
    section = Column(String)
    is_active = Column(Boolean, default=True)
    face_encoding_id = Column(Integer, index=True)  # Reference to FAISS index
    photo_path = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    attendance_records = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Student {self.roll_number}: {self.name}>"
