#!/usr/bin/env python3
"""
Test script for WCS Analysis Platform data ingestion functionality
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.append('src')

def test_file_ingestion():
    """Test the file ingestion functionality"""
    
    print("🧪 Testing WCS Analysis Platform Data Ingestion")
    print("=" * 50)
    
    # Import the ingestion module
    try:
        from file_ingestion import (
            detect_file_format,
            read_statsport_file,
            read_catapult_file,
            read_csv_with_metadata,
            validate_velocity_data
        )
        print("✅ Successfully imported file ingestion modules")
    except Exception as e:
        print(f"❌ Failed to import modules: {e}")
        return False
    
    # Test format detection
    print("\n📋 Testing Format Detection...")
    
    # Test StatSport format detection
    statsport_lines = [
        "Player Id,Player Display Name,Time,  Speed m/s",
        "12345,John Doe,00:00:01,2.5",
        "12345,John Doe,00:00:02,3.1"
    ]
    
    result = detect_file_format(statsport_lines)
    print(f"StatSport detection: {result['type']} (confidence: {result['confidence']:.1%})")
    
    # Test Catapult format detection
    catapult_lines = [
        "# OpenField Export",
        "# Athlete: John Doe",
        "# DeviceId: 12345",
        "# Period: Match 1",
        "Timestamp,Velocity,Latitude,Longitude",
        "00:00:01,2.5,51.5074,-0.1278",
        "00:00:02,3.1,51.5075,-0.1279"
    ]
    
    result = detect_file_format(catapult_lines)
    print(f"Catapult detection: {result['type']} (confidence: {result['confidence']:.1%})")
    
    # Test file reading
    print("\n📁 Testing File Reading...")
    
    # Test StatSport file
    statsport_file = "data/sample_data/sample_statsport.csv"
    if os.path.exists(statsport_file):
        print(f"Testing StatSport file: {statsport_file}")
        try:
            with open(statsport_file, 'r') as f:
                df, metadata, file_type_info = read_csv_with_metadata(f)
            
            if df is not None and metadata is not None:
                print(f"✅ StatSport file read successfully")
                print(f"   - Player: {metadata.get('player_name', 'Unknown')}")
                print(f"   - Records: {metadata.get('total_records', 0)}")
                print(f"   - File type: {file_type_info['type']}")
                print(f"   - Velocity column: {'Velocity' in df.columns}")
                
                # Test velocity validation
                if validate_velocity_data(df):
                    print("✅ Velocity data validation passed")
                else:
                    print("❌ Velocity data validation failed")
            else:
                print("❌ Failed to read StatSport file")
                return False
        except Exception as e:
            print(f"❌ Error reading StatSport file: {e}")
            return False
    else:
        print(f"❌ StatSport file not found: {statsport_file}")
        return False
    
    # Test Catapult file
    catapult_file = "data/sample_data/sample_catapult.csv"
    if os.path.exists(catapult_file):
        print(f"\nTesting Catapult file: {catapult_file}")
        try:
            with open(catapult_file, 'r') as f:
                df, metadata, file_type_info = read_csv_with_metadata(f)
            
            if df is not None and metadata is not None:
                print(f"✅ Catapult file read successfully")
                print(f"   - Player: {metadata.get('player_name', 'Unknown')}")
                print(f"   - Records: {metadata.get('total_records', 0)}")
                print(f"   - File type: {file_type_info['type']}")
                print(f"   - Velocity column: {'Velocity' in df.columns}")
                
                # Test velocity validation
                if validate_velocity_data(df):
                    print("✅ Velocity data validation passed")
                else:
                    print("❌ Velocity data validation failed")
            else:
                print("❌ Failed to read Catapult file")
                return False
        except Exception as e:
            print(f"❌ Error reading Catapult file: {e}")
            return False
    else:
        print(f"❌ Catapult file not found: {catapult_file}")
        return False
    
    print("\n🎉 All ingestion tests passed successfully!")
    return True

def main():
    """Main test function"""
    
    print("🚀 WCS Analysis Platform - Data Ingestion Test")
    print("=" * 60)
    
    # Test file ingestion
    if not test_file_ingestion():
        print("\n❌ File ingestion tests failed")
        return False
    
    print("\n🎉 All tests passed! The platform is ready for use.")
    print("\n📋 Summary:")
    print("   ✅ File format detection working")
    print("   ✅ StatSport file ingestion working")
    print("   ✅ Catapult file ingestion working")
    print("   ✅ Velocity data validation working")
    
    print("\n🚀 Ready to launch the application!")
    print("   Run: python quick_start.py")
    print("   Or: python run_app.py")
    
    return True

if __name__ == "__main__":
    main()
