#!/usr/bin/env python3
"""
Test Advanced Analytics in Batch Mode
This script tests the advanced analytics functionality with multiple files
to verify the cohort analysis and visualization features work correctly.
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from advanced_analytics import analyze_cohort_performance, create_cohort_report
from file_ingestion import read_csv_with_metadata, validate_velocity_data
from wcs_analysis import perform_wcs_analysis
from batch_processing import process_batch_files

def load_and_validate_file(file_path: str):
    """Load and validate a file using the existing file_ingestion functions"""
    try:
        # Use the existing function from file_ingestion
        df, metadata, file_type_info = read_csv_with_metadata(file_path)
        
        if df is not None and metadata is not None:
            # Validate velocity data
            if validate_velocity_data(df):
                return df
            else:
                print(f"❌ Velocity data validation failed for {file_path}")
                return None
        else:
            print(f"❌ Failed to read file {file_path}")
            return None
            
    except Exception as e:
        print(f"❌ Error loading file {file_path}: {str(e)}")
        return None

def test_advanced_analytics_batch():
    """Test advanced analytics with multiple files in batch mode"""
    
    print("🧪 Testing Advanced Analytics in Batch Mode")
    print("=" * 50)
    
    # Sample data directory
    sample_dir = Path("data/sample_data")
    
    # Get all CSV files for testing
    csv_files = list(sample_dir.glob("*.csv"))
    
    if not csv_files:
        print("❌ No CSV files found in sample_data directory")
        return False
    
    print(f"📁 Found {len(csv_files)} CSV files for testing")
    
    # Process files in batch mode
    print("\n🔄 Processing files in batch mode...")
    
    try:
        # Load and process each file
        processed_data = []
        
        for i, file_path in enumerate(csv_files[:5]):  # Limit to 5 files for testing
            print(f"  📄 Processing {file_path.name} ({i+1}/{min(5, len(csv_files))})")
            
            try:
                # Load and validate file
                data = load_and_validate_file(str(file_path))
                
                if data is not None and not data.empty:
                    # Analyze WCS data
                    # Create metadata and parameters for the analysis
                    metadata = {'player_name': file_path.stem, 'file_name': file_path.name}
                    file_type_info = {'type': 'generic_gps', 'confidence': 0.8}
                    parameters = {
                        'method': 'rolling',
                        'default_threshold_min': 5.5,
                        'default_threshold_max': 7.0,
                        'epoch_duration': 300,
                        'sampling_rate': 10
                    }
                    
                    wcs_results = perform_wcs_analysis(data, metadata, file_type_info, parameters)
                    
                    if wcs_results and 'rolling_wcs_results' in wcs_results:
                        # Add file metadata
                        wcs_results['file_name'] = file_path.stem
                        wcs_results['file_path'] = str(file_path)
                        processed_data.append(wcs_results)
                        print(f"    ✅ Successfully processed {file_path.name}")
                    else:
                        print(f"    ⚠️  No WCS data generated for {file_path.name}")
                else:
                    print(f"    ❌ Failed to load {file_path.name}")
                    
            except Exception as e:
                print(f"    ❌ Error processing {file_path.name}: {str(e)}")
        
        print(f"\n📊 Successfully processed {len(processed_data)} files")
        
        if len(processed_data) < 3:
            print("⚠️  Need at least 3 files for meaningful cohort analysis")
            return False
        
        # Test Advanced Analytics
        print("\n🔬 Testing Advanced Analytics...")
        
        # Prepare data for cohort analysis
        cohort_data = []
        for result in processed_data:
            if 'rolling_wcs_results' in result and result['rolling_wcs_results']:
                # Convert rolling WCS results to DataFrame
                wcs_data = []
                for epoch_data in result['rolling_wcs_results']:
                    if epoch_data:  # Check if epoch has data
                        for wcs_event in epoch_data:
                            wcs_data.append({
                                'distance': wcs_event.get('distance', 0),
                                'velocity': wcs_event.get('velocity', 0),
                                'duration': wcs_event.get('duration', 0),
                                'start_time': wcs_event.get('start_time', 0),
                                'end_time': wcs_event.get('end_time', 0)
                            })
                
                if wcs_data:
                    wcs_df = pd.DataFrame(wcs_data)
                    wcs_df['player'] = result['file_name']
                    cohort_data.append(wcs_df)
        
        if not cohort_data:
            print("❌ No valid WCS data for cohort analysis")
            return False
        
        # Combine all data
        combined_data = pd.concat(cohort_data, ignore_index=True)
        print(f"📈 Combined data shape: {combined_data.shape}")
        print(f"👥 Players in cohort: {combined_data['player'].nunique()}")
        
        # Test cohort performance analysis
        print("\n📊 Running cohort performance analysis...")
        
        try:
            cohort_analysis = analyze_cohort_performance(combined_data)
            
            if cohort_analysis:
                print("✅ Cohort analysis completed successfully")
                
                # Display key metrics
                if 'summary' in cohort_analysis:
                    summary = cohort_analysis['summary']
                    print(f"\n📋 Cohort Summary:")
                    print(f"  - Total players: {summary.get('total_players', 'N/A')}")
                    print(f"  - Total sessions: {summary.get('total_sessions', 'N/A')}")
                    print(f"  - Total WCS events: {summary.get('total_wcs_events', 'N/A')}")
                
                if 'statistics' in cohort_analysis:
                    stats = cohort_analysis['statistics']
                    if 'overall' in stats:
                        overall = stats['overall']
                        print(f"\n📊 Overall Statistics:")
                        print(f"  - Mean distance: {overall.get('mean_distance', 'N/A'):.2f}")
                        print(f"  - Mean velocity: {overall.get('mean_velocity', 'N/A'):.2f}")
                        print(f"  - Total events: {overall.get('total_events', 'N/A')}")
                
                # Test report generation
                print("\n📄 Testing report generation...")
                try:
                    report = create_cohort_report(cohort_analysis, "Test Cohort Report")
                    print("✅ Report generation completed")
                    print(f"📄 Report content length: {len(report) if report else 0} characters")
                except Exception as e:
                    print(f"❌ Report generation failed: {str(e)}")
                
                return True
            else:
                print("❌ Cohort analysis returned None")
                return False
                
        except Exception as e:
            print(f"❌ Cohort analysis failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Batch processing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_components():
    """Test individual components of advanced analytics"""
    
    print("\n🔧 Testing Individual Components")
    print("=" * 40)
    
    # Test with a single file first
    sample_file = Path("data/sample_data/test_generic.csv")
    
    if not sample_file.exists():
        print(f"❌ Test file not found: {sample_file}")
        return False
    
    print(f"📄 Testing with single file: {sample_file.name}")
    
    try:
        # Load file
        data = load_and_validate_file(str(sample_file))
        
        if data is None or data.empty:
            print("❌ Failed to load test file")
            return False
        
        print(f"✅ Loaded data shape: {data.shape}")
        
        # Analyze WCS
        metadata = {'player_name': 'test_player', 'file_name': sample_file.name}
        file_type_info = {'type': 'generic_gps', 'confidence': 0.8}
        parameters = {
            'method': 'rolling',
            'default_threshold_min': 5.5,
            'default_threshold_max': 7.0,
            'epoch_duration': 300,
            'sampling_rate': 10
        }
        
        wcs_results = perform_wcs_analysis(data, metadata, file_type_info, parameters)
        
        if not wcs_results or 'rolling_wcs_results' not in wcs_results:
            print("❌ WCS analysis failed")
            return False
        
        # Convert rolling WCS results to DataFrame
        wcs_data = []
        for epoch_data in wcs_results['rolling_wcs_results']:
            if epoch_data:  # Check if epoch has data
                for wcs_event in epoch_data:
                    wcs_data.append({
                        'distance': wcs_event.get('distance', 0),
                        'velocity': wcs_event.get('velocity', 0),
                        'duration': wcs_event.get('duration', 0),
                        'start_time': wcs_event.get('start_time', 0),
                        'end_time': wcs_event.get('end_time', 0)
                    })
        
        if wcs_data:
            wcs_df = pd.DataFrame(wcs_data)
            wcs_df['player'] = 'test_player'
            print(f"✅ WCS analysis completed, data shape: {wcs_df.shape}")
        else:
            print("❌ No WCS data generated")
            return False
        
        # Test cohort analysis with single player
        print("\n🔬 Testing cohort analysis with single player...")
        
        cohort_analysis = analyze_cohort_performance(wcs_df)
        
        if cohort_analysis:
            print("✅ Single-player cohort analysis completed")
            return True
        else:
            print("❌ Single-player cohort analysis failed")
            return False
            
    except Exception as e:
        print(f"❌ Component test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Advanced Analytics Batch Mode Test")
    print("=" * 50)
    
    # Test individual components first
    component_success = test_individual_components()
    
    if component_success:
        print("\n" + "="*50)
        # Test full batch mode
        batch_success = test_advanced_analytics_batch()
        
        if batch_success:
            print("\n🎉 All tests passed! Advanced analytics working correctly.")
        else:
            print("\n❌ Batch mode test failed.")
    else:
        print("\n❌ Component test failed. Cannot proceed with batch test.")
    
    print("\n🏁 Test completed.") 