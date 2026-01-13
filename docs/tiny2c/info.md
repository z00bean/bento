# AC020 / Tiny2C Thermal Camera – Linux (Ubuntu x64) SDK Usage Guide

### Folder Overview

The `libir_sample` directory contains example programs and supporting code for using the AC020/Tiny2C thermal camera on Linux and Windows platforms. Inside this folder, `simple_sample` and `complex_sample` contain ready-to-build demonstration programs. `simple_sample` provides a minimal example that captures a single thermal frame and saves it to a binary file, while `complex_sample` contains more advanced examples that may handle multiple frames, additional processing, or extended features of the camera.

Other subfolders serve specific purposes: `common` holds shared utility code used by multiple samples, `drivers` contains low-level hardware interface code, `interfaces` defines camera control and data structures, and `components` may include modular pieces of the SDK. There are also configuration files in `config`, third-party dependencies in `thirdparty`, and miscellaneous helper scripts in `other`. Together, these folders organize the SDK to separate sample applications, reusable libraries, and device-specific drivers for easier development and experimentation.



This documents how to **build and run the official AC020 (Tiny2C) Linux SDK**
to capture thermal image data from the camera on **Ubuntu x64**.

The SDK does **not** display live video on Linux.  
It captures **one frame** and saves it as a binary file (`frame_data.bin`), which must be
parsed and displayed manually.

This behavior is **by design** in the vendor SDK.

---

## Tested Environment

- OS: Ubuntu 20.04 / 22.04 (x86_64)
- Camera: AC020 / Tiny2C (USB)
- SDK: `AC020_win&&linux_SDK_2.4.21`
- Interface: USB (UVC control + video)

---

## SDK Path Used

```
AC020_win&&linux_SDK_2.4.21 3/
└─ AC020_win&&linux_SDK/
└─ libir_sample/
└─ simple_sample/
└─ cmd_camera/
└─ linux/
└─ uvc_usb/
```


---

## 1. Install Dependencies

Run:

```
bash
sudo apt update
sudo apt install -y \
  build-essential \
  cmake \
  libusb-1.0-0-dev \
  python3 \
  python3-opencv
```

2. Go to the Sample Directory

Run:
```
cd "AC020_win&&linux_SDK_2.4.21 3/AC020_win&&linux_SDK/libir_sample/simple_sample/cmd_camera/linux/uvc_usb"
```

Verify files:

```
ls
```

Expected output:

```
CMakeLists.txt
README.md
cross_compilation_tool_chain.sh
sample.cpp
```

3. Ignore Cross-Compilation

Do not run:
```
sh cross_compilation_tool_chain.sh
```

4. Build the Sample (Native Ubuntu x64)

Run:

```
mkdir build
cd build
cmake ..
make
```

Verify the executable exists:
```ls```

Expected output:

```sample_cmd_camera_linux```

5. Export SDK Libraries

The executable depends on shared libraries located in linux/x64.

Run:

```export LD_LIBRARY_PATH=../../../../../linux/x64:$LD_LIBRARY_PATH```

Verify library resolution:
```
ldd ./sample_cmd_camera_linux | grep libir
```

No libraries should show not found.


6. Connect and Verify the Camera

Plug in the AC020 / Tiny2C USB camera.

Run:

```
lsusb
ls /dev/video*
```

At least one /dev/videoX device must be present.

7. Capture a Thermal Frame

Run:

```
sudo ./sample_cmd_camera_linux
```
Expected behavior:

No GUI window

Program exits after initialization

A binary file is created

Verify:
```ls```

Expected output:

```frame_data.bin```

This file contains:
```
[ image data ]
[ temperature data ]
[ metadata rows ]
```


8. View the Thermal Image (Quick Viewer)

Create a file named view.py in the same directory:

```
import numpy as np
import cv2

WIDTH = 384
HEIGHT = 288

data = np.fromfile("frame_data.bin", dtype=np.uint8)

# First section is image data (YUYV, 2 bytes per pixel)
img = data[:WIDTH * HEIGHT * 2].reshape((HEIGHT, WIDTH, 2))
gray = img[:, :, 0]

cv2.normalize(gray, gray, 0, 255, cv2.NORM_MINMAX)
gray = gray.astype(np.uint8)

cv2.imshow("Thermal Image", gray)
cv2.waitKey(0)
```

Run:

```python3 view.py```

A grayscale thermal image should appear.


##Common Problems

error while loading shared libraries

Fix LD_LIBRARY_PATH and retry.

No frame_data.bin

Verify camera detection:

dmesg | tail

Garbled or incorrect image: Adjust resolution values in view.py.

Common resolutions: 384×288 or 256×192

## Next Steps

- Modify `sample.cpp` to capture frames continuously
- Add OpenCV display on Linux for live video
- Parse temperature data from the frame buffer
- Convert frames to RGB using a custom color palette
- Stream processed frames using `ffmpeg`
