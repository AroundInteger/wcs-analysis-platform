#!/bin/bash

# WCS Analysis Platform Launcher Script
# This script launches the Streamlit app with the correct Python path

echo "🚀 Launching WCS Analysis Platform..."

# Check if we're in the right directory
if [ ! -f "src/app.py" ]; then
    echo "❌ Error: src/app.py not found"
    echo "Please run this script from the wcs-test directory"
    exit 1
fi

# Set the port (default 8501, or use first argument)
PORT=${1:-8501}

echo "📁 Working directory: $(pwd)"
echo "📄 App file: src/app.py"
echo "🌐 The app will open in your browser at: http://localhost:$PORT"
echo "⏹️  Press Ctrl+C to stop the server"

# Launch Streamlit with the correct Python path
PYTHONPATH=src streamlit run src/app.py --server.port $PORT 