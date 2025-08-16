#!/usr/bin/env python3
"""
WSGI Entry Point for Railway Deployment
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from web.app import app
    print("✓ Flask app imported successfully for WSGI")
except ImportError as e:
    print(f"Flask app import error: {e}")
    # Create a minimal Flask app as fallback
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return "Automa - AI Agent & Productivity Tool"
    
    @app.route('/health')
    def health():
        return {"status": "healthy"}

# WSGI application
application = app
