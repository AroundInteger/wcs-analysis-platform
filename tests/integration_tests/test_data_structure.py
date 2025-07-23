#!/usr/bin/env python3
"""
Test script to verify data structure and debug Results tab
"""

import sys
import os
sys.path.append('.')

from src.file_ingestion import read_csv_with_metadata, validate_velocity_data
from src.wcs_analysis import perform_wcs_analysis

def test_data_structure():
    """Test the data structure with a sample file"""
    
    print("🧪 Testing Data Structure")
    print("=" * 50)
    
    # Test with one of the generated files
    test_file = "test_data_advanced_analytics/Forward_Player_A_TestMatch(MD1).csv"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return
    
    try:
        # Read and validate data
        print(f"📁 Reading file: {test_file}")
        df, metadata, file_type_info = read_csv_with_metadata(test_file)
        
        if df is None or metadata is None:
            print("❌ Failed to read file")
            return
        
        print(f"✅ File read successfully")
        print(f"   - Records: {len(df)}")
        print(f"   - Player: {metadata.get('player_name', 'Unknown')}")
        print(f"   - Duration: {metadata.get('duration_minutes', 0):.1f} minutes")
        
        # Validate velocity data
        print("🔍 Validating velocity data...")
        validation_result = validate_velocity_data(df)
        print(f"   - Validation result: {validation_result}")
        
        if not validation_result:
            print("❌ Velocity data validation failed")
            return
        
        print("✅ Velocity data validated")
        
        # Check data statistics
        print(f"   - Velocity range: {df['Velocity'].min():.2f} - {df['Velocity'].max():.2f} m/s")
        print(f"   - Data length: {len(df)} records")
        print(f"   - Missing values: {df['Velocity'].isna().sum()}")
        
        # Prepare parameters
        parameters = {
            'sampling_rate': 10,
            'epoch_durations': [5.0],  # 5 minutes
            'th0_min': 0.0,
            'th0_max': 100.0,
            'th1_min': 5.5,
            'th1_max': 7.0
        }
        
        # Perform WCS analysis
        print("🔬 Performing WCS analysis...")
        print(f"   - Parameters: {parameters}")
        print(f"   - DataFrame shape: {df.shape}")
        print(f"   - DataFrame columns: {list(df.columns)}")
        
        try:
            results = perform_wcs_analysis(df, metadata, file_type_info, parameters)
            
            if results is None:
                print("❌ WCS analysis failed - returned None")
                print("   - This suggests validate_velocity_data failed inside perform_wcs_analysis")
                return
                
        except Exception as e:
            print(f"❌ WCS analysis failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            return
        
        print("✅ WCS analysis completed")
        
        # Create the data structure that would be passed to display_batch_summary
        all_results = [{
            'file_path': test_file,
            'metadata': metadata,
            'results': results
        }]
        
        print("\n📊 Data Structure Analysis:")
        print("=" * 30)
        
        # Test the structure
        result = all_results[0]
        
        print(f"✅ Has 'metadata': {'metadata' in result}")
        print(f"✅ Has 'results': {'results' in result}")
        print(f"✅ Has 'file_path': {'file_path' in result}")
        
        # Check metadata structure
        metadata = result['metadata']
        print(f"\n📋 Metadata keys: {list(metadata.keys())}")
        print(f"   - player_name: {metadata.get('player_name', 'Not found')}")
        print(f"   - total_records: {metadata.get('total_records', 'Not found')}")
        print(f"   - duration_minutes: {metadata.get('duration_minutes', 'Not found')}")
        
        # Check results structure
        wcs_results = result['results']
        print(f"\n🔬 Results keys: {list(wcs_results.keys())}")
        
        # Check for WCS data
        if 'wcs_rolling' in wcs_results:
            rolling_data = wcs_results['wcs_rolling']
            print(f"✅ Has wcs_rolling data: {len(rolling_data)} epochs")
            
            if rolling_data:
                first_epoch = rolling_data[0]
                print(f"   - First epoch structure: {type(first_epoch)}")
                if isinstance(first_epoch, list):
                    print(f"   - First epoch length: {len(first_epoch)}")
                    if len(first_epoch) >= 8:
                        print(f"   - Default threshold distance: {first_epoch[0]:.1f} m")
                        print(f"   - Default threshold duration: {first_epoch[1]:.1f} s")
        
        if 'wcs_contiguous' in wcs_results:
            contiguous_data = wcs_results['wcs_contiguous']
            print(f"✅ Has wcs_contiguous data: {len(contiguous_data)} epochs")
        
        # Test the display_batch_summary logic
        print(f"\n🧪 Testing display_batch_summary logic:")
        print("=" * 40)
        
        total_files = len(all_results)
        successful_files = len([r for r in all_results if r and 'metadata' in r and 'results' in r])
        failed_files = total_files - successful_files
        
        print(f"   - Total files: {total_files}")
        print(f"   - Successful files: {successful_files}")
        print(f"   - Failed files: {failed_files}")
        print(f"   - Success rate: {(successful_files / total_files * 100):.1f}%")
        
        # Test file details creation
        file_details = []
        for i, result in enumerate(all_results, 1):
            if result and 'metadata' in result and 'results' in result:
                metadata = result['metadata']
                file_details.append({
                    'File': i,
                    'Player': metadata.get('player_name', 'Unknown'),
                    'Type': metadata.get('file_type', 'Unknown'),
                    'Records': metadata.get('total_records', 0),
                    'Duration (min)': f"{metadata.get('duration_minutes', 0):.1f}",
                    'Status': 'Success'
                })
        
        print(f"   - File details created: {len(file_details)} entries")
        if file_details:
            print(f"   - First file: {file_details[0]}")
        
        # Test WCS summary calculation
        total_wcs_distance = 0
        total_wcs_periods = 0
        
        for result in all_results:
            if result and 'results' in result:
                wcs_results = result['results']
                if 'wcs_rolling' in wcs_results:
                    for period in wcs_results['wcs_rolling']:
                        if isinstance(period, list) and len(period) >= 8:
                            total_wcs_distance += period[0]  # distance is at index 0
                            total_wcs_periods += 1
        
        print(f"   - Total WCS distance: {total_wcs_distance:.1f} m")
        print(f"   - Total WCS periods: {total_wcs_periods}")
        
        print("\n✅ Data structure test completed successfully!")
        print("🌐 The Results tab should now work properly in the web interface.")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_structure() 