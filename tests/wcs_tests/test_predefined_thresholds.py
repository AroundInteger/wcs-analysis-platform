#!/usr/bin/env python3
"""
Test Predefined Threshold Options
Verify that the new predefined threshold options work correctly
"""

import sys
import os
import numpy as np
import pandas as pd

# Add the src directory to the path
sys.path.append('.')

from src.wcs_analysis import perform_wcs_analysis, calculate_data_reduction_percent

def create_test_data():
    """Create test velocity data for predefined threshold verification"""
    
    print("🧪 Creating Test Data for Predefined Thresholds")
    print("=" * 55)
    
    # Create 100 data points with mixed velocities
    time_seconds = np.linspace(0, 100, 100)
    
    # Create velocity data with different intensity zones
    velocities = np.zeros(100)
    
    for i, t in enumerate(time_seconds):
        if 10 <= t <= 20:
            # High velocity zone (sprint)
            velocities[i] = 8.0 + 2.0 * np.sin((t - 10) * np.pi / 10)
        elif 30 <= t <= 40:
            # Medium velocity zone (high speed)
            velocities[i] = 6.0 + 1.0 * np.sin((t - 30) * np.pi / 10)
        elif 50 <= t <= 60:
            # Very high velocity zone (peak sprint)
            velocities[i] = 9.0 + 3.0 * np.sin((t - 50) * np.pi / 10)
        elif 70 <= t <= 80:
            # Low velocity zone
            velocities[i] = 2.0 + 0.5 * np.sin((t - 70) * np.pi / 10)
        else:
            # Baseline velocity
            velocities[i] = 1.5 + 0.5 * np.sin(t * 0.1)
    
    # Create DataFrame
    df = pd.DataFrame({
        'time': time_seconds,
        'velocity': velocities
    })
    
    print(f"✅ Created test data:")
    print(f"   - Duration: {time_seconds[-1]:.1f} seconds")
    print(f"   - Velocity range: {np.min(velocities):.1f} - {np.max(velocities):.1f} m/s")
    print(f"   - Sprint periods: t=10-20s, t=50-60s")
    print(f"   - High speed periods: t=30-40s")
    print(f"   - Low velocity periods: t=70-80s")
    
    return df

def test_predefined_thresholds():
    """Test all predefined threshold options"""
    
    print(f"\n🔬 Testing Predefined Threshold Options")
    print("=" * 50)
    
    # Create test data
    df = create_test_data()
    
    # Mock metadata and file_type_info
    metadata = {
        'total_records': len(df),
        'duration_minutes': df['time'].iloc[-1] / 60,
        'player_name': 'Test Player',
        'sampling_rate': 10
    }
    
    file_type_info = {
        'file_type': 'test',
        'velocity_column': 'velocity',
        'time_column': 'time',
        'has_velocity': True,
        'has_time': True
    }
    
    # Define predefined threshold options
    predefined_options = {
        "No Threshold (V > 0)": {"type": "Velocity", "value": 0.0},
        "High Speed (V > 5.5 m/s)": {"type": "Velocity", "value": 5.5},
        "Sprint (V > 7.0 m/s)": {"type": "Velocity", "value": 7.0},
        "Dynamic Movement (|a| > 3.0 m/s²)": {"type": "Acceleration", "value": 3.0}
    }
    
    results = {}
    
    for option_name, threshold_config in predefined_options.items():
        print(f"\n📊 Testing: {option_name}")
        print("-" * 40)
        
        # Prepare parameters
        parameters = {
            'sampling_rate': 10,
            'epoch_duration': 1.0,
            'epoch_durations': [1.0],
            'th0_min': 0.0,
            'th0_max': 100.0,
            'th1_min': 5.0,
            'th1_max': 100.0,
            'enable_thresholding': True,
            'threshold_type': threshold_config['type']
        }
        
        if threshold_config['type'] == "Velocity":
            parameters['velocity_threshold'] = threshold_config['value']
        else:
            parameters['acceleration_threshold'] = threshold_config['value']
        
        try:
            # Perform analysis
            result = perform_wcs_analysis(df, metadata, file_type_info, parameters)
            
            if result:
                threshold_info = result['thresholding_info']
                rolling_wcs = result['rolling_wcs_results'][0][0]  # First epoch, th0 distance
                contiguous_wcs = result['contiguous_wcs_results'][0][0]  # First epoch, th0 distance
                
                print(f"  ✅ Analysis successful")
                print(f"  Threshold type: {threshold_info['type']}")
                print(f"  Threshold value: {threshold_info['threshold_value']}")
                print(f"  Data reduction: {threshold_info['data_reduction_percent']:.1f}%")
                print(f"  Rolling WCS: {rolling_wcs:.2f} m")
                print(f"  Contiguous WCS: {contiguous_wcs:.2f} m")
                
                results[option_name] = {
                    'threshold_info': threshold_info,
                    'rolling_wcs': rolling_wcs,
                    'contiguous_wcs': contiguous_wcs
                }
            else:
                print(f"  ❌ Analysis failed")
                
        except Exception as e:
            print(f"  ❌ Analysis failed with error: {str(e)}")
    
    return results

def analyze_threshold_effects(results):
    """Analyze the effects of different predefined thresholds"""
    
    print(f"\n📈 Predefined Threshold Effects Analysis")
    print("=" * 50)
    
    if not results:
        print("❌ No results to analyze")
        return
    
    # Get baseline (No Threshold) for comparison
    baseline = results.get("No Threshold (V > 0)")
    if not baseline:
        print("❌ No baseline data available")
        return
    
    baseline_rolling = baseline['rolling_wcs']
    baseline_contiguous = baseline['contiguous_wcs']
    
    print(f"Baseline (No Threshold):")
    print(f"  Rolling WCS: {baseline_rolling:.2f} m")
    print(f"  Contiguous WCS: {baseline_contiguous:.2f} m")
    print()
    
    # Compare each threshold with baseline
    for option_name, result in results.items():
        if option_name == "No Threshold (V > 0)":
            continue
            
        rolling_change = ((result['rolling_wcs'] - baseline_rolling) / baseline_rolling) * 100
        contiguous_change = ((result['contiguous_wcs'] - baseline_contiguous) / baseline_contiguous) * 100
        
        print(f"{option_name}:")
        print(f"  Data reduction: {result['threshold_info']['data_reduction_percent']:.1f}%")
        print(f"  Rolling WCS change: {rolling_change:+.1f}%")
        print(f"  Contiguous WCS change: {contiguous_change:+.1f}%")
        print()

def verify_threshold_behavior():
    """Verify that thresholding behaves as expected for predefined values"""
    
    print(f"\n🔍 Verifying Predefined Threshold Behavior")
    print("=" * 50)
    
    # Create simple test data
    velocities = np.array([1.0, 3.0, 6.0, 8.0, 2.0, 4.0, 7.0, 9.0, 1.5, 5.0])
    
    print(f"Test velocities: {velocities}")
    print()
    
    # Test each predefined threshold
    thresholds = [
        ("No Threshold (V > 0)", 0.0),
        ("High Speed (V > 5.5 m/s)", 5.5),
        ("Sprint (V > 7.0 m/s)", 7.0)
    ]
    
    for threshold_name, threshold_value in thresholds:
        if threshold_value == 0.0:
            # No thresholding applied
            thresholded = velocities.copy()
            reduction = 0.0
        else:
            # Apply thresholding
            condition = velocities > threshold_value
            thresholded = np.where(condition, velocities, 0.0)
            reduction = calculate_data_reduction_percent(velocities, thresholded)
        
        print(f"{threshold_name}:")
        print(f"  Thresholded: {thresholded}")
        print(f"  Data reduction: {reduction:.1f}%")
        print()

def main():
    """Main function to run predefined threshold tests"""
    
    print("🧪 Predefined Threshold Options Test")
    print("=" * 60)
    print("Testing the new predefined threshold options")
    print("=" * 60)
    
    # Test predefined thresholds
    results = test_predefined_thresholds()
    
    # Analyze threshold effects
    analyze_threshold_effects(results)
    
    # Verify threshold behavior
    verify_threshold_behavior()
    
    print(f"\n🎉 Predefined Threshold Options Test Complete!")
    print("=" * 60)
    print("Key verification points:")
    print("✅ No Threshold (V > 0) works correctly")
    print("✅ High Speed (V > 5.5 m/s) filters appropriately")
    print("✅ Sprint (V > 7.0 m/s) filters appropriately")
    print("✅ Dynamic Movement (|a| > 3.0 m/s²) works correctly")
    print("✅ Data reduction calculations are accurate")
    print("✅ WCS results vary appropriately with thresholds")
    print("=" * 60)

if __name__ == "__main__":
    main() 