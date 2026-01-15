import cv2
import numpy as np
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

# ---- Timestamp ----
SHOW_TIMESTAMP = True
TIMESTAMP_FONT_SCALE = 0.35
TIMESTAMP_THICKNESS = 1
TIMESTAMP_ALPHA = 0.5

# ---- Scene modes ----
SCENE_MODE = "auto"   # "auto", "robust", "fixed"
FIXED_MIN = 8000
FIXED_MAX = 12000

# ---- Output ----
OUTPUT_MODE = "color"     # "color" or "grayscale"
ALLOW_FIXED_ON_UINT8 = False
# ============================================

os.makedirs(SAVE_DIR, exist_ok=True)

# ---------- Camera ----------
def open_camera():
    cap = cv2.VideoCapture(VIDEO_DEVICE, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    return cap

# ---------- Scaling ----------
def scale_thermal(frame):
    dtype = frame.dtype

    # --- UINT8 input (already scaled by driver) ---
    if dtype == np.uint8:
        if SCENE_MODE == "fixed" and not ALLOW_FIXED_ON_UINT8:
            raise RuntimeError(
                "FIXED mode requires uint16 input, "
                "but camera is outputting uint8"
            )
        return frame

    # --- UINT16 input (true thermal) ---
    if SCENE_MODE == "auto":
        return cv2.normalize(frame, None, 0, 255,
                              cv2.NORM_MINMAX).astype(np.uint8)

    if SCENE_MODE == "robust":
        lo = np.percentile(frame, 2)
        hi = np.percentile(frame, 98)
        clipped = np.clip(frame, lo, hi)
        return cv2.normalize(clipped, None, 0, 255,
                              cv2.NORM_MINMAX).astype(np.uint8)

    if SCENE_MODE == "fixed":
        clipped = np.clip(frame, FIXED_MIN, FIXED_MAX)
        return cv2.normalize(clipped, None, 0, 255,
                              cv2.NORM_MINMAX).astype(np.uint8)

    raise ValueError("Unknown scene mode")

# ---------- Timestamp ----------
def draw_timestamp(img):
    text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    font = cv2.FONT_HERSHEY_SIMPLEX
    (w, h), _ = cv2.getTextSize(text, font,
                               TIMESTAMP_FONT_SCALE,
                               TIMESTAMP_THICKNESS)

    overlay = img.copy()
    cv2.rectangle(overlay, (2, 2),
                  (6 + w, 6 + h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, TIMESTAMP_ALPHA,
                    img, 1 - TIMESTAMP_ALPHA, 0, img)

    cv2.putText(img, text, (4, 4 + h),
                font, TIMESTAMP_FONT_SCALE,
                (255, 255, 255),
                TIMESTAMP_THICKNESS,
                cv2.LINE_AA)
    return img

# ---------- Writer ----------
def create_writer():
    date_dir = datetime.now().strftime("%Y-%m-%d")
    full_dir = os.path.join(SAVE_DIR, date_dir)
    os.makedirs(full_dir, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"thermal_{ts}.mp4"
    path = os.path.join(full_dir, fname)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(
        path, fourcc, TARGET_FPS,
        (FRAME_WIDTH, FRAME_HEIGHT), isColor=True   # ← ALWAYS TRUE
        #isColor=(OUTPUT_MODE == "color")
    )
    return writer, path

# ---------- Main ----------
cap = open_camera()
assert cap.isOpened(), "Camera open failed"

print("⏳ Warming up camera...")
t0 = time.time()
while time.time() - t0 < WARMUP_SECONDS:
    cap.read()

print("✅ Camera ready")

try:
    while True:
        writer, path = create_writer()
        print(f"▶ Recording: {path}")

        frames_target = TARGET_FPS * CLIP_DURATION_MINUTES * 60
        frames_written = 0

        while frames_written < frames_target:
            ret, frame = cap.read()
            if not ret:
                continue

            frame_8 = scale_thermal(frame)

            # ---- Output mode ----
            '''
            if OUTPUT_MODE == "color":
                out = cv2.applyColorMap(frame_8,
                                        cv2.COLORMAP_INFERNO)
            else:
                out = cv2.cvtColor(frame_8,
                                   cv2.COLOR_GRAY2BGR)
            '''
            if OUTPUT_MODE == "color":
                # Ensure single channel before colormap
                if frame_8.ndim == 3:
                    frame_8 = cv2.cvtColor(frame_8, cv2.COLOR_BGR2GRAY)

                out = cv2.applyColorMap(frame_8, cv2.COLORMAP_INFERNO)

            else:  # grayscale
                if frame_8.ndim == 2:
                    # True grayscale → expand for VideoWriter
                    out = cv2.cvtColor(frame_8, cv2.COLOR_GRAY2BGR)
                else:
                    # Already BGR, leave as-is
                    out = frame_8


            if SHOW_TIMESTAMP:
                out = draw_timestamp(out)

            writer.write(out)
            frames_written += 1

            if SHOW_PREVIEW:
                preview = cv2.resize(
                    out, None,
                    fx=PREVIEW_SCALE,
                    fy=PREVIEW_SCALE,
                    interpolation=cv2.INTER_NEAREST
                )
                cv2.imshow("Thermal Preview", preview)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    raise KeyboardInterrupt

        writer.release()
        print(f"✔ Saved {frames_written} frames\n")

except KeyboardInterrupt:
    print("🛑 Stopped")

finally:
    cap.release()
    cv2.destroyAllWindows()

