#!/usr/bin/env python3
"""
Test script to compare contiguous vs rolling WCS methods on a normalized normal distribution.
Peak velocity is normalized to exactly 8 m/s.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from wcs_analysis import calculate_wcs_period_rolling, calculate_wcs_period_contiguous

def generate_normalized_velocity():
    """Generate a normal distribution velocity signal with peak normalized to 8 m/s."""
    # Parameters
    sigma = 10  # seconds
    mu = 9 * sigma  # peak at 90 seconds
    t = np.linspace(0, sigma * 18, 1800)  # 3 minutes at 10Hz
    
    # Generate velocity using normal distribution
    velocity = norm.pdf(t, mu, sigma)
    
    # Normalize so peak is exactly 8 m/s
    velocity = velocity / np.max(velocity) * 8.0
    
    # Create DataFrame
    df = pd.DataFrame({
        'Time': t,
        'Velocity': velocity
    })
    
    return df

def calculate_rolling_wcs_centered(velocity_data, window_samples=600, threshold_min=5.0, threshold_max=15.0):
    """
    Calculate rolling WCS with centered window approach.
    
    Args:
        velocity_data: Array of velocity values
        window_samples: Number of samples in the rolling window (600 = 1 minute at 10Hz)
        threshold_min: Minimum velocity threshold
        threshold_max: Maximum velocity threshold
        
    Returns:
        Array of WCS values for each center position
    """
    wcs_values = []
    sampling_rate = 10  # Hz
    half_window = window_samples // 2
    
    # Calculate WCS for each center position
    for center_idx in range(len(velocity_data)):
        # Calculate window boundaries
        start_idx = center_idx - half_window
        end_idx = center_idx + half_window
        
        # Handle edge cases by padding with zeros
        if start_idx < 0:
            # Pad with zeros at the beginning
            padding_size = abs(start_idx)
            window_data = np.concatenate([np.zeros(padding_size), velocity_data[:end_idx]])
        elif end_idx > len(velocity_data):
            # Pad with zeros at the end
            padding_size = end_idx - len(velocity_data)
            window_data = np.concatenate([velocity_data[start_idx:], np.zeros(padding_size)])
        else:
            # Full window fits
            window_data = velocity_data[start_idx:end_idx]
        
        # Calculate WCS for this window
        distance, time, wcs_start_idx, wcs_end_idx = calculate_wcs_period_rolling(
            window_data, 
            window_samples / sampling_rate,  # Convert to seconds
            sampling_rate,
            threshold_min,
            threshold_max
        )
        
        wcs_values.append(distance)
    
    return np.array(wcs_values)

def calculate_contiguous_wcs_windows(velocity_data, window_samples=600, threshold_min=5.0, threshold_max=15.0):
    """
    Calculate WCS for contiguous windows.
    
    Args:
        velocity_data: Array of velocity values
        window_samples: Number of samples in each window (600 = 1 minute at 10Hz)
        threshold_min: Minimum velocity threshold
        threshold_max: Maximum velocity threshold
        
    Returns:
        List of WCS results for each contiguous window
    """
    wcs_results = []
    sampling_rate = 10  # Hz
    
    # Calculate number of complete windows
    num_windows = len(velocity_data) // window_samples
    
    for i in range(num_windows):
        start_idx = i * window_samples
        end_idx = start_idx + window_samples
        window_data = velocity_data[start_idx:end_idx]
        
        # Calculate WCS for this contiguous window
        distance, time, wcs_start_idx, wcs_end_idx = calculate_wcs_period_contiguous(
            window_data, 
            window_samples / sampling_rate,  # Convert to seconds
            sampling_rate,
            threshold_min,
            threshold_max
        )
        
        wcs_results.append({
            'window_idx': i,
            'start_time': start_idx / sampling_rate,
            'end_time': end_idx / sampling_rate,
            'distance': distance,
            'time': time,
            'wcs_start_idx': wcs_start_idx,
            'wcs_end_idx': wcs_end_idx
        })
    
    return wcs_results

def plot_comparison():
    """Plot velocity signal with both rolling and contiguous WCS analysis."""
    print("🔬 Comparing Rolling vs Contiguous WCS Methods")
    print("=" * 60)
    
    # Generate test data
    df = generate_normalized_velocity()
    velocity_data = df['Velocity'].values
    
    print(f"📊 Generated {len(df)} data points over {df['Time'].max():.1f} seconds")
    print(f"📈 Peak velocity: {df['Velocity'].max():.3f} m/s at {df.loc[df['Velocity'].idxmax(), 'Time']:.1f}s")
    
    # Analysis parameters
    window_samples = 600  # 1 minute at 10Hz
    threshold_min, threshold_max = 5.0, 15.0
    
    print(f"\n⚙️  Analysis Parameters:")
    print(f"   Window size: {window_samples} samples ({window_samples/10:.1f} seconds)")
    print(f"   Threshold range: {threshold_min}-{threshold_max} m/s")
    
    # Calculate both methods
    print(f"\n🔄 Calculating Rolling WCS (centered window)...")
    rolling_wcs = calculate_rolling_wcs_centered(velocity_data, window_samples, threshold_min, threshold_max)
    
    print(f"📏 Calculating Contiguous WCS...")
    contiguous_results = calculate_contiguous_wcs_windows(velocity_data, window_samples, threshold_min, threshold_max)
    
    # Display results
    print(f"\n📋 WCS Analysis Results:")
    print(f"   Rolling WCS - Max: {np.max(rolling_wcs):.3f} m, Mean: {np.mean(rolling_wcs):.3f} m")
    print(f"   Contiguous WCS - {len(contiguous_results)} windows:")
    
    for i, result in enumerate(contiguous_results):
        print(f"     Window {i+1}: {result['distance']:.3f} m ({result['time']:.1f}s)")
    
    # Create visualization
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12))
    
    # Plot 1: Velocity signal
    ax1.plot(df['Time'], df['Velocity'], 'b-', linewidth=2, label='Velocity')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Velocity (m/s)')
    ax1.set_title('Normal Distribution Velocity Signal (Peak = 8 m/s)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Add threshold lines
    ax1.axhline(y=threshold_min, color='orange', linestyle='--', alpha=0.7, label=f'Threshold Min ({threshold_min} m/s)')
    ax1.axhline(y=threshold_max, color='orange', linestyle='--', alpha=0.7, label=f'Threshold Max ({threshold_max} m/s)')
    
    # Highlight contiguous windows
    for i, result in enumerate(contiguous_results):
        color = ['red', 'green', 'blue'][i % 3]
        ax1.axvspan(result['start_time'], result['end_time'], alpha=0.2, color=color, 
                   label=f'Contiguous Window {i+1}' if i < 3 else "")
    
    # Plot 2: Rolling WCS values
    ax2.plot(df['Time'], rolling_wcs, 'g-', linewidth=2, label='Rolling WCS Distance')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('WCS Distance (m)')
    ax2.set_title(f'Rolling WCS Values (Centered Window: {window_samples/10:.1f}s)')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Add horizontal line at maximum rolling WCS
    max_rolling = np.max(rolling_wcs)
    ax2.axhline(y=max_rolling, color='red', linestyle='--', alpha=0.7, label=f'Max Rolling WCS: {max_rolling:.1f}m')
    
    # Plot 3: Contiguous WCS comparison
    contiguous_distances = [result['distance'] for result in contiguous_results]
    contiguous_times = [result['start_time'] + result['time']/2 for result in contiguous_results]  # Center of each window
    
    ax3.bar(range(len(contiguous_results)), contiguous_distances, color=['red', 'green', 'blue'][:len(contiguous_results)], 
            alpha=0.7, label='Contiguous WCS')
    ax3.set_xlabel('Window Number')
    ax3.set_ylabel('WCS Distance (m)')
    ax3.set_title('Contiguous WCS Results')
    ax3.set_xticks(range(len(contiguous_results)))
    ax3.set_xticklabels([f'Window {i+1}' for i in range(len(contiguous_results))])
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # Add horizontal line at maximum contiguous WCS
    max_contiguous = max(contiguous_distances) if contiguous_distances else 0
    ax3.axhline(y=max_contiguous, color='red', linestyle='--', alpha=0.7, label=f'Max Contiguous WCS: {max_contiguous:.1f}m')
    
    plt.tight_layout()
    plt.savefig('test_wcs_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"\n💾 Visualization saved as 'test_wcs_comparison.png'")
    
    # Method comparison
    print(f"\n✅ Method Comparison:")
    print(f"   Rolling WCS max: {max_rolling:.3f} m")
    print(f"   Contiguous WCS max: {max_contiguous:.3f} m")
    print(f"   Difference: {abs(max_rolling - max_contiguous):.3f} m")
    
    if abs(max_rolling - max_contiguous) < 0.1:
        print(f"   ✅ Methods agree (within 0.1m tolerance)")
    else:
        print(f"   ⚠️  Methods differ significantly")
    
    return rolling_wcs, contiguous_results, df

if __name__ == "__main__":
    rolling_wcs, contiguous_results, df = plot_comparison() 