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

def contiguous_wcs(velocity_data, epoch_duration, sampling_rate=10):
    """
    Contiguous WCS calculation - finds best continuous period of exact duration
    """
    # Convert epoch duration to samples
    epoch_samples = int(epoch_duration * 60 * sampling_rate)
    
    if len(velocity_data) < epoch_samples:
        # If data is shorter than epoch, use all available data
        epoch_samples = len(velocity_data)
    
    # Calculate cumulative distance for each window
    max_distance = 0
    max_time = 0
    start_index = 0
    end_index = 0
    
    # Slide window through data to find best contiguous period
    for i in range(len(velocity_data) - epoch_samples + 1):
        window_data = velocity_data[i:i + epoch_samples]
        
        # Calculate distance for this window (velocity * time)
        # Each sample represents 1/sampling_rate seconds
        time_per_sample = 1.0 / sampling_rate
        window_distance = np.sum(window_data * time_per_sample)
        
        # Calculate time within window
        window_time = len(window_data) * time_per_sample
        
        # Update maximum if this window has higher distance
        if window_distance > max_distance:
            max_distance = window_distance
            max_time = window_time
            start_index = i
            end_index = i + epoch_samples
    
    return max_distance, max_time, start_index, end_index

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

print("=== Normal Distribution WCS Comparison Test ===")
print(f"Data length: {len(velocity_data)} samples ({len(velocity_data)/sampling_rate/60:.1f} minutes)")
print(f"Velocity range: {velocity_data.min():.2f} - {velocity_data.max():.2f} m/s")
print(f"Mean velocity: {velocity_data.mean():.2f} m/s")
print(f"Peak velocity: {velocity_data.max():.2f} m/s")
print()

# Calculate using MATLAB-equivalent rolling method
rolling_distance, rolling_time, rolling_start, rolling_end, rolling_center = matlab_equivalent_rolling_wcs(
    velocity_data, epoch_duration, sampling_rate
)

# Calculate using contiguous method
contiguous_distance, contiguous_time, contiguous_start, contiguous_end = contiguous_wcs(
    velocity_data, epoch_duration, sampling_rate
)

print("Results Comparison:")
print(f"{'Method':<20} {'Distance (m)':<12} {'Time (s)':<10} {'Start':<8} {'End':<8} {'Center':<8}")
print("-" * 70)
print(f"{'Rolling (MATLAB)':<20} {rolling_distance:<12.2f} {rolling_time:<10.2f} {rolling_start:<8} {rolling_end:<8} {rolling_center:<8}")
print(f"{'Contiguous':<20} {contiguous_distance:<12.2f} {contiguous_time:<10.2f} {contiguous_start:<8} {contiguous_end:<8} {'N/A':<8}")
print()

# Plot results
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Plot 1: Velocity data with windows
ax1.plot(velocity_data, 'b-', alpha=0.7, label='Velocity', linewidth=1)
ax1.axvspan(rolling_start, rolling_end, alpha=0.3, color='red', 
           label=f'Rolling Window (Distance: {rolling_distance:.2f}m)')
ax1.axvspan(contiguous_start, contiguous_end, alpha=0.3, color='green', 
           label=f'Contiguous Window (Distance: {contiguous_distance:.2f}m)')
ax1.axvline(rolling_center, color='red', linestyle='--', alpha=0.8, linewidth=2, label='Rolling Center')
ax1.axhline(8.0, color='orange', linestyle=':', alpha=0.7, label='Peak Velocity (8 m/s)')
ax1.set_xlabel('Sample Index')
ax1.set_ylabel('Velocity (m/s)')
ax1.set_title('Normal Distribution Velocity Data with WCS Windows')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Moving sums comparison
# Calculate moving sums for rolling method
rolling_sums = []
contiguous_sums = []

window_size = int(epoch_duration * 60 * sampling_rate)
dt = window_size // 2

for i in range(len(velocity_data)):
    # Rolling method (MATLAB equivalent)
    start_idx = max(0, i - dt)
    end_idx = min(len(velocity_data), i + dt + (1 if window_size % 2 == 1 else 0))
    rolling_sum = np.sum(velocity_data[start_idx:end_idx])
    rolling_sums.append(rolling_sum)
    
    # Contiguous method (only for valid windows)
    if i <= len(velocity_data) - window_size:
        contiguous_sum = np.sum(velocity_data[i:i + window_size])
    else:
        contiguous_sum = 0
    contiguous_sums.append(contiguous_sum)

ax2.plot(rolling_sums, 'r-', label='Rolling Moving Sum', alpha=0.8, linewidth=1)
ax2.plot(contiguous_sums, 'g-', label='Contiguous Moving Sum', alpha=0.8, linewidth=1)
ax2.axvline(rolling_center, color='red', linestyle='--', alpha=0.8, linewidth=2, label='Rolling Max')
ax2.axvline(contiguous_start + dt, color='green', linestyle='--', alpha=0.8, linewidth=2, label='Contiguous Max')
ax2.set_xlabel('Sample Index')
ax2.set_ylabel('Window Sum (m/s)')
ax2.set_title('Moving Window Sums Comparison')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("Analysis:")
print(f"Rolling method found maximum at center index {rolling_center}")
print(f"Contiguous method found maximum starting at index {contiguous_start}")
print(f"Distance difference: {abs(rolling_distance - contiguous_distance):.2f} m")
print(f"Agreement: {'Yes' if abs(rolling_distance - contiguous_distance) < 0.01 else 'No'}")

# Additional analysis
print(f"\nDetailed Analysis:")
print(f"Rolling window center velocity: {velocity_data[rolling_center]:.2f} m/s")
print(f"Rolling window average velocity: {np.mean(velocity_data[rolling_start:rolling_end]):.2f} m/s")
print(f"Contiguous window average velocity: {np.mean(velocity_data[contiguous_start:contiguous_end]):.2f} m/s")

# Check if windows overlap
overlap_start = max(rolling_start, contiguous_start)
overlap_end = min(rolling_end, contiguous_end)
if overlap_end > overlap_start:
    overlap_samples = overlap_end - overlap_start
    print(f"Window overlap: {overlap_samples} samples ({overlap_samples/sampling_rate:.1f} seconds)")
else:
    print("No window overlap")

# Show the actual velocity values at key points
print(f"\nKey Velocity Values:")
print(f"Rolling center (index {rolling_center}): {velocity_data[rolling_center]:.2f} m/s")
print(f"Contiguous start (index {contiguous_start}): {velocity_data[contiguous_start]:.2f} m/s")
print(f"Contiguous end (index {contiguous_end-1}): {velocity_data[contiguous_end-1]:.2f} m/s") 