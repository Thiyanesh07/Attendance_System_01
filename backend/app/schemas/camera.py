"""
Pydantic schemas for Camera
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CameraBase(BaseModel):
    name: str
    ip_address: str
    location: Optional[str] = None
    fps: int = 30
    resolution: str = "640x480"


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    ip_address: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None
    fps: Optional[int] = None
    resolution: Optional[str] = None


class CameraResponse(CameraBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
