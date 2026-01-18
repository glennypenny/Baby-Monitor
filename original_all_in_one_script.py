#!/usr/bin/env python3
import io
import time
import threading
import numpy as np
from flask import Flask, Response, request
from flask import send_file
from picamera2 import Picamera2
from PIL import Image
from gpiozero import MotionSensor
import pyaudio  # ADDED

# ============================================================================
# STEP 1: SETUP MOTION SENSOR FIRST (BEFORE FLASK)
# ============================================================================

print("🚨 Setting up motion sensor on GPIO 12...")
pir = MotionSensor(17)
motion_detected_now = False
last_motion_time = "Never"

def check_motion():
    """Simplified motion detection"""
    global motion_detected_now, last_motion_time

    print("   Waiting 2 seconds for PIR warm-up...")
    time.sleep(2)
    print("   ✅ Motion sensor ready!")

    while True:
        if pir.motion_detected:
            motion_detected_now = True
            last_motion_time = time.strftime("%H:%M:%S.%f")[:-3]
            print(f"[{last_motion_time}] 🚨 MOTION DETECTED!")
            time.sleep(0.5)
            motion_detected_now = False

        time.sleep(0.02)

print("   Starting motion detection in background...")
motion_thread = threading.Thread(target=check_motion, daemon=True)
motion_thread.start()

# ============================================================================
# STEP 2: SETUP CAMERA
# ============================================================================

print("\n📷 Setting up camera...")
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (1280, 720), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()

# Let auto-exposure settle
time.sleep(2.0)
md = picam2.capture_metadata()

# Apply camera settings (your existing code)
exposure_time = md.get("ExposureTime")
analogue_gain = md.get("AnalogueGain")
colour_gains = md.get("ColourGains")

controls_to_set = {}
if exposure_time is not None:
    controls_to_set["ExposureTime"] = exposure_time
if analogue_gain is not None:
    controls_to_set["AnalogueGain"] = analogue_gain
if colour_gains is not None:
    controls_to_set["ColourGains"] = colour_gains

controls_to_set["AeEnable"] = False
controls_to_set["AwbEnable"] = False

if controls_to_set:
    picam2.set_controls(controls_to_set)

print("   ✅ Camera ready!")

# ============================================================================
# STEP 3: SETUP MICROPHONE FOR LIVE STREAMING
# ============================================================================

print("\n🎤 Setting up microphone...")

# Audio settings
CHUNK = 128
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
DEVICE_INDEX = 3  # Your USB mic from arecord -l

# Initialize PyAudio
p = pyaudio.PyAudio()

# ============================================================================
# STEP 4: SETUP FLASK APP
# ============================================================================

app = Flask(__name__)


def generate_mjpeg():
    """Yield an endless MJPEG stream."""
    while True:
        frame = picam2.capture_array()
        buf = io.BytesIO()
        Image.fromarray(frame).save(buf, format="JPEG", quality=80)
        jpeg = buf.getvalue()

        yield (b"--FRAME\r\n"
               b"Content-Type: image/jpeg\r\n"
               b"Content-Length: " + str(len(jpeg)).encode() + b"\r\n\r\n" +
               jpeg + b"\r\n")


# ============================================================================
# UPDATED HTML PAGE WITH AUDIO PLAYER
# ============================================================================

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>G&S Baby Monitor</title>
    <style>
        body {
            background: black;
            color: white;
            font-family: Arial;
            text-align: center;
            padding: 20px;
        }
        #video {
            width: 80%;
            max-width: 800px;
            border: 3px solid #444;
            border-radius: 10px;
            display: block;
            margin: 0 auto;
            transform: rotate(180deg);
        }
        .audio-container {
            width: 90%;
            max-width: 900px;
            margin: 20px auto;
            background: #2c3e50;
            padding: 20px;
            border-radius: 10px;
        }
        audio {
            width: 100%;
            height: 50px;
        }
        
        .status {
            background: #27ae60;
            padding: 20px;
            margin: 20px auto;
            width: 80%;
            max-width: 800px;
            border-radius: 10px;
            font-size: 20px;
        }
        .alert {
            background: #e74c3c;
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        button {
            background: #3498db;
            color: white;
            border: none;
            padding: 15px 30px;
            margin: 10px;
            border-radius: 5px;
            font-size: 18px;
            cursor: pointer;
        }
        .controls {
            margin: 20px;
        }
    </style>
</head>
<body>
    <h1>👶 Baby Monitor with Live Audio</h1>

    <img id="video" src="/video" alt="Live Feed">

<div class="audio-container">
    <h3>🎤 Live Audio Stream</h3>
    <audio id="audio-stream" controls>
        <source src="/audio" type="audio/x-wav">
    </audio>
    <p><small>Volume: <input type="range" id="volume" min="0" max="1" step="0.1" value="0.5" 
           onchange="document.getElementById('audio-stream').volume = this.value;"></small></p>
    <p id="audio-help" style="font-size: 12px; color: #95a5a6;">
        <span id="desktop-hint">Click play to start audio</span>
        <span id="mobile-hint" style="display:none; color:#f39c12;">
            📱 Mobile: You may need to tap twice to start audio
        </span>
    </p>
</div>

    <div id="motion-status" class="status">
        Motion: <span id="motion-text">No</span>
    </div>

    <p>Last motion: <span id="last-motion">Never</span></p>

    <div class="controls">
        <button onclick="document.getElementById('alert-sound').play().then(() => { document.getElementById('alert-sound').pause(); })">
            🔊 Enable Motion Alerts
        </button>
        <button onclick="takeSnapshot()">📸 Take Photo</button>
        <button onclick="toggleAudio()" id="audio-btn">🔇 Mute Audio</button>
    </div>

    <!-- Motion alert sound -->
    <audio id="alert-sound" preload="auto" style="display:none;">
        <source src="/alert.mp3" type="audio/mpeg">
    </audio>

    <script>
        let audioMuted = false;

        function toggleAudio() {
            const audio = document.getElementById('audio-stream');
            const btn = document.getElementById('audio-btn');

            if (audioMuted) {
                audio.muted = false;
                btn.textContent = "🔇 Mute Audio";
                audioMuted = false;
            } else {
                audio.muted = true;
                btn.textContent = "🔊 Unmute Audio";
                audioMuted = true;
            }
        }

        function updateMotionStatus() {
            fetch('/motion')
                .then(response => response.json())
                .then(data => {
                    const status = document.getElementById('motion-status');
                    const text = document.getElementById('motion-text');
                    const last = document.getElementById('last-motion');

                    if (data.motion) {
                        text.textContent = "DETECTED! 🚨";
                        status.className = "status alert";
                        document.getElementById('alert-sound').play();
                    } else {
                        text.textContent = "No";
                        status.className = "status";
                    }

                    last.textContent = data.last_time;
                });
        }

        function takeSnapshot() {
            const video = document.getElementById('video');
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth || 640;
            canvas.height = video.videoHeight || 480;

            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);

            const link = document.createElement('a');
            link.download = 'baby-' + new Date().toISOString() + '.png';
            link.href = canvas.toDataURL();
            link.click();

            alert('Photo saved!');
        }

        // Update motion status every 2 seconds
        setInterval(updateMotionStatus, 500);
        updateMotionStatus();

        // Auto-reconnect audio if it stops
        setInterval(() => {
            const audio = document.getElementById('audio-stream');
            if (audio.error || audio.ended) {
                console.log('Reconnecting audio...');
                audio.load();
            }
        }, 10000);
        
               // Mobile detection for audio
        if (/iPhone|iPad|iPod|Android/i.test(navigator.userAgent)) {
            document.getElementById('mobile-hint').style.display = 'inline';
            document.getElementById('desktop-hint').style.display = 'none';
            
            // Mobile Safari workaround
            let audioTapped = false;
            document.getElementById('audio-stream').addEventListener('click', function() {
                if (!audioTapped) {
                    audioTapped = true;
                    this.play().catch(e => {
                        console.log("Mobile audio requires user gesture");
                    });
                }
            });
        }
        
        // Volume control
        document.getElementById('volume').oninput = function() {
            document.getElementById('audio-stream').volume = this.value;
        };
         
    </script>
</body>
</html>
"""

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/alert.mp3')
def serve_alert():
    return send_file('/home/glen/static/alert.mp3', mimetype='audio/mpeg')


@app.route("/")
def home():
    return HTML_PAGE


@app.route("/video")
def video():
    return Response(
        generate_mjpeg(),
        mimetype="multipart/x-mixed-replace; boundary=FRAME",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
    )


@app.route("/audio")
def audio():
    """Audio stream with WAV header for Safari compatibility."""

    def generate():
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=512,
            input_device_index=DEVICE_INDEX
        )

        # WAV header (44 bytes) - REQUIRED for Safari
        header = bytearray(44)
        # RIFF header
        header[0:4] = b'RIFF'
        header[4:8] = (0xFFFFFFFF).to_bytes(4, 'little')  # Large size
        header[8:12] = b'WAVE'
        # fmt chunk
        header[12:16] = b'fmt '
        header[16:20] = (16).to_bytes(4, 'little')  # PCM header size
        header[20:22] = (1).to_bytes(2, 'little')  # PCM format
        header[22:24] = (CHANNELS).to_bytes(2, 'little')
        header[24:28] = (RATE).to_bytes(4, 'little')
        header[28:32] = (RATE * CHANNELS * 2).to_bytes(4, 'little')  # Byte rate
        header[32:34] = (CHANNELS * 2).to_bytes(2, 'little')  # Block align
        header[34:36] = (16).to_bytes(2, 'little')  # 16-bit
        # data chunk
        header[36:40] = b'data'
        header[40:44] = (0xFFFFFFFF).to_bytes(4, 'little')  # Data size

        yield bytes(header)

        print("🎤 Audio streaming started...")

        try:
            while True:
                data = stream.read(1024, exception_on_overflow=False)
                yield data
        except Exception as e:
            print(f"Audio error: {e}")
        finally:
            stream.stop_stream()
            stream.close()

    return Response(
        generate(),
        mimetype='audio/x-wav',  # MUST match HTML type="audio/x-wav"
        headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
    )

@app.route("/motion")
def motion():
    return {
        'motion': motion_detected_now,
        'last_time': last_motion_time
    }


# ============================================================================
# START EVERYTHING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("👶 BABY MONITOR WITH LIVE AUDIO STARTING!")
    print("=" * 50)
    print("Status:")
    print("  Motion sensor: Warming up (30 seconds in background)")
    print("  Camera: Ready")
    print("  Microphone: Ready (USB device 3)")
    print("  Web server: Starting...")
    print("\n✅ WEBSITE READY NOW!")
    print("   Open browser to: http://your-pi-ip:8080")
    print("\nNote: Motion detection will be ready in 30 seconds")
    print("=" * 50 + "\n")

    # Start Flask
    app.run(host="0.0.0.0", port=8080, threaded=True, debug=False)