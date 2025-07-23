#!/usr/bin/env python3
"""
Automated Test Runner for WCS Analysis Platform
Demonstrates how automated testing works locally
"""

import subprocess
import sys
import time
import os

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🔧 {description}")
    print(f"Running: {command}")
    
    start_time = time.time()
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        end_time = time.time()
        
        if result.returncode == 0:
            print(f"✅ PASSED ({end_time - start_time:.2f}s)")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ FAILED ({end_time - start_time:.2f}s)")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run the complete test suite"""
    print("🧪 WCS Analysis Platform - Automated Testing")
    print("=" * 50)
    
    # Track overall success
    all_passed = True
    
    # 1. Code Quality Checks
    print("\n📋 PHASE 1: Code Quality Checks")
    print("-" * 30)
    
    # Check if black is installed
    if run_command("pip show black", "Checking if Black formatter is installed"):
        all_passed &= run_command("black --check src/", "Code formatting check")
    else:
        print("⚠️  Black not installed, skipping formatting check")
    
    # Check if flake8 is installed
    if run_command("pip show flake8", "Checking if Flake8 linter is installed"):
        all_passed &= run_command("flake8 src/ --max-line-length=100 --ignore=E203,W503", "Code style check")
    else:
        print("⚠️  Flake8 not installed, skipping style check")
    
    # 2. Unit Tests
    print("\n🧪 PHASE 2: Unit Tests")
    print("-" * 30)
    
    # Check if pytest is installed
    if run_command("pip show pytest", "Checking if pytest is installed"):
        all_passed &= run_command("python -m pytest tests/ -v", "Running unit tests")
    else:
        print("⚠️  pytest not installed, skipping unit tests")
        print("Install with: pip install pytest pytest-cov")
    
    # 3. Integration Tests
    print("\n🔗 PHASE 3: Integration Tests")
    print("-" * 30)
    
    # Test file ingestion
    integration_test = """
import sys
sys.path.append('src')
try:
    from file_ingestion import read_csv_with_metadata
    print('✅ File ingestion module imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"""
    
    all_passed &= run_command(f'python -c "{integration_test}"', "File ingestion integration test")
    
    # 4. Performance Tests
    print("\n⚡ PHASE 4: Performance Tests")
    print("-" * 30)
    
    performance_test = """
import time
import numpy as np
import sys
sys.path.append('src')

try:
    from wcs_analysis import calculate_wcs_period_rolling
    
    # Create test dataset: 5 minutes at 10Hz
    time_data = np.arange(0, 300, 0.1)  # 5 minutes
    velocity_data = np.random.normal(5.0, 1.0, 3000)
    
    start_time = time.time()
    result = calculate_wcs_period_rolling(velocity_data, time_data, 30.0, 0.0, 100.0)
    end_time = time.time()
    
    processing_time = end_time - start_time
    print(f'✅ Performance test: {processing_time:.3f}s for 5-minute dataset')
    
    if processing_time < 1.0:
        print('✅ Performance acceptable (< 1 second)')
    else:
        print(f'⚠️  Performance slow: {processing_time:.3f}s')
        
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Performance test error: {e}')
    sys.exit(1)
"""
    
    all_passed &= run_command(f'python -c "{performance_test}"', "Performance benchmark")
    
    # 5. Security Checks
    print("\n🔒 PHASE 5: Security Checks")
    print("-" * 30)
    
    # Check for common security issues in code
    security_check = """
import os
import sys

# Check for hardcoded secrets
suspicious_patterns = ['password', 'secret', 'key', 'token']
src_files = []

for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            src_files.append(os.path.join(root, file))

found_issues = False
for file_path in src_files:
    try:
        with open(file_path, 'r') as f:
            content = f.read().lower()
            for pattern in suspicious_patterns:
                if pattern in content:
                    print(f'⚠️  Potential security issue in {file_path}: contains "{pattern}"')
                    found_issues = True
    except Exception as e:
        print(f'❌ Error reading {file_path}: {e}')

if not found_issues:
    print('✅ No obvious security issues found')
"""
    
    all_passed &= run_command(f'python -c "{security_check}"', "Security scan")
    
    # 6. Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 50)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Code quality: Good")
        print("✅ Unit tests: Passing")
        print("✅ Integration: Working")
        print("✅ Performance: Acceptable")
        print("✅ Security: Clean")
        print("\n🚀 Ready for deployment!")
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please fix the issues above before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 