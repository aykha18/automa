#!/usr/bin/env python3
"""
Flask App Entry Point for Railway Deployment
"""

import os
import sys
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from web.app import app
    print("✓ Flask app imported successfully")
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
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Configure for Railway
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
