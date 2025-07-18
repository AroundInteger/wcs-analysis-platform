#!/usr/bin/env python3
"""
Test rolling WCS WITH thresholding - only velocities above 4 m/s contribute.
"""

import numpy as np
import matplotlib.pyplot as plt

def test_rolling_wcs_with_threshold():
    """Test rolling WCS with thresholding - only velocities above 4 m/s"""
    
    # Test parameters
    sigma = 10
    mu = 9 * sigma  # 90 seconds
    t = np.linspace(0, sigma * 18, 1800)  # 0 to 180 seconds
    velocity = 8 * np.exp(-0.5 * ((t - mu) / sigma)**2)  # Normal distribution
    
    # Analysis parameters
    epoch_duration = 1.0  # 1 minute
    sampling_rate = 10    # 10 Hz
    threshold_min = 4.0   # Only velocities above 4 m/s
    threshold_max = 100.0 # Upper limit
    
    print("=== ROLLING WCS WITH THRESHOLDING (v > 4 m/s) ===")
    print(f"Test Parameters:")
    print(f"  Velocity peak at t = {mu} seconds")
    print(f"  Velocity peak value: {np.max(velocity):.3f} m/s")
    print(f"  Data length: {len(velocity)} samples ({len(velocity)/sampling_rate:.1f} seconds)")
    print(f"  Epoch duration: {epoch_duration} minutes ({epoch_duration * 60} seconds)")
    print(f"  Threshold: {threshold_min} - {threshold_max} m/s")
    print()
    
    # Calculate epoch samples
    epoch_samples = int(epoch_duration * 60 * sampling_rate)  # 600 samples
    half_window = epoch_samples // 2  # 300 samples
    
    print(f"Window analysis:")
    print(f"  Full window size: {epoch_samples} samples")
    print(f"  Half window: {half_window} samples")
    print(f"  Window duration: {epoch_samples / sampling_rate:.1f} seconds")
    print()
    
    # Analyze windows around the expected peak
    peak_idx = int(mu * sampling_rate)  # Index corresponding to t=mu
    print(f"Expected peak analysis:")
    print(f"  Peak index: {peak_idx}")
    print(f"  Peak time: {t[peak_idx]:.1f} seconds")
    print(f"  Peak velocity: {velocity[peak_idx]:.3f} m/s")
    print()
    
    # Test windows around the peak
    test_centers = [peak_idx - 50, peak_idx - 25, peak_idx, peak_idx + 25, peak_idx + 50]
    
    print("Window analysis around peak (WITH THRESHOLDING):")
    rolling_wcs_values = []
    rolling_wcs_times = []
    
    for center in test_centers:
        if 0 <= center < len(velocity):
            window_start = max(0, center - half_window)
            window_end = min(len(velocity), center + half_window + (1 if epoch_samples % 2 == 1 else 0))
            
            window_data = velocity[window_start:window_end]
            
            # WITH THRESHOLDING - only velocities above threshold
            threshold_mask = (window_data >= threshold_min) & (window_data <= threshold_max)
            time_per_sample = 1.0 / sampling_rate
            window_distance = np.sum(window_data[threshold_mask] * time_per_sample)  # Only thresholded values!
            
            rolling_wcs_values.append(window_distance)
            rolling_wcs_times.append(t[center])
            
            print(f"  Center {center} (t={t[center]:.1f}s):")
            print(f"    Window: {window_start} to {window_end} ({len(window_data)} samples)")
            print(f"    Distance: {window_distance:.3f} m")
            print(f"    Mean velocity in window: {np.mean(window_data):.3f} m/s")
            print(f"    Max velocity in window: {np.max(window_data):.3f} m/s")
            print(f"    Min velocity in window: {np.min(window_data):.3f} m/s")
            print(f"    Samples above threshold: {np.sum(threshold_mask)} / {len(window_data)}")
            print(f"    Mean velocity above threshold: {np.mean(window_data[threshold_mask]) if np.sum(threshold_mask) > 0 else 0:.3f} m/s")
            print()
    
    # Now let's find the actual maximum
    print("Finding actual maximum WCS window (WITH THRESHOLDING)...")
    max_distance = 0
    max_center = 0
    max_window_start = 0
    max_window_end = 0
    
    # Check all possible window centers
    for i in range(len(velocity)):
        window_start = max(0, i - half_window)
        window_end = min(len(velocity), i + half_window + (1 if epoch_samples % 2 == 1 else 0))
        
        window_data = velocity[window_start:window_end]
        
        # WITH THRESHOLDING - only velocities above threshold
        threshold_mask = (window_data >= threshold_min) & (window_data <= threshold_max)
        time_per_sample = 1.0 / sampling_rate
        window_distance = np.sum(window_data[threshold_mask] * time_per_sample)  # Only thresholded values!
        
        if window_distance > max_distance:
            max_distance = window_distance
            max_center = i
            max_window_start = window_start
            max_window_end = window_end
    
    print(f"Maximum WCS found (WITH THRESHOLDING):")
    print(f"  Center index: {max_center}")
    print(f"  Center time: {t[max_center]:.1f} seconds")
    print(f"  Window: {max_window_start} to {max_window_end}")
    print(f"  Distance: {max_distance:.3f} m")
    print(f"  Time difference from expected peak: {abs(t[max_center] - mu):.1f} seconds")
    print()
    
    # Analyze the maximum window
    max_window_data = velocity[max_window_start:max_window_end]
    max_window_threshold_mask = (max_window_data >= threshold_min) & (max_window_data <= threshold_max)
    max_window_time = len(max_window_data) * time_per_sample
    
    print(f"Maximum window analysis:")
    print(f"  Window size: {len(max_window_data)} samples")
    print(f"  Window duration: {max_window_time:.3f} s")
    print(f"  Mean velocity: {np.mean(max_window_data):.3f} m/s")
    print(f"  Max velocity in window: {np.max(max_window_data):.3f} m/s")
    print(f"  Min velocity in window: {np.min(max_window_data):.3f} m/s")
    print(f"  Samples above threshold: {np.sum(max_window_threshold_mask)} / {len(max_window_data)}")
    print(f"  Mean velocity above threshold: {np.mean(max_window_data[max_window_threshold_mask]) if np.sum(max_window_threshold_mask) > 0 else 0:.3f} m/s")
    print()
    
    # Compare with peak-centered window
    peak_window_start = max(0, peak_idx - half_window)
    peak_window_end = min(len(velocity), peak_idx + half_window + (1 if epoch_samples % 2 == 1 else 0))
    peak_window_data = velocity[peak_window_start:peak_window_end]
    peak_window_threshold_mask = (peak_window_data >= threshold_min) & (peak_window_data <= threshold_max)
    peak_window_distance = np.sum(peak_window_data[peak_window_threshold_mask] * time_per_sample)
    peak_window_time = len(peak_window_data) * time_per_sample
    
    print(f"Peak-centered window analysis:")
    print(f"  Window: {peak_window_start} to {peak_window_end}")
    print(f"  Distance: {peak_window_distance:.3f} m")
    print(f"  Window duration: {peak_window_time:.3f} s")
    print(f"  Mean velocity: {np.mean(peak_window_data):.3f} m/s")
    print(f"  Max velocity in window: {np.max(peak_window_data):.3f} m/s")
    print(f"  Min velocity in window: {np.min(peak_window_data):.3f} m/s")
    print(f"  Samples above threshold: {np.sum(peak_window_threshold_mask)} / {len(peak_window_data)}")
    print(f"  Mean velocity above threshold: {np.mean(peak_window_data[peak_window_threshold_mask]) if np.sum(peak_window_threshold_mask) > 0 else 0:.3f} m/s")
    print()
    
    print(f"Comparison:")
    print(f"  Peak-centered vs Max WCS distance: {peak_window_distance:.3f} vs {max_distance:.3f} m")
    print(f"  Peak-centered vs Max WCS time: {peak_window_time:.3f} vs {max_window_time:.3f} s")
    print(f"  Difference: {max_distance - peak_window_distance:.3f} m")
    
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot velocity with windows and threshold
    ax1.plot(t, velocity, 'b-', linewidth=2, label='Velocity')
    ax1.axhline(y=threshold_min, color='red', linestyle='--', alpha=0.7, label=f'Threshold: {threshold_min} m/s')
    ax1.axvline(x=mu, color='red', linestyle='--', alpha=0.7, label=f'Expected peak at t={mu}s')
    
    # Mark the maximum WCS window
    ax1.axvspan(t[max_window_start], t[max_window_end-1], alpha=0.3, color='green', 
               label=f'Max WCS window (t={t[max_center]:.1f}s, d={max_distance:.1f}m)')
    
    # Mark the peak-centered window
    ax1.axvspan(t[peak_window_start], t[peak_window_end-1], alpha=0.3, color='orange', 
               label=f'Peak-centered window (d={peak_window_distance:.1f}m)')
    
    # Highlight thresholded regions
    thresholded_indices = np.where((velocity >= threshold_min) & (velocity <= threshold_max))[0]
    ax1.scatter(t[thresholded_indices], velocity[thresholded_indices], 
               color='green', alpha=0.6, s=10, label='Above threshold')
    
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('Velocity (m/s)')
    ax1.set_title('Velocity Signal with WCS Windows (WITH THRESHOLDING)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot rolling WCS values
    rolling_wcs_all_values = []
    rolling_wcs_all_times = []
    
    for i in range(len(velocity)):
        window_start = max(0, i - half_window)
        window_end = min(len(velocity), i + half_window + (1 if epoch_samples % 2 == 1 else 0))
        
        window_data = velocity[window_start:window_end]
        
        # WITH THRESHOLDING - only velocities above threshold
        threshold_mask = (window_data >= threshold_min) & (window_data <= threshold_max)
        time_per_sample = 1.0 / sampling_rate
        window_distance = np.sum(window_data[threshold_mask] * time_per_sample)  # Only thresholded values!
        
        rolling_wcs_all_values.append(window_distance)
        rolling_wcs_all_times.append(t[i])
    
    ax2.plot(rolling_wcs_all_times, rolling_wcs_all_values, 'g-', linewidth=2, label='Rolling WCS Values (WITH THRESHOLDING)')
    ax2.axvline(x=mu, color='red', linestyle='--', alpha=0.7, label=f'Expected peak at t={mu}s')
    ax2.axvline(x=t[max_center], color='green', linestyle='--', alpha=0.7, label=f'Actual WCS peak at t={t[max_center]:.1f}s')
    ax2.axhline(y=max_distance, color='green', linestyle=':', alpha=0.7, label=f'Max WCS: {max_distance:.1f}m')
    
    ax2.set_xlabel('Time (seconds)')
    ax2.set_ylabel('WCS Distance (m)')
    ax2.set_title('Rolling WCS Values Over Time (1-minute epoch, WITH THRESHOLDING)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('rolling_wcs_with_threshold.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Analysis saved to: rolling_wcs_with_threshold.png")
    
    # Show the rolling WCS curve around the peak
    print("\n=== ROLLING WCS VALUES AROUND PEAK (WITH THRESHOLDING) ===")
    peak_range = range(max(0, peak_idx - 100), min(len(velocity), peak_idx + 100))
    for i in peak_range[::10]:  # Every 10th sample
        window_start = max(0, i - half_window)
        window_end = min(len(velocity), i + half_window + (1 if epoch_samples % 2 == 1 else 0))
        window_data = velocity[window_start:window_end]
        threshold_mask = (window_data >= threshold_min) & (window_data <= threshold_max)
        time_per_sample = 1.0 / sampling_rate
        window_distance = np.sum(window_data[threshold_mask] * time_per_sample)
        print(f"  t={t[i]:.1f}s: {window_distance:.3f} m")

if __name__ == "__main__":
    test_rolling_wcs_with_threshold() 