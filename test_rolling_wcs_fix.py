#!/usr/bin/env python3
"""
Test script to analyze and fix rolling WCS edge handling and peak detection.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add src to path
sys.path.append('src')

from wcs_analysis import calculate_wcs_period_rolling

def test_rolling_wcs_issues():
    """Test rolling WCS with focus on edge handling and peak detection"""
    
    # Test parameters - same as before
    sigma = 10
    mu = 9 * sigma  # 90 seconds
    t = np.linspace(0, sigma * 18, 1800)  # 0 to 180 seconds
    velocity = 8 * np.exp(-0.5 * ((t - mu) / sigma)**2)  # Normal distribution
    
    # Analysis parameters
    epoch_duration = 1.0  # 1 minute
    sampling_rate = 10    # 10 Hz
    th1_min, th1_max = 5.0, 100.0  # Threshold 1
    
    print(f"Test Parameters:")
    print(f"  Velocity peak at t = {mu} seconds")
    print(f"  Velocity peak value: {np.max(velocity):.3f} m/s")
    print(f"  Data length: {len(velocity)} samples ({len(velocity)/sampling_rate:.1f} seconds)")
    print(f"  Epoch duration: {epoch_duration} minutes ({epoch_duration * 60 * sampling_rate} samples)")
    print()
    
    # Calculate rolling WCS values for each window center to see the curve
    epoch_samples = int(epoch_duration * 60 * sampling_rate)
    half_window = epoch_samples // 2
    
    rolling_wcs_values = []
    rolling_wcs_times = []
    rolling_wcs_centers = []
    
    print("Current implementation only processes windows from index", half_window, "to", len(velocity) - half_window)
    print("This means we miss the first and last", half_window, "samples!")
    print()
    
    # Current implementation (problematic)
    for i in range(half_window, len(velocity) - half_window):
        window_start = i - half_window
        window_end = i + half_window + (1 if epoch_samples % 2 == 1 else 0)
        
        window_data = velocity[window_start:window_end]
        threshold_mask = (window_data >= th1_min) & (window_data <= th1_max)
        
        time_per_sample = 1.0 / sampling_rate
        window_distance = np.sum(window_data[threshold_mask] * time_per_sample)
        
        rolling_wcs_values.append(window_distance)
        rolling_wcs_times.append(t[i])
        rolling_wcs_centers.append(i)
    
    # Find the peak
    if rolling_wcs_values:
        max_idx = np.argmax(rolling_wcs_values)
        max_time = rolling_wcs_times[max_idx]
        max_value = rolling_wcs_values[max_idx]
        max_center = rolling_wcs_centers[max_idx]
        
        print("Current Implementation Results:")
        print(f"  Peak WCS value: {max_value:.3f} m")
        print(f"  Peak time: {max_time:.1f} seconds")
        print(f"  Peak center index: {max_center}")
        print(f"  Expected peak time: {mu} seconds")
        print(f"  Time difference: {abs(max_time - mu):.1f} seconds")
        print()
    
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot velocity
    ax1.plot(t, velocity, 'b-', linewidth=2, label='Velocity')
    ax1.axvline(x=mu, color='red', linestyle='--', alpha=0.7, label=f'Expected peak at t={mu}s')
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('Velocity (m/s)')
    ax1.set_title('Velocity Signal')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot rolling WCS values
    if rolling_wcs_values:
        ax2.plot(rolling_wcs_times, rolling_wcs_values, 'r-', linewidth=2, label='Rolling WCS Values')
        ax2.axvline(x=mu, color='red', linestyle='--', alpha=0.7, label=f'Expected peak at t={mu}s')
        if rolling_wcs_values:
            ax2.axhline(y=max(rolling_wcs_values), color='red', linestyle=':', alpha=0.7, 
                       label=f'Max WCS: {max(rolling_wcs_values):.1f}m')
        
        # Mark the actual peak
        ax2.plot(max_time, max_value, 'ro', markersize=8, label=f'Actual peak at t={max_time:.1f}s')
    
    ax2.set_xlabel('Time (seconds)')
    ax2.set_ylabel('WCS Distance (m)')
    ax2.set_title('Rolling WCS Values Over Time (Current Implementation)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('rolling_wcs_issues.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Results saved to: rolling_wcs_issues.png")
    
    # Now let's implement the correct rolling WCS
    print("\n" + "="*50)
    print("IMPLEMENTING CORRECT ROLLING WCS")
    print("="*50)
    
    # Correct implementation with proper edge handling
    correct_rolling_wcs_values = []
    correct_rolling_wcs_times = []
    correct_rolling_wcs_centers = []
    
    # Process ALL possible window centers, including edges
    for i in range(len(velocity)):
        # Calculate window bounds with proper edge handling
        window_start = max(0, i - half_window)
        window_end = min(len(velocity), i + half_window + (1 if epoch_samples % 2 == 1 else 0))
        
        # Get window data (may be smaller at edges)
        window_data = velocity[window_start:window_end]
        threshold_mask = (window_data >= th1_min) & (window_data <= th1_max)
        
        # Calculate distance
        time_per_sample = 1.0 / sampling_rate
        window_distance = np.sum(window_data[threshold_mask] * time_per_sample)
        
        correct_rolling_wcs_values.append(window_distance)
        correct_rolling_wcs_times.append(t[i])
        correct_rolling_wcs_centers.append(i)
    
    # Find the peak in correct implementation
    if correct_rolling_wcs_values:
        correct_max_idx = np.argmax(correct_rolling_wcs_values)
        correct_max_time = correct_rolling_wcs_times[correct_max_idx]
        correct_max_value = correct_rolling_wcs_values[correct_max_idx]
        correct_max_center = correct_rolling_wcs_centers[correct_max_idx]
        
        print("Correct Implementation Results:")
        print(f"  Peak WCS value: {correct_max_value:.3f} m")
        print(f"  Peak time: {correct_max_time:.1f} seconds")
        print(f"  Peak center index: {correct_max_center}")
        print(f"  Expected peak time: {mu} seconds")
        print(f"  Time difference: {abs(correct_max_time - mu):.1f} seconds")
        print()
        
        print("Comparison:")
        print(f"  Current vs Correct peak time: {max_time:.1f} vs {correct_max_time:.1f} seconds")
        print(f"  Current vs Correct peak value: {max_value:.3f} vs {correct_max_value:.3f} m")
    
    # Create comparison visualization
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot velocity
    ax1.plot(t, velocity, 'b-', linewidth=2, label='Velocity')
    ax1.axvline(x=mu, color='red', linestyle='--', alpha=0.7, label=f'Expected peak at t={mu}s')
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('Velocity (m/s)')
    ax1.set_title('Velocity Signal')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot both implementations
    if rolling_wcs_values and correct_rolling_wcs_values:
        ax2.plot(rolling_wcs_times, rolling_wcs_values, 'r-', linewidth=2, alpha=0.7, label='Current (edges missing)')
        ax2.plot(correct_rolling_wcs_times, correct_rolling_wcs_values, 'g-', linewidth=2, label='Correct (with edges)')
        ax2.axvline(x=mu, color='red', linestyle='--', alpha=0.7, label=f'Expected peak at t={mu}s')
        
        # Mark peaks
        ax2.plot(max_time, max_value, 'ro', markersize=8, label=f'Current peak at t={max_time:.1f}s')
        ax2.plot(correct_max_time, correct_max_value, 'go', markersize=8, label=f'Correct peak at t={correct_max_time:.1f}s')
    
    ax2.set_xlabel('Time (seconds)')
    ax2.set_ylabel('WCS Distance (m)')
    ax2.set_title('Rolling WCS Values Comparison')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('rolling_wcs_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Comparison saved to: rolling_wcs_comparison.png")

if __name__ == "__main__":
    test_rolling_wcs_issues() 