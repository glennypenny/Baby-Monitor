Raspberry Pi Baby Monitor
A simple Raspberry Pi baby monitor that streams video over your local network using Flask. Features motion detection, audio monitoring, and a web interface for remote viewing.

What Actually Works
Right now, only flask_app.py is fully functional on the Pi (it contains all the web app features). The other scripts are for future development and organization.

Quick Start
Run the monitor (cleans up system first):
./start_monitor.sh
This script:
Resets GPIO pins
Clears previous sessions
Launches flask_app.py

Access the web interface:
Open your browser and go to:

text
http://<your-pi-ip-address>:5000
Stop the monitor:

bash
./stop_monitor.sh
Cleans up the system for next use.

Why Two Streaming Methods?
The project explores two approaches:

HLS (HTTP Live Streaming): Short video segments, good for reliability
MJPEG: Continuous JPEG stream, lower latency for real-time monitoring (this is the better of the two!)

Prerequisites
Raspberry Pi with camera module, motion detector and microphone enabled

Raspberry Pi OS (Desktop recommended for easier camera setup)

Installation
bash
# Update system
sudo apt update && sudo apt -y full-upgrade

# Install dependencies
sudo apt install -y libcamera-apps python3-picamera2 python3-flask python3-pil ffmpeg

# Enable camera
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
sudo reboot
File Structure
flask_app.py - Main working application (use this)

start_monitor.sh - Launch script (resets system, then runs Flask app)

stop_monitor.sh - Cleanup script

Other files (camera.py, audio_stream.py, etc.) - For future modular development

Notes
I'm currently refactoring the code into separate modules for better organization

The motion sensor requires a fresh start each time (hence the start/stop scripts)

All development is done via SSH on Raspberry Pi OS Desktop

Troubleshooting
If the web interface doesn't show video:

Stop the monitor: ./stop_monitor.sh

Start fresh: ./start_monitor.sh

Check camera is enabled in raspi-config

Future Plans
Split monolithic script into separate modules

Add automated startup on boot

Improve motion detection reliability

Add mobile notifications
