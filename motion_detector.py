#!/usr/bin/env python3
import time
import threading
from gpiozero import MotionSensor


class MotionDetector:
    def __init__(self, gpio_pin=17):
        self.pir = MotionSensor(gpio_pin)
        self.motion_detected = False
        self.last_motion_time = "Never"
        self.callbacks = []

    def add_callback(self, callback):
        """Add a function to call when motion is detected"""
        self.callbacks.append(callback)

    def start(self):
        """Start motion detection in background thread"""

        def detect_loop():
            print("   Waiting 2 seconds for PIR warm-up...")
            time.sleep(2)
            print("   ✅ Motion sensor ready!")

            while True:
                if self.pir.motion_detected:
                    self.motion_detected = True
                    self.last_motion_time = time.strftime("%H:%M:%S")
                    print(f"[{self.last_motion_time}] 🚨 MOTION!")

                    # Call all registered callbacks
                    for callback in self.callbacks:
                        callback()

                    time.sleep(0.5)
                    self.motion_detected = False

                time.sleep(0.02)

        thread = threading.Thread(target=detect_loop, daemon=True)
        thread.start()
        return thread