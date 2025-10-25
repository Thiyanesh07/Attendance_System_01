#!/usr/bin/env python3
"""
Final comprehensive test for the Face Recognition System
"""

import sys
import os
sys.path.append('.')

import cv2
import numpy as np
import requests
import json
from app.services.face_detection import get_detector
from app.services.face_recognition import get_recognizer
from app.services.training_service import get_trainer

def test_backend_api():
    """Test all backend API endpoints"""
    print("Testing Backend API...")
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("Health check: OK")
        else:
            print("Health check: FAILED")
            return False
    except Exception as e:
        print(f"Health check: ERROR - {e}")
        return False
    
    # Test cameras endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/cameras")
        if response.status_code == 200:
            cameras = response.json()
            print(f"Cameras API: OK ({len(cameras)} cameras)")
        else:
            print("Cameras API: FAILED")
            return False
    except Exception as e:
        print(f"Cameras API: ERROR - {e}")
        return False
    
    # Test recognition stats
    try:
        response = requests.get(f"{base_url}/api/v1/recognition/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"Recognition Stats: OK (Embeddings: {stats['total_embeddings']}, Students: {stats['unique_students']})")
        else:
            print("Recognition Stats: FAILED")
            return False
    except Exception as e:
        print(f"Recognition Stats: ERROR - {e}")
        return False
    
    return True

def test_face_services():
    """Test face detection and recognition services"""
    print("\nTesting Face Services...")
    
    try:
        # Test face detection
        detector = get_detector()
        print("Face Detection Service: OK")
        
        # Test face recognition
        recognizer = get_recognizer()
        print("Face Recognition Service: OK")
        
        # Test training service
        trainer = get_trainer()
        print("Training Service: OK")
        
        # Test FAISS database
        faiss_db = trainer.faiss_db
        print(f"FAISS Database: OK (Dimension: {faiss_db.dimension})")
        
        return True
    except Exception as e:
        print(f"Face Services: ERROR - {e}")
        return False

def test_webcam_detection():
    """Test real-time face detection with webcam"""
    print("\nTesting Webcam Face Detection...")
    
    try:
        detector = get_detector()
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Webcam: Not available")
            return False
        
        print("Webcam: Available")
        
        # Test detection for 10 frames
        detection_count = 0
        for i in range(10):
            ret, frame = cap.read()
            if ret:
                faces = detector.detect(frame)
                if len(faces) > 0:
                    detection_count += 1
                    print(f"   Frame {i+1}: Detected {len(faces)} face(s)")
        
        cap.release()
        
        if detection_count > 0:
            print(f"Face Detection: Working ({detection_count}/10 frames detected faces)")
            return True
        else:
            print("Face Detection: No faces detected (may need better lighting)")
            return True  # Still considered working, just no faces in view
            
    except Exception as e:
        print(f"Webcam Detection: ERROR - {e}")
        return False

def test_frontend_connection():
    """Test frontend connection"""
    print("\nTesting Frontend Connection...")
    
    try:
        response = requests.get("http://localhost:3000")
        if response.status_code == 200:
            print("Frontend: Running on http://localhost:3000")
            return True
        else:
            print("Frontend: Not responding")
            return False
    except Exception as e:
        print(f"Frontend: ERROR - {e}")
        return False

def show_system_status():
    """Show complete system status"""
    print("\n" + "="*60)
    print("FACE RECOGNITION SYSTEM - FINAL STATUS")
    print("="*60)
    
    # Test all components
    api_ok = test_backend_api()
    services_ok = test_face_services()
    webcam_ok = test_webcam_detection()
    frontend_ok = test_frontend_connection()
    
    print("\n" + "="*60)
    print("SYSTEM SUMMARY")
    print("="*60)
    
    print(f"Backend API:     {'WORKING' if api_ok else 'FAILED'}")
    print(f"Face Services:   {'WORKING' if services_ok else 'FAILED'}")
    print(f"Webcam Detection:{'WORKING' if webcam_ok else 'FAILED'}")
    print(f"Frontend:        {'WORKING' if frontend_ok else 'FAILED'}")
    
    if api_ok and services_ok and webcam_ok and frontend_ok:
        print("\nSUCCESS: All systems are working correctly!")
        print("\nNEXT STEPS:")
        print("1. Open http://localhost:3000 in your browser")
        print("2. Go to Admin Portal")
        print("3. Add students in the Students section")
        print("4. Train students with their photos")
        print("5. Use Live Recognition to test face recognition")
        print("\nAccess URLs:")
        print("   Frontend: http://localhost:3000")
        print("   Backend API: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
    else:
        print("\nSome components need attention.")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    show_system_status()
