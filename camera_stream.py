#!/usr/bin/env python3
import io
import time
import threading
from picamera2 import Picamera2
from PIL import Image


class CameraStream:
    def __init__(self, resolution=(1280, 720), fps=15):
        self.picam2 = Picamera2()
        config = self.picam2.create_video_configuration(
            main={"size": resolution, "format": "RGB888"}
        )
        self.picam2.configure(config)
        self.picam2.start()
        time.sleep(2)
        self.frame_interval = 1.0 / fps

    def generate_mjpeg(self):
        last_frame_time = 0
        while True:
            current_time = time.time()
            if current_time - last_frame_time < self.frame_interval:
                time.sleep(0.001)
                continue

            frame = self.picam2.capture_array()
            buf = io.BytesIO()
            Image.fromarray(frame).save(buf, format="JPEG", quality=70)
            jpeg = buf.getvalue()

            yield (b"--FRAME\r\n"
                   b"Content-Type: image/jpeg\r\n"
                   b"Content-Length: " + str(len(jpeg)).encode() + b"\r\n\r\n" +
                   jpeg + b"\r\n")

            last_frame_time = current_time

    def stop(self):
        self.picam2.stop()