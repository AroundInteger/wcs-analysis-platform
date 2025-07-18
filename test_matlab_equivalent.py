import numpy as np
import matplotlib.pyplot as plt

def matlab_equivalent_rolling_wcs(velocity_data, epoch_duration, sampling_rate=10):
    """
    MATLAB-equivalent rolling window WCS calculation
    
    Args:
        velocity_data: Array of velocity values
        epoch_duration: Duration of epoch in minutes
        sampling_rate: Sampling rate in Hz
        
    Returns:
        Tuple of (max_distance, max_time, start_index, end_index, center_index)
    """
    # Convert epoch duration to samples
    window_size = int(epoch_duration * 60 * sampling_rate)
    
    if len(velocity_data) < window_size:
        # If data is shorter than epoch, use all available data
        window_size = len(velocity_data)
    
    # Calculate half window size
    dt = window_size // 2
    
    # MATLAB equivalent: movsum with 'Endpoints','shrink'
    # This means the window shrinks at the edges
    moving_sums = []
    
    for i in range(len(velocity_data)):
        # Calculate window bounds with shrinking at edges
        start_idx = max(0, i - dt)
        end_idx = min(len(velocity_data), i + dt + (1 if window_size % 2 == 1 else 0))
        
        # Calculate sum for this window
        window_sum = np.sum(velocity_data[start_idx:end_idx])
        moving_sums.append(window_sum)
    
    moving_sums = np.array(moving_sums)
    
    # Find maximum value and index (MATLAB: [mv,imx] = max(M))
    max_distance = np.max(moving_sums)
    max_indices = np.where(moving_sums == max_distance)[0]
    
    # Handle ties by taking mean (MATLAB: if numel(mvi)>1; imx = ceil(mean(mvi)); end)
    if len(max_indices) > 1:
        center_index = int(np.ceil(np.mean(max_indices)))
    else:
        center_index = max_indices[0]
    
    # Convert to window bounds (MATLAB: id_mx = imx-dt+1:imx+dt)
    start_index = max(0, center_index - dt)
    end_index = min(len(velocity_data), center_index + dt + (1 if window_size % 2 == 1 else 0))
    
    # Calculate time within window
    time_per_sample = 1.0 / sampling_rate
    max_time = (end_index - start_index) * time_per_sample
    
    return max_distance * time_per_sample, max_time, start_index, end_index, center_index

def current_rolling_wcs(velocity_data, epoch_duration, sampling_rate=10):
    """
    Our current rolling window implementation for comparison
    """
    # Convert epoch duration to samples
    epoch_samples = int(epoch_duration * 60 * sampling_rate)
    
    if len(velocity_data) < epoch_samples:
        epoch_samples = len(velocity_data)
    
    # Calculate half-window size for central point focus
    half_window = epoch_samples // 2
    
    # Slide window through data with central point focus
    max_distance = 0
    max_time = 0
    start_index = 0
    end_index = 0
    center_index = 0
    
    for i in range(half_window, len(velocity_data) - half_window):
        # Window is centered on point i
        window_start = i - half_window
        window_end = i + half_window + (1 if epoch_samples % 2 == 1 else 0)
        
        window_data = velocity_data[window_start:window_end]
        
        # Calculate distance for this window
        time_per_sample = 1.0 / sampling_rate
        window_distance = np.sum(window_data) * time_per_sample
        
        # Update maximum if this window has higher distance
        if window_distance > max_distance:
            max_distance = window_distance
            max_time = len(window_data) * time_per_sample
            start_index = window_start
            end_index = window_end
            center_index = i
    
    return max_distance, max_time, start_index, end_index, center_index

# Test with normal distribution
np.random.seed(42)
sampling_rate = 10
duration_minutes = 3
total_samples = duration_minutes * 60 * sampling_rate

# Create normal distribution with peak at 8 m/s
mu = 8.0
sigma = 1.0
velocity_data = np.random.normal(mu, sigma, total_samples)
velocity_data = np.maximum(velocity_data, 0)  # Ensure non-negative velocities

# Test parameters
epoch_duration = 1.0  # 1 minute

print("=== MATLAB-Equivalent Rolling WCS Test ===")
print(f"Data length: {len(velocity_data)} samples ({len(velocity_data)/sampling_rate/60:.1f} minutes)")
print(f"Velocity range: {velocity_data.min():.2f} - {velocity_data.max():.2f} m/s")
print(f"Mean velocity: {velocity_data.mean():.2f} m/s")
print()

# Calculate using MATLAB-equivalent method
matlab_distance, matlab_time, matlab_start, matlab_end, matlab_center = matlab_equivalent_rolling_wcs(
    velocity_data, epoch_duration, sampling_rate
)

# Calculate using current method
current_distance, current_time, current_start, current_end, current_center = current_rolling_wcs(
    velocity_data, epoch_duration, sampling_rate
)

print("Results Comparison:")
print(f"{'Method':<20} {'Distance (m)':<12} {'Time (s)':<10} {'Start':<8} {'End':<8} {'Center':<8}")
print("-" * 70)
print(f"{'MATLAB-equivalent':<20} {matlab_distance:<12.2f} {matlab_time:<10.2f} {matlab_start:<8} {matlab_end:<8} {matlab_center:<8}")
print(f"{'Current':<20} {current_distance:<12.2f} {current_time:<10.2f} {current_start:<8} {current_end:<8} {current_center:<8}")
print()

# Plot results
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# Plot 1: Velocity data with windows
ax1.plot(velocity_data, 'b-', alpha=0.7, label='Velocity')
ax1.axvspan(matlab_start, matlab_end, alpha=0.3, color='red', label=f'MATLAB Window (Distance: {matlab_distance:.2f}m)')
ax1.axvspan(current_start, current_end, alpha=0.3, color='green', label=f'Current Window (Distance: {current_distance:.2f}m)')
ax1.axvline(matlab_center, color='red', linestyle='--', alpha=0.8, label='MATLAB Center')
ax1.axvline(current_center, color='green', linestyle='--', alpha=0.8, label='Current Center')
ax1.set_xlabel('Sample Index')
ax1.set_ylabel('Velocity (m/s)')
ax1.set_title('Velocity Data with WCS Windows')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Moving sums comparison
# Calculate moving sums for both methods
matlab_sums = []
current_sums = []

window_size = int(epoch_duration * 60 * sampling_rate)
dt = window_size // 2

for i in range(len(velocity_data)):
    # MATLAB method
    start_idx = max(0, i - dt)
    end_idx = min(len(velocity_data), i + dt + (1 if window_size % 2 == 1 else 0))
    matlab_sum = np.sum(velocity_data[start_idx:end_idx])
    matlab_sums.append(matlab_sum)
    
    # Current method (only for valid center points)
    if dt <= i < len(velocity_data) - dt:
        window_start = i - dt
        window_end = i + dt + (1 if window_size % 2 == 1 else 0)
        current_sum = np.sum(velocity_data[window_start:window_end])
    else:
        current_sum = 0
    current_sums.append(current_sum)

ax2.plot(matlab_sums, 'r-', label='MATLAB Moving Sum', alpha=0.8)
ax2.plot(current_sums, 'g-', label='Current Moving Sum', alpha=0.8)
ax2.axvline(matlab_center, color='red', linestyle='--', alpha=0.8, label='MATLAB Max')
ax2.axvline(current_center, color='green', linestyle='--', alpha=0.8, label='Current Max')
ax2.set_xlabel('Sample Index')
ax2.set_ylabel('Window Sum (m/s)')
ax2.set_title('Moving Window Sums')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("Analysis:")
print(f"MATLAB method found maximum at center index {matlab_center}")
print(f"Current method found maximum at center index {current_center}")
print(f"Distance difference: {abs(matlab_distance - current_distance):.2f} m")
print(f"Agreement: {'Yes' if matlab_distance == current_distance else 'No'}") 