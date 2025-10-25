"""
Camera database model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Camera(Base):
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    ip_address = Column(String, unique=True, nullable=False)
    location = Column(String)
    is_active = Column(Boolean, default=True)
    fps = Column(Integer, default=30)
    resolution = Column(String, default="640x480")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    attendance_records = relationship("Attendance", back_populates="camera")
    
    def __repr__(self):
        return f"<Camera {self.name}: {self.ip_address}>"
