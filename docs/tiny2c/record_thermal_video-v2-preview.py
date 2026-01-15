# conda activate yv8.2.14

import cv2
import os
import time
from datetime import datetime

# ================== CONFIG ==================
VIDEO_DEVICE = "/dev/video2"

FRAME_WIDTH  = 256
FRAME_HEIGHT = 194

TARGET_FPS = 30
CLIP_DURATION_MINUTES = 1

SAVE_DIR = "clips/thermal_tiny2c"
USE_MP4 = True

WARMUP_SECONDS = 3

# ---- Preview ----
SHOW_PREVIEW = True
PREVIEW_SCALE = 2.0

# ---- Timestamp overlay ----
SHOW_TIMESTAMP = True
TIMESTAMP_FONT_SCALE = 0.35     # tuned for tiny frames
TIMESTAMP_THICKNESS = 1
TIMESTAMP_PADDING = 3
TIMESTAMP_ALPHA = 0.5           # transparency of background
# ============================================

os.makedirs(SAVE_DIR, exist_ok=True)

def open_camera():
    cap = cv2.VideoCapture(VIDEO_DEVICE, cv2.CAP_V4L2)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))

    return cap

def get_dated_save_dir():
    date_folder = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(SAVE_DIR, date_folder)
    os.makedirs(path, exist_ok=True)
    return path

def create_writer():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_dir = get_dated_save_dir()

    if USE_MP4:
        filename = f"thermal_{timestamp}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    else:
        filename = f"thermal_{timestamp}.avi"
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')

    path = os.path.join(save_dir, filename)

    writer = cv2.VideoWriter(
        path,
        fourcc,
        TARGET_FPS,
        (FRAME_WIDTH, FRAME_HEIGHT)
    )

    return writer, path

def draw_timestamp(frame):
    text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    font = cv2.FONT_HERSHEY_SIMPLEX

    (tw, th), baseline = cv2.getTextSize(
        text, font, TIMESTAMP_FONT_SCALE, TIMESTAMP_THICKNESS
    )

    x, y = 2, 2 + th

    # Background rectangle
    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (x - TIMESTAMP_PADDING, y - th - TIMESTAMP_PADDING),
        (x + tw + TIMESTAMP_PADDING, y + baseline + TIMESTAMP_PADDING),
        (0, 0, 0),
        -1
    )

    # Blend translucent background
    cv2.addWeighted(
        overlay, TIMESTAMP_ALPHA,
        frame, 1 - TIMESTAMP_ALPHA,
        0, frame
    )

    # Draw text
    cv2.putText(
        frame, text,
        (x, y),
        font,
        TIMESTAMP_FONT_SCALE,
        (255, 255, 255),
        TIMESTAMP_THICKNESS,
        cv2.LINE_AA
    )

    return frame

cap = open_camera()
assert cap.isOpened(), "❌ Failed to open camera"

# -------- Warm-up --------
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

            if SHOW_TIMESTAMP:
                frame = draw_timestamp(frame)

            writer.write(frame)
            written += 1

            # ---------- Preview ----------
            if SHOW_PREVIEW:
                preview = frame
                if PREVIEW_SCALE != 1.0:
                    preview = cv2.resize(
                        preview,
                        None,
                        fx=PREVIEW_SCALE,
                        fy=PREVIEW_SCALE,
                        interpolation=cv2.INTER_NEAREST
                    )

                cv2.imshow("Thermal Preview", preview)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    raise KeyboardInterrupt

        elapsed = time.time() - t_start
        writer.release()

        print(f"✔ Saved {written} frames")
        print(f"⏱ Real time: {elapsed:.1f}s")
        print(f"🎞 Video duration: {written / TARGET_FPS:.1f}s\n")

except KeyboardInterrupt:
    print("\n🛑 Stopped by user")

finally:
    cap.release()
    cv2.destroyAllWindows()

