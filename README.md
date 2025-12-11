
# Raspberry Pi Baby Monitor – HLS & MJPEG Streaming

A simple Raspberry Pi camera streaming setup I’m building as a **LAN baby monitor**.  
The repo currently contains two approaches:
- **MJPEG over HTTP** via `image_uploader.py
- **HLS** HTTP Live Streaming via `video_uploader.py

## Why two scripts?

I initially tried short **video uploads** to the LAN (HLS segments) but wanted **constant streaming** with minimal delay, so I created the MJPEG approach to push images continuously and delete them from memory, providing a fairly solid “video-like” stream for my baby monitor. In MJPEG, the server sends a sequence of JPEGs in a multipart response; most browsers can display this as motion.

## Setup Issues
I first tried Raspberry Pi OS Lite over SSH, but I couldn’t get the camera stack working reliably with sudo apt alone. Switching to the Desktop image solved it because the video/camera software was already present. I still configure everything via SSH, but Desktop made initial camera enablement much easier. I’ll keep iterating on headless/Lite instructions as I refine the install steps.

## Inspirations & References

- I took inspiration from the **Picamera2** project (great API and examples):  
  `picamera2.py` – https://github.com/raspberrypi/picamera2/blob/main/picamera2/picamera2.py

- This YouTube video motivated the baby monitor idea:  
  **“Raspberry Pi Security Camera/Monitor”** – https://www.youtube.com/watch?v=OaexSiNUwuE

> Note: My code is intentionally simple for learning; I’ll be adding more features, improving performance, and cleaning things up as I go.

## Current Features

- **HLS**: Rolling playlist and short segments for resilient streaming; old segments are deleted automatically.
- **MJPEG**: Continuous frames served from Flask, with optional frame-rate cap to reduce CPU/bandwidth.
- **Camera controls**: Brief AE/AWB stabilization and then lock exposure/white balance for consistent image.

## Getting Started

### Prerequisites
- Raspberry Pi with camera module, configured with **Pi Camera Module**.
- Python environment with: `picamera2`, `Pillow`, `Flask`.  
- For HLS viewing, any HTTP server (e.g., `python -m http.server`) or nginx.

I connected to my Pi via SSH, however you may wish to do it using the GUI. Once you're in the Pi:

# Base update
sudo apt update && sudo apt -y full-upgrade

# Camera stack + Picamera2
sudo apt install -y libcamera-apps python3-picamera
# If using Raspberry Pi OS Desktop, Picamera2 may already be installed.

# Python bits your scripts need
sudo apt install -y python3-flask python3-pil ffmpeg

# Enable camera
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot


### Run MJPEG (Flask)
```bash
python3 image_uploader.py
# Then open http://<pi-ip>:8080/ in your browser