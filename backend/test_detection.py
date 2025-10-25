#!/usr/bin/env python3
"""
Simple test script for face detection and recognition
"""

import sys
import os
sys.path.append('.')

import cv2
import numpy as np
from app.services.face_detection import get_detector
from app.services.face_recognition import get_recognizer
from app.services.training_service import get_trainer

def test_face_detection():
    """Test face detection with a simple synthetic face"""
    print("Testing face detection...")
    
    detector = get_detector()
    
    # Create a simple synthetic face-like image
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Draw a simple face
    cv2.circle(img, (320, 200), 80, (255, 255, 255), -1)  # Face outline
    cv2.circle(img, (300, 180), 10, (0, 0, 0), -1)  # Left eye
    cv2.circle(img, (340, 180), 10, (0, 0, 0), -1)  # Right eye
    cv2.ellipse(img, (320, 220), (20, 10), 0, 0, 180, (0, 0, 0), 2)  # Mouth
    
    # Test detection
    faces = detector.detect(img)
    print(f"Detected {len(faces)} faces")
    
    if faces:
        for i, face in enumerate(faces):
            print(f"Face {i+1}: bbox={face['bbox']}, score={face['score']:.3f}")
    
    return len(faces) > 0

def test_face_recognition():
    """Test face recognition pipeline"""
    print("\nTesting face recognition pipeline...")
    
    trainer = get_trainer()
    
    # Create test frames with synthetic faces
    frames = []
    for i in range(3):
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        # Draw a simple face
        cv2.circle(img, (320, 200), 80, (255, 255, 255), -1)
        cv2.circle(img, (300, 180), 10, (0, 0, 0), -1)
        cv2.circle(img, (340, 180), 10, (0, 0, 0), -1)
        cv2.ellipse(img, (320, 220), (20, 10), 0, 0, 180, (0, 0, 0), 2)
        frames.append(img)
    
    # Test training
    result = trainer.process_student_frames(frames, 1, min_faces=1)
    print(f"Training result: {result}")
    
    if result['success']:
        # Test recognition
        test_frame = frames[0]
        recognition_results = trainer.recognize_face(test_frame)
        print(f"Recognition results: {recognition_results}")
        return len(recognition_results) > 0
    
    return False

def test_with_webcam():
    """Test with webcam if available"""
    print("\nTesting with webcam...")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No webcam available")
        return False
    
    detector = get_detector()
    
    print("Press 'q' to quit, 's' to save frame for testing")
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Detect faces every 10 frames to avoid performance issues
        if frame_count % 10 == 0:
            faces = detector.detect(frame)
            print(f"Frame {frame_count}: Detected {len(faces)} faces")
            
            if faces:
                # Draw faces
                for face in faces:
                    bbox = face['bbox']
                    cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
                    cv2.putText(frame, f"{face['score']:.2f}", (bbox[0], bbox[1]-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        cv2.imshow('Face Detection Test', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Save frame for testing
            cv2.imwrite('test_frame.jpg', frame)
            print("Frame saved as test_frame.jpg")
    
    cap.release()
    cv2.destroyAllWindows()
    return True

if __name__ == "__main__":
    print("Face Detection and Recognition Test")
    print("=" * 40)
    
    # Test 1: Basic detection
    detection_works = test_face_detection()
    
    # Test 2: Recognition pipeline
    recognition_works = test_face_recognition()
    
    # Test 3: Webcam (optional)
    try:
        webcam_works = test_with_webcam()
    except Exception as e:
        print(f"Webcam test failed: {e}")
        webcam_works = False
    
    print("\n" + "=" * 40)
    print("Test Results:")
    print(f"Face Detection: {'PASS' if detection_works else 'FAIL'}")
    print(f"Face Recognition: {'PASS' if recognition_works else 'FAIL'}")
    print(f"Webcam Test: {'PASS' if webcam_works else 'FAIL'}")
    
    if detection_works and recognition_works:
        print("\nSUCCESS: System is working correctly!")
    else:
        print("\nISSUES: System has problems that need to be fixed.")
