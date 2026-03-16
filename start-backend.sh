#!/bin/bash

# Start only the backend API server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting Balance Manager API Server..."
echo ""
echo "📊 API: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Check if Python dependencies are installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  Installing Python dependencies..."
    pip install -r requirements.txt
fi

exec python3 backend/main.py
