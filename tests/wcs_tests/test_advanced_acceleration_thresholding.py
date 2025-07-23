#!/usr/bin/env python3
"""
Advanced WCS Testing with Acceleration Thresholding
Multiple scenarios with different threshold levels and realistic sports data patterns
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.append('.')

from src.wcs_analysis import calculate_wcs_period_rolling, calculate_wcs_period_contiguous, calculate_acceleration

def create_realistic_sports_velocity_data():
    """Create realistic sports velocity data with multiple intensity zones"""
    
    print("🏃‍♂️ Creating Realistic Sports Velocity Data")
    print("=" * 50)
    
    # Create time series (10Hz for 3 minutes)
    sampling_rate = 10
    duration_seconds = 180
    num_samples = duration_seconds * sampling_rate
    time_seconds = np.linspace(0, duration_seconds, num_samples)
    
    # Create realistic sports velocity profile
    velocities = np.zeros(num_samples)
    
    for i, t in enumerate(time_seconds):
        # Baseline walking/jogging velocity
        baseline = 1.5
        
        # Add realistic sports patterns
        if 20 <= t <= 35:
            # Sprint acceleration phase
            phase_progress = (t - 20) / 15
            intensity = 8.0 * np.sin(phase_progress * np.pi / 2) ** 2
            
        elif 35 < t <= 50:
            # Sprint maintenance phase
            intensity = 8.0 * np.exp(-0.1 * (t - 35))
            
        elif 50 < t <= 65:
            # Sprint deceleration phase
            phase_progress = (65 - t) / 15
            intensity = 8.0 * np.sin(phase_progress * np.pi / 2) ** 2
            
        elif 80 <= t <= 95:
            # High-intensity interval
            phase_progress = (t - 80) / 15
            intensity = 6.0 * np.sin(phase_progress * np.pi) ** 2
            
        elif 95 < t <= 110:
            # Recovery phase
            intensity = 2.0 * np.exp(-0.2 * (t - 95))
            
        elif 130 <= t <= 145:
            # Moderate intensity phase
            phase_progress = (t - 130) / 15
            intensity = 4.0 * np.sin(phase_progress * np.pi) ** 2
            
        elif 145 < t <= 160:
            # Cool-down phase
            phase_progress = (160 - t) / 15
            intensity = 3.0 * np.sin(phase_progress * np.pi / 2) ** 2
            
        else:
            # Low-intensity periods
            intensity = 0.5 * np.sin(t * 0.1) ** 2
        
        velocities[i] = baseline + intensity
    
    print(f"✅ Created realistic sports velocity data:")
    print(f"   - Duration: {duration_seconds} seconds")
    print(f"   - Sprint phases: t=20-35s (accel), t=35-50s (maintain), t=50-65s (decel)")
    print(f"   - High-intensity interval: t=80-95s")
    print(f"   - Recovery phase: t=95-110s")
    print(f"   - Moderate intensity: t=130-145s")
    print(f"   - Cool-down: t=145-160s")
    print(f"   - Baseline: 1.5 m/s (walking/jogging)")
    print(f"   - Peak velocity: ~9.5 m/s (sprint)")
    print(f"   - Sampling rate: {sampling_rate} Hz")
    
    return velocities, time_seconds, sampling_rate

def test_multiple_acceleration_thresholds(velocities, time_seconds, sampling_rate):
    """Test WCS with multiple acceleration threshold levels"""
    
    print(f"\n🔬 Testing Multiple Acceleration Thresholds")
    print("=" * 55)
    
    # Calculate acceleration
    acceleration = calculate_acceleration(velocities, sampling_rate)
    
    # Test different threshold levels
    thresholds = [0.1, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0]
    epoch_duration = 20.0 / 60.0  # 20 seconds
    
    results = {}
    
    for threshold in thresholds:
        print(f"\n📊 Testing threshold: |a| >= {threshold} m/s²")
        print("-" * 40)
        
        # Apply threshold
        threshold_mask = np.abs(acceleration) >= threshold
        thresholded_velocities = np.where(threshold_mask, velocities, 0.0)
        thresholded_acceleration = np.where(threshold_mask, acceleration, 0.0)
        
        # Calculate statistics
        original_nonzero = np.sum(velocities > 0)
        thresholded_nonzero = np.sum(thresholded_velocities > 0)
        reduction_percent = ((original_nonzero - thresholded_nonzero) / original_nonzero) * 100
        
        print(f"  Data reduction: {reduction_percent:.1f}%")
        print(f"  Remaining data: {thresholded_nonzero}/{original_nonzero} samples")
        
        # Calculate WCS for both methods
        try:
            # Rolling WCS
            rolling_distance, rolling_time, rolling_start, rolling_end = calculate_wcs_period_rolling(
                thresholded_velocities, epoch_duration, sampling_rate, 0.0, 100.0
            )
            
            # Contiguous WCS
            contiguous_distance, contiguous_time, contiguous_start, contiguous_end = calculate_wcs_period_contiguous(
                thresholded_velocities, epoch_duration, sampling_rate, 0.0, 100.0
            )
            
            # Store results
            results[threshold] = {
                'reduction_percent': reduction_percent,
                'rolling_wcs': {
                    'distance': rolling_distance,
                    'time': rolling_time,
                    'start': rolling_start,
                    'end': rolling_end,
                    'center_time': time_seconds[rolling_start + (rolling_end - rolling_start) // 2] if rolling_start < rolling_end else 0
                },
                'contiguous_wcs': {
                    'distance': contiguous_distance,
                    'time': contiguous_time,
                    'start': contiguous_start,
                    'end': contiguous_end,
                    'center_time': time_seconds[contiguous_start + (contiguous_end - contiguous_start) // 2] if contiguous_start < contiguous_end else 0
                }
            }
            
            print(f"  Rolling WCS: {rolling_distance:.1f}m at t={time_seconds[rolling_start + (rolling_end - rolling_start) // 2]:.1f}s")
            print(f"  Contiguous WCS: {contiguous_distance:.1f}m at t={time_seconds[contiguous_start + (contiguous_end - contiguous_start) // 2]:.1f}s")
            
        except Exception as e:
            print(f"  Error calculating WCS: {e}")
            results[threshold] = None
    
    return results, acceleration

def analyze_threshold_effects(results, acceleration):
    """Analyze the effects of different acceleration thresholds"""
    
    print(f"\n📈 Acceleration Threshold Effect Analysis")
    print("=" * 50)
    
    # Create analysis table
    print(f"{'Threshold':<10} {'Reduction':<12} {'Rolling WCS':<15} {'Contiguous WCS':<15} {'Rolling Center':<15} {'Contiguous Center':<15}")
    print("-" * 90)
    
    for threshold, result in results.items():
        if result is not None:
            rolling = result['rolling_wcs']
            contiguous = result['contiguous_wcs']
            print(f"{threshold:<10.1f} {result['reduction_percent']:<12.1f} {rolling['distance']:<15.1f} {contiguous['distance']:<15.1f} {rolling['center_time']:<15.1f} {contiguous['center_time']:<15.1f}")
    
    # Find optimal threshold (best balance of data retention and dynamic focus)
    valid_results = {k: v for k, v in results.items() if v is not None}
    
    if valid_results:
        # Calculate optimal threshold (where we have meaningful WCS but still filter noise)
        optimal_threshold = None
        best_balance = 0
        
        for threshold, result in valid_results.items():
            # Balance between data retention and meaningful filtering
            data_retention = 100 - result['reduction_percent']
            rolling_wcs = result['rolling_wcs']['distance']
            
            # Score based on data retention and WCS magnitude
            balance_score = data_retention * rolling_wcs / 100
            
            if balance_score > best_balance:
                best_balance = balance_score
                optimal_threshold = threshold
        
        print(f"\n🎯 Optimal Threshold Analysis:")
        print(f"  Recommended threshold: {optimal_threshold} m/s²")
        print(f"  Balance score: {best_balance:.1f}")
        
        if optimal_threshold:
            optimal_result = valid_results[optimal_threshold]
            print(f"  Data reduction: {optimal_result['reduction_percent']:.1f}%")
            print(f"  Rolling WCS: {optimal_result['rolling_wcs']['distance']:.1f}m")
            print(f"  Contiguous WCS: {optimal_result['contiguous_wcs']['distance']:.1f}m")

def plot_threshold_comparison(velocities, acceleration, time_seconds, results):
    """Create comprehensive visualization of threshold effects"""
    
    print(f"\n📊 Generating Threshold Comparison Plots")
    print("=" * 45)
    
    # Create figure with subplots
    fig, axes = plt.subplots(3, 2, figsize=(15, 12))
    fig.suptitle('WCS Analysis with Multiple Acceleration Thresholds', fontsize=16, fontweight='bold')
    
    # Plot 1: Original velocity and acceleration
    ax1 = axes[0, 0]
    ax1.plot(time_seconds, velocities, 'b-', linewidth=2, label='Velocity')
    ax1.set_ylabel('Velocity (m/s)', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.set_title('Original Velocity Profile')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    ax1_twin = ax1.twinx()
    ax1_twin.plot(time_seconds, acceleration, 'r-', linewidth=1, alpha=0.7, label='Acceleration')
    ax1_twin.set_ylabel('Acceleration (m/s²)', color='r')
    ax1_twin.tick_params(axis='y', labelcolor='r')
    ax1_twin.legend(loc='upper right')
    
    # Plot 2: Acceleration magnitude distribution
    ax2 = axes[0, 1]
    accel_magnitude = np.abs(acceleration)
    ax2.hist(accel_magnitude, bins=50, alpha=0.7, color='orange', edgecolor='black')
    ax2.axvline(x=0.5, color='red', linestyle='--', label='Threshold = 0.5 m/s²')
    ax2.axvline(x=1.0, color='red', linestyle=':', label='Threshold = 1.0 m/s²')
    ax2.set_xlabel('Acceleration Magnitude (m/s²)')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Acceleration Magnitude Distribution')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Data reduction vs threshold
    ax3 = axes[1, 0]
    thresholds = list(results.keys())
    reductions = [results[t]['reduction_percent'] if results[t] else 0 for t in thresholds]
    ax3.plot(thresholds, reductions, 'go-', linewidth=2, markersize=8)
    ax3.set_xlabel('Acceleration Threshold (m/s²)')
    ax3.set_ylabel('Data Reduction (%)')
    ax3.set_title('Data Reduction vs Threshold')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: WCS distance vs threshold
    ax4 = axes[1, 1]
    rolling_distances = [results[t]['rolling_wcs']['distance'] if results[t] else 0 for t in thresholds]
    contiguous_distances = [results[t]['contiguous_wcs']['distance'] if results[t] else 0 for t in thresholds]
    
    ax4.plot(thresholds, rolling_distances, 'bo-', linewidth=2, markersize=8, label='Rolling WCS')
    ax4.plot(thresholds, contiguous_distances, 'ro-', linewidth=2, markersize=8, label='Contiguous WCS')
    ax4.set_xlabel('Acceleration Threshold (m/s²)')
    ax4.set_ylabel('WCS Distance (m)')
    ax4.set_title('WCS Distance vs Threshold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Plot 5: Thresholded velocity comparison (selective thresholds)
    ax5 = axes[2, 0]
    select_thresholds = [0.1, 0.5, 1.0]
    colors = ['green', 'orange', 'red']
    
    for i, threshold in enumerate(select_thresholds):
        if threshold in results and results[threshold]:
            threshold_mask = np.abs(acceleration) >= threshold
            thresholded_vel = np.where(threshold_mask, velocities, 0.0)
            ax5.plot(time_seconds, thresholded_vel, color=colors[i], alpha=0.7, 
                    linewidth=1, label=f'Threshold = {threshold} m/s²')
    
    ax5.set_xlabel('Time (s)')
    ax5.set_ylabel('Velocity (m/s)')
    ax5.set_title('Velocity After Thresholding')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # Plot 6: WCS center time vs threshold
    ax6 = axes[2, 1]
    rolling_centers = [results[t]['rolling_wcs']['center_time'] if results[t] else 0 for t in thresholds]
    contiguous_centers = [results[t]['contiguous_wcs']['center_time'] if results[t] else 0 for t in thresholds]
    
    ax6.plot(thresholds, rolling_centers, 'bo-', linewidth=2, markersize=8, label='Rolling WCS')
    ax6.plot(thresholds, contiguous_centers, 'ro-', linewidth=2, markersize=8, label='Contiguous WCS')
    ax6.set_xlabel('Acceleration Threshold (m/s²)')
    ax6.set_ylabel('WCS Center Time (s)')
    ax6.set_title('WCS Center Time vs Threshold')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"advanced_acceleration_thresholding_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✅ Saved plot: {filename}")
    
    plt.show()

def main():
    """Main function to run advanced acceleration thresholding tests"""
    
    print("🧪 Advanced WCS Acceleration Thresholding Test")
    print("=" * 70)
    print("Testing multiple acceleration thresholds with realistic sports data")
    print("=" * 70)
    
    # Create realistic sports velocity data
    velocities, time_seconds, sampling_rate = create_realistic_sports_velocity_data()
    
    # Test multiple acceleration thresholds
    results, acceleration = test_multiple_acceleration_thresholds(velocities, time_seconds, sampling_rate)
    
    # Analyze threshold effects
    analyze_threshold_effects(results, acceleration)
    
    # Create comprehensive visualization
    plot_threshold_comparison(velocities, acceleration, time_seconds, results)
    
    print(f"\n🎉 Advanced Acceleration Thresholding Test Complete!")
    print("=" * 70)
    print("Key findings:")
    print("- Different thresholds provide different levels of data filtering")
    print("- Optimal threshold balances data retention with dynamic focus")
    print("- WCS results vary significantly with threshold level")
    print("- Both rolling and contiguous methods affected by thresholding")
    print("=" * 70)

if __name__ == "__main__":
    main() 