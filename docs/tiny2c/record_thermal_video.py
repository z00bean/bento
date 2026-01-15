# conda activate yv8.2.14

import cv2
import os
import time
from datetime import datetime

# ================== CONFIG ==================
VIDEO_DEVICE = "/dev/video2"

FRAME_WIDTH  = 256
FRAME_HEIGHT = 194

TARGET_FPS = 30                  # desired fps in file
CLIP_DURATION_MINUTES = 1        # exact clip length

SAVE_DIR = "clips/thermal_tiny2c"
USE_MP4 = True                   # <-- MP4 ON by default
WARMUP_SECONDS = 3               # camera stabilization
# ============================================

os.makedirs(SAVE_DIR, exist_ok=True)

def open_camera():
    cap = cv2.VideoCapture(VIDEO_DEVICE, cv2.CAP_V4L2)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))

    # Let driver decide FPS (more reliable for thermal cams)
    return cap

def create_writer():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if USE_MP4:
        filename = f"thermal_{timestamp}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    else:
        filename = f"thermal_{timestamp}.avi"
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')

    path = os.path.join(SAVE_DIR, filename)

    writer = cv2.VideoWriter(
        path,
        fourcc,
        TARGET_FPS,
        (FRAME_WIDTH, FRAME_HEIGHT)
    )

    return writer, path

cap = open_camera()
assert cap.isOpened(), "❌ Failed to open camera"

# -------- Camera Warm-up --------
print("⏳ Warming up camera...")
t0 = time.time()
while time.time() - t0 < WARMUP_SECONDS:
    cap.read()

print("✅ Camera ready")

try:
    while True:
        writer, filepath = create_writer()
        print(f"▶ Recording: {filepath}")

        total_frames = TARGET_FPS * CLIP_DURATION_MINUTES * 60
        written = 0
        t_start = time.time()

        while written < total_frames:
            ret, frame = cap.read()
            if not ret:
                print("⚠ Frame drop")
                continue

            writer.write(frame)
            written += 1

        elapsed = time.time() - t_start
        writer.release()

        print(f"✔ Saved {written} frames")
        print(f"⏱ Real time: {elapsed:.1f}s")
        print(f"🎞 Video duration: {written / TARGET_FPS:.1f}s\n")

except KeyboardInterrupt:
    print("\n🛑 Stopped by user")

finally:
    cap.release()

