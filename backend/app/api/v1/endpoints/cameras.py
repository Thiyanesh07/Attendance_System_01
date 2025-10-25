"""
Camera API routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate, CameraResponse

router = APIRouter()


@router.get("/", response_model=List[CameraResponse])
def get_cameras(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """Get all cameras"""
    query = db.query(Camera)
    
    if is_active is not None:
        query = query.filter(Camera.is_active == is_active)
    
    cameras = query.offset(skip).limit(limit).all()
    return cameras


@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera(camera_id: int, db: Session = Depends(get_db)):
    """Get camera by ID"""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.post("/", response_model=CameraResponse)
def create_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    """Create new camera"""
    # Check if IP address already exists
    existing = db.query(Camera).filter(Camera.ip_address == camera.ip_address).first()
    if existing:
        raise HTTPException(status_code=400, detail="Camera with this IP address already exists")
    
    db_camera = Camera(**camera.dict())
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera


@router.put("/{camera_id}", response_model=CameraResponse)
def update_camera(
    camera_id: int,
    camera_update: CameraUpdate,
    db: Session = Depends(get_db)
):
    """Update camera"""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # Check if IP address is being updated and already exists
    if camera_update.ip_address and camera_update.ip_address != camera.ip_address:
        existing = db.query(Camera).filter(Camera.ip_address == camera_update.ip_address).first()
        if existing:
            raise HTTPException(status_code=400, detail="Camera with this IP address already exists")
    
    # Update fields
    update_data = camera_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(camera, field, value)
    
    db.commit()
    db.refresh(camera)
    return camera


@router.delete("/{camera_id}")
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    """Delete camera"""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    db.delete(camera)
    db.commit()
    return {"message": "Camera deleted successfully"}


@router.post("/{camera_id}/toggle")
def toggle_camera(camera_id: int, db: Session = Depends(get_db)):
    """Toggle camera active status"""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    camera.is_active = not camera.is_active
    db.commit()
    db.refresh(camera)
    return camera
