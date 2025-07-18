#!/usr/bin/env python3
"""
Simple test to show the exact Python code for rolling WCS calculation.
"""

import numpy as np
import matplotlib.pyplot as plt

def simple_rolling_wcs_calculation():
    """Show the exact Python code for rolling WCS calculation"""
    
    # Test parameters
    sigma = 10
    mu = 9 * sigma  # 90 seconds
    t = np.linspace(0, sigma * 18, 1800)  # 0 to 180 seconds
    velocity = 8 * np.exp(-0.5 * ((t - mu) / sigma)**2)  # Normal distribution
    
    # Analysis parameters
    epoch_duration = 1/6  # 10 seconds
    sampling_rate = 10    # 10 Hz
    th1_min, th1_max = 5.0, 100.0  # Threshold 1
    
    print("=== EXACT PYTHON CODE FOR ROLLING WCS ===")
    print("epoch_samples = int(epoch_duration * 60 * sampling_rate)  # 100 samples")
    print("half_window = epoch_samples // 2  # 50 samples")
    print()
    print("for i in range(len(velocity)):")
    print("    window_start = max(0, i - half_window)")
    print("    window_end = min(len(velocity), i + half_window + (1 if epoch_samples % 2 == 1 else 0))")
    print("    window_data = velocity[window_start:window_end]")
    print("    threshold_mask = (window_data >= th1_min) & (window_data <= th1_max)")
    print("    time_per_sample = 1.0 / sampling_rate")
    print("    window_distance = np.sum(window_data[threshold_mask] * time_per_sample)")
    print()
    
    # Calculate epoch samples
    epoch_samples = int(epoch_duration * 60 * sampling_rate)  # 100 samples
    half_window = epoch_samples // 2  # 50 samples
    
    print(f"Calculated values:")
    print(f"  epoch_samples = {epoch_samples}")
    print(f"  half_window = {half_window}")
    print(f"  time_per_sample = {1.0/sampling_rate}")
    print()
    
    # Show the exact calculation for a few windows
    test_centers = [850, 860, 870, 880, 890, 900, 910, 920, 930, 940, 950]
    
    print("=== DETAILED CALCULATION FOR SELECTED WINDOWS ===")
    rolling_wcs_values = []
    rolling_wcs_times = []
    
    for center in test_centers:
        # EXACT CODE BEING USED:
        window_start = max(0, center - half_window)
        window_end = min(len(velocity), center + half_window + (1 if epoch_samples % 2 == 1 else 0))
        window_data = velocity[window_start:window_end]
        threshold_mask = (window_data >= th1_min) & (window_data <= th1_max)
        time_per_sample = 1.0 / sampling_rate
        window_distance = np.sum(window_data[threshold_mask] * time_per_sample)
        
        rolling_wcs_values.append(window_distance)
        rolling_wcs_times.append(t[center])
        
        print(f"Center {center} (t={t[center]:.1f}s):")
        print(f"  window_start = max(0, {center} - {half_window}) = {window_start}")
        print(f"  window_end = min({len(velocity)}, {center} + {half_window} + 1) = {window_end}")
        print(f"  window_data = velocity[{window_start}:{window_end}] = {len(window_data)} samples")
        print(f"  threshold_mask = (window_data >= {th1_min}) & (window_data <= {th1_max})")
        print(f"  samples_in_threshold = {np.sum(threshold_mask)}")
        print(f"  window_distance = np.sum(window_data[threshold_mask] * {time_per_sample}) = {window_distance:.3f} m")
        print(f"  mean_velocity_in_window = {np.mean(window_data):.3f} m/s")
        print(f"  max_velocity_in_window = {np.max(window_data):.3f} m/s")
        print()
    
    # Now let's see what happens when we look at the threshold mask more carefully
    print("=== THRESHOLD ANALYSIS ===")
    center = 900  # Peak center
    window_start = max(0, center - half_window)
    window_end = min(len(velocity), center + half_window + (1 if epoch_samples % 2 == 1 else 0))
    window_data = velocity[window_start:window_end]
    threshold_mask = (window_data >= th1_min) & (window_data <= th1_max)
    
    print(f"Window centered at t={t[center]:.1f}s:")
    print(f"  Window data range: {np.min(window_data):.3f} to {np.max(window_data):.3f} m/s")
    print(f"  Threshold range: {th1_min} to {th1_max} m/s")
    print(f"  Samples in threshold: {np.sum(threshold_mask)} out of {len(window_data)}")
    print(f"  Threshold percentage: {100*np.sum(threshold_mask)/len(window_data):.1f}%")
    print()
    
    # Show the actual values being summed
    print("=== VALUES BEING SUMMED ===")
    values_in_threshold = window_data[threshold_mask]
    print(f"Values in threshold: {len(values_in_threshold)} samples")
    if len(values_in_threshold) > 0:
        print(f"  Range: {np.min(values_in_threshold):.3f} to {np.max(values_in_threshold):.3f} m/s")
        print(f"  Sum: {np.sum(values_in_threshold):.3f} m/s")
        print(f"  Distance = {np.sum(values_in_threshold) * time_per_sample:.3f} m")
    else:
        print("  No values in threshold!")
    print()
    
    # Create visualization
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12))
    
    # Plot velocity with threshold
    ax1.plot(t, velocity, 'b-', linewidth=2, label='Velocity')
    ax1.axhline(y=th1_min, color='red', linestyle='--', alpha=0.7, label=f'Threshold min: {th1_min} m/s')
    ax1.axhline(y=th1_max, color='red', linestyle='--', alpha=0.7, label=f'Threshold max: {th1_max} m/s')
    ax1.fill_between(t, th1_min, th1_max, alpha=0.2, color='red', label='Threshold range')
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('Velocity (m/s)')
    ax1.set_title('Velocity Signal with Threshold Range')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot rolling WCS values
    ax2.plot(rolling_wcs_times, rolling_wcs_values, 'g-o', linewidth=2, markersize=6, label='Rolling WCS Values')
    ax2.axvline(x=mu, color='red', linestyle='--', alpha=0.7, label=f'Expected peak at t={mu}s')
    ax2.set_xlabel('Time (seconds)')
    ax2.set_ylabel('WCS Distance (m)')
    ax2.set_title('Rolling WCS Values Over Time (10s epoch)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot window size over time
    window_sizes = []
    for i in range(len(velocity)):
        window_start = max(0, i - half_window)
        window_end = min(len(velocity), i + half_window + (1 if epoch_samples % 2 == 1 else 0))
        window_sizes.append(window_end - window_start)
    
    ax3.plot(t, window_sizes, 'purple', linewidth=2, label='Window Size')
    ax3.axhline(y=epoch_samples, color='purple', linestyle='--', alpha=0.7, label=f'Full window size: {epoch_samples}')
    ax3.set_xlabel('Time (seconds)')
    ax3.set_ylabel('Window Size (samples)')
    ax3.set_title('Window Size Over Time')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('simple_wcs_calculation.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Analysis saved to: simple_wcs_calculation.png")
    
    # Now let's test with a much lower threshold to see the effect
    print("\n=== TESTING WITH LOWER THRESHOLD ===")
    th1_min_low, th1_max_low = 2.0, 100.0  # Lower threshold
    
    rolling_wcs_low = []
    for center in test_centers:
        window_start = max(0, center - half_window)
        window_end = min(len(velocity), center + half_window + (1 if epoch_samples % 2 == 1 else 0))
        window_data = velocity[window_start:window_end]
        threshold_mask = (window_data >= th1_min_low) & (window_data <= th1_max_low)
        time_per_sample = 1.0 / sampling_rate
        window_distance = np.sum(window_data[threshold_mask] * time_per_sample)
        rolling_wcs_low.append(window_distance)
    
    print(f"With threshold {th1_min_low}-{th1_max_low} m/s:")
    for i, center in enumerate(test_centers):
        print(f"  t={t[center]:.1f}s: {rolling_wcs_low[i]:.3f} m")
    
    # Plot comparison
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    ax.plot(rolling_wcs_times, rolling_wcs_values, 'g-o', linewidth=2, markersize=6, label=f'Threshold {th1_min}-{th1_max} m/s')
    ax.plot(rolling_wcs_times, rolling_wcs_low, 'b-o', linewidth=2, markersize=6, label=f'Threshold {th1_min_low}-{th1_max_low} m/s')
    ax.axvline(x=mu, color='red', linestyle='--', alpha=0.7, label=f'Expected peak at t={mu}s')
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('WCS Distance (m)')
    ax.set_title('Rolling WCS Values with Different Thresholds')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('wcs_threshold_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Threshold comparison saved to: wcs_threshold_comparison.png")

if __name__ == "__main__":
    simple_rolling_wcs_calculation() 