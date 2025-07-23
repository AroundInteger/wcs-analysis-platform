#!/usr/bin/env python3
"""
Test rolling WCS with a 3-peak velocity system - more realistic and complex.
"""

import numpy as np
import matplotlib.pyplot as plt

def test_rolling_wcs_3_peaks():
    """Test rolling WCS with a 3-peak velocity system"""
    
    # Test parameters
    t = np.linspace(0, 300, 3000)  # 5 minutes at 10 Hz
    sampling_rate = 10
    
    # Create 3 peaks with different characteristics
    # Peak 1: Early, moderate intensity
    peak1_time = 30  # 30 seconds
    peak1_velocity = 6.0  # 6 m/s
    peak1_width = 8  # 8 seconds FWHM
    
    # Peak 2: Middle, highest intensity
    peak2_time = 120  # 2 minutes
    peak2_velocity = 8.5  # 8.5 m/s
    peak2_width = 12  # 12 seconds FWHM
    
    # Peak 3: Late, moderate intensity but broader
    peak3_time = 210  # 3.5 minutes
    peak3_velocity = 7.0  # 7 m/s
    peak3_width = 15  # 15 seconds FWHM
    
    # Create velocity signal with 3 Gaussian peaks
    velocity = (peak1_velocity * np.exp(-0.5 * ((t - peak1_time) / (peak1_width/2.355))**2) +
               peak2_velocity * np.exp(-0.5 * ((t - peak2_time) / (peak2_width/2.355))**2) +
               peak3_velocity * np.exp(-0.5 * ((t - peak3_time) / (peak3_width/2.355))**2))
    
    # Add some baseline activity
    baseline = 1.5 + 0.5 * np.sin(2 * np.pi * t / 60)  # 1.5 m/s baseline with slow oscillation
    velocity += baseline
    
    # Analysis parameters
    epoch_duration = 1.0  # 1 minute
    threshold_min = 4.0   # Only velocities above 4 m/s (for comparison)
    threshold_max = 100.0
    
    print("=== ROLLING WCS WITH 3-PEAK SYSTEM ===")
    print(f"Test Parameters:")
    print(f"  Peak 1: {peak1_velocity:.1f} m/s at {peak1_time}s (width: {peak1_width}s)")
    print(f"  Peak 2: {peak2_velocity:.1f} m/s at {peak2_time}s (width: {peak2_width}s)")
    print(f"  Peak 3: {peak3_velocity:.1f} m/s at {peak3_time}s (width: {peak3_width}s)")
    print(f"  Data length: {len(velocity)} samples ({len(velocity)/sampling_rate:.1f} seconds)")
    print(f"  Epoch duration: {epoch_duration} minutes ({epoch_duration * 60} seconds)")
    print()
    
    # Calculate epoch samples
    epoch_samples = int(epoch_duration * 60 * sampling_rate)  # 600 samples
    half_window = epoch_samples // 2  # 300 samples
    
    print(f"Window analysis:")
    print(f"  Full window size: {epoch_samples} samples")
    print(f"  Half window: {half_window} samples")
    print(f"  Window duration: {epoch_samples / sampling_rate:.1f} seconds")
    print()
    
    # Test windows around each peak
    peak_indices = [int(peak1_time * sampling_rate), int(peak2_time * sampling_rate), int(peak3_time * sampling_rate)]
    peak_times = [peak1_time, peak2_time, peak3_time]
    peak_velocities = [peak1_velocity, peak2_velocity, peak3_velocity]
    
    print("Window analysis around each peak (NO THRESHOLDING):")
    for i, (peak_idx, peak_time, peak_vel) in enumerate(zip(peak_indices, peak_times, peak_velocities)):
        print(f"\nPeak {i+1} analysis:")
        print(f"  Peak index: {peak_idx}")
        print(f"  Peak time: {peak_time:.1f} seconds")
        print(f"  Peak velocity: {peak_vel:.3f} m/s")
        
        # Test window centered on this peak
        window_start = max(0, peak_idx - half_window)
        window_end = min(len(velocity), peak_idx + half_window + (1 if epoch_samples % 2 == 1 else 0))
        window_data = velocity[window_start:window_end]
        
        # NO THRESHOLDING - just simple summation
        time_per_sample = 1.0 / sampling_rate
        window_distance = np.sum(window_data * time_per_sample)  # All values included!
        
        print(f"  Window: {window_start} to {window_end} ({len(window_data)} samples)")
        print(f"  Distance: {window_distance:.3f} m")
        print(f"  Mean velocity in window: {np.mean(window_data):.3f} m/s")
        print(f"  Max velocity in window: {np.max(window_data):.3f} m/s")
        print(f"  Min velocity in window: {np.min(window_data):.3f} m/s")
    
    # Now find the actual maximum WCS (NO THRESHOLDING)
    print("\nFinding actual maximum WCS window (NO THRESHOLDING)...")
    max_distance = 0
    max_center = 0
    max_window_start = 0
    max_window_end = 0
    
    # Check all possible window centers
    for i in range(len(velocity)):
        window_start = max(0, i - half_window)
        window_end = min(len(velocity), i + half_window + (1 if epoch_samples % 2 == 1 else 0))
        
        window_data = velocity[window_start:window_end]
        
        # NO THRESHOLDING - just simple summation
        time_per_sample = 1.0 / sampling_rate
        window_distance = np.sum(window_data * time_per_sample)  # All values included!
        
        if window_distance > max_distance:
            max_distance = window_distance
            max_center = i
            max_window_start = window_start
            max_window_end = window_end
    
    print(f"\nMaximum WCS found (NO THRESHOLDING):")
    print(f"  Center index: {max_center}")
    print(f"  Center time: {t[max_center]:.1f} seconds")
    print(f"  Window: {max_window_start} to {max_window_end}")
    print(f"  Distance: {max_distance:.3f} m")
    
    # Find which peak is closest to the maximum
    distances_to_peaks = [abs(t[max_center] - pt) for pt in peak_times]
    closest_peak_idx = np.argmin(distances_to_peaks)
    print(f"  Closest to Peak {closest_peak_idx + 1} (distance: {distances_to_peaks[closest_peak_idx]:.1f}s)")
    print()
    
    # Now test WITH THRESHOLDING for comparison
    print("Finding maximum WCS window (WITH THRESHOLDING)...")
    max_distance_thresh = 0
    max_center_thresh = 0
    max_window_start_thresh = 0
    max_window_end_thresh = 0
    
    # Check all possible window centers
    for i in range(len(velocity)):
        window_start = max(0, i - half_window)
        window_end = min(len(velocity), i + half_window + (1 if epoch_samples % 2 == 1 else 0))
        
        window_data = velocity[window_start:window_end]
        
        # WITH THRESHOLDING - only velocities above threshold
        threshold_mask = (window_data >= threshold_min) & (window_data <= threshold_max)
        time_per_sample = 1.0 / sampling_rate
        window_distance = np.sum(window_data[threshold_mask] * time_per_sample)  # Only thresholded values!
        
        if window_distance > max_distance_thresh:
            max_distance_thresh = window_distance
            max_center_thresh = i
            max_window_start_thresh = window_start
            max_window_end_thresh = window_end
    
    print(f"\nMaximum WCS found (WITH THRESHOLDING):")
    print(f"  Center index: {max_center_thresh}")
    print(f"  Center time: {t[max_center_thresh]:.1f} seconds")
    print(f"  Window: {max_window_start_thresh} to {max_window_end_thresh}")
    print(f"  Distance: {max_distance_thresh:.3f} m")
    
    # Find which peak is closest to the thresholded maximum
    distances_to_peaks_thresh = [abs(t[max_center_thresh] - pt) for pt in peak_times]
    closest_peak_idx_thresh = np.argmin(distances_to_peaks_thresh)
    print(f"  Closest to Peak {closest_peak_idx_thresh + 1} (distance: {distances_to_peaks_thresh[closest_peak_idx_thresh]:.1f}s)")
    print()
    
    print(f"Comparison:")
    print(f"  No threshold vs With threshold: {max_distance:.3f} vs {max_distance_thresh:.3f} m")
    print(f"  No threshold vs With threshold center: {t[max_center]:.1f}s vs {t[max_center_thresh]:.1f}s")
    print(f"  Difference in distance: {max_distance - max_distance_thresh:.3f} m")
    print(f"  Difference in center time: {abs(t[max_center] - t[max_center_thresh]):.1f} s")
    
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
    
    # Plot velocity with peaks and windows
    ax1.plot(t, velocity, 'b-', linewidth=2, label='Velocity')
    ax1.axhline(y=threshold_min, color='red', linestyle='--', alpha=0.7, label=f'Threshold: {threshold_min} m/s')
    
    # Mark the peaks
    for i, (peak_time, peak_vel) in enumerate(zip(peak_times, peak_velocities)):
        ax1.axvline(x=peak_time, color='orange', linestyle='--', alpha=0.7, 
                   label=f'Peak {i+1}: {peak_vel:.1f} m/s at {peak_time}s')
    
    # Mark the maximum WCS windows
    ax1.axvspan(t[max_window_start], t[max_window_end-1], alpha=0.3, color='green', 
               label=f'Max WCS (no threshold): {max_distance:.1f}m at {t[max_center]:.1f}s')
    ax1.axvspan(t[max_window_start_thresh], t[max_window_end_thresh-1], alpha=0.3, color='purple', 
               label=f'Max WCS (with threshold): {max_distance_thresh:.1f}m at {t[max_center_thresh]:.1f}s')
    
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('Velocity (m/s)')
    ax1.set_title('3-Peak Velocity Signal with WCS Windows')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot rolling WCS values
    rolling_wcs_no_thresh = []
    rolling_wcs_with_thresh = []
    rolling_wcs_times = []
    
    for i in range(len(velocity)):
        window_start = max(0, i - half_window)
        window_end = min(len(velocity), i + half_window + (1 if epoch_samples % 2 == 1 else 0))
        
        window_data = velocity[window_start:window_end]
        
        # NO THRESHOLDING
        time_per_sample = 1.0 / sampling_rate
        window_distance_no_thresh = np.sum(window_data * time_per_sample)
        
        # WITH THRESHOLDING
        threshold_mask = (window_data >= threshold_min) & (window_data <= threshold_max)
        window_distance_with_thresh = np.sum(window_data[threshold_mask] * time_per_sample)
        
        rolling_wcs_no_thresh.append(window_distance_no_thresh)
        rolling_wcs_with_thresh.append(window_distance_with_thresh)
        rolling_wcs_times.append(t[i])
    
    ax2.plot(rolling_wcs_times, rolling_wcs_no_thresh, 'g-', linewidth=2, label='Rolling WCS (NO THRESHOLDING)')
    ax2.plot(rolling_wcs_times, rolling_wcs_with_thresh, 'purple', linewidth=2, label='Rolling WCS (WITH THRESHOLDING)')
    
    # Mark the peaks
    for i, peak_time in enumerate(peak_times):
        ax2.axvline(x=peak_time, color='orange', linestyle='--', alpha=0.7, 
                   label=f'Peak {i+1} at {peak_time}s')
    
    # Mark the maximums
    ax2.axvline(x=t[max_center], color='green', linestyle='--', alpha=0.7, 
               label=f'Max WCS (no threshold): {t[max_center]:.1f}s')
    ax2.axvline(x=t[max_center_thresh], color='purple', linestyle='--', alpha=0.7, 
               label=f'Max WCS (with threshold): {t[max_center_thresh]:.1f}s')
    
    ax2.set_xlabel('Time (seconds)')
    ax2.set_ylabel('WCS Distance (m)')
    ax2.set_title('Rolling WCS Values Over Time (1-minute epoch)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('rolling_wcs_3_peaks.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Analysis saved to: rolling_wcs_3_peaks.png")
    
    # Show the rolling WCS curve around each peak
    print("\n=== ROLLING WCS VALUES AROUND EACH PEAK ===")
    for i, (peak_idx, peak_time) in enumerate(zip(peak_indices, peak_times)):
        print(f"\nPeak {i+1} (t={peak_time:.1f}s):")
        peak_range = range(max(0, peak_idx - 50), min(len(velocity), peak_idx + 50))
        for j in peak_range[::10]:  # Every 10th sample
            window_start = max(0, j - half_window)
            window_end = min(len(velocity), j + half_window + (1 if epoch_samples % 2 == 1 else 0))
            window_data = velocity[window_start:window_end]
            time_per_sample = 1.0 / sampling_rate
            window_distance = np.sum(window_data * time_per_sample)
            print(f"  t={t[j]:.1f}s: {window_distance:.3f} m")

if __name__ == "__main__":
    test_rolling_wcs_3_peaks() 