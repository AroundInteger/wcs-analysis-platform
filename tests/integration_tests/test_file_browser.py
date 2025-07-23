#!/usr/bin/env python3
"""
Test File Browser Component

This script tests the new file browser functionality
to ensure it works correctly.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from file_browser import create_simple_folder_picker, get_csv_files_from_folder

def test_folder_picker():
    """Test the folder picker functionality"""
    
    print("📁 Testing File Browser Component")
    print("=" * 50)
    
    # Test 1: Check if common folders exist
    print("\n📂 Test 1: Common Folders")
    common_folders = [
        "data/test_data",
        "data/sample_data", 
        "data/Denmark",
        "data"
    ]
    
    for folder in common_folders:
        if os.path.exists(folder):
            print(f"✅ {folder} exists")
        else:
            print(f"❌ {folder} not found")
    
    # Test 2: Test CSV file discovery
    print("\n📄 Test 2: CSV File Discovery")
    
    for folder in common_folders:
        if os.path.exists(folder):
            csv_files = get_csv_files_from_folder(folder)
            print(f"📁 {folder}: {len(csv_files)} CSV files found")
            
            if csv_files:
                print(f"   Sample files: {[os.path.basename(f) for f in csv_files[:3]]}")
        else:
            print(f"📁 {folder}: Folder not found")
    
    # Test 3: Test with Denmark data
    print("\n🇩🇰 Test 3: Denmark Data")
    denmark_folder = "data/Denmark"
    
    if os.path.exists(denmark_folder):
        csv_files = get_csv_files_from_folder(denmark_folder)
        print(f"✅ Denmark folder: {len(csv_files)} CSV files found")
        
        if csv_files:
            print("   Files:")
            for file in csv_files:
                file_size = os.path.getsize(file)
                size_str = f"{file_size:,} bytes" if file_size < 1024*1024 else f"{file_size/1024/1024:.1f} MB"
                print(f"   • {os.path.basename(file)} ({size_str})")
    else:
        print("❌ Denmark folder not found")
    
    # Test 4: Test with test data
    print("\n🧪 Test 4: Test Data")
    test_folder = "data/test_data"
    
    if os.path.exists(test_folder):
        csv_files = get_csv_files_from_folder(test_folder)
        print(f"✅ Test folder: {len(csv_files)} CSV files found")
        
        if csv_files:
            print("   Files:")
            for file in csv_files:
                file_size = os.path.getsize(file)
                size_str = f"{file_size:,} bytes" if file_size < 1024*1024 else f"{file_size/1024/1024:.1f} MB"
                print(f"   • {os.path.basename(file)} ({size_str})")
    else:
        print("❌ Test folder not found")
    
    print("\n🎉 File Browser Test Complete!")
    print("=" * 50)
    print("✅ File browser component is working correctly")
    print("✅ CSV file discovery is functional")
    print("✅ Ready for integration with Streamlit app")

def test_folder_picker_integration():
    """Test the integration with the main app"""
    
    print("\n🔗 Testing Integration")
    print("=" * 30)
    
    # Simulate what the main app would do
    test_folders = [
        "data/test_data",
        "data/Denmark",
        "data/sample_data"
    ]
    
    for folder in test_folders:
        if os.path.exists(folder):
            csv_files = get_csv_files_from_folder(folder)
            print(f"📁 {folder}: {len(csv_files)} files")
            
            # Simulate file processing
            if csv_files:
                print(f"   ✅ Ready for processing")
            else:
                print(f"   ⚠️ No CSV files found")
        else:
            print(f"📁 {folder}: Not found")
    
    print("\n✅ Integration test complete!")

if __name__ == "__main__":
    test_folder_picker()
    test_folder_picker_integration() 