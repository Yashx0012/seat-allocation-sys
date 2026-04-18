#!/bin/bash

# Start Attendance Tool Server
cd "$(dirname "$0")"
echo "🎯 Starting Attendance Tool on Port 5001..."
python app.py &
APP_PID=$!
echo "✅ Attendance Tool running with PID: $APP_PID"
sleep 2

# Test connection
if curl -s http://localhost:5001/ > /dev/null 2>&1; then
    echo "✅ Server is responding on http://localhost:5001"
else
    echo "⚠️  Server may not be responding yet, checking in 5 seconds..."
    sleep 5
    if curl -s http://localhost:5001/ > /dev/null 2>&1; then
        echo "✅ Server is now responding on http://localhost:5001"
    else
        echo "❌ Server failed to start"
        kill $APP_PID 2>/dev/null
        exit 1
    fi
fi

echo ""
echo "📝 Attendance Tool Features:"
echo "  • Upload attendance reports"
echo "  • Generate attendance documents"
echo "  • Download reports"
echo ""
echo "🌐 Access at: http://localhost:5001"
echo ""
echo "To stop the server, run: pkill -f 'python app.py'"
wait $APP_PID
