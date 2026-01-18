#!/bin/bash
# start_monitor.sh - Starts baby monitor with cleanup

echo "========================================"
echo "👶 Baby Monitor System $(date)"
echo "========================================"

# Wait for network to be fully up
sleep 5

# Kill existing processes
echo "🧹 Cleaning existing processes..."
pkill -f flask_app.py 2>/dev/null
pkill -f python3.*camera 2>/dev/null
sleep 2

# Reset GPIO
echo "🔄 Resetting GPIO..."
if command -v gpio &> /dev/null; then
    gpio unexportall
fi

# Start the Flask app
echo "🚀 Starting Flask baby monitor..."
cd /home/glen || exit 1

# Get IP address
IP_ADDRESS=$(hostname -I | awk '{print $1}')
echo "   IP: http://${IP_ADDRESS}:8080"
echo "   Logs: sudo journalctl -u baby-monitor -f"
echo ""

# Run in foreground (systemd will handle background)
exec python3 flask_app.py