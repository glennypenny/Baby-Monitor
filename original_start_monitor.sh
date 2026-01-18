#!/bin/bash
# start_monitor.sh - Starts the baby monitor system

echo "========================================"
echo "👶 Starting Baby Monitor System"
echo "========================================"
date
echo ""

cd ~ || exit 1

# 1. Kill any existing processes first
echo "🧹 Cleaning up any existing processes..."
./stop_monitor.sh  # Use the stop script to cleanup
sleep 2

# Extra camera cleanup
echo "📷 Cleaning camera processes..."
sudo pkill -f libcamera 2>/dev/null
sudo pkill -f picamera 2>/dev/null
sleep 3

# 2. Reset GPIO pins
echo "🔄 Resetting GPIO pins..."
if command -v gpio &> /dev/null; then
    gpio unexportall
fi
sleep 1

# 3. Create log directory
mkdir -p logs

# 4. Start the Flask app in background
echo "🚀 Starting Flask baby monitor..."
IP_ADDRESS=$(hostname -I | awk '{print $1}')
echo "   IP Address: ${IP_ADDRESS}"
echo "   Web: http://${IP_ADDRESS}:8080"
echo "   Logs: ~/logs/monitor.log"
echo ""

# Remove old log
rm -f logs/monitor.log

# Start Flask
nohup python3 flask_app.py > logs/monitor.log 2>&1 &
FLASK_PID=$!

# Save PID
echo $FLASK_PID > /tmp/baby_monitor.pid

# 5. Wait for website to be ready (with visual progress)
echo "⏳ Waiting for website to start..."
echo -n "   Progress: ["

TIMEOUT=40
STARTED=0

for i in $(seq 1 $TIMEOUT); do
    # Check if Flask process is still running
    if ! ps -p $FLASK_PID > /dev/null; then
        echo "] ✗"
        echo "❌ Flask process died! Check logs:"
        tail -20 logs/monitor.log
        exit 1
    fi

    # Check if website responds
    if curl -s --connect-timeout 2 "http://localhost:8080" > /dev/null 2>&1; then
        STARTED=1
        echo -n "✓"
        break
    fi

    # Show progress bar
    if (( i % 4 == 0 )); then
        echo -n "."
    fi
    sleep 1
done

echo "]"

# 6. Final status
if [ $STARTED -eq 1 ]; then
    echo ""
    echo "✅ ✅ ✅ WEBSITE IS READY! ✅ ✅ ✅"
    echo ""
    echo "📡 Open your browser and go to:"
    echo "   http://${IP_ADDRESS}:8080"
    echo ""
    echo "📊 Check logs: tail -f ~/logs/monitor.log"
    echo "🛑 Stop with: ./stop_monitor.sh"
else
    echo ""
    echo "❌ Website didn't start within ${TIMEOUT} seconds!"
    echo ""
    echo "Debugging info:"
    echo "1. Is Flask running?:"
    ps aux | grep flask_app.py | grep -v grep
    echo ""
    echo "2. Last 20 lines of log:"
    tail -20 logs/monitor.log
    echo ""
    echo "3. Try: ./stop_monitor.sh then ./start_monitor.sh again"
    exit 1
fi

echo "========================================"