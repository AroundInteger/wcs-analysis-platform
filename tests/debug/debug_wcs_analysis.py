#!/usr/bin/env python3
"""
Debug WCS Analysis Script

This script tests the WCS analysis functionality to identify any issues
that might be causing the app to stop when "Run WCS Analysis" is pressed.
"""

import sys
import os
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, 'src')

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from file_ingestion import read_csv_with_metadata, validate_velocity_data
        print("✅ file_ingestion imported successfully")
    except Exception as e:
        print(f"❌ Error importing file_ingestion: {e}")
        return False
    
    try:
        from wcs_analysis import perform_wcs_analysis
        print("✅ wcs_analysis imported successfully")
    except Exception as e:
        print(f"❌ Error importing wcs_analysis: {e}")
        return False
    
    try:
        from visualization import create_velocity_visualization
        print("✅ visualization imported successfully")
    except Exception as e:
        print(f"❌ Error importing visualization: {e}")
        return False
    
    return True

def test_file_ingestion():
    """Test file ingestion with a sample file"""
    print("\n🔍 Testing file ingestion...")
    
    # Look for test files
    test_files = [
        "data/test_data/sample_data.csv",
        "data/sample_data/sample_data.csv",
        "data/test_data/*.csv"
    ]
    
    import glob
    for pattern in test_files:
        if '*' in pattern:
            files = glob.glob(pattern)
            if files:
                test_file = files[0]
                break
        elif os.path.exists(pattern):
            test_file = pattern
            break
    else:
        print("❌ No test files found")
        return False
    
    print(f"📄 Testing with file: {test_file}")
    
    try:
        from file_ingestion import read_csv_with_metadata, validate_velocity_data
        
        # Read file
        df, metadata, file_type_info = read_csv_with_metadata(test_file)
        
        if df is None:
            print("❌ Failed to read file")
            return False
        
        print(f"✅ File read successfully")
        print(f"   - Shape: {df.shape}")
        print(f"   - Columns: {list(df.columns)}")
        print(f"   - Metadata: {metadata}")
        print(f"   - File type: {file_type_info}")
        
        # Validate velocity data
        if validate_velocity_data(df):
            print("✅ Velocity data validation passed")
        else:
            print("❌ Velocity data validation failed")
            return False
        
        return df, metadata, file_type_info
        
    except Exception as e:
        print(f"❌ Error in file ingestion: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_wcs_analysis(df, metadata, file_type_info):
    """Test WCS analysis"""
    print("\n🔍 Testing WCS analysis...")
    
    try:
        from wcs_analysis import perform_wcs_analysis
        
        # Prepare parameters
        parameters = {
            'sampling_rate': 10,
            'epoch_duration': 1.0,
            'epoch_durations': [1.0, 2.0, 5.0],
            'th0_min': 0.0,
            'th0_max': 100.0,
            'th1_min': 5.0,
            'th1_max': 100.0,
        }
        
        print(f"📊 Parameters: {parameters}")
        
        # Perform analysis
        results = perform_wcs_analysis(df, metadata, file_type_info, parameters)
        
        if results is None:
            print("❌ WCS analysis returned None")
            return False
        
        print("✅ WCS analysis completed successfully")
        print(f"   - Velocity stats: {results.get('velocity_stats', {})}")
        print(f"   - Rolling WCS results: {len(results.get('rolling_wcs_results', []))} epochs")
        print(f"   - Contiguous WCS results: {len(results.get('contiguous_wcs_results', []))} epochs")
        
        return results
        
    except Exception as e:
        print(f"❌ Error in WCS analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_visualization(results):
    """Test visualization creation"""
    print("\n🔍 Testing visualization...")
    
    try:
        from visualization import create_velocity_visualization
        
        # Test visualization creation
        fig = create_velocity_visualization(
            results['processed_data'],
            results['metadata'],
            results.get('rolling_wcs_results', [])
        )
        
        if fig is not None:
            print("✅ Visualization created successfully")
        else:
            print("❌ Visualization creation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in visualization: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 WCS Analysis Debug Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed - cannot continue")
        return
    
    # Test file ingestion
    ingestion_result = test_file_ingestion()
    if not ingestion_result:
        print("\n❌ File ingestion test failed - cannot continue")
        return
    
    df, metadata, file_type_info = ingestion_result
    
    # Test WCS analysis
    analysis_result = test_wcs_analysis(df, metadata, file_type_info)
    if not analysis_result:
        print("\n❌ WCS analysis test failed")
        return
    
    # Test visualization
    if not test_visualization(analysis_result):
        print("\n❌ Visualization test failed")
        return
    
    print("\n🎉 All tests passed! WCS analysis should work correctly.")
    print("\n💡 If the app is still stopping, the issue might be:")
    print("   - Streamlit-specific error handling")
    print("   - Memory issues with large files")
    print("   - UI rendering problems")
    print("   - Session state issues")

if __name__ == "__main__":
    main() 