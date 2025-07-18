#!/usr/bin/env python3
"""
Test script to plot WCS values for rolling windows across a normal distribution velocity signal.
This shows how WCS analysis works at each window position.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from wcs_analysis import calculate_wcs_period_rolling

def generate_normal_distribution_velocity():
    """Generate a normal distribution velocity signal for testing."""
    # Parameters
    sigma = 10  # seconds
    mu = 9 * sigma  # peak at 90 seconds
    t = np.linspace(0, sigma * 18, 1800)  # 3 minutes at 10Hz
    
    # Generate velocity using normal distribution
    velocity = norm.pdf(t, mu, sigma)
    
    # Scale to reasonable velocity values (m/s) - multiply by 10000 to get velocities over 5 m/s
    velocity = velocity * 10000  # Scale factor to get velocities over 5 m/s
    
    # Create DataFrame
    df = pd.DataFrame({
        'Time': t,
        'Velocity': velocity
    })
    
    return df

def calculate_rolling_wcs_values(velocity_data, window_samples=600, threshold_min=5.0, threshold_max=15.0):
    """
    Calculate WCS values for each rolling window position.
    
    Args:
        velocity_data: Array of velocity values
        window_samples: Number of samples in the rolling window (600 = 1 minute at 10Hz)
        threshold_min: Minimum velocity threshold
        threshold_max: Maximum velocity threshold
        
    Returns:
        Array of WCS values for each window position
    """
    wcs_values = []
    sampling_rate = 10  # Hz
    
    # Calculate WCS for each window position
    for i in range(len(velocity_data) - window_samples + 1):
        # Extract window data
        window_data = velocity_data[i:i + window_samples]
        
        # Debug: Check if any values are in threshold range
        in_threshold = np.sum((window_data >= threshold_min) & (window_data <= threshold_max))
        
        # Calculate WCS for this window
        distance, time, start_idx, end_idx = calculate_wcs_period_rolling(
            window_data, 
            window_samples / sampling_rate,  # Convert to seconds
            sampling_rate,
            threshold_min,
            threshold_max
        )
        
        wcs_values.append(distance)
        
        # Debug: Print first few windows and window around peak
        if i < 5 or (i >= 890 and i <= 910):  # Around peak (90s * 10Hz = 900)
            print(f"Window {i}: max_vel={np.max(window_data):.2f}, in_threshold={in_threshold}, wcs={distance:.3f}")
    
    return np.array(wcs_values)

def plot_velocity_and_wcs():
    """Plot velocity signal with rolling WCS values below."""
    print("🔬 Plotting Velocity Signal with Rolling WCS Values")
    print("=" * 60)
    
    # Generate test data
    df = generate_normal_distribution_velocity()
    velocity_data = df['Velocity'].values
    
    print(f"📊 Generated {len(df)} data points over {df['Time'].max():.1f} seconds")
    print(f"📈 Peak velocity: {df['Velocity'].max():.3f} m/s at {df.loc[df['Velocity'].idxmax(), 'Time']:.1f}s")
    
    # Calculate rolling WCS values
    window_samples = 600  # 1 minute at 10Hz
    threshold_min, threshold_max = 10.0, 50.0  # Adjusted to include our peak
    
    print(f"\n⚙️  Analysis Parameters:")
    print(f"   Window size: {window_samples} samples ({window_samples/10:.1f} seconds)")
    print(f"   Threshold range: {threshold_min}-{threshold_max} m/s")
    print(f"   Number of rolling windows: {len(velocity_data) - window_samples + 1}")
    
    wcs_values = calculate_rolling_wcs_values(velocity_data, window_samples, threshold_min, threshold_max)
    
    print(f"\n📋 WCS Analysis Results:")
    print(f"   Maximum WCS distance: {np.max(wcs_values):.3f} m")
    print(f"   Mean WCS distance: {np.mean(wcs_values):.3f} m")
    print(f"   Minimum WCS distance: {np.min(wcs_values):.3f} m")
    
    # Find the window with maximum WCS
    max_wcs_idx = np.argmax(wcs_values)
    max_wcs_time = df.iloc[max_wcs_idx]['Time']
    print(f"   Best WCS window starts at: {max_wcs_time:.1f}s")
    
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Plot velocity signal
    ax1.plot(df['Time'], df['Velocity'], 'b-', linewidth=2, label='Velocity')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Velocity (m/s)')
    ax1.set_title('Normal Distribution Velocity Signal (Scaled x10000)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Add threshold lines
    ax1.axhline(y=threshold_min, color='orange', linestyle='--', alpha=0.7, label=f'Threshold Min ({threshold_min} m/s)')
    ax1.axhline(y=threshold_max, color='orange', linestyle='--', alpha=0.7, label=f'Threshold Max ({threshold_max} m/s)')
    
    # Highlight the best WCS window
    best_window_start = max_wcs_time
    best_window_end = best_window_start + window_samples / 10  # Convert samples to seconds
    ax1.axvspan(best_window_start, best_window_end, alpha=0.3, color='red', label=f'Best WCS Window ({wcs_values[max_wcs_idx]:.1f}m)')
    
    # Plot WCS values
    # Create time array for WCS values (start of each window)
    wcs_times = df['Time'].values[:len(wcs_values)]
    
    ax2.plot(wcs_times, wcs_values, 'g-', linewidth=2, label='Rolling WCS Distance')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('WCS Distance (m)')
    ax2.set_title(f'Rolling WCS Values (Window: {window_samples/10:.1f}s, Threshold: {threshold_min}-{threshold_max} m/s)')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Add horizontal line at maximum WCS
    ax2.axhline(y=np.max(wcs_values), color='red', linestyle='--', alpha=0.7, label=f'Max WCS: {np.max(wcs_values):.1f}m')
    
    # Highlight the best window position
    ax2.axvline(x=best_window_start, color='red', linestyle='-', alpha=0.7, label=f'Best Window Start: {best_window_start:.1f}s')
    
    plt.tight_layout()
    plt.savefig('test_wcs_rolling_plot.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"\n💾 Visualization saved as 'test_wcs_rolling_plot.png'")
    
    # Additional analysis
    print(f"\n📊 Detailed Analysis:")
    print(f"   Windows with WCS > 0: {np.sum(wcs_values > 0)}")
    print(f"   Windows with WCS = 0: {np.sum(wcs_values == 0)}")
    print(f"   Percentage of windows with activity: {100 * np.sum(wcs_values > 0) / len(wcs_values):.1f}%")
    
    # Show WCS values around the peak
    peak_idx = df['Velocity'].idxmax()
    peak_time = df.iloc[peak_idx]['Time']
    print(f"\n🎯 Peak Analysis:")
    print(f"   Velocity peak at: {peak_time:.1f}s")
    print(f"   WCS at peak window: {wcs_values[max(0, peak_idx - window_samples//2)]:.3f} m")
    
    return wcs_values, df

if __name__ == "__main__":
    wcs_values, df = plot_velocity_and_wcs() 