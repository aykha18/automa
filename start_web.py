#!/usr/bin/env python3
"""
Startup script for the AI Agent & Productivity Tool Web Interface
"""

import os
import sys
import webbrowser
import time
from pathlib import Path

def main():
    print("🤖 AI Agent & Productivity Tool")
    print("==================================================")
    print("Starting web interface...")
    
    # Add src directory to Python path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        # Import and run Flask app
        from web.app import app
        
        print("✓ Web interface starting on http://localhost:5000")
        print("🌐 Opening browser...")
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:5000')
        
        import threading
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Run the Flask app
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")
        print("Please check that all dependencies are installed.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
