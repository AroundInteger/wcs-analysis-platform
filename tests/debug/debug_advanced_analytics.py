#!/usr/bin/env python3
"""
Debug Advanced Analytics
This script tests the advanced analytics function directly to identify any issues.
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from advanced_analytics import analyze_cohort_performance
from file_ingestion import read_csv_with_metadata, validate_velocity_data
from wcs_analysis import perform_wcs_analysis

def test_advanced_analytics_directly():
    """Test the advanced analytics function directly"""
    
    print("🔍 Debugging Advanced Analytics")
    print("=" * 50)
    
    # Test with one of our test files
    test_file = Path("test_data_advanced_analytics/Forward_Player_A_TestMatch(MD1).csv")
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print(f"📄 Testing with: {test_file.name}")
    
    try:
        # Load and process the file
        df, metadata, file_type_info = read_csv_with_metadata(str(test_file))
        
        if df is None or df.empty:
            print("❌ Failed to load file")
            return False
        
        print(f"✅ Loaded data shape: {df.shape}")
        
        # Create analysis parameters
        parameters = {
            'method': 'rolling',
            'default_threshold_min': 5.5,
            'default_threshold_max': 7.0,
            'epoch_duration': 300,
            'sampling_rate': 10
        }
        
        # Perform WCS analysis
        print("🔄 Performing WCS analysis...")
        wcs_results = perform_wcs_analysis(df, metadata, file_type_info, parameters)
        
        if not wcs_results:
            print("❌ WCS analysis failed")
            return False
        
        print("✅ WCS analysis completed")
        
        # Create the results structure expected by advanced analytics
        results = [{
            'results': wcs_results,
            'metadata': metadata,
            'file_name': test_file.stem
        }]
        
        print(f"📊 Results structure: {type(results)}")
        print(f"📊 Number of results: {len(results)}")
        
        # Test advanced analytics
        print("\n🔬 Testing Advanced Analytics...")
        cohort_analysis = analyze_cohort_performance(results)
        
        if cohort_analysis:
            print("✅ Advanced analytics completed successfully!")
            
            # Check what's in the results
            print(f"📋 Keys in cohort_analysis: {list(cohort_analysis.keys())}")
            
            if 'error' in cohort_analysis:
                print(f"❌ Error in cohort analysis: {cohort_analysis['error']}")
                return False
            
            if 'summary' in cohort_analysis:
                summary = cohort_analysis['summary']
                print(f"📊 Summary: {summary}")
            
            if 'statistics' in cohort_analysis:
                stats = cohort_analysis['statistics']
                print(f"📈 Statistics keys: {list(stats.keys())}")
            
            return True
        else:
            print("❌ Advanced analytics returned None")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_data_structure():
    """Test the data structure expected by advanced analytics"""
    
    print("\n🔍 Testing Data Structure")
    print("=" * 40)
    
    # Create a simple test data structure
    test_data = {
        'results': {
            'wcs_analysis': [
                {
                    'epoch_duration': 300,
                    'thresholds': [
                        {
                            'threshold_name': 'Default',
                            'distance': 25.5,
                            'time_range': [0, 300],
                            'frequency': 5,
                            'avg_velocity': 6.2,
                            'max_velocity': 7.1
                        }
                    ]
                }
            ]
        },
        'metadata': {
            'player_name': 'Test_Player'
        }
    }
    
    results = [test_data, test_data]  # Need at least 2 files
    
    print("📊 Testing with simple data structure (2 files)...")
    cohort_analysis = analyze_cohort_performance(results)
    
    if cohort_analysis and 'error' not in cohort_analysis:
        print("✅ Simple data structure works!")
        return True
    else:
        print(f"❌ Simple data structure failed: {cohort_analysis}")
        return False

if __name__ == "__main__":
    print("🚀 Advanced Analytics Debug Test")
    print("=" * 50)
    
    # Test data structure first
    structure_ok = test_data_structure()
    
    if structure_ok:
        print("\n" + "="*50)
        # Test with real file
        file_ok = test_advanced_analytics_directly()
        
        if file_ok:
            print("\n🎉 All tests passed! Advanced analytics should work.")
        else:
            print("\n❌ File test failed.")
    else:
        print("\n❌ Data structure test failed.")
    
    print("\n🏁 Debug test completed.") 