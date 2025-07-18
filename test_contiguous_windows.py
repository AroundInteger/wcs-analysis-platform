import numpy as np
import matplotlib.pyplot as plt

def show_contiguous_windows(velocity_data, epoch_duration, sampling_rate=10):
    """
    Show all possible contiguous windows for a given epoch duration
    """
    # Convert epoch duration to samples
    epoch_samples = int(epoch_duration * 60 * sampling_rate)
    
    print(f"Dataset length: {len(velocity_data)} samples")
    print(f"Epoch duration: {epoch_duration} minutes = {epoch_samples} samples")
    print(f"Number of possible contiguous windows: {len(velocity_data) - epoch_samples + 1}")
    print()
    
    # Calculate distance for each possible window
    window_results = []
    
    for i in range(len(velocity_data) - epoch_samples + 1):
        window_data = velocity_data[i:i + epoch_samples]
        time_per_sample = 1.0 / sampling_rate
        window_distance = np.sum(window_data * time_per_sample)
        window_avg_velocity = np.mean(window_data)
        
        window_results.append({
            'start_index': i,
            'end_index': i + epoch_samples,
            'start_time': i / sampling_rate,
            'end_time': (i + epoch_samples) / sampling_rate,
            'distance': window_distance,
            'avg_velocity': window_avg_velocity
        })
    
    # Find the best window
    best_window = max(window_results, key=lambda x: x['distance'])
    
    # Show only the 3 main windows (every 600 samples)
    main_windows = []
    for i in range(0, len(velocity_data) - epoch_samples + 1, epoch_samples):
        if i + epoch_samples <= len(velocity_data):
            main_windows.append(window_results[i])
    
    print("Main 1-minute windows (non-overlapping):")
    for i, window in enumerate(main_windows):
        print(f"Window {i+1}: samples {window['start_index']}-{window['end_index']-1} (t={window['start_time']:.1f}-{window['end_time']:.1f}s)")
        print(f"  Distance: {window['distance']:.4f} m")
        print(f"  Avg velocity: {window['avg_velocity']:.4f} m/s")
        print()
    
    print(f"Best contiguous window (among all possible):")
    print(f"  Window starting at sample {best_window['start_index']}: samples {best_window['start_index']}-{best_window['end_index']-1}")
    print(f"  Time: {best_window['start_time']:.1f}-{best_window['end_time']:.1f} seconds")
    print(f"  Distance: {best_window['distance']:.4f} m")
    print(f"  Avg velocity: {best_window['avg_velocity']:.4f} m/s")
    
    return window_results, best_window, main_windows

# Create the simple 1-peak velocity curve
sigma = 10
mu = 9 * sigma  # mu = 90
sampling_rate = 10
duration_minutes = 3
total_samples = duration_minutes * 60 * sampling_rate  # 1800 samples

# Create time array
t = np.linspace(0, sigma * 18, total_samples)

# Create normal distribution
velocity_data = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((t - mu) / sigma) ** 2)

# Scale to get reasonable velocity values (peak around 8 m/s)
peak_velocity = 8.0
velocity_data = velocity_data * (peak_velocity / np.max(velocity_data))

print("=== Contiguous Windows Analysis ===")
print(f"Parameters: sigma={sigma}, mu={mu}, peak_velocity={peak_velocity} m/s")
print(f"Peak location: t = {t[np.argmax(velocity_data)]:.1f} seconds")
print()

# Analyze contiguous windows
epoch_duration = 1.0  # 1 minute
window_results, best_window, main_windows = show_contiguous_windows(velocity_data, epoch_duration, sampling_rate)

# Plot the results
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Plot 1: Velocity data with main windows
ax1.plot(t, velocity_data, 'b-', alpha=0.7, label='Velocity', linewidth=1)

# Color each main window differently
colors = ['red', 'green', 'purple']
for i, window in enumerate(main_windows):
    alpha = 0.3 if window == best_window else 0.1
    ax1.axvspan(window['start_time'], window['end_time'], alpha=alpha, 
               color=colors[i], label=f"Window {i+1} ({window['distance']:.2f}m)")

# Highlight the best window among all possible
ax1.axvspan(best_window['start_time'], best_window['end_time'], alpha=0.2, 
           color='orange', label=f"Best Window ({best_window['distance']:.2f}m)")

ax1.axvline(t[np.argmax(velocity_data)], color='orange', linestyle=':', alpha=0.7, linewidth=2, label='Peak Location')
ax1.set_xlabel('Time (seconds)')
ax1.set_ylabel('Velocity (m/s)')
ax1.set_title('Main 1-Minute Windows vs Best Contiguous Window')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Distance for main windows
window_numbers = list(range(1, len(main_windows) + 1))
distances = [w['distance'] for w in main_windows]

ax2.bar(window_numbers, distances, color=colors[:len(main_windows)], alpha=0.7)
ax2.set_xlabel('Window Number')
ax2.set_ylabel('Distance (m)')
ax2.set_title('Distance Covered by Main 1-Minute Windows')
ax2.grid(True, alpha=0.3)

# Add value labels on bars
for i, distance in enumerate(distances):
    ax2.text(i+1, distance + 0.5, f'{distance:.2f}m', ha='center', va='bottom')

plt.tight_layout()
plt.show()

print("\nSummary:")
print(f"There are exactly {len(main_windows)} main 1-minute windows in this 3-minute dataset.")
print(f"Each main window represents a different 60-second period with no overlap.")
print(f"The best window among all possible positions is at sample {best_window['start_index']} with {best_window['distance']:.4f} m distance.")
print(f"Among the main windows, Window {main_windows.index(max(main_windows, key=lambda x: x['distance']))+1} has the highest distance.") 