#!/usr/bin/env python3
"""
Test Blackpool Data with Valid Velocity Values

This script tests the WCS analysis with a different Blackpool player's data
to verify it works with valid velocity values.
"""

import sys
import os
import pandas as pd
import numpy as np
import traceback

# Add src to path
sys.path.insert(0, 'src')

def test_blackpool_players():
    """Test with different Blackpool players to find one with valid data"""
    print("🔍 Testing different Blackpool players for valid data...")
    
    # List of Blackpool files to test
    blackpool_files = [
        "/Users/rowanbrown/Library/CloudStorage/OneDrive-SwanseaUniversity/Research/WIPS/Intensity Monitoring/DATA2/Blackpool (A) 13.08.22/BLACKPOOL (A) Export for Ben Cabango 41603.csv",
        "/Users/rowanbrown/Library/CloudStorage/OneDrive-SwanseaUniversity/Research/WIPS/Intensity Monitoring/DATA2/Blackpool (A) 13.08.22/BLACKPOOL (A) Export for Cam Congreve 22665.csv",
        "/Users/rowanbrown/Library/CloudStorage/OneDrive-SwanseaUniversity/Research/WIPS/Intensity Monitoring/DATA2/Blackpool (A) 13.08.22/BLACKPOOL (A) Export for Harry Darling 22303.csv",
        "/Users/rowanbrown/Library/CloudStorage/OneDrive-SwanseaUniversity/Research/WIPS/Intensity Monitoring/DATA2/Blackpool (A) 13.08.22/BLACKPOOL (A) Export for Jay Fulton 22198.csv",
        "/Users/rowanbrown/Library/CloudStorage/OneDrive-SwanseaUniversity/Research/WIPS/Intensity Monitoring/DATA2/Blackpool (A) 13.08.22/BLACKPOOL (A) Export for Joe Allen 27404.csv"
    ]
    
    try:
        from file_ingestion import read_csv_with_metadata, validate_velocity_data
        
        for file_path in blackpool_files:
            if not os.path.exists(file_path):
                print(f"❌ File not found: {os.path.basename(file_path)}")
                continue
            
            print(f"\n📄 Testing: {os.path.basename(file_path)}")
            
            # Read file
            df, metadata, file_type_info = read_csv_with_metadata(file_path)
            
            if df is None:
                print("❌ Failed to read file")
                continue
            
            # Check velocity data
            velocity_data = df['Velocity'].values
            non_zero_velocities = velocity_data[velocity_data > 0]
            
            print(f"   - Shape: {df.shape}")
            print(f"   - Total velocity points: {len(velocity_data)}")
            print(f"   - Non-zero velocity points: {len(non_zero_velocities)}")
            print(f"   - Velocity range: {np.min(velocity_data):.2f} to {np.max(velocity_data):.2f}")
            print(f"   - Mean velocity: {np.mean(velocity_data):.2f}")
            
            if len(non_zero_velocities) > 0:
                print(f"✅ Found valid data! Player: {metadata.get('player_name', 'Unknown')}")
                return df, metadata, file_type_info
            else:
                print("❌ No valid velocity data")
        
        print("\n❌ No players found with valid velocity data")
        return None, None, None
        
    except Exception as e:
        print(f"❌ Error testing players: {e}")
        traceback.print_exc()
        return None, None, None

def test_wcs_analysis_with_valid_data(df, metadata, file_type_info):
    """Test WCS analysis with valid data"""
    print("\n🔍 Testing WCS analysis with valid data...")
    
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
        
        # Perform WCS analysis
        results = perform_wcs_analysis(df, metadata, file_type_info, parameters)
        
        if results is None:
            print("❌ WCS analysis returned None")
            return False
        
        print("✅ WCS analysis completed successfully")
        print(f"   - Velocity stats: {results.get('velocity_stats', {})}")
        print(f"   - Rolling WCS results: {len(results.get('rolling_wcs_results', []))} epochs")
        print(f"   - Contiguous WCS results: {len(results.get('contiguous_wcs_results', []))} epochs")
        
        # Show some WCS results
        if results.get('rolling_wcs_results'):
            print("\n📈 Sample Rolling WCS Results:")
            for i, result in enumerate(results['rolling_wcs_results']):
                epoch_duration = result[8]
                th0_distance = result[0]
                th1_distance = result[4]
                print(f"   Epoch {i+1} ({epoch_duration}min): TH0={th0_distance:.1f}m, TH1={th1_distance:.1f}m")
        
        return results
        
    except Exception as e:
        print(f"❌ Error in WCS analysis: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Blackpool Valid Data WCS Analysis Test")
    print("=" * 60)
    
    # Test imports
    print("🔍 Testing imports...")
    try:
        from file_ingestion import read_csv_with_metadata, validate_velocity_data
        from wcs_analysis import perform_wcs_analysis
        print("✅ All imports successful")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return
    
    # Test with different Blackpool players
    df, metadata, file_type_info = test_blackpool_players()
    if df is None:
        print("\n❌ No valid data found - cannot continue")
        return
    
    # Test WCS analysis with valid data
    results = test_wcs_analysis_with_valid_data(df, metadata, file_type_info)
    if not results:
        print("\n❌ WCS analysis test failed")
        return
    
    print("\n🎉 All tests passed! WCS analysis is working correctly with valid data.")
    print(f"✅ Successfully analyzed: {metadata.get('player_name', 'Unknown')}")

if __name__ == "__main__":
    main() 