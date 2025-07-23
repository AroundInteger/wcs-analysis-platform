#!/usr/bin/env python3
"""
Quick Folder Test - Command Line Version

This script quickly tests folder contents and zero-velocity files from the command line.
"""

import sys
import os
import glob
import pandas as pd

# Add src to path
sys.path.insert(0, 'src')

def quick_folder_analysis():
    """Quick analysis of the folder contents"""
    print("🔍 Quick Folder Analysis")
    print("=" * 50)
    
    # Test folder
    test_folder = "/Users/rowanbrown/Library/CloudStorage/OneDrive-SwanseaUniversity/Research/WIPS/Intensity Monitoring/DATA2/Blackpool (A) 13.08.22/"
    
    if not os.path.exists(test_folder):
        print(f"❌ Folder not found: {test_folder}")
        return
    
    # Get all CSV files
    csv_files = glob.glob(os.path.join(test_folder, "*.csv"))
    print(f"📄 Found {len(csv_files)} CSV files")
    
    if not csv_files:
        print("❌ No CSV files found in folder")
        return
    
    # List all files
    print("\n📋 All CSV files:")
    for i, file_path in enumerate(csv_files, 1):
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        print(f"{i:2d}. {os.path.basename(file_path)} ({file_size:.2f} MB)")
    
    # Test a few files for velocity data
    print("\n🔬 Testing velocity data in files...")
    
    try:
        from file_ingestion import read_csv_with_metadata, validate_velocity_data
        
        zero_velocity_files = []
        valid_files = []
        error_files = []
        
        for i, file_path in enumerate(csv_files[:10]):  # Test first 10 files
            filename = os.path.basename(file_path)
            print(f"\n📊 Testing {i+1}/10: {filename}")
            
            try:
                # Read file
                df, metadata, file_type_info = read_csv_with_metadata(file_path)
                
                if df is None:
                    print(f"  ❌ File reading failed")
                    error_files.append(filename)
                    continue
                
                print(f"  ✅ File read - Shape: {df.shape}")
                
                # Find velocity column
                velocity_col = None
                for col in df.columns:
                    if 'velocity' in col.lower() or 'speed' in col.lower():
                        velocity_col = col
                        break
                
                if velocity_col is None:
                    print(f"  ❌ No velocity column found")
                    error_files.append(filename)
                    continue
                
                print(f"  📈 Velocity column: {velocity_col}")
                
                # Check velocity data
                velocity_data = df[velocity_col].dropna()
                non_zero_count = len(velocity_data[velocity_data > 0])
                zero_count = len(velocity_data[velocity_data == 0])
                max_velocity = velocity_data.max()
                
                print(f"  📊 Total points: {len(velocity_data)}")
                print(f"  📊 Non-zero points: {non_zero_count}")
                print(f"  📊 Zero points: {zero_count}")
                print(f"  📊 Max velocity: {max_velocity:.2f}")
                
                if non_zero_count == 0:
                    print(f"  🛑 ZERO VELOCITY - No movement recorded")
                    zero_velocity_files.append(filename)
                else:
                    print(f"  ✅ Has movement data")
                    valid_files.append(filename)
                
                # Test validation
                is_valid = validate_velocity_data(df)
                print(f"  🔍 Data validation: {'✅' if is_valid else '❌'}")
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                error_files.append(filename)
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 SUMMARY")
        print("=" * 50)
        print(f"📄 Total files in folder: {len(csv_files)}")
        print(f"✅ Files with movement: {len(valid_files)}")
        print(f"🛑 Zero velocity files: {len(zero_velocity_files)}")
        print(f"❌ Error files: {len(error_files)}")
        
        if zero_velocity_files:
            print(f"\n🛑 Zero-velocity files found:")
            for filename in zero_velocity_files:
                print(f"  - {filename}")
        
        if valid_files:
            print(f"\n✅ Files with valid movement data:")
            for filename in valid_files[:5]:  # Show first 5
                print(f"  - {filename}")
            if len(valid_files) > 5:
                print(f"  ... and {len(valid_files) - 5} more")
        
        # Test WCS analysis on one valid file
        if valid_files:
            print(f"\n🔬 Testing WCS analysis on: {valid_files[0]}")
            test_wcs_analysis(csv_files[0])
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_wcs_analysis(file_path):
    """Test WCS analysis on a single file"""
    try:
        from file_ingestion import read_csv_with_metadata, validate_velocity_data
        from wcs_analysis import perform_wcs_analysis
        
        print(f"  📖 Reading file...")
        df, metadata, file_type_info = read_csv_with_metadata(file_path)
        
        if df is None:
            print(f"  ❌ File reading failed")
            return
        
        print(f"  ✅ File read successfully")
        
        if not validate_velocity_data(df):
            print(f"  ❌ Data validation failed")
            return
        
        print(f"  ✅ Data validation passed")
        
        # Set up parameters
        parameters = {
            'sampling_rate': 10,
            'epoch_duration': 1.0,
            'epoch_durations': [1.0, 2.0, 5.0],
            'th0_min': 0.0,
            'th0_max': 100.0,
            'th1_min': 5.0,
            'th1_max': 100.0,
        }
        
        print(f"  🔬 Running WCS analysis...")
        results = perform_wcs_analysis(df, metadata, file_type_info, parameters)
        
        if results is None:
            print(f"  ❌ WCS analysis returned None")
            return
        
        print(f"  ✅ WCS analysis completed successfully!")
        print(f"  📊 Rolling WCS results: {len(results.get('rolling_wcs_results', []))} epochs")
        print(f"  📊 Contiguous WCS results: {len(results.get('contiguous_wcs_results', []))} epochs")
        
        # Show sample results
        if results.get('rolling_wcs_results'):
            print(f"  📋 Sample results:")
            for i, result in enumerate(results['rolling_wcs_results'][:3]):
                epoch_duration = result[8]
                th0_distance = result[0]
                th1_distance = result[4]
                print(f"    Epoch {i+1} ({epoch_duration}min): TH0={th0_distance:.1f}m, TH1={th1_distance:.1f}m")
        
        print(f"  🎉 WCS analysis is working correctly!")
        
    except Exception as e:
        print(f"  ❌ WCS analysis error: {e}")

if __name__ == "__main__":
    quick_folder_analysis() 