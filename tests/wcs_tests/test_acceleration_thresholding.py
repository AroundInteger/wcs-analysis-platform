#!/usr/bin/env python3
"""
Test WCS with acceleration thresholding: acceleration < 2 m/s² sets a and V to zero
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

def create_test_velocity_data():
    """Create velocity data with single peak and smooth transitions"""
    
    print("🧪 Creating Test Velocity Data")
    print("=" * 40)
    
    # Create time series (10Hz for 2 minutes)
    sampling_rate = 10
    duration_seconds = 120
    num_samples = duration_seconds * sampling_rate
    time_seconds = np.linspace(0, duration_seconds, num_samples)
    
    # Create velocity data with single peak and smooth transitions
    velocities = np.zeros(num_samples)
    
    for i, t in enumerate(time_seconds):
        # Baseline velocity (below threshold)
        baseline = 2.0
        
        # Create smooth dynamic velocity profile with continuous transitions
        # Use smooth functions to avoid discontinuities
        
        # Phase 1: Smooth acceleration (t=20-40s)
        if 20 <= t <= 40:
            # Smooth quadratic rise from 0 to 6 m/s
            phase_progress = (t - 20) / 20  # 0 to 1
            intensity = 6.0 * phase_progress ** 2
            
        # Phase 2: Smooth deceleration (t=40-60s) 
        elif 40 < t <= 60:
            # Smooth quadratic fall from 6 to 0 m/s
            phase_progress = (60 - t) / 20  # 1 to 0
            intensity = 6.0 * phase_progress ** 2
            
        # Phase 3: Oscillating phase (t=70-90s) with smooth start/end
        elif 70 <= t <= 90:
            # Smooth envelope function to avoid discontinuities
            envelope = np.exp(-0.5 * ((t - 80) / 8) ** 2)  # Gaussian envelope
            oscillation = np.sin((t - 70) * np.pi / 10) ** 2
            intensity = 4.0 * envelope * oscillation
            
        else:
            intensity = 0
        
        velocities[i] = baseline + intensity
    
    print(f"✅ Created test velocity data:")
    print(f"   - Duration: {duration_seconds} seconds")
    print(f"   - Dynamic phases: t=20-40s (acceleration), t=40-60s (deceleration), t=70-90s (oscillating)")
    print(f"   - Baseline: 2.0 m/s")
    print(f"   - Higher accelerations expected for thresholding effect")
    print(f"   - Sampling rate: {sampling_rate} Hz")
    
    return velocities, time_seconds, sampling_rate

def calculate_acceleration_data(velocities, sampling_rate):
    """Calculate acceleration from velocity data"""
    
    print(f"\n🔬 Calculating Acceleration")
    print("=" * 30)
    
    # Calculate acceleration using central difference
    acceleration = calculate_acceleration(velocities, sampling_rate)
    
    # Calculate some statistics
    max_accel = np.max(acceleration)
    min_accel = np.min(acceleration)
    mean_accel = np.mean(acceleration)
    
    print(f"Acceleration Statistics:")
    print(f"  Maximum: {max_accel:.2f} m/s²")
    print(f"  Minimum: {min_accel:.2f} m/s²")
    print(f"  Mean: {mean_accel:.2f} m/s²")
    print(f"  Threshold: 0.5 m/s² (adjusted for realistic accelerations)")
    
    return acceleration

def apply_acceleration_threshold(velocities, acceleration, threshold=0.5):
    """Apply acceleration threshold: a < threshold sets both a and V to zero"""
    
    print(f"\n🔬 Applying Acceleration Threshold")
    print("=" * 40)
    
    # Create thresholded data
    thresholded_velocities = velocities.copy()
    thresholded_acceleration = acceleration.copy()
    
    # Apply threshold: where acceleration < threshold, set both a and V to zero
    threshold_mask = np.abs(acceleration) < threshold
    
    thresholded_velocities[threshold_mask] = 0.0
    thresholded_acceleration[threshold_mask] = 0.0
    
    # Calculate statistics
    original_nonzero = np.sum(velocities > 0)
    thresholded_nonzero = np.sum(thresholded_velocities > 0)
    reduction_percent = ((original_nonzero - thresholded_nonzero) / original_nonzero) * 100 if original_nonzero > 0 else 0
    
    print(f"Thresholding Effect:")
    print(f"  Original non-zero velocities: {original_nonzero}")
    print(f"  After thresholding: {thresholded_nonzero}")
    print(f"  Reduction: {reduction_percent:.1f}%")
    print(f"  Threshold: |acceleration| >= {threshold} m/s²")
    
    return thresholded_velocities, thresholded_acceleration

def calculate_wcs_with_acceleration_thresholding(velocities, time_seconds, sampling_rate):
    """Calculate WCS with acceleration thresholding"""
    
    print(f"\n🔬 WCS Analysis with Acceleration Thresholding")
    print("=" * 60)
    
    # Test parameters
    epoch_duration = 20.0 / 60.0  # 20 seconds (converted to minutes)
    
    print(f"Parameters:")
    print(f"  - Epoch duration: {epoch_duration:.3f} minutes ({epoch_duration*60:.1f} seconds)")
    print(f"  - Sampling rate: {sampling_rate} Hz")
    print(f"  - Acceleration threshold: 0.5 m/s²")
    print(f"  - Where |a| < 0.5 m/s²: both a and V set to zero")
    
    # Calculate acceleration
    acceleration = calculate_acceleration_data(velocities, sampling_rate)
    
    # Apply acceleration thresholding
    thresholded_velocities, thresholded_acceleration = apply_acceleration_threshold(velocities, acceleration, 2.0)
    
    results = {}
    
    # Test 1: Original data (no acceleration thresholding)
    print(f"\n📊 Test 1: Original Data (no acceleration thresholding)")
    print("-" * 60)
    
    # Rolling WCS (original data)
    max_distance_rolling_orig, max_time_rolling_orig, start_idx_rolling_orig, end_idx_rolling_orig = calculate_wcs_period_rolling(
        velocities, epoch_duration, sampling_rate, 0.0, 100.0
    )
    
    max_wcs_time_rolling_orig = time_seconds[start_idx_rolling_orig + (end_idx_rolling_orig - start_idx_rolling_orig) // 2]
    
    print(f"  Rolling WCS:")
    print(f"    Distance: {max_distance_rolling_orig:.3f} m")
    print(f"    Time: {max_time_rolling_orig:.3f} s")
    print(f"    Center: t={max_wcs_time_rolling_orig:.1f}s")
    print(f"    Window: {time_seconds[start_idx_rolling_orig]:.1f}s - {time_seconds[end_idx_rolling_orig-1]:.1f}s")
    
    # Contiguous WCS (original data)
    max_distance_cont_orig, max_time_cont_orig, start_idx_cont_orig, end_idx_cont_orig = calculate_wcs_period_contiguous(
        velocities, epoch_duration, sampling_rate, 0.0, 100.0
    )
    
    max_wcs_time_cont_orig = time_seconds[start_idx_cont_orig + (end_idx_cont_orig - start_idx_cont_orig) // 2]
    
    print(f"  Contiguous WCS:")
    print(f"    Distance: {max_distance_cont_orig:.3f} m")
    print(f"    Time: {max_time_cont_orig:.3f} s")
    print(f"    Center: t={max_wcs_time_cont_orig:.1f}s")
    print(f"    Window: {time_seconds[start_idx_cont_orig]:.1f}s - {time_seconds[end_idx_cont_orig-1]:.1f}s")
    
    results['original'] = {
        'rolling': {
            'distance': max_distance_rolling_orig,
            'time': max_time_rolling_orig,
            'start_idx': start_idx_rolling_orig,
            'end_idx': end_idx_rolling_orig,
            'center_time': max_wcs_time_rolling_orig
        },
        'contiguous': {
            'distance': max_distance_cont_orig,
            'time': max_time_cont_orig,
            'start_idx': start_idx_cont_orig,
            'end_idx': end_idx_cont_orig,
            'center_time': max_wcs_time_cont_orig
        }
    }
    
    # Test 2: With acceleration thresholding
    print(f"\n📊 Test 2: With Acceleration Thresholding (|a| >= 0.5 m/s²)")
    print("-" * 60)
    
    # Rolling WCS (acceleration thresholded data)
    max_distance_rolling_th, max_time_rolling_th, start_idx_rolling_th, end_idx_rolling_th = calculate_wcs_period_rolling(
        thresholded_velocities, epoch_duration, sampling_rate, 0.0, 100.0
    )
    
    max_wcs_time_rolling_th = time_seconds[start_idx_rolling_th + (end_idx_rolling_th - start_idx_rolling_th) // 2]
    
    print(f"  Rolling WCS:")
    print(f"    Distance: {max_distance_rolling_th:.3f} m")
    print(f"    Time: {max_time_rolling_th:.3f} s")
    print(f"    Center: t={max_wcs_time_rolling_th:.1f}s")
    print(f"    Window: {time_seconds[start_idx_rolling_th]:.1f}s - {time_seconds[end_idx_rolling_th-1]:.1f}s")
    
    # Contiguous WCS (acceleration thresholded data)
    max_distance_cont_th, max_time_cont_th, start_idx_cont_th, end_idx_cont_th = calculate_wcs_period_contiguous(
        thresholded_velocities, epoch_duration, sampling_rate, 0.0, 100.0
    )
    
    max_wcs_time_cont_th = time_seconds[start_idx_cont_th + (end_idx_cont_th - start_idx_cont_th) // 2]
    
    print(f"  Contiguous WCS:")
    print(f"    Distance: {max_distance_cont_th:.3f} m")
    print(f"    Time: {max_time_cont_th:.3f} s")
    print(f"    Center: t={max_wcs_time_cont_th:.1f}s")
    print(f"    Window: {time_seconds[start_idx_cont_th]:.1f}s - {time_seconds[end_idx_cont_th-1]:.1f}s")
    
    results['acceleration_thresholded'] = {
        'rolling': {
            'distance': max_distance_rolling_th,
            'time': max_time_rolling_th,
            'start_idx': start_idx_rolling_th,
            'end_idx': end_idx_rolling_th,
            'center_time': max_wcs_time_rolling_th
        },
        'contiguous': {
            'distance': max_distance_cont_th,
            'time': max_time_cont_th,
            'start_idx': start_idx_cont_th,
            'end_idx': end_idx_cont_th,
            'center_time': max_wcs_time_cont_th
        }
    }
    
    return results, acceleration, thresholded_velocities, thresholded_acceleration

def plot_acceleration_thresholding_comparison(velocities, acceleration, thresholded_velocities, thresholded_acceleration, time_seconds, results):
    """Plot comparison of WCS with and without acceleration thresholding"""
    
    plt.figure(figsize=(18, 12))
    
    # Plot 1: Original velocity and acceleration
    plt.subplot(3, 3, 1)
    plt.plot(time_seconds, velocities, 'b-', linewidth=2, label='Velocity', alpha=0.8)
    plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Velocity (m/s)')
    plt.title('Original Velocity Profile')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(3, 3, 2)
    plt.plot(time_seconds, acceleration, 'r-', linewidth=2, label='Acceleration', alpha=0.8)
    plt.axhline(y=0.5, color='orange', linestyle='--', alpha=0.8, label='Threshold: 0.5 m/s²')
    plt.axhline(y=-0.5, color='orange', linestyle='--', alpha=0.8)
    plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Acceleration (m/s²)')
    plt.title('Original Acceleration Profile')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Thresholded velocity and acceleration
    plt.subplot(3, 3, 3)
    plt.plot(time_seconds, thresholded_velocities, 'orange', linewidth=2, label='Thresholded Velocity', alpha=0.8)
    plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Velocity (m/s)')
    plt.title('Thresholded Velocity (|a| < 0.5 m/s² → V = 0)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(3, 3, 4)
    plt.plot(time_seconds, thresholded_acceleration, 'orange', linewidth=2, label='Thresholded Acceleration', alpha=0.8)
    plt.axhline(y=0.5, color='orange', linestyle='--', alpha=0.8, label='Threshold: 0.5 m/s²')
    plt.axhline(y=-0.5, color='orange', linestyle='--', alpha=0.8)
    plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Acceleration (m/s²)')
    plt.title('Thresholded Acceleration (|a| < 0.5 m/s² → a = 0)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 3: WCS windows comparison
    plt.subplot(3, 3, 5)
    plt.plot(time_seconds, velocities, 'b-', linewidth=1.5, label='Original Velocity', alpha=0.6)
    plt.plot(time_seconds, thresholded_velocities, 'orange', linewidth=1.5, label='Thresholded Velocity', alpha=0.8)
    
    # Highlight WCS windows
    orig_rolling = results['original']['rolling']
    thresh_rolling = results['acceleration_thresholded']['rolling']
    
    # Original WCS window
    start_time_orig = time_seconds[orig_rolling['start_idx']]
    end_time_orig = time_seconds[orig_rolling['end_idx'] - 1]
    plt.axvspan(start_time_orig, end_time_orig, alpha=0.3, color='blue', 
                label=f'Original WCS: {orig_rolling["distance"]:.1f}m')
    
    # Thresholded WCS window
    start_time_th = time_seconds[thresh_rolling['start_idx']]
    end_time_th = time_seconds[thresh_rolling['end_idx'] - 1]
    plt.axvspan(start_time_th, end_time_th, alpha=0.3, color='orange', 
                label=f'Thresholded WCS: {thresh_rolling["distance"]:.1f}m')
    
    plt.xlabel('Time (seconds)')
    plt.ylabel('Velocity (m/s)')
    plt.title('WCS Windows Comparison')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 4: Rolling WCS distance over time (original)
    plt.subplot(3, 3, 6)
    
    # Calculate rolling WCS distance for each window position (original)
    epoch_duration = 20.0 / 60.0
    sampling_rate = 10
    epoch_samples = int(epoch_duration * 60 * sampling_rate)
    half_window = epoch_samples // 2
    
    wcs_distances_orig = []
    wcs_times_orig = []
    
    for i in range(half_window, len(velocities) - half_window):
        window_start = i - half_window
        window_end = i + half_window + (1 if epoch_samples % 2 == 1 else 0)
        window_data = velocities[window_start:window_end]
        
        time_per_sample = 1.0 / sampling_rate
        window_distance = np.sum(window_data * time_per_sample)
        
        wcs_distances_orig.append(window_distance)
        wcs_times_orig.append(time_seconds[i])
    
    plt.plot(wcs_times_orig, wcs_distances_orig, 'b-', linewidth=2, label='Original WCS Distance')
    plt.axvline(x=orig_rolling['center_time'], color='blue', linestyle='--', 
                label=f'Max Original: {orig_rolling["distance"]:.1f}m')
    
    plt.xlabel('Time (seconds)')
    plt.ylabel('WCS Distance (m)')
    plt.title('Rolling WCS Distance (Original)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 5: Rolling WCS distance over time (thresholded)
    plt.subplot(3, 3, 7)
    
    wcs_distances_th = []
    wcs_times_th = []
    
    for i in range(half_window, len(thresholded_velocities) - half_window):
        window_start = i - half_window
        window_end = i + half_window + (1 if epoch_samples % 2 == 1 else 0)
        window_data = thresholded_velocities[window_start:window_end]
        
        time_per_sample = 1.0 / sampling_rate
        window_distance = np.sum(window_data * time_per_sample)
        
        wcs_distances_th.append(window_distance)
        wcs_times_th.append(time_seconds[i])
    
    plt.plot(wcs_times_th, wcs_distances_th, 'orange', linewidth=2, label='Thresholded WCS Distance')
    plt.axvline(x=thresh_rolling['center_time'], color='orange', linestyle='--', 
                label=f'Max Thresholded: {thresh_rolling["distance"]:.1f}m')
    
    plt.xlabel('Time (seconds)')
    plt.ylabel('WCS Distance (m)')
    plt.title('Rolling WCS Distance (Acceleration Thresholded)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 6: Contiguous WCS comparison
    plt.subplot(3, 3, 8)
    
    # Calculate contiguous WCS for both cases
    wcs_distances_cont_orig = []
    wcs_distances_cont_th = []
    wcs_times_cont = []
    
    for i in range(0, len(velocities) - epoch_samples + 1, epoch_samples):
        window_data_orig = velocities[i:i + epoch_samples]
        window_data_th = thresholded_velocities[i:i + epoch_samples]
        
        time_per_sample = 1.0 / sampling_rate
        window_distance_orig = np.sum(window_data_orig * time_per_sample)
        window_distance_th = np.sum(window_data_th * time_per_sample)
        
        wcs_distances_cont_orig.append(window_distance_orig)
        wcs_distances_cont_th.append(window_distance_th)
        wcs_times_cont.append(time_seconds[i + epoch_samples // 2])
    
    plt.plot(wcs_times_cont, wcs_distances_cont_orig, 'b-', linewidth=2, label='Original Contiguous WCS')
    plt.plot(wcs_times_cont, wcs_distances_cont_th, 'orange', linewidth=2, label='Thresholded Contiguous WCS')
    
    # Mark the best periods
    orig_cont = results['original']['contiguous']
    thresh_cont = results['acceleration_thresholded']['contiguous']
    
    plt.axvline(x=orig_cont['center_time'], color='blue', linestyle='--', 
                label=f'Best Original: {orig_cont["distance"]:.1f}m')
    plt.axvline(x=thresh_cont['center_time'], color='orange', linestyle='--', 
                label=f'Best Thresholded: {thresh_cont["distance"]:.1f}m')
    
    plt.xlabel('Time (seconds)')
    plt.ylabel('WCS Distance (m)')
    plt.title('Contiguous WCS Comparison')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 7: Summary comparison
    plt.subplot(3, 3, 9)
    
    # Create comparison table
    comparison_text = f"""
Acceleration Thresholding Comparison
(20-second epoch, |a| >= 2.0 m/s²)

ORIGINAL DATA:
Rolling WCS:
• Distance: {orig_rolling['distance']:.1f} m
• Center: t={orig_rolling['center_time']:.1f}s

Contiguous WCS:
• Distance: {orig_cont['distance']:.1f} m
• Center: t={orig_cont['center_time']:.1f}s

ACCELERATION THRESHOLDED:
Rolling WCS:
• Distance: {thresh_rolling['distance']:.1f} m
• Center: t={thresh_rolling['center_time']:.1f}s

Contiguous WCS:
• Distance: {thresh_cont['distance']:.1f} m
• Center: t={thresh_cont['center_time']:.1f}s

Thresholding Effect:
• Rolling: {((thresh_rolling['distance'] / orig_rolling['distance']) * 100):.1f}% of original
• Contiguous: {((thresh_cont['distance'] / orig_cont['distance']) * 100):.1f}% of original
• Where |a| < 2.0 m/s²: both a and V set to zero
    """
    
    plt.text(0.05, 0.95, comparison_text, transform=plt.gca().transAxes, 
             fontsize=8, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.9))
    
    plt.axis('off')
    plt.title('Acceleration Thresholding Summary')
    
    plt.tight_layout()
    plt.savefig('acceleration_thresholding_wcs.png', dpi=300, bbox_inches='tight')
    plt.show()

def analyze_acceleration_thresholding_effect(results):
    """Analyze the effect of acceleration thresholding on WCS calculations"""
    
    print(f"\n📊 Acceleration Thresholding Effect Analysis")
    print("=" * 60)
    
    orig_rolling = results['original']['rolling']
    thresh_rolling = results['acceleration_thresholded']['rolling']
    orig_cont = results['original']['contiguous']
    thresh_cont = results['acceleration_thresholded']['contiguous']
    
    # Rolling WCS thresholding effect
    rolling_ratio = thresh_rolling['distance'] / orig_rolling['distance'] if orig_rolling['distance'] > 0 else 0
    rolling_reduction = (1 - rolling_ratio) * 100
    
    print(f"Rolling WCS Acceleration Thresholding Effect:")
    print(f"  Original: {orig_rolling['distance']:.1f} m")
    print(f"  Thresholded: {thresh_rolling['distance']:.1f} m")
    print(f"  Reduction: {rolling_reduction:.1f}%")
    print(f"  Remaining: {rolling_ratio*100:.1f}% of original")
    
    # Contiguous WCS thresholding effect
    cont_ratio = thresh_cont['distance'] / orig_cont['distance'] if orig_cont['distance'] > 0 else 0
    cont_reduction = (1 - cont_ratio) * 100
    
    print(f"\nContiguous WCS Acceleration Thresholding Effect:")
    print(f"  Original: {orig_cont['distance']:.1f} m")
    print(f"  Thresholded: {thresh_cont['distance']:.1f} m")
    print(f"  Reduction: {cont_reduction:.1f}%")
    print(f"  Remaining: {cont_ratio*100:.1f}% of original")
    
    # Position changes
    rolling_pos_change = abs(orig_rolling['center_time'] - thresh_rolling['center_time'])
    cont_pos_change = abs(orig_cont['center_time'] - thresh_cont['center_time'])
    
    print(f"\nPosition Changes:")
    print(f"  Rolling WCS: {rolling_pos_change:.1f}s difference")
    print(f"  Contiguous WCS: {cont_pos_change:.1f}s difference")
    
    # Interpretation
    print(f"\n🎯 Interpretation:")
    print(f"  Acceleration thresholding focuses on dynamic periods only")
    print(f"  Where |acceleration| < 0.5 m/s²: both a and V are set to zero")
    print(f"  This eliminates steady-state or low-dynamic periods")
    print(f"  WCS now measures only high-dynamic performance periods")

def main():
    """Run WCS acceleration thresholding test"""
    
    print("🧪 WCS Acceleration Thresholding Test")
    print("=" * 70)
    print("Testing acceleration thresholding: |a| < 2 m/s² sets both a and V to zero")
    print("=" * 70)
    
    # Create test data
    velocities, time_seconds, sampling_rate = create_test_velocity_data()
    
    # Calculate WCS with acceleration thresholding
    results, acceleration, thresholded_velocities, thresholded_acceleration = calculate_wcs_with_acceleration_thresholding(
        velocities, time_seconds, sampling_rate
    )
    
    # Analyze acceleration thresholding effect
    analyze_acceleration_thresholding_effect(results)
    
    # Plot results
    print(f"\n📊 Generating acceleration thresholding comparison plots...")
    plot_acceleration_thresholding_comparison(
        velocities, acceleration, thresholded_velocities, thresholded_acceleration, time_seconds, results
    )
    
    print(f"\n🎉 WCS Acceleration Thresholding Test Complete!")
    print("=" * 70)
    print("Check the generated plot: acceleration_thresholding_wcs.png")
    print("=" * 70)

if __name__ == "__main__":
    main() 