"""
Camera API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import cv2
import numpy as np

from app.core.database import get_db
from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate, CameraResponse
from app.services.video_service import VideoCapture
from app.services.camera_runner import get_camera_manager

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


@router.post("/start-all-bg")
def start_all_background(db: Session = Depends(get_db), fps: int = 1):
    """Start background recognition for all active cameras."""
    manager = get_camera_manager()
    cameras = db.query(Camera).filter(Camera.is_active == True).all()
    for cam in cameras:
        manager.start(cam, fps=fps)
    return manager.all_status()


@router.post("/stop-all-bg")
def stop_all_background():
    """Stop all background recognition workers."""
    manager = get_camera_manager()
    manager.stop_all()
    return {"message": "all stopped"}


@router.get("/bg-status")
def all_background_status():
    """Get status for all background workers."""
    manager = get_camera_manager()
    return manager.all_status()


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


@router.post("/test-connection")
def test_camera_connection(camera: CameraCreate):
    """Test camera connection without saving to database"""
    source = camera.ip_address
    
    try:
        with VideoCapture(source) as cap:
            if not cap.is_opened:
                raise HTTPException(
                    status_code=503, 
                    detail=f"Unable to open camera source: {source}. Check IP/URL and network connectivity."
                )

            frame = cap.read()
            if frame is None:
                raise HTTPException(
                    status_code=504, 
                    detail="Camera opened but failed to read frame. Check camera stream."
                )

        # If we get here, connection was successful
        return {
            "success": True,
            "message": f"Successfully connected to camera at {source}",
            "source": source
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Connection test failed: {str(e)}"
        )


@router.get("/{camera_id}/snapshot")
def get_camera_snapshot(
    camera_id: int,
    width: int = 640,
    height: int = 480,
    db: Session = Depends(get_db)
):
    """Return a single JPEG snapshot from the specified camera.

    Supports integer device indices (e.g., "0") or URL sources (HTTP/RTSP/file).
    """
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    source = camera.ip_address

    # Try to open, read one frame, then close
    with VideoCapture(source) as cap:
        if not cap.is_opened:
            raise HTTPException(status_code=503, detail=f"Unable to open camera source: {source}")

        frame = cap.read()
        if frame is None:
            raise HTTPException(status_code=504, detail="Failed to read frame from camera")

    # Optional resize
    if width and height and width > 0 and height > 0:
        try:
            frame = cv2.resize(frame, (int(width), int(height)))
        except Exception:
            pass

    # Encode to JPEG
    success, buffer = cv2.imencode('.jpg', frame)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to encode frame")

    return Response(content=buffer.tobytes(), media_type="image/jpeg")


@router.post("/{camera_id}/start-bg")
def start_camera_background(
    camera_id: int,
    fps: int = 1,
    db: Session = Depends(get_db)
):
    """Start background recognition for a camera (marks attendance)."""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    manager = get_camera_manager()
    worker = manager.start(camera, fps=fps)
    return manager.status(camera_id)


@router.post("/{camera_id}/stop-bg")
def stop_camera_background(camera_id: int):
    """Stop background recognition for a camera."""
    manager = get_camera_manager()
    ok = manager.stop(camera_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Camera worker not found")
    return {"message": "stopped", "camera_id": camera_id}


@router.get("/{camera_id}/status")
def camera_background_status(camera_id: int):
    """Get background worker status for a camera."""
    manager = get_camera_manager()
    return manager.status(camera_id)


    
