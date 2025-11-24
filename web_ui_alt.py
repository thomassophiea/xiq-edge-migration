#!/usr/bin/env python3
"""
Web UI for XIQ to Edge Services Migration Tool (Port 8080)
Alternative version for systems where port 5000 is blocked
"""

# This is identical to web_ui.py but uses port 8080 instead of 5000
import sys
import os

# Import the original web_ui module
sys.path.insert(0, os.path.dirname(__file__))
from web_ui import app

if __name__ == '__main__':
    print('=' * 70)
    print('XIQ to Edge Services Migration Tool - Web UI')
    print('=' * 70)
    print()
    print('Starting web server on PORT 8080...')
    print('Open your browser and navigate to: http://localhost:8080')
    print()
    print('Press Ctrl+C to stop the server')
    print('=' * 70)

    app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)
