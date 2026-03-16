#!/bin/bash

# Balance Manager - Start Script
# Starts both backend API server and frontend dev server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting Balance Manager..."
echo ""

# Check if Python dependencies are installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Check if Node dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  Installing Node dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo ""
echo "📊 Backend API: http://localhost:8000"
echo "🎨 Frontend:    http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Start backend in background
python3 backend/main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
cd frontend
npm run dev
FRONTEND_EXIT=$?

# Cleanup
kill $BACKEND_PID 2>/dev/null || true

exit $FRONTEND_EXIT
