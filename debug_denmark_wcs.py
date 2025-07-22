#!/usr/bin/env python3
"""
Debug WCS Analysis with Denmark Data

This script tests the WCS analysis functionality specifically with Denmark data
to identify what might be causing the app to stop when "Run WCS Analysis" is pressed.
"""

import sys
import os
import pandas as pd
import numpy as np
import traceback

# Add src to path
sys.path.insert(0, 'src')

def test_denmark_file():
    """Test with a specific Denmark file"""
    print("🔍 Testing with Denmark data...")
    
    # Use a specific Denmark file
    denmark_file = "data/Denmark/PORTUGAL (AWAY) MD2 (DENMARK) Export for Cadi Rodgers 46247.csv"
    
    if not os.path.exists(denmark_file):
        print(f"❌ File not found: {denmark_file}")
        return False
    
    print(f"📄 Testing with file: {denmark_file}")
    print(f"📊 File size: {os.path.getsize(denmark_file) / (1024*1024):.1f} MB")
    
    try:
        from file_ingestion import read_csv_with_metadata, validate_velocity_data
        
        # Read file
        print("📖 Reading file...")
        df, metadata, file_type_info = read_csv_with_metadata(denmark_file)
        
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

def test_visualization_with_denmark(results):
    """Test visualization creation with Denmark data"""
    print("\n🔍 Testing visualization with Denmark data...")
    
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

def test_memory_usage():
    """Test memory usage during processing"""
    print("\n🔍 Testing memory usage...")
    
    import psutil
    import gc
    
    # Get initial memory usage
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    print(f"📊 Initial memory usage: {initial_memory:.1f} MB")
    
    # Test with Denmark file
    denmark_file = "data/Denmark/PORTUGAL (AWAY) MD2 (DENMARK) Export for Cadi Rodgers 46247.csv"
    
    try:
        from file_ingestion import read_csv_with_metadata
        
        # Read file
        df, metadata, file_type_info = read_csv_with_metadata(denmark_file)
        
        # Check memory after reading
        memory_after_read = process.memory_info().rss / 1024 / 1024
        print(f"📊 Memory after reading file: {memory_after_read:.1f} MB (+{memory_after_read - initial_memory:.1f} MB)")
        
        # Test WCS analysis
        from wcs_analysis import perform_wcs_analysis
        parameters = {
            'sampling_rate': 10,
            'epoch_duration': 1.0,
            'epoch_durations': [1.0, 2.0, 5.0],
            'th0_min': 0.0,
            'th0_max': 100.0,
            'th1_min': 5.0,
            'th1_max': 100.0,
        }
        
        results = perform_wcs_analysis(df, metadata, file_type_info, parameters)
        
        # Check memory after analysis
        memory_after_analysis = process.memory_info().rss / 1024 / 1024
        print(f"📊 Memory after WCS analysis: {memory_after_analysis:.1f} MB (+{memory_after_analysis - initial_memory:.1f} MB)")
        
        # Clean up
        del df, results
        gc.collect()
        
        # Check memory after cleanup
        memory_after_cleanup = process.memory_info().rss / 1024 / 1024
        print(f"📊 Memory after cleanup: {memory_after_cleanup:.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in memory test: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Denmark WCS Analysis Debug Test")
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
    
    # Test with Denmark file
    ingestion_result = test_denmark_file()
    if not ingestion_result:
        print("\n❌ Denmark file test failed - cannot continue")
        return
    
    df, metadata, file_type_info = ingestion_result
    
    # Test WCS analysis step by step
    analysis_result = test_wcs_analysis_step_by_step(df, metadata, file_type_info)
    if not analysis_result:
        print("\n❌ WCS analysis test failed")
        return
    
    # Test visualization
    if not test_visualization_with_denmark(analysis_result):
        print("\n❌ Visualization test failed")
        return
    
    # Test memory usage
    if not test_memory_usage():
        print("\n❌ Memory test failed")
        return
    
    print("\n🎉 All Denmark tests passed! WCS analysis should work correctly.")
    print("\n💡 If the app is still stopping, the issue might be:")
    print("   - Streamlit-specific error handling")
    print("   - UI rendering problems with large datasets")
    print("   - Session state issues")
    print("   - Browser timeout with large visualizations")

if __name__ == "__main__":
    main() 