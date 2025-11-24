#!/bin/bash

# Web UI Diagnostic Script
# This script checks for common issues that prevent the Web UI from working

echo "======================================================================"
echo "Web UI Diagnostic Tool"
echo "======================================================================"
echo ""

# Check 1: Virtual environment
echo "Check 1: Virtual Environment"
if [ -d "venv" ]; then
    echo "  ✓ Virtual environment exists"
else
    echo "  ✗ Virtual environment NOT found"
    echo "  → Run: ./setup.sh"
    exit 1
fi
echo ""

# Check 2: Activate venv and check Python
echo "Check 2: Python Version"
source venv/bin/activate
python_version=$(python3 --version)
echo "  ✓ $python_version"
echo ""

# Check 3: Flask installation
echo "Check 3: Flask Installation"
if python3 -c "import flask" 2>/dev/null; then
    flask_version=$(python3 -c "import flask; print(flask.__version__)")
    echo "  ✓ Flask $flask_version installed"
else
    echo "  ✗ Flask NOT installed"
    echo "  → Installing Flask..."
    pip install flask flask-cors
fi
echo ""

# Check 4: Flask-CORS installation
echo "Check 4: Flask-CORS Installation"
if python3 -c "import flask_cors" 2>/dev/null; then
    echo "  ✓ Flask-CORS installed"
else
    echo "  ✗ Flask-CORS NOT installed"
    echo "  → Installing Flask-CORS..."
    pip install flask-cors
fi
echo ""

# Check 5: web_ui.py syntax
echo "Check 5: web_ui.py Syntax"
if python3 -m py_compile web_ui.py 2>/dev/null; then
    echo "  ✓ web_ui.py syntax is valid"
else
    echo "  ✗ web_ui.py has syntax errors"
    python3 -m py_compile web_ui.py
    exit 1
fi
echo ""

# Check 6: Port 5000 availability
echo "Check 6: Port 5000 Availability"
port_check=$(lsof -i :5000 2>/dev/null)
if [ -z "$port_check" ]; then
    echo "  ✓ Port 5000 is available"
else
    echo "  ⚠ Port 5000 is in use:"
    echo "$port_check" | head -2 | sed 's/^/    /'
    echo ""
    echo "  Common on macOS: AirPlay Receiver uses port 5000"
    echo "  → Solution: Disable AirPlay Receiver in System Preferences"
    echo "  → Or use: python3 web_ui_alt.py (uses port 8080)"
fi
echo ""

# Check 7: Port 8080 availability
echo "Check 7: Port 8080 Availability (Alternative)"
port_check=$(lsof -i :8080 2>/dev/null)
if [ -z "$port_check" ]; then
    echo "  ✓ Port 8080 is available"
else
    echo "  ⚠ Port 8080 is in use:"
    echo "$port_check" | head -2 | sed 's/^/    /'
fi
echo ""

# Check 8: File permissions
echo "Check 8: File Permissions"
if [ -r "web_ui.py" ]; then
    echo "  ✓ web_ui.py is readable"
else
    echo "  ✗ web_ui.py is NOT readable"
    echo "  → Run: chmod +r web_ui.py"
fi
echo ""

# Summary
echo "======================================================================"
echo "Diagnostic Summary"
echo "======================================================================"
echo ""
echo "If all checks passed, try these commands:"
echo ""
echo "Option 1 - Use port 5000 (standard):"
echo "  python3 web_ui.py"
echo "  Then open: http://localhost:5000"
echo ""
echo "Option 2 - Use port 8080 (if port 5000 is blocked):"
echo "  python3 web_ui_alt.py"
echo "  Then open: http://localhost:8080"
echo ""
echo "Option 3 - Test Flask installation:"
echo "  python3 test_flask.py"
echo "  Then open: http://localhost:8888"
echo ""
echo "======================================================================"
