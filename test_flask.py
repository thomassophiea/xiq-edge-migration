#!/usr/bin/env python3
"""
Simple Flask test to verify Flask is working
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <html>
    <head><title>Flask Test</title></head>
    <body style="font-family: Arial; padding: 50px; text-align: center;">
        <h1 style="color: green;">✓ Flask is Working!</h1>
        <p>If you can see this page, Flask is installed and running correctly.</p>
        <p>You can now close this and try the migration tool.</p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print('=' * 70)
    print('Flask Test Server')
    print('=' * 70)
    print()
    print('Testing Flask on port 8888...')
    print('Open your browser: http://localhost:8888')
    print()
    print('If you see a green checkmark, Flask is working!')
    print('Press Ctrl+C to stop')
    print('=' * 70)
    print()

    app.run(host='127.0.0.1', port=8888, debug=False)
