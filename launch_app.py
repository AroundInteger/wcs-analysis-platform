#!/usr/bin/env python3
"""
WCS Analysis Platform Launcher - Fixed Version
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def setup_environment():
    """Setup the Python environment for the app"""
    # Get the project root directory
    project_root = Path(__file__).parent.absolute()
    src_path = project_root / "src"
    
    # Add src directory to Python path
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    print(f"📁 Project root: {project_root}")
    print(f"📁 Source path: {src_path}")
    print(f"🐍 Python path updated")

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
    
    # Setup environment
    setup_environment()
    
    # Check if we're in the right directory
    if not Path("src/app.py").exists():
        print("❌ Error: src/app.py not found")
        print("Please run this script from the wcs-test directory")
        return
    
    # Check dependencies
    check_dependencies()
    
    # Launch the app
    port = 8501
    print(f"🌐 The app will open in your browser at: http://localhost:{port}")
    print("⏹️  Press Ctrl+C to stop the server")
    
    try:
        # Start Streamlit with proper environment
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{os.path.join(os.getcwd(), 'src')}:{env.get('PYTHONPATH', '')}"
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "src/app.py",
            "--server.port", str(port),
            "--server.headless", "true"
        ], env=env)
    except KeyboardInterrupt:
        print("\n👋 WCS Analysis Platform stopped")
    except Exception as e:
        print(f"❌ Error launching app: {e}")

if __name__ == "__main__":
    main() 