# conda activate yv8.2.14

import cv2
import os
import time
from datetime import datetime

# ================== CONFIG ==================
VIDEO_DEVICE = "/dev/video2" 	# AW m15-Ubuntu20.04: /dev/video2
FRAME_WIDTH = 256
FRAME_HEIGHT = 194
FPS = 30

CLIP_DURATION_MINUTES = 1      # in minutes
SAVE_DIR = "clips/thermal_tiny2c"
# ============================================

os.makedirs(SAVE_DIR, exist_ok=True)

def open_camera():
    cap = cv2.VideoCapture(VIDEO_DEVICE, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
    return cap

def create_writer():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"thermal_{timestamp}.avi"
    path = os.path.join(SAVE_DIR, filename)

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    writer = cv2.VideoWriter(path, fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT))
    return writer, path

cap = open_camera()
assert cap.isOpened(), "❌ Failed to open camera"

try:
    while True:
        writer, filepath = create_writer()
        print(f"▶ Recording: {filepath}")

        start_time = time.time()
        duration = CLIP_DURATION_MINUTES * 60

        while time.time() - start_time < duration:
            ret, frame = cap.read()
            if not ret:
                print("⚠ Frame drop")
                break

            writer.write(frame)

        writer.release()
        print("✔ Clip saved")

except KeyboardInterrupt:
    print("\n🛑 Stopped by user")

finally:
    cap.release()

