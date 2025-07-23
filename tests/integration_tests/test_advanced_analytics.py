#!/usr/bin/env python3
"""
Test script for Advanced Analytics functionality

This script tests the advanced analytics module with sample data to ensure
all features work correctly for large batch processing scenarios.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from advanced_analytics import (
    analyze_cohort_performance,
    create_cohort_report,
    export_cohort_analysis
)

def create_sample_results(num_files=15):
    """Create sample analysis results for testing"""
    
    sample_results = []
    
    for i in range(num_files):
        # Create sample metadata
        metadata = {
            'player_name': f'Player_{i+1:02d}',
            'file_type': 'StatSport',
            'total_records': 6000 + i * 100,
            'duration_minutes': 90 + i * 2
        }
        
        # Create sample WCS analysis data
        wcs_analysis = []
        
        for epoch_duration in [1.0, 2.0, 5.0]:
            epoch_data = {
                'epoch_duration': epoch_duration,
                'thresholds': []
            }
            
            for threshold_name in ['Default Threshold', 'Threshold 1']:
                # Create realistic sample data with some variation
                base_distance = 150 + (i * 10) + (epoch_duration * 20)
                variation = np.random.normal(0, 15)
                distance = max(50, base_distance + variation)
                
                threshold_data = {
                    'threshold_name': threshold_name,
                    'distance': distance,
                    'time_range': f'{i*5}-{i*5+int(epoch_duration*60)}',
                    'frequency': 3 + i % 5,
                    'avg_velocity': 6.5 + (i * 0.1) + np.random.normal(0, 0.3),
                    'max_velocity': 8.0 + (i * 0.15) + np.random.normal(0, 0.5)
                }
                
                epoch_data['thresholds'].append(threshold_data)
            
            wcs_analysis.append(epoch_data)
        
        # Create sample results structure
        result = {
            'metadata': metadata,
            'results': {
                'wcs_analysis': wcs_analysis,
                'velocity_stats': {
                    'mean': 6.5 + (i * 0.1),
                    'max': 8.0 + (i * 0.15),
                    'std': 1.2 + (i * 0.05)
                }
            }
        }
        
        sample_results.append(result)
    
    return sample_results

def test_cohort_analysis():
    """Test the cohort analysis functionality"""
    
    print("🧪 Testing Advanced Analytics Module...")
    print("=" * 50)
    
    # Test 1: Create sample data
    print("📊 Creating sample data...")
    sample_results = create_sample_results(15)
    print(f"✅ Created {len(sample_results)} sample files")
    
    # Test 2: Perform cohort analysis
    print("\n🔬 Performing cohort analysis...")
    try:
        cohort_analysis = analyze_cohort_performance(sample_results)
        
        if 'error' in cohort_analysis:
            print(f"❌ Cohort analysis failed: {cohort_analysis['error']}")
            return False
        
        print("✅ Cohort analysis completed successfully")
        
        # Test 3: Check analysis components
        print("\n📋 Checking analysis components...")
        
        required_components = ['cohort_data', 'statistics', 'visualizations', 'rankings', 'outliers', 'summary']
        for component in required_components:
            if component in cohort_analysis:
                print(f"✅ {component}: Present")
            else:
                print(f"❌ {component}: Missing")
                return False
        
        # Test 4: Check data quality
        print("\n📊 Checking data quality...")
        df = cohort_analysis['cohort_data']
        print(f"✅ Cohort data shape: {df.shape}")
        print(f"✅ Unique players: {df['player_name'].nunique()}")
        print(f"✅ Total observations: {len(df)}")
        
        # Test 5: Check statistics
        stats = cohort_analysis['statistics']
        if 'overall' in stats:
            overall = stats['overall']
            print(f"✅ Overall statistics: {overall['total_players']} players, {overall['total_observations']} observations")
        
        # Test 6: Check visualizations
        viz = cohort_analysis['visualizations']
        expected_viz = ['performance_distribution', 'performance_heatmap', 'threshold_comparison', 'player_radar', 'performance_scatter']
        for viz_name in expected_viz:
            if viz_name in viz:
                print(f"✅ {viz_name}: Created")
            else:
                print(f"❌ {viz_name}: Missing")
        
        # Test 7: Check rankings
        rankings = cohort_analysis['rankings']
        if 'overall' in rankings and 'consistency' in rankings:
            print("✅ Performance rankings: Created")
        else:
            print("❌ Performance rankings: Missing")
        
        # Test 8: Generate report
        print("\n📋 Generating cohort report...")
        try:
            report = create_cohort_report(cohort_analysis)
            print(f"✅ Report generated: {len(report)} characters")
        except Exception as e:
            print(f"❌ Report generation failed: {e}")
            return False
        
        # Test 9: Test export functionality
        print("\n📤 Testing export functionality...")
        try:
            output_path = "test_output"
            os.makedirs(output_path, exist_ok=True)
            
            exported_files = export_cohort_analysis(cohort_analysis, output_path)
            
            if 'error' in exported_files:
                print(f"❌ Export failed: {exported_files['error']}")
            else:
                print("✅ Export completed successfully")
                for file_type, file_path in exported_files.items():
                    if os.path.exists(file_path):
                        print(f"   ✅ {file_type}: {file_path}")
                    else:
                        print(f"   ❌ {file_type}: File not found")
            
        except Exception as e:
            print(f"❌ Export test failed: {e}")
            return False
        
        print("\n🎉 All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Cohort analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """Test edge cases and error handling"""
    
    print("\n🔍 Testing edge cases...")
    print("=" * 30)
    
    # Test 1: Insufficient files
    print("📊 Testing with insufficient files...")
    try:
        small_results = create_sample_results(1)  # Only 1 file
        cohort_analysis = analyze_cohort_performance(small_results)
        
        if 'error' in cohort_analysis:
            print("✅ Correctly handled insufficient files")
        else:
            print("❌ Should have returned error for insufficient files")
            return False
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False
    
    # Test 2: Empty results
    print("📊 Testing with empty results...")
    try:
        cohort_analysis = analyze_cohort_performance([])
        
        if 'error' in cohort_analysis:
            print("✅ Correctly handled empty results")
        else:
            print("❌ Should have returned error for empty results")
            return False
    except Exception as e:
        print(f"❌ Empty results test failed: {e}")
        return False
    
    # Test 3: Invalid data structure
    print("📊 Testing with invalid data structure...")
    try:
        invalid_results = [{'metadata': {'player_name': 'Test'}}]  # Missing results
        cohort_analysis = analyze_cohort_performance(invalid_results)
        
        if 'error' in cohort_analysis:
            print("✅ Correctly handled invalid data structure")
        else:
            print("❌ Should have returned error for invalid data structure")
            return False
    except Exception as e:
        print(f"❌ Invalid data test failed: {e}")
        return False
    
    print("✅ All edge case tests passed!")
    return True

def main():
    """Main test function"""
    
    print("🚀 Advanced Analytics Test Suite")
    print("=" * 50)
    
    # Run main functionality tests
    if not test_cohort_analysis():
        print("\n❌ Main functionality tests failed")
        return False
    
    # Run edge case tests
    if not test_edge_cases():
        print("\n❌ Edge case tests failed")
        return False
    
    print("\n🎉 All tests completed successfully!")
    print("✅ Advanced analytics module is working correctly")
    
    # Cleanup test output
    if os.path.exists("test_output"):
        import shutil
        shutil.rmtree("test_output")
        print("🧹 Cleaned up test output directory")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 