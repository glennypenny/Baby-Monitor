#!/usr/bin/env python3
import time
from flask import Flask, Response, send_file
from camera_stream import CameraStream
from motion_detector import MotionDetector
from audio_stream import AudioStream

# Initialize components
camera = CameraStream(resolution=(1280, 720), fps=15)
audio = AudioStream(device_index=3)
motion = MotionDetector(gpio_pin=17)

app = Flask(__name__)

# Motion alert callback
def play_motion_alert():
    print("   Playing motion alert...")
    # In a real implementation, this would trigger something

motion.add_callback(play_motion_alert)

# Start motion detection
motion.start()

# HTML page (same as before, shortened)
HTML_PAGE = """
<!DOCTYPE html>
<html>
... your HTML from before ...
</html>
"""

# Routes
@app.route('/')
def home():
    return HTML_PAGE

@app.route('/video')
def video():
    return Response(
        camera.generate_mjpeg(),
        mimetype="multipart/x-mixed-replace; boundary=FRAME",
        headers={"Cache-Control": "no-cache"}
    )

@app.route('/audio')
def audio_stream():
    return Response(
        audio.generate_audio(),
        mimetype='audio/x-wav',
        headers={'Cache-Control': 'no-cache'}
    )

@app.route('/motion')
def get_motion():
    return {
        'motion': motion.motion_detected,
        'last_time': motion.last_motion_time
    }

@app.route('/alert.mp3')
def serve_alert():
    return send_file('/home/glen/static/alert.mp3', mimetype='audio/mpeg')

if __name__ == "__main__":
    print("👶 Baby Monitor Starting...")
    try:
        app.run(host="0.0.0.0", port=8080, threaded=True, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        camera.stop()
        audio.cleanup()