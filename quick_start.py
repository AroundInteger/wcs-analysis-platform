#!/usr/bin/env python3
"""
Quick Start Script for WCS Analysis Platform

This script helps you get started quickly with the WCS Analysis Platform.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("🔥 WCS Analysis Platform - Quick Start")
    print("=" * 60)
    print()


def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = ['streamlit', 'pandas', 'numpy', 'plotly']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📥 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages, check=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    
    return True


def create_sample_data():
    """Create sample data if it doesn't exist"""
    print("\n📁 Checking sample data...")
    
    sample_dir = Path("data/sample_data")
    if not sample_dir.exists():
        print("📁 Creating sample data directory...")
        sample_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if sample files exist
    sample_files = ["sample_statsport.csv", "sample_catapult.csv"]
    missing_files = []
    
    for file in sample_files:
        if not (sample_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️  Sample files missing: {', '.join(missing_files)}")
        print("   You can add your own CSV files to the data/sample_data/ directory")
    
    return True


def run_tests():
    """Run basic tests"""
    print("\n🧪 Running basic tests...")
    
    try:
        # Test imports
        sys.path.append('src')
        from file_ingestion import detect_file_format
        from wcs_analysis import process_velocity_data
        from visualization import create_velocity_visualization
        
        print("✅ All modules imported successfully")
        
        # Test format detection
        test_lines = ["Player Id,Player Display Name,Time,  Speed m/s"]
        result = detect_file_format(test_lines)
        if result['type'] == 'statsport':
            print("✅ Format detection working")
        else:
            print("⚠️  Format detection may have issues")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False


def launch_app():
    """Launch the Streamlit app"""
    print("\n🚀 Launching WCS Analysis Platform...")
    print("📱 The app will open in your browser")
    print("⏹️  Press Ctrl+C to stop the server")
    print()
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "src/app.py",
            "--server.port", "8501",
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n👋 WCS Analysis Platform stopped")
    except Exception as e:
        print(f"❌ Error launching app: {str(e)}")


def main():
    """Main quick start function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Create sample data
    create_sample_data()
    
    # Run tests
    if not run_tests():
        print("⚠️  Some tests failed, but you can still try running the app")
    
    # Ask user what to do next
    print("\n" + "=" * 60)
    print("🎯 What would you like to do next?")
    print("1. Launch the app now")
    print("2. View sample data")
    print("3. Run full test suite")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            launch_app()
            break
        elif choice == "2":
            print("\n📁 Sample data location: data/sample_data/")
            print("   - sample_statsport.csv (StatSport format)")
            print("   - sample_catapult.csv (Catapult format)")
            print("\n   You can add your own CSV files to test with!")
            break
        elif choice == "3":
            print("\n🧪 Running full test suite...")
            try:
                subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])
            except FileNotFoundError:
                print("❌ pytest not found. Install with: pip install pytest")
            break
        elif choice == "4":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main() 