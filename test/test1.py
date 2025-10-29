import cv2
from insightface.app import FaceAnalysis

# Initialize FaceAnalysis
app = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])

# Prepare the model (adjust detection size as needed)
app.prepare(ctx_id=0, det_size=(640, 640))  # 1280x1280 is too large for most streams

# Optional: lower detection confidence threshold for small faces
app.models['detection'].confidence_threshold = 0.3

# RTSP stream
url = 'rtsp://user:User%40123@10.10.131.71:554/live.sdp'
cap = cv2.VideoCapture(url)

if not cap.isOpened():
    print("❌ Failed to open RTSP stream.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        print("⚠️ Frame not received from camera.")
        continue

    # Detect faces
    faces = app.get(frame)

    if not faces:
        cv2.putText(frame, "No faces detected", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    else:
        for face in faces:
            # Draw bounding box
            box = face.bbox.astype(int)
            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)

            # Draw landmarks safely
            if face.landmark is not None:
                for landmark in face.landmark.astype(int):
                    cv2.circle(frame, tuple(landmark), 2, (0, 0, 255), -1)
            else:
                print("⚠️ No landmarks for one detected face.")

    cv2.imshow("SCRFD Face Detection (RTSP)", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()