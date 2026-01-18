#!/bin/bash
# SAFE_stop_monitor.sh - Won't break your terminal

echo "========================================"
echo "🛑 SAFELY Stopping Baby Monitor"
echo "========================================"

# Only kill our specific processes, not everything
echo "Looking for baby monitor processes..."

# Method 1: Kill by PID file
if [ -f /tmp/baby_monitor.pid ]; then
    PID=$(cat /tmp/baby_monitor.pid)
    echo "Found PID: $PID"
    if ps -p $PID > /dev/null; then
        echo "Stopping process $PID gently..."
        kill $PID
        sleep 2
    fi
    rm -f /tmp/baby_monitor.pid
fi

# Method 2: Kill by script name (more specific)
echo "Stopping flask_app.py processes..."
pkill -f "flask_app.py" 2>/dev/null

# Method 3: Kill camera processes (carefully)
echo "Stopping camera processes..."
sudo pkill -f "libcamera" 2>/dev/null || true
sudo pkill -f "picamera" 2>/dev/null || true

# Method 4: Reset GPIO
echo "Resetting GPIO..."
if command -v gpio &> /dev/null; then
    gpio unexportall 2>/dev/null || true
fi

echo ""
echo "✅ Done! Terminal is safe."
echo "========================================"