#!/bin/bash
echo "Starting Smart Quiz Generator..."

# Start backend
cd backend 
echo "Installing backend dependencies..."
source ../.venv/bin/activate
pip install -r requirements.txt
echo "Starting backend server..."
python main.py &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait for backend to initialize
sleep 5

# Start frontend
cd ../frontend
echo "Installing frontend dependencies..."
npm install
echo "Starting frontend server..."
npm start &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

echo "=============================================="
echo "🚀 Smart Quiz Generator is running!"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "=============================================="
echo "Press Ctrl+C to stop both services"

# Store PIDs for cleanup
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

# Wait for interrupt signal
trap 'bash stop.sh' SIGINT SIGTERM
wait
