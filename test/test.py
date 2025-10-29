# import cv2
# from insightface.app import FaceAnalysis
# from cv2 import dnn_superres

# # ✅ 1. Initialize super-resolution model (Option 3)
# sr = dnn_superres.DnnSuperResImpl_create()
# sr.readModel("test\EDSR_x2.pb")  # You must download this model once
# sr.setModel("edsr", 2)      # Upscale factor = 2x

# # ✅ 2. Initialize the FaceAnalysis app with stronger model (Option 1)
# # buffalo_l = large model with better small-face detection
# app = FaceAnalysis(name="buffalo_l", providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
# app.prepare(ctx_id=0, det_size=(640, 360))  # higher resolution (Option 2)

# # ✅ 3. Open the RTSP stream (with encoded password)
# url = 'rtsp://user:User%40123@10.10.131.71:554/live.sdp'
# cap = cv2.VideoCapture(url)

# if not cap.isOpened():
#     print("❌ Unable to access the camera.")
#     exit()

# print("✅ Camera started. Press 'q' to quit.")

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("⚠️ Failed to capture frame from camera.")
#         break

#     # --- Apply Super Resolution ---
#     try:
#         frame = sr.upsample(frame)  # enhances details for small/distant faces
#     except Exception as e:
#         print(f"⚠️ Super-resolution failed: {e}")

#     # --- Detect faces ---
#     faces = app.get(frame)

#     if len(faces) == 0:
#         cv2.putText(frame, "No face detected", (20, 40),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
#     else:
#         for face in faces:
#             box = face.bbox.astype(int)  # [x1, y1, x2, y2]
#             cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)

#             if face.landmark is not None:
#                 for landmark in face.landmark.astype(int):
#                     cv2.circle(frame, tuple(landmark), 2, (0, 0, 255), -1)

#     cv2.imshow("Enhanced SCRFD Face Detection", frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()
# print("👋 Camera closed successfully.")


import cv2
from insightface.app import FaceAnalysis
import os
import time
import onnxruntime as ort

print("🚀 Initializing GPU-accelerated face detection system...")
print(f"� Available ONNX providers: {ort.get_available_providers()}")

# Check GPU availability
if 'CUDAExecutionProvider' in ort.get_available_providers():
    print("✅ GPU (CUDA) is available!")
    providers = ['CUDAExecutionProvider']
else:
    print("⚠️ GPU not available, using CPU")
    providers = ['CPUExecutionProvider']

# --- Face model (NO SUPER RESOLUTION - causes lag) ---
print("🔧 Initializing face detection model with GPU...")
try:
    app = FaceAnalysis(name="buffalo_l", providers=providers)
    app.prepare(ctx_id=0, det_size=(640, 480))  # Reduced for speed
    print("✅ Face detection model loaded")
    print(f"   Using provider: {providers[0]}")
except Exception as e:
    print(f"❌ Failed to initialize face model: {e}")
    exit(1)

# --- RTSP stream ---
print("📹 Connecting to RTSP stream...")
url = 'rtsp://user:User%40123@10.10.131.71:554/live.sdp'
cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize latency
# Don't set FPS - let camera provide its natural rate

if not cap.isOpened():
    print("❌ Unable to access the camera. Please check:")
    print("   - Network connection")
    print("   - Camera IP address and credentials")
    print("   - RTSP URL format")
    exit(1)

print("✅ Camera connected successfully!")
print("📊 Press 'q' to quit | Press 'p' to process every Nth frame")

cv2.namedWindow("GPU-Accelerated Face Detection", cv2.WINDOW_NORMAL)
cv2.resizeWindow("GPU-Accelerated Face Detection", 1280, 720)

frame_count = 0
processed_count = 0
start_time = time.time()
skip_frames = 1  # Process every frame initially (1 = no skip)
faces = []  # Store last detection result

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Failed to capture frame. Retrying...")
        time.sleep(0.1)
        continue

    frame_count += 1
    
    # Process face detection only on certain frames (skip others for speed)
    if frame_count % skip_frames == 0:
        try:
            faces = app.get(frame)
            processed_count += 1
        except Exception as e:
            print(f"⚠️ Face detection failed: {e}")
            faces = []

    # Draw results (use last detection result)
    if len(faces) == 0:
        cv2.putText(frame, "No face detected", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    else:
        for idx, face in enumerate(faces):
            box = face.bbox.astype(int)
            # Draw bounding box
            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 3)
            
            # Draw face number
            cv2.putText(frame, f"Face {idx + 1}", (box[0], box[1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Draw landmarks if available
            if face.landmark is not None:
                for landmark in face.landmark.astype(int):
                    cv2.circle(frame, tuple(landmark), 2, (0, 0, 255), -1)
    
    # Display FPS and statistics
    elapsed = time.time() - start_time
    fps = frame_count / elapsed if elapsed > 0 else 0
    detection_fps = processed_count / elapsed if elapsed > 0 else 0
    
    cv2.putText(frame, f"Display FPS: {fps:.1f} | Detection FPS: {detection_fps:.1f}", 
                (20, frame.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Faces: {len(faces)} | Skip: 1/{skip_frames}", 
                (20, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    cv2.putText(frame, f"GPU: {providers[0]}", 
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("GPU-Accelerated Face Detection", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("🛑 Stopping camera...")
        break
    elif key == ord('p'):
        skip_frames = (skip_frames % 5) + 1  # Cycle through 1, 2, 3, 4, 5
        print(f"🔄 Processing every {skip_frames} frame(s)")

cap.release()
cv2.destroyAllWindows()

# Print statistics
elapsed = time.time() - start_time
print("\n📊 Session Statistics:")
print(f"   Total frames displayed: {frame_count}")
print(f"   Total frames processed: {processed_count}")
print(f"   Total time: {elapsed:.2f} seconds")
print(f"   Average display FPS: {frame_count / elapsed:.2f}")
print(f"   Average detection FPS: {processed_count / elapsed:.2f}")
print(f"   GPU Provider: {providers[0]}")
print("👋 Camera closed successfully.")
