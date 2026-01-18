#!/usr/bin/env python3
import os
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

# === Project notes ============================================================
# This script captures video from a Raspberry Pi Camera and writes out an HLS
# (HTTP Live Streaming) playlist + short .ts segments to a local directory.                                                        
# ==============================================================================

# Ensure output directory exists
OUT_DIR = "/home/glen/hls"
os.makedirs(OUT_DIR, exist_ok=True)

# Create and configure the camera for 1280x720 video
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (1280, 720)}))

# Hardware video encoder (H.264). Lower bitrate if WiFi/CPU struggles.
encoder = H264Encoder(bitrate=3_000_000)

# FFmpegOutput tells Picamera2 to pipe encoded video into an HLS muxer.
# Live HLS: short segments, rolling list, delete old segments automatically
output = FfmpegOutput(
    "-f hls "
    "-hls_time 2 "
    "-hls_list_size 6 "
    "-hls_flags delete_segments+append_list+independent_segments "
    "-hls_delete_threshold 1 "
    f"-hls_segment_filename {OUT_DIR}/stream%03d.ts "
    f"{OUT_DIR}/stream.m3u8"
)

try:
    # Start recording: camera -> H.264 encoder -> FFmpeg (HLS) -> files
    picam2.start_recording(encoder, output)
    print("Streaming started.")
    print("Playlist URL: http://192.168.28.25:8000/stream.m3u8 (Python http.server)")
    print("or            http://192.168.28.25/stream.m3u8 (nginx, if configured)")

    # Keep process alive
    while True:
        pass
    
except KeyboardInterrupt:
    # CTRL+C stops the script gracefully
    print("Stopping stream...")

finally:
    # Always stop recording to release the camera cleanly
    try:
        picam2.stop_recording()
    except Exception as e:
        print(f"Stop error (safe to ignore if already stopped): {e}")