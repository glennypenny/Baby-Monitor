
#!/usr/bin/env python3
import io
import time
from flask import Flask, Response
from picamera2 import Picamera2
from PIL import Image

app = Flask(__name__)


# === Project notes ============================================================
# This script serves a continuous MJPEG stream over HTTP using Flask.
# MJPEG = a series of JPEG images pushed one after another with a multipart
# response. Most browsers and media players can display it as "video".
# Compared to HLS, MJPEG trades compression efficiency for simplicity/latency


# Configure camera (adjust resolution if needed)
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (1280, 720), "format": "RGB888"}  # or (854, 480)
)
picam2.configure(config)
picam2.start()

# Let auto-exposure (AE) and auto white balance (AWB) settle, then lock them. **STILL HAVING ISSUES WITH CONTRAST/BRIGHTNESS**
time.sleep(2.0)
md = picam2.capture_metadata()

# Read current exposure/analogue gain/colour gains if available
exposure_time = md.get("ExposureTime")        # in microseconds
analogue_gain = md.get("AnalogueGain")
colour_gains  = md.get("ColourGains")         # (R_gain, B_gain)

controls_to_set = {}
if exposure_time is not None:
    controls_to_set["ExposureTime"] = exposure_time
if analogue_gain is not None:
    controls_to_set["AnalogueGain"] = analogue_gain
if colour_gains is not None:
    controls_to_set["ColourGains"] = colour_gains

# Disable auto-exposure/auto white balance after setting the values.
controls_to_set["AeEnable"] = False
controls_to_set["AwbEnable"] = False

# Apply the lock controls (skip if nothing to set)
if controls_to_set:
    picam2.set_controls(controls_to_set)

def generate_mjpeg():
    """Yield an endless MJPEG stream."""
    while True:
        # Grab a frame as NumPy array (RGB)
        frame = picam2.capture_array()

        # Encode to JPEG in memory (quality 1..100)
        buf = io.BytesIO()
        Image.fromarray(frame).save(buf, format="JPEG", quality=80)
        jpeg = buf.getvalue()

        # Multipart MJPEG frame
        yield (b"--FRAME\r\n"
               b"Content-Type: image/jpeg\r\n"
               b"Content-Length: " + str(len(jpeg)).encode() + b"\r\n\r\n" +
               jpeg + b"\r\n")

        # Optional frame rate cap to reduce CPU/bandwidth
        # time.sleep(0.03)  # ~33 fps

@app.route("/")
def mjpeg():
    # Flask endpoint that returns a never-ending multipart MJPEG stream.
    # Use http://<pi-ip>:8080/ in a browser or an <img> tag/video widget.
    return Response(
        generate_mjpeg(),
        mimetype="multipart/x-mixed-replace; boundary=FRAME",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
    )

if __name__ == "__main__":
    # Listen on all interfaces so devices on your LAN can access the stream
    app.run(host="0.0.0.0", port=8080, threaded=True)