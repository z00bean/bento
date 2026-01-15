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
SAVE_DIR = "images/thermal_tint2c-y16"

WARMUP_SECONDS = 2
SKIP_FRAMES = 3          # flush bad frames

# JPEG options
SAVE_AS_JPEG = True       # True = save JPEG, False = save PNG
JPEG_QUALITY = 90         # 0-100, higher = better quality
# ============================================

os.makedirs(SAVE_DIR, exist_ok=True)

cap = cv2.VideoCapture(VIDEO_DEVICE, cv2.CAP_V4L2)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

assert cap.isOpened(), "❌ Failed to open camera"

# ---------- Warm-up ----------
print("⏳ Warming up thermal camera...")
time.sleep(WARMUP_SECONDS)

print("📸 Thermal capture started (Y16)")

try:
    while True:
        # Flush unstable frames
        for _ in range(SKIP_FRAMES):
            cap.read()
            time.sleep(0.1)  # small delay between reads

        ret, frame_16 = cap.read()
        if not ret:
            print("⚠ Frame read failed")
            time.sleep(2)
            continue

        # Sanity check
        print("Frame:", frame_16.shape, frame_16.dtype)

        # Normalize 16-bit → 8-bit
        frame_8 = cv2.normalize(
            frame_16, None, 0, 255, cv2.NORM_MINMAX
        ).astype("uint8")

        # Apply thermal colormap
        frame_color = cv2.applyColorMap(
            frame_8, cv2.COLORMAP_INFERNO
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if SAVE_AS_JPEG:
            filename = f"thermal_{timestamp}.jpg"
            filepath = os.path.join(SAVE_DIR, filename)
            # Save as JPEG with compression quality
            cv2.imwrite(filepath, frame_color, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        else:
            filename = f"thermal_{timestamp}.png"
            filepath = os.path.join(SAVE_DIR, filename)
            cv2.imwrite(filepath, frame_color)

        print(f"✔ Saved {filepath}")

        time.sleep(CAPTURE_INTERVAL_SEC)

except KeyboardInterrupt:
    print("\n🛑 Stopped by user")

finally:
    cap.release()

