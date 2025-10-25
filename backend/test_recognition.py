#!/usr/bin/env python3
"""
Simple test for face recognition with real webcam data
"""

import sys
import os
sys.path.append('.')

import cv2
import numpy as np
from app.services.training_service import get_trainer

def test_real_face_recognition():
    """Test face recognition with real webcam data"""
    print("Testing face recognition with real webcam data...")
    
    trainer = get_trainer()
    
    # Capture frames from webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No webcam available")
        return False
    
    print("Look at the camera and press 'c' to capture frames for training...")
    print("Press 'q' to quit")
    
    frames = []
    frame_count = 0
    
    while len(frames) < 10:  # Capture 10 frames
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Detect faces every 5 frames
        if frame_count % 5 == 0:
            faces = trainer.detector.detect(frame)
            if faces:
                print(f"Frame {frame_count}: Detected {len(faces)} faces")
                # Draw faces
                for face in faces:
                    bbox = face['bbox']
                    cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
                    cv2.putText(frame, f"{face['score']:.2f}", (bbox[0], bbox[1]-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        cv2.imshow('Face Recognition Test', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            # Capture frame for training
            frames.append(frame.copy())
            print(f"Captured frame {len(frames)}/10")
    
    cap.release()
    cv2.destroyAllWindows()
    
    if len(frames) == 0:
        print("No frames captured")
        return False
    
    print(f"\nProcessing {len(frames)} captured frames...")
    
    # Train with captured frames
    result = trainer.process_student_frames(frames, 1, min_faces=3)
    print(f"Training result: {result}")
    
    if result['success']:
        print("Training successful! Now testing recognition...")
        
        # Test recognition with new frames
        cap = cv2.VideoCapture(0)
        print("Look at the camera for recognition test. Press 'q' to quit.")
        
        recognition_count = 0
        while recognition_count < 20:  # Test for 20 frames
            ret, frame = cap.read()
            if not ret:
                break
            
            recognition_count += 1
            
            # Recognize faces
            if recognition_count % 3 == 0:  # Every 3rd frame
                results = trainer.recognize_face(frame)
                
                # Draw results
                for result in results:
                    bbox = result['bbox']
                    if result['student_id'] is not None:
                        color = (0, 255, 0)  # Green for recognized
                        text = f"Student {result['student_id']} ({result['confidence']:.2f})"
                    else:
                        color = (0, 0, 255)  # Red for unknown
                        text = "Unknown"
                    
                    cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
                    cv2.putText(frame, text, (bbox[0], bbox[1]-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                print(f"Recognition frame {recognition_count}: {len(results)} faces detected")
            
            cv2.imshow('Face Recognition Test', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        return True
    else:
        print("Training failed")
        return False

if __name__ == "__main__":
    print("Real Face Recognition Test")
    print("=" * 40)
    
    success = test_real_face_recognition()
    
    print("\n" + "=" * 40)
    if success:
        print("SUCCESS: Face recognition is working!")
    else:
        print("FAILED: Face recognition needs more work.")
