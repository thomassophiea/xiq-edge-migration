#!/bin/bash

# Web UI Launcher for XIQ to Edge Services Migration Tool
# This script starts the Flask web server for the migration tool

echo "======================================================================"
echo "XIQ to Edge Services Migration Tool - Web UI"
echo "======================================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found!"
    echo ""
    echo "Please run setup.sh first to create the virtual environment:"
    echo "  ./setup.sh"
    echo ""
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing web UI dependencies..."
    pip install flask flask-cors
fi

# Check Python syntax
echo "Checking Python syntax..."
python3 -m py_compile web_ui.py
if [ $? -ne 0 ]; then
    echo "❌ Syntax error in web_ui.py"
    exit 1
fi

echo "✓ Syntax check passed"
echo ""

# Start the web server
echo "======================================================================"
echo "Starting web server..."
echo "======================================================================"
echo ""
echo "🌐 Open your browser and navigate to:"
echo ""
echo "    http://localhost:5000"
echo ""
echo "Or access from another device on your network using:"
echo "    http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "======================================================================"
echo "Press Ctrl+C to stop the server"
echo "======================================================================"
echo ""

python3 web_ui.py
