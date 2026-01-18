# Raspberry Pi Baby Monitor

A simple Raspberry Pi baby monitor that streams video over your local network using Flask. Features motion detection, audio monitoring, and a web interface for remote viewing.

## Quick Start

### What Actually Works
Right now, **only `flask_app.py`** is fully functional on the Pi (it contains all the web app features). The other scripts are for future development and organization.

### Run the Monitor
*Start the system* (cleans up first, then launches the app):
   ./start_monitor.sh

This script:
Resets GPIO pins
Clears previous sessions
Launches flask_app.py

To access the web interface:
Open your browser and navigate to: http://<your-pi-ip-address>:5000

*Stop the monitor* (cleanup for next use):
  ./stop_monitor.sh

### Project Structure
.
├── flask_app.py              # Main working application (use this)
├── start_monitor.sh          # Launch script with system reset
├── stop_monitor.sh           # Cleanup script
├── camera.py                 # Camera module (future)
├── audio_stream.py           # Audio streaming (future)
├── camera_stream.py          # Camera streaming (future)
├── motion_detector.py        # Motion detection (future)
├── logs/                     # Log files
└── .idea/                    # IDE configuration

### Setup
Prerequisites
Raspberry Pi with camera module
Raspberry Pi OS (Desktop recommended for easier camera setup)
Microphone (for audio monitoring)

### Installation
# Update system
sudo apt update && sudo apt -y full-upgrade
# Install dependencies
sudo apt install -y libcamera-apps python3-picamera2 python3-flask python3-pil ffmpeg
# Enable camera
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
sudo reboot

# Important Notes
Motion Sensor Quirk: The motion sensor requires a fresh start each time. This is why the start_monitor.sh script resets everything before launching.
Development Environment: All development is done via SSH on Raspberry Pi OS Desktop. The Desktop version made initial camera setup much easier.
Code Structure: The code is currently being refactored from a monolithic script (flask_app.py) into separate modules for better organisation.

# Troubleshooting
Web Interface Shows No Video
Stop the monitor: ./stop_monitor.sh
Start fresh: ./start_monitor.sh
Verify camera is enabled: sudo raspi-config # Interface Options → Camera → Enable

Check permissions on scripts: chmod +x start_monitor.sh stop_monitor.sh

# Future Plans
Split monolithic script into separate modules
Add automated startup on boot
Improve motion detection reliability
Add mobile notifications
Create headless/Lite OS installation instructions

### Contributing
This is a learning project. The code is intentionally kept simple as I learn and improve it over time. Feel free to suggest improvements!

# References & Inspiration
Picamera2 Library: raspberrypi/picamera2
YouTube Tutorial: "Raspberry Pi Security Camera/Monitor"
