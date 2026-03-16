#!/bin/bash

# Start only the frontend dev server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/frontend"

echo "🎨 Starting Balance Manager Frontend..."
echo ""
echo "🌐 Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Check if Node dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "⚠️  Installing Node dependencies..."
    npm install
fi

exec npm run dev
