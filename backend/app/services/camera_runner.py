"""
Background camera runner to process camera streams and mark attendance.
"""

import threading
import time
from typing import Dict, Optional
import cv2

from app.services.video_service import VideoCapture
from app.services.training_service import get_trainer
from app.core.database import SessionLocal
from app.models.attendance import Attendance
from app.models.student import Student
from app.models.camera import Camera
from datetime import date, datetime


class CameraWorker:
    def __init__(self, camera_id: int, source: str, fps: int = 1):
        self.camera_id = camera_id
        self.source = source
        self.fps = max(0.2, min(fps, 5))  # poll between 0.2 and 5 fps
        self.thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.running = False
        self.last_result = None
        self.error: Optional[str] = None

    def start(self):
        if self.running:
            return
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        self.running = True

    def stop(self):
        if self.thread and self.thread.is_alive():
            self.stop_event.set()
            self.thread.join(timeout=5)
        self.running = False

    def _run(self):
        trainer = get_trainer()
        interval = 1.0 / self.fps if self.fps > 0 else 1.0

        while not self.stop_event.is_set():
            start_t = time.time()
            try:
                # Open and read one frame per cycle to avoid long-lived connections for fragile IP cams
                with VideoCapture(self.source) as cap:
                    if not cap.is_opened:
                        self.error = f"Unable to open source: {self.source}"
                        time.sleep(2)
                        continue
                    frame = cap.read()
                    if frame is None:
                        self.error = "Failed to read frame"
                        time.sleep(1)
                        continue

                # Recognize
                results = trainer.recognize_face(frame)

                # Mark attendance for recognized faces
                today = date.today()
                now = datetime.now()
                db = SessionLocal()
                try:
                    for result in results:
                        sid = result.get('student_id')
                        if sid:
                            existing = db.query(Attendance).filter(
                                Attendance.student_id == sid,
                                Attendance.date == today
                            ).first()
                            if not existing:
                                attendance = Attendance(
                                    student_id=sid,
                                    date=today,
                                    time=now,
                                    camera_id=self.camera_id,
                                    confidence=result.get('confidence', 0.0),
                                    status='present'
                                )
                                db.add(attendance)
                                db.commit()
                    # keep a lightweight summary
                    self.last_result = {
                        'timestamp': now.isoformat(),
                        'recognized': [r.get('student_id') for r in results if r.get('student_id')],
                        'count': len([r for r in results if r.get('student_id')])
                    }
                    self.error = None
                finally:
                    db.close()

            except Exception as e:
                self.error = str(e)

            # sleep until next interval
            elapsed = time.time() - start_t
            sleep_time = max(0.1, interval - elapsed)
            if self.stop_event.wait(timeout=sleep_time):
                break


class BackgroundCameraManager:
    def __init__(self):
        self.workers: Dict[int, CameraWorker] = {}
        self.lock = threading.Lock()

    def start(self, camera: Camera, fps: int = 1):
        with self.lock:
            worker = self.workers.get(camera.id)
            if worker and worker.running:
                return worker
            worker = CameraWorker(camera.id, camera.ip_address, fps=fps)
            self.workers[camera.id] = worker
            worker.start()
            return worker

    def stop(self, camera_id: int):
        with self.lock:
            worker = self.workers.get(camera_id)
            if worker:
                worker.stop()
                return True
            return False

    def stop_all(self):
        with self.lock:
            for worker in list(self.workers.values()):
                worker.stop()
            return True

    def status(self, camera_id: int):
        with self.lock:
            worker = self.workers.get(camera_id)
            if not worker:
                return {'running': False}
            return {
                'running': worker.running,
                'error': worker.error,
                'last_result': worker.last_result,
                'fps': worker.fps,
                'camera_id': camera_id
            }

    def all_status(self):
        with self.lock:
            return {cid: self.status(cid) for cid in self.workers.keys()}


_manager = BackgroundCameraManager()


def get_camera_manager() -> BackgroundCameraManager:
    return _manager
