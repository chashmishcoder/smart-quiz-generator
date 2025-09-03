#!/bin/bash
echo "Stopping Smart Quiz Generator services..."

# Kill processes by PID if available
if [ -f backend.pid ]; then
    BACKEND_PID=$(cat backend.pid)
    echo "Stopping backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null
    rm backend.pid
fi

if [ -f frontend.pid ]; then
    FRONTEND_PID=$(cat frontend.pid)
    echo "Stopping frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null
    rm frontend.pid
fi

# Fallback: kill by process name
echo "Ensuring all services are stopped..."
pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "npm start" 2>/dev/null
pkill -f "node.*react-scripts" 2>/dev/null

# Wait a moment for processes to terminate
sleep 2

echo "✅ All services stopped successfully!"
