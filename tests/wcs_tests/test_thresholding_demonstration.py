#!/usr/bin/env python3
"""
WCS Thresholding Demonstration
Step-by-step demonstration of how thresholding works with clear examples
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Add the src directory to the path
sys.path.append('.')

from src.wcs_analysis import calculate_wcs_period_rolling, calculate_wcs_period_contiguous, calculate_acceleration

def create_simple_example_data():
    """Create simple example data to demonstrate thresholding"""
    
    print("📊 Creating Simple Example Data")
    print("=" * 40)
    
    # Create 10 data points for demonstration
    N = 10
    time_seconds = np.arange(N)
    
    # Simple velocity profile: [2, 3, 8, 7, 4, 1, 6, 9, 5, 2]
    velocities = np.array([2.0, 3.0, 8.0, 7.0, 4.0, 1.0, 6.0, 9.0, 5.0, 2.0])
    
    # Calculate acceleration using central difference
    acceleration = calculate_acceleration(velocities, 1.0)  # 1 Hz sampling
    
    print(f"Original Data (N={N} points):")
    print(f"Index:     {list(range(N))}")
    print(f"Velocity:  {velocities}")
    print(f"Acceleration: {acceleration}")
    print()
    
    return velocities, acceleration, time_seconds

def demonstrate_velocity_thresholding(velocities, acceleration, time_seconds):
    """Demonstrate velocity thresholding step by step"""
    
    print("🔍 Velocity Thresholding Demonstration")
    print("=" * 50)
    
    # Example: V > 5 m/s threshold
    threshold_value = 5.0
    print(f"Threshold condition: V > {threshold_value} m/s")
    print()
    
    # Step 1: Create threshold condition
    threshold_condition = velocities > threshold_value
    print(f"Step 1 - Threshold condition (V > {threshold_value}):")
    print(f"Index:     {list(range(len(velocities)))}")
    print(f"Velocity:  {velocities}")
    print(f"Condition: {threshold_condition}")
    print()
    
    # Step 2: Apply thresholding
    modified_velocities = np.where(threshold_condition, velocities, 0.0)
    print(f"Step 2 - Modified velocities (V > {threshold_value}):")
    print(f"Index:     {list(range(len(velocities)))}")
    print(f"Original:  {velocities}")
    print(f"Modified:  {modified_velocities}")
    print()
    
    # Step 3: Calculate data reduction
    original_nonzero = np.sum(velocities > 0)
    modified_nonzero = np.sum(modified_velocities > 0)
    reduction_percent = ((original_nonzero - modified_nonzero) / original_nonzero) * 100
    
    print(f"Step 3 - Data reduction analysis:")
    print(f"  Original non-zero values: {original_nonzero}")
    print(f"  Modified non-zero values: {modified_nonzero}")
    print(f"  Data reduction: {reduction_percent:.1f}%")
    print()
    
    return modified_velocities, threshold_condition, reduction_percent

def demonstrate_acceleration_thresholding(velocities, acceleration, time_seconds):
    """Demonstrate acceleration thresholding step by step"""
    
    print("🔍 Acceleration Thresholding Demonstration")
    print("=" * 55)
    
    # Example: |a| > 1.0 m/s² threshold
    threshold_value = 1.0
    print(f"Threshold condition: |a| > {threshold_value} m/s²")
    print()
    
    # Step 1: Create threshold condition
    threshold_condition = np.abs(acceleration) > threshold_value
    print(f"Step 1 - Threshold condition (|a| > {threshold_value}):")
    print(f"Index:        {list(range(len(acceleration)))}")
    print(f"Acceleration: {acceleration}")
    print(f"|a|:          {np.abs(acceleration)}")
    print(f"Condition:    {threshold_condition}")
    print()
    
    # Step 2: Apply thresholding to both velocity and acceleration
    modified_velocities = np.where(threshold_condition, velocities, 0.0)
    modified_acceleration = np.where(threshold_condition, acceleration, 0.0)
    
    print(f"Step 2 - Modified data (|a| > {threshold_value}):")
    print(f"Index:        {list(range(len(acceleration)))}")
    print(f"Original V:   {velocities}")
    print(f"Modified V:   {modified_velocities}")
    print(f"Original a:   {acceleration}")
    print(f"Modified a:   {modified_acceleration}")
    print()
    
    # Step 3: Calculate data reduction
    original_nonzero = np.sum(velocities > 0)
    modified_nonzero = np.sum(modified_velocities > 0)
    reduction_percent = ((original_nonzero - modified_nonzero) / original_nonzero) * 100
    
    print(f"Step 3 - Data reduction analysis:")
    print(f"  Original non-zero velocities: {original_nonzero}")
    print(f"  Modified non-zero velocities: {modified_nonzero}")
    print(f"  Data reduction: {reduction_percent:.1f}%")
    print()
    
    return modified_velocities, modified_acceleration, threshold_condition, reduction_percent

def demonstrate_multiple_thresholds(velocities, acceleration, time_seconds):
    """Demonstrate testing multiple threshold values"""
    
    print("🔍 Multiple Threshold Testing Demonstration")
    print("=" * 55)
    
    # Test different velocity thresholds
    velocity_thresholds = [3.0, 5.0, 7.0]
    
    print("Testing multiple velocity thresholds:")
    print(f"Thresholds: {velocity_thresholds}")
    print()
    
    results = {}
    
    for threshold in velocity_thresholds:
        print(f"📊 Testing V > {threshold} m/s:")
        
        # Apply threshold
        threshold_condition = velocities > threshold
        modified_velocities = np.where(threshold_condition, velocities, 0.0)
        
        # Calculate reduction
        original_nonzero = np.sum(velocities > 0)
        modified_nonzero = np.sum(modified_velocities > 0)
        reduction_percent = ((original_nonzero - modified_nonzero) / original_nonzero) * 100
        
        print(f"  Original:  {velocities}")
        print(f"  Modified:  {modified_velocities}")
        print(f"  Reduction: {reduction_percent:.1f}%")
        print()
        
        results[threshold] = {
            'modified_velocities': modified_velocities,
            'reduction_percent': reduction_percent
        }
    
    return results

def demonstrate_wcs_with_thresholding(velocities, acceleration, time_seconds):
    """Demonstrate WCS calculation with and without thresholding"""
    
    print("🔍 WCS Calculation with Thresholding")
    print("=" * 45)
    
    # Parameters for WCS calculation
    epoch_duration = 5.0 / 60.0  # 5 seconds
    sampling_rate = 1.0  # 1 Hz
    
    # Calculate WCS without thresholding (baseline)
    print("📊 Baseline WCS (no thresholding):")
    try:
        rolling_distance, rolling_time, rolling_start, rolling_end = calculate_wcs_period_rolling(
            velocities, epoch_duration, sampling_rate, 0.0, 100.0
        )
        print(f"  Rolling WCS: {rolling_distance:.1f}m at t={time_seconds[rolling_start]:.1f}s")
    except Exception as e:
        print(f"  Rolling WCS: Error - {e}")
    
    try:
        contiguous_distance, contiguous_time, contiguous_start, contiguous_end = calculate_wcs_period_contiguous(
            velocities, epoch_duration, sampling_rate, 0.0, 100.0
        )
        print(f"  Contiguous WCS: {contiguous_distance:.1f}m at t={time_seconds[contiguous_start]:.1f}s")
    except Exception as e:
        print(f"  Contiguous WCS: Error - {e}")
    print()
    
    # Calculate WCS with velocity thresholding
    print("📊 WCS with velocity thresholding (V > 5 m/s):")
    threshold_condition = velocities > 5.0
    modified_velocities = np.where(threshold_condition, velocities, 0.0)
    
    try:
        rolling_distance, rolling_time, rolling_start, rolling_end = calculate_wcs_period_rolling(
            modified_velocities, epoch_duration, sampling_rate, 0.0, 100.0
        )
        print(f"  Rolling WCS: {rolling_distance:.1f}m at t={time_seconds[rolling_start]:.1f}s")
    except Exception as e:
        print(f"  Rolling WCS: Error - {e}")
    
    try:
        contiguous_distance, contiguous_time, contiguous_start, contiguous_end = calculate_wcs_period_contiguous(
            modified_velocities, epoch_duration, sampling_rate, 0.0, 100.0
        )
        print(f"  Contiguous WCS: {contiguous_distance:.1f}m at t={time_seconds[contiguous_start]:.1f}s")
    except Exception as e:
        print(f"  Contiguous WCS: Error - {e}")
    print()

def plot_thresholding_demonstration(velocities, acceleration, time_seconds, results):
    """Create visualization of thresholding demonstration"""
    
    print("📊 Generating Thresholding Demonstration Plots")
    print("=" * 50)
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('WCS Thresholding Demonstration', fontsize=16, fontweight='bold')
    
    # Plot 1: Original data
    ax1 = axes[0, 0]
    ax1.plot(time_seconds, velocities, 'bo-', linewidth=2, markersize=8, label='Velocity')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Velocity (m/s)')
    ax1.set_title('Original Velocity Data')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Add acceleration on secondary axis
    ax1_twin = ax1.twinx()
    ax1_twin.plot(time_seconds, acceleration, 'ro-', linewidth=2, markersize=6, alpha=0.7, label='Acceleration')
    ax1_twin.set_ylabel('Acceleration (m/s²)', color='r')
    ax1_twin.tick_params(axis='y', labelcolor='r')
    ax1_twin.legend(loc='upper right')
    
    # Plot 2: Velocity thresholding
    ax2 = axes[0, 1]
    threshold_condition = velocities > 5.0
    modified_velocities = np.where(threshold_condition, velocities, 0.0)
    
    ax2.plot(time_seconds, velocities, 'bo-', linewidth=2, markersize=8, label='Original', alpha=0.5)
    ax2.plot(time_seconds, modified_velocities, 'go-', linewidth=2, markersize=8, label='V > 5 m/s')
    ax2.axhline(y=5.0, color='red', linestyle='--', alpha=0.7, label='Threshold')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Velocity (m/s)')
    ax2.set_title('Velocity Thresholding (V > 5 m/s)')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Plot 3: Acceleration thresholding
    ax3 = axes[1, 0]
    accel_threshold_condition = np.abs(acceleration) > 1.0
    modified_velocities_accel = np.where(accel_threshold_condition, velocities, 0.0)
    
    ax3.plot(time_seconds, velocities, 'bo-', linewidth=2, markersize=8, label='Original', alpha=0.5)
    ax3.plot(time_seconds, modified_velocities_accel, 'mo-', linewidth=2, markersize=8, label='|a| > 1 m/s²')
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Velocity (m/s)')
    ax3.set_title('Acceleration Thresholding (|a| > 1 m/s²)')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # Plot 4: Multiple thresholds comparison
    ax4 = axes[1, 1]
    thresholds = [3.0, 5.0, 7.0]
    colors = ['green', 'orange', 'red']
    
    for i, threshold in enumerate(thresholds):
        threshold_condition = velocities > threshold
        modified_vel = np.where(threshold_condition, velocities, 0.0)
        ax4.plot(time_seconds, modified_vel, color=colors[i], marker='o', linewidth=2, 
                markersize=6, label=f'V > {threshold} m/s', alpha=0.8)
    
    ax4.plot(time_seconds, velocities, 'bo-', linewidth=2, markersize=8, label='Original', alpha=0.3)
    ax4.set_xlabel('Time (s)')
    ax4.set_ylabel('Velocity (m/s)')
    ax4.set_title('Multiple Velocity Thresholds')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    plt.tight_layout()
    
    # Save the plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"thresholding_demonstration_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✅ Saved plot: {filename}")
    
    plt.show()

def main():
    """Main function to run thresholding demonstration"""
    
    print("🧪 WCS Thresholding Demonstration")
    print("=" * 60)
    print("Step-by-step demonstration of thresholding process")
    print("=" * 60)
    
    # Create simple example data
    velocities, acceleration, time_seconds = create_simple_example_data()
    
    # Demonstrate velocity thresholding
    modified_velocities, vel_condition, vel_reduction = demonstrate_velocity_thresholding(
        velocities, acceleration, time_seconds
    )
    
    # Demonstrate acceleration thresholding
    modified_vel_accel, modified_accel, accel_condition, accel_reduction = demonstrate_acceleration_thresholding(
        velocities, acceleration, time_seconds
    )
    
    # Demonstrate multiple thresholds
    multiple_results = demonstrate_multiple_thresholds(velocities, acceleration, time_seconds)
    
    # Demonstrate WCS calculation with thresholding
    demonstrate_wcs_with_thresholding(velocities, acceleration, time_seconds)
    
    # Create visualization
    plot_thresholding_demonstration(velocities, acceleration, time_seconds, multiple_results)
    
    print(f"\n🎉 Thresholding Demonstration Complete!")
    print("=" * 60)
    print("Key concepts demonstrated:")
    print("1. Threshold conditions create boolean masks")
    print("2. np.where() applies thresholding (TRUE=original, FALSE=0)")
    print("3. Data reduction measures thresholding effect")
    print("4. WCS calculation uses modified datasets")
    print("5. Multiple thresholds require reinitializing original data")
    print("=" * 60)

if __name__ == "__main__":
    main() 