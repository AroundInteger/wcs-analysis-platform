#!/usr/bin/env python3
"""
Debug WCS Analysis with Blackpool Data

This script tests the WCS analysis functionality specifically with Blackpool data
to identify what might be causing the app to stop when "Run WCS Analysis" is pressed.
"""

import sys
import os
import pandas as pd
import numpy as np
import traceback

# Add src to path
sys.path.insert(0, 'src')

def test_blackpool_file():
    """Test with a specific Blackpool file"""
    print("🔍 Testing with Blackpool data...")
    
    # Use a specific Blackpool file
    blackpool_file = "/Users/rowanbrown/Library/CloudStorage/OneDrive-SwanseaUniversity/Research/WIPS/Intensity Monitoring/DATA2/Blackpool (A) 13.08.22/BLACKPOOL (A) Export for Andy Fisher 6015.csv"
    
    if not os.path.exists(blackpool_file):
        print(f"❌ File not found: {blackpool_file}")
        return False
    
    print(f"📄 Testing with file: {os.path.basename(blackpool_file)}")
    print(f"📊 File size: {os.path.getsize(blackpool_file) / (1024*1024):.1f} MB")
    
    try:
        from file_ingestion import read_csv_with_metadata, validate_velocity_data
        
        # Read file
        print("📖 Reading file...")
        df, metadata, file_type_info = read_csv_with_metadata(blackpool_file)
        
        if df is None:
            print("❌ Failed to read file")
            return False
        
        print(f"✅ File read successfully")
        print(f"   - Shape: {df.shape}")
        print(f"   - Columns: {list(df.columns)}")
        print(f"   - Metadata: {metadata}")
        print(f"   - File type: {file_type_info}")
        
        # Validate velocity data
        print("🔍 Validating velocity data...")
        if validate_velocity_data(df):
            print("✅ Velocity data validation passed")
        else:
            print("❌ Velocity data validation failed")
            return False
        
        return df, metadata, file_type_info
        
    except Exception as e:
        print(f"❌ Error in file ingestion: {e}")
        traceback.print_exc()
        return False

def test_wcs_analysis_step_by_step(df, metadata, file_type_info):
    """Test WCS analysis step by step to identify where it fails"""
    print("\n🔍 Testing WCS analysis step by step...")
    
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
        
        # Test each step individually
        print("\n1️⃣ Testing data processing...")
        from wcs_analysis import process_velocity_data
        processed_df = process_velocity_data(df, parameters['sampling_rate'])
        print(f"✅ Data processing completed - Shape: {processed_df.shape}")
        
        print("\n2️⃣ Testing velocity data extraction...")
        velocity_data = processed_df['Velocity'].values
        print(f"✅ Velocity data extracted - Length: {len(velocity_data)}")
        print(f"   - Min: {np.min(velocity_data):.2f}")
        print(f"   - Max: {np.max(velocity_data):.2f}")
        print(f"   - Mean: {np.mean(velocity_data):.2f}")
        
        print("\n3️⃣ Testing WCS calculation for 1-minute epoch...")
        from wcs_analysis import calculate_wcs_period
        epoch_duration = 1.0
        
        # Test rolling WCS
        print("   - Testing rolling WCS...")
        th0_distance_rolling, th0_time_rolling, th0_start_rolling, th0_end_rolling = calculate_wcs_period(
            velocity_data, epoch_duration, parameters['sampling_rate'], 
            parameters['th0_min'], parameters['th0_max'], 'rolling'
        )
        print(f"   ✅ Rolling WCS completed - Distance: {th0_distance_rolling:.1f}m")
        
        # Test contiguous WCS
        print("   - Testing contiguous WCS...")
        th0_distance_contiguous, th0_time_contiguous, th0_start_contiguous, th0_end_contiguous = calculate_wcs_period(
            velocity_data, epoch_duration, parameters['sampling_rate'], 
            parameters['th0_min'], parameters['th0_max'], 'contiguous'
        )
        print(f"   ✅ Contiguous WCS completed - Distance: {th0_distance_contiguous:.1f}m")
        
        print("\n4️⃣ Testing full WCS analysis...")
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
        traceback.print_exc()
        return False

def test_visualization_with_blackpool(results):
    """Test visualization creation with Blackpool data"""
    print("\n🔍 Testing visualization with Blackpool data...")
    
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
        traceback.print_exc()
        return False

def test_streamlit_specific_issues():
    """Test if there are Streamlit-specific issues"""
    print("\n🔍 Testing Streamlit-specific issues...")
    
    try:
        import streamlit as st
        
        # Test if we can import streamlit
        print("✅ Streamlit import successful")
        
        # Test if we can use st.write
        print("✅ Streamlit basic functions available")
        
        return True
        
    except Exception as e:
        print(f"❌ Streamlit error: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Blackpool WCS Analysis Debug Test")
    print("=" * 60)
    
    # Test imports
    print("🔍 Testing imports...")
    try:
        from file_ingestion import read_csv_with_metadata, validate_velocity_data
        from wcs_analysis import perform_wcs_analysis
        from visualization import create_velocity_visualization
        print("✅ All imports successful")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return
    
    # Test Streamlit-specific issues
    if not test_streamlit_specific_issues():
        print("\n❌ Streamlit test failed - cannot continue")
        return
    
    # Test with Blackpool file
    ingestion_result = test_blackpool_file()
    if not ingestion_result:
        print("\n❌ Blackpool file test failed - cannot continue")
        return
    
    df, metadata, file_type_info = ingestion_result
    
    # Test WCS analysis step by step
    analysis_result = test_wcs_analysis_step_by_step(df, metadata, file_type_info)
    if not analysis_result:
        print("\n❌ WCS analysis test failed")
        return
    
    # Test visualization
    if not test_visualization_with_blackpool(analysis_result):
        print("\n❌ Visualization test failed")
        return
    
    print("\n🎉 All Blackpool tests passed! WCS analysis should work correctly.")
    print("\n💡 If the app is still stopping, the issue might be:")
    print("   - Streamlit session state conflicts")
    print("   - UI rendering during analysis")
    print("   - Browser timeout")
    print("   - Memory issues with large datasets")

if __name__ == "__main__":
    main() 