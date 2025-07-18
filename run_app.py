#!/usr/bin/env python3
"""
WCS Analysis Platform Launcher
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['streamlit', 'pandas', 'numpy', 'plotly']
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages)
        print("✅ Dependencies installed successfully")
    else:
        print("✅ All dependencies are installed")

def main():
    """Launch the WCS Analysis Platform"""
    
    print("🚀 Launching WCS Analysis Platform...")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"📄 App file: src/app.py")
    
    # Check if we're in the right directory
    if not Path("src/app.py").exists():
        print("❌ Error: src/app.py not found")
        print("Please run this script from the wcs-analysis-platform directory")
        return
    
    # Check dependencies
    check_dependencies()
    
    # Launch the app
    port = 8501
    print(f"🌐 The app will open in your browser at: http://localhost:{port}")
    print("⏹️  Press Ctrl+C to stop the server")
    
    try:
        # Start Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "src/app.py",
            "--server.port", str(port),
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n👋 WCS Analysis Platform stopped")
    except Exception as e:
        print(f"❌ Error launching app: {e}")

if __name__ == "__main__":
    main() 