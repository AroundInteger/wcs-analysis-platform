#!/usr/bin/env python3
"""
Create additional sample files for advanced analytics demo
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def create_sample_gps_file(filename, player_name, duration_minutes=90, sampling_rate=10):
    """Create a sample GPS data file"""
    
    # Calculate number of records
    total_seconds = duration_minutes * 60
    num_records = total_seconds // sampling_rate
    
    # Create time series
    start_time = datetime.now()
    timestamps = [start_time + timedelta(seconds=i*sampling_rate) for i in range(num_records)]
    
    # Create realistic GPS data
    np.random.seed(hash(player_name) % 1000)  # Consistent but different for each player
    
    # Base coordinates (somewhere in the UK)
    base_lat = 51.5074 + np.random.uniform(-0.1, 0.1)
    base_lon = -0.1278 + np.random.uniform(-0.1, 0.1)
    
    # Generate movement patterns
    lat_drift = np.cumsum(np.random.normal(0, 0.0001, num_records))
    lon_drift = np.cumsum(np.random.normal(0, 0.0001, num_records))
    
    # Add some periodic movement (like a football match)
    match_pattern = np.sin(np.linspace(0, 4*np.pi, num_records)) * 0.0005
    
    latitudes = base_lat + lat_drift + match_pattern
    longitudes = base_lon + lon_drift + match_pattern
    
    # Calculate velocities
    distances = np.sqrt(np.diff(latitudes)**2 + np.diff(longitudes)**2) * 111000  # Convert to meters
    velocities = np.concatenate([[0], distances]) / sampling_rate
    
    # Add some high-intensity periods
    high_intensity_periods = np.random.choice([0, 1], num_records, p=[0.7, 0.3])
    velocities = velocities * (1 + high_intensity_periods * np.random.uniform(0.5, 2.0, num_records))
    
    # Create DataFrame
    data = {
        'timestamp': timestamps,
        'latitude': latitudes,
        'longitude': longitudes,
        'velocity': velocities,
        'player_name': player_name
    }
    
    df = pd.DataFrame(data)
    
    # Save to file
    output_path = f"data/test_data/{filename}"
    df.to_csv(output_path, index=False)
    
    print(f"✅ Created {filename} with {len(df)} records for {player_name}")
    return output_path

def main():
    """Create additional sample files"""
    
    print("🔧 Creating additional sample files for advanced analytics demo...")
    
    # Ensure test_data directory exists
    os.makedirs("data/test_data", exist_ok=True)
    
    # Create additional sample files
    sample_files = [
        ("Sample_Player_11.csv", "Player_11"),
        ("Sample_Player_12.csv", "Player_12"),
        ("Sample_Player_13.csv", "Player_13"),
        ("Sample_Player_14.csv", "Player_14"),
        ("Sample_Player_15.csv", "Player_15"),
    ]
    
    created_files = []
    for filename, player_name in sample_files:
        file_path = create_sample_gps_file(filename, player_name)
        created_files.append(file_path)
    
    print(f"\n✅ Created {len(created_files)} additional sample files")
    print("📁 Files created:")
    for file_path in created_files:
        print(f"   • {os.path.basename(file_path)}")
    
    print(f"\n🎯 Total files now available: {len(os.listdir('data/test_data')) - 1}")  # -1 for .DS_Store
    print("🚀 Ready for advanced analytics demo with ≥10 files!")

if __name__ == "__main__":
    main() 