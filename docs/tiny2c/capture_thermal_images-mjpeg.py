# conda activate yv8.2.14

# conda activate yv8.2.14

import cv2
import os
import time
from datetime import datetime

# ================== CONFIG ==================
VIDEO_DEVICE = "/dev/video2"

FRAME_WIDTH  = 256
FRAME_HEIGHT = 194

CAPTURE_INTERVAL_SEC = 10
SAVE_DIR = "images/thermal_tiny2c_mjpeg"

WARMUP_SECONDS = 4
SKIP_FRAMES = 3

# JPEG options
SAVE_AS_JPEG = True         # True = save JPEG, False = save PNG
JPEG_QUALITY = 90            # 0-100, higher = better quality
# ============================================

os.makedirs(SAVE_DIR, exist_ok=True)

cap = cv2.VideoCapture(VIDEO_DEVICE, cv2.CAP_V4L2)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

# ✅ Request MJPEG explicitly
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

assert cap.isOpened(), "❌ Failed to open camera"

print("⏳ Warming up camera...")
time.sleep(WARMUP_SECONDS)

print("📸 Thermal capture started (MJPEG/RGB)")

try:
    while True:
        # Flush initial unstable frames
        for _ in range(SKIP_FRAMES):
            cap.read()

        ret, frame_bgr = cap.read()
        if not ret:
            print("⚠ Frame read failed")
            time.sleep(2)
            continue

        print("Frame:", frame_bgr.shape, frame_bgr.dtype)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if SAVE_AS_JPEG:
            filename = f"thermal_{timestamp}.jpg"
            filepath = os.path.join(SAVE_DIR, filename)
            # Save JPEG with compression quality
            cv2.imwrite(filepath, frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        else:
            filename = f"thermal_{timestamp}.png"
            filepath = os.path.join(SAVE_DIR, filename)
            cv2.imwrite(filepath, frame_bgr)

        print(f"✔ Saved {filepath}")

        time.sleep(CAPTURE_INTERVAL_SEC)

except KeyboardInterrupt:
    print("\n🛑 Stopped by user")

finally:
    cap.release()

