# conda activate yv8.2.14

import cv2
import os
import time
from datetime import datetime

# ================== CONFIG ==================
VIDEO_DEVICE = "/dev/video2"
FRAME_WIDTH = 256
FRAME_HEIGHT = 194

CAPTURE_INTERVAL_SEC = 10      # 30 / 60 / 90
SAVE_DIR = "iamges/thermal_tiny2c/"
# ============================================

os.makedirs(SAVE_DIR, exist_ok=True)

cap = cv2.VideoCapture(VIDEO_DEVICE, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))

assert cap.isOpened(), "❌ Failed to open camera"

print("📸 Thermal capture started (Ctrl+C to stop)")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠ Frame read failed")
            time.sleep(1)
            continue

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"thermal_{timestamp}.png"
        filepath = os.path.join(SAVE_DIR, filename)

        cv2.imwrite(filepath, frame)
        print(f"✔ Saved {filepath}")

        time.sleep(CAPTURE_INTERVAL_SEC)

except KeyboardInterrupt:
    print("\n🛑 Stopped by user")

finally:
    cap.release()

