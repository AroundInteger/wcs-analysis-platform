#!/usr/bin/env python3
"""
Create Test Data for Advanced Analytics
This script creates sample data files that work with the WCS analysis system
to test the advanced analytics functionality.
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path

def create_test_data_files():
    """Create test data files for advanced analytics testing"""
    
    # Create test data directory if it doesn't exist
    test_dir = Path("test_data_advanced_analytics")
    test_dir.mkdir(exist_ok=True)
    
    print(f"📁 Creating test data in: {test_dir}")
    
    # Create multiple test files with different player data
    players = [
        {"name": "Player_A", "position": "Forward", "avg_speed": 3.5, "max_speed": 8.0},
        {"name": "Player_B", "position": "Midfielder", "avg_speed": 4.2, "max_speed": 9.5},
        {"name": "Player_C", "position": "Defender", "avg_speed": 3.8, "max_speed": 7.8},
        {"name": "Player_D", "position": "Forward", "avg_speed": 4.0, "max_speed": 8.5},
        {"name": "Player_E", "position": "Midfielder", "avg_speed": 3.9, "max_speed": 8.2},
    ]
    
    created_files = []
    
    for i, player in enumerate(players):
        print(f"  📄 Creating data for {player['name']}...")
        
        # Generate realistic GPS data
        duration_seconds = 3600  # 1 hour of data
        sampling_rate = 10  # 10 Hz
        n_samples = duration_seconds * sampling_rate
        
        # Create timestamp array
        timestamps = np.arange(0, duration_seconds, 1/sampling_rate)
        
        # Generate realistic velocity data with WCS events
        velocities = []
        for t in timestamps:
            # Base velocity with some variation
            base_vel = player['avg_speed'] + np.random.normal(0, 0.5)
            
            # Add WCS events (high-speed periods)
            wcs_probability = 0.02  # 2% chance of WCS event
            if np.random.random() < wcs_probability:
                # WCS event: high speed for 5-15 seconds
                wcs_duration = np.random.randint(5, 15)
                wcs_speed = np.random.uniform(player['max_speed'] - 1, player['max_speed'])
                
                # Apply WCS speed for the duration
                for _ in range(wcs_duration):
                    velocities.append(wcs_speed + np.random.normal(0, 0.3))
            else:
                velocities.append(max(0, base_vel))
        
        # Ensure we have the right number of samples
        velocities = velocities[:n_samples]
        if len(velocities) < n_samples:
            # Pad with base velocity if needed
            while len(velocities) < n_samples:
                velocities.append(player['avg_speed'] + np.random.normal(0, 0.5))
        
        # Generate GPS coordinates (simple movement pattern)
        lat_start = 51.5074 + np.random.normal(0, 0.01)  # London area
        lon_start = -0.1278 + np.random.normal(0, 0.01)
        
        latitudes = [lat_start]
        longitudes = [lon_start]
        
        for vel in velocities[1:]:
            # Simple movement: move in random direction based on velocity
            angle = np.random.uniform(0, 2 * np.pi)
            distance = vel * (1/sampling_rate)  # distance = velocity * time
            
            # Convert to lat/lon change (approximate)
            lat_change = distance * np.cos(angle) / 111000  # rough conversion
            lon_change = distance * np.sin(angle) / (111000 * np.cos(np.radians(latitudes[-1])))
            
            latitudes.append(latitudes[-1] + lat_change)
            longitudes.append(longitudes[-1] + lon_change)
        
        # Create DataFrame with correct column names
        df = pd.DataFrame({
            'Timestamp': timestamps,
            'Velocity': velocities,  # Use 'Velocity' column name
            'Latitude': latitudes,
            'Longitude': longitudes
        })
        
        # Create filename
        filename = f"{player['position']}_{player['name']}_TestMatch(MD1).csv"
        filepath = test_dir / filename
        
        # Save file
        df.to_csv(filepath, index=False)
        created_files.append(filepath)
        
        print(f"    ✅ Created {filename} with {len(df)} records")
        print(f"    📊 Velocity range: {df['Velocity'].min():.2f} - {df['Velocity'].max():.2f} m/s")
        print(f"    🏃 WCS events (speed > 5.5 m/s): {(df['Velocity'] > 5.5).sum()}")
    
    print(f"\n🎉 Created {len(created_files)} test files")
    print(f"📁 Files saved in: {test_dir}")
    
    # Create a summary file
    summary_file = test_dir / "README.md"
    with open(summary_file, 'w') as f:
        f.write("# Test Data for Advanced Analytics\n\n")
        f.write("This directory contains test data files for testing the WCS Analysis Platform's advanced analytics features.\n\n")
        f.write("## Files Created:\n\n")
        for filepath in created_files:
            f.write(f"- `{filepath.name}`\n")
        f.write("\n## Usage:\n\n")
        f.write("1. Upload these files to the WCS Analysis Platform\n")
        f.write("2. Process them in batch mode\n")
        f.write("3. Navigate to the 'Advanced Analytics' tab\n")
        f.write("4. Test cohort analysis and visualizations\n\n")
        f.write("## Data Characteristics:\n\n")
        f.write("- 5 different players with varying performance profiles\n")
        f.write("- 1 hour of data per player at 10 Hz sampling rate\n")
        f.write("- Realistic WCS events embedded in the data\n")
        f.write("- Proper column names: Timestamp, Velocity, Latitude, Longitude\n")
    
    print(f"📄 Created summary: {summary_file}")
    
    return created_files

if __name__ == "__main__":
    print("🚀 Creating Test Data for Advanced Analytics")
    print("=" * 50)
    
    files = create_test_data_files()
    
    print("\n✅ Test data creation completed!")
    print("\n📋 Next Steps:")
    print("1. Open the WCS Analysis Platform in your browser")
    print("2. Upload the files from the 'test_data_advanced_analytics' folder")
    print("3. Process them in batch mode")
    print("4. Navigate to the 'Advanced Analytics' tab to test the functionality")
    print(f"\n🌐 Platform URL: http://localhost:8501") 