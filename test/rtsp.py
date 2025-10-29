# import cv2

# cap = cv2.VideoCapture("rtsp://user:User@123@10.10.131.71:554/live.sdp")

# if not cap.isOpened():
#     print("❌ Failed to open RTSP stream")
# else:
#     print("✅ Stream opened successfully")
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print("⚠️ Frame not received")
#             break
#         cv2.imshow("RTSP Test", frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

# cap.release()
# cv2.destroyAllWindows()
import cv2
import time

url = "rtsp://user:User%40123@10.10.131.71:554/live.sdp"  # replace @ with %40
cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
time.sleep(2)

if not cap.isOpened():
    print("❌ Failed to open RTSP stream")
else:
    print("✅ Stream opened successfully")
    while True:
        ret, frame = cap.read()
        print("Frame received:", ret)
        if not ret:
            print("⚠️ Frame not received")
            break
        cv2.imshow("RTSP Stream", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
