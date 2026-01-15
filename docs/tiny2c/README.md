# Tiny2C / AC020 Thermal Camera Setup on Ubuntu x64 (USB-C, V4L2)

This guide documents **exactly what worked** to bring up a **Tiny2C / AC020 thermal camera** on **Ubuntu x64** and reach a **stable video stream via V4L2**.

The vendor SDK sample (`sample_cmd_camera_linux`) **does compile**, but **fails to open the device** (`ret = -619`).  
The **reliable and correct solution** is to use the **standard Linux UVC + V4L2 pipeline**, which works out of the box once verified.

This README is suitable for **GitHub** and avoids exposing private folder names.

---

## 1. System Information

- OS: Ubuntu 20.04 / 22.04 (x64)
- Kernel: `5.15.x`
- Camera: Tiny2C / AC020 (USB-C)
- USB VID:PID: `3474:4321`
- Interface: UVC (`uvcvideo`)
- Resolution: `256 × 194`
- Pixel format: `YUYV`

---

## 2. Prerequisites

Install required system tools:

```bash
sudo apt update
sudo apt install -y \
  build-essential \
  cmake \
  v4l-utils \
  ffmpeg \
  libusb-1.0-0-dev \
  pkg-config
```

## 3. Verify Camera Detection

### 3.1 USB detection

```
lsusb
```

Expected output (example):

```
Bus 001 Device 007: ID 3474:4321 Thermal Cam Co.,Ltd Camera 
```

### 3.2 Video devices

Before plugging the thermal camera:

```ls /dev/video*```

After plugging in the thermal camera:

```
ls /dev/video*
```

Expected additional devices:

```
/dev/video2
/dev/video3
```

### 3.3 Map devices to hardware

```
v4l2-ctl --list-devices
```

Expected:

```
Camera: Camera (usb-xxxx:xx:xx.x-xx):
    /dev/video2
    /dev/video3
```

## 4. Build the Camera SDK (CMake)

After extracting the vendor SDK package, navigate to the SDK root directory.

### Install build dependencies

```bash
sudo apt update
sudo apt install -y build-essential cmake pkg-config \
                    libusb-1.0-0-dev \
                    v4l-utils \
                    ffmpeg
```

Create a build directory:

```
cd <SDK_ROOT>
mkdir build
cd build
```

Configure with CMake (Ubuntu x64)

```
cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_SYSTEM_PROCESSOR=x86_64
```

If configuration succeeds, build the SDK:

```
make -j$(nproc)
```

### 5. SDK Runtime Library Path Setup

The SDK binaries depend on shared libraries located in:

```
<SDK_ROOT>/linux/x64
```

Export runtime library path

From the directory where the sample binary exists:

```
export LD_LIBRARY_PATH=<SDK_ROOT>/linux/x64:$LD_LIBRARY_PATH
```

To make this permanent (optional):

```
echo 'export LD_LIBRARY_PATH=<SDK_ROOT>/linux/x64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

Verify library resolution

```
ldd ./sample_cmd_camera_linux | grep libir
```

✅ Expected result:

No libraries should show not found.

### 6. Connect and Verify the Camera

Plug in the AC020 / Tiny2C USB thermal camera.

Verify USB detection

```
lsusb
```

ou should see a device corresponding to the thermal camera vendor.

### Verify V4L2 device nodes

```
ls /dev/video*
```

At least one /dev/videoX device should appear.

To inspect details:

```
v4l2-ctl --list-devices
```

### 7. Test SDK Sample Application

Run the vendor-provided sample:

```
sudo ./sample_cmd_camera_linux
```
If successful, the camera initializes and captures thermal frames.

Or

### 8. Identify Correct Video Device

Check which /dev/videoX node corresponds to the thermal stream:

```
v4l2-ctl --list-formats-ext -d /dev/video2
```
Look for: 
```
Resolution: 256x194

Pixel format: YUYV / YUYV422
```

### 9. Verify Video Stream with FFplay

Once the correct device is identified, test live video:

```
ffplay -f v4l2 \
       -pixel_format yuyv422 \
       -video_size 256x194 \
       /dev/video2
```


✅ Result:

Live thermal video stream appears in an FFplay window.

### 10. Notes

- The camera exposes a standard **V4L2** interface.
- Once **FFplay** works, the device can also be accessed via:
  - **Python** (`cv2.VideoCapture`)
  - **GStreamer**
  - **FFmpeg`
- No kernel driver compilation was required beyond

### 11. Troubleshooting

Permission issues

If /dev/videoX access fails:

```
sudo usermod -aG video $USER
logout
login
```

Confirm pixel format

```
v4l2-ctl -d /dev/video2 --get-fmt-video
```

---

SDK built with CMake

Runtime libraries resolved

Camera detected via USB

V4L2 device created

FFplay successfully displays thermal video.


