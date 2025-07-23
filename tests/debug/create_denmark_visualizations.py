#!/usr/bin/env python3
"""
Create Visualizations for Denmark Data Test Results

This script generates and saves all visualizations for the Denmark data analysis.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from batch_processing import create_combined_visualizations, create_combined_wcs_dataframe
from data_export import export_data_matlab_format

def load_denmark_results():
    """Load the Denmark test results from CSV"""
    
    # Find the most recent Denmark test output
    output_dir = Path("OUTPUT")
    denmark_dirs = [d for d in output_dir.iterdir() if d.is_dir() and "denmark_test" in d.name]
    
    if not denmark_dirs:
        print("❌ No Denmark test output directories found")
        return None
    
    # Get the most recent one
    latest_dir = max(denmark_dirs, key=lambda x: x.stat().st_mtime)
    csv_file = latest_dir / "WCS_Analysis_Results_20250721_210744.csv"
    
    if not csv_file.exists():
        print(f"❌ CSV file not found: {csv_file}")
        return None
    
    print(f"📁 Loading results from: {csv_file}")
    
    # Load CSV data
    df = pd.read_csv(csv_file)
    print(f"✅ Loaded {len(df)} data rows")
    
    return df, latest_dir

def create_results_structure(df):
    """Convert CSV data back to the results structure expected by visualization functions"""
    
    results = []
    
    # Group by file
    for file_name in df['File_Name'].unique():
        file_data = df[df['File_Name'] == file_name]
        
        # Create metadata
        metadata = {
            'player_name': file_data['Player_Name'].iloc[0],
            'file_name': file_name,
            'total_records': file_data['Total_Records'].iloc[0],
            'duration_minutes': file_data['Duration_Minutes'].iloc[0]
        }
        
        # Create WCS analysis structure
        wcs_analysis = []
        
        for epoch_duration in sorted(file_data['Epoch_Duration_Minutes'].unique()):
            epoch_data = file_data[file_data['Epoch_Duration_Minutes'] == epoch_duration]
            
            epoch_result = {
                'epoch_duration': epoch_duration,
                'thresholds': []
            }
            
            for _, row in epoch_data.iterrows():
                threshold_data = {
                    'threshold_name': row['Threshold_Type'],
                    'distance': row['WCS_Distance_m'],
                    'time_range': [row['Start_Time_s'], row['End_Time_s']],
                    'avg_velocity': row['Avg_Velocity_m_s'],
                    'max_velocity': row['File_Max_Velocity_m_s']
                }
                epoch_result['thresholds'].append(threshold_data)
            
            wcs_analysis.append(epoch_result)
        
        # Create velocity stats
        velocity_stats = {
            'mean': file_data['File_Mean_Velocity_m_s'].iloc[0],
            'max': file_data['File_Max_Velocity_m_s'].iloc[0],
            'min': file_data['File_Min_Velocity_m_s'].iloc[0],
            'std': file_data['File_Velocity_Std_m_s'].iloc[0]
        }
        
        # Create result structure
        result = {
            'metadata': metadata,
            'wcs_analysis': wcs_analysis,
            'velocity_stats': velocity_stats,
            'file_name': file_name
        }
        
        results.append(result)
    
    return results

def save_visualizations(visualizations, output_dir):
    """Save all visualizations to files"""
    
    print(f"\n📈 Saving visualizations to: {output_dir}")
    
    saved_files = []
    
    for viz_name, fig in visualizations.items():
        try:
            # Create filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"denmark_{viz_name}_{timestamp}.html"
            filepath = output_dir / filename
            
            # Save as HTML
            fig.write_html(str(filepath))
            saved_files.append(filename)
            print(f"✅ Saved: {filename}")
            
            # Also save as PNG if possible
            try:
                png_filename = f"denmark_{viz_name}_{timestamp}.png"
                png_filepath = output_dir / png_filename
                fig.write_image(str(png_filepath), width=1200, height=800)
                saved_files.append(png_filename)
                print(f"✅ Saved: {png_filename}")
            except Exception as e:
                print(f"⚠️  PNG save failed for {viz_name}: {str(e)}")
                
        except Exception as e:
            print(f"❌ Failed to save {viz_name}: {str(e)}")
    
    return saved_files

def main():
    """Main function to create and save Denmark visualizations"""
    
    print("🇩🇰 Creating Denmark Data Visualizations")
    print("=" * 50)
    
    # Step 1: Load results
    print("\n📁 Step 1: Loading Denmark test results...")
    
    result = load_denmark_results()
    if result is None:
        return
    
    df, output_dir = result
    
    # Step 2: Create results structure
    print("\n🔄 Step 2: Converting data structure...")
    
    all_results = create_results_structure(df)
    print(f"✅ Created results structure for {len(all_results)} players")
    
    # Step 3: Create visualizations
    print("\n📈 Step 3: Creating combined visualizations...")
    
    try:
        visualizations = create_combined_visualizations(all_results)
        
        if not visualizations:
            print("❌ No visualizations created")
            return
        
        print(f"✅ Created {len(visualizations)} visualizations:")
        for viz_name in visualizations.keys():
            print(f"   • {viz_name}")
            
    except Exception as e:
        print(f"❌ Visualization creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Save visualizations
    print("\n💾 Step 4: Saving visualizations...")
    
    saved_files = save_visualizations(visualizations, output_dir)
    
    # Step 5: Create summary
    print("\n📋 Step 5: Creating visualization summary...")
    
    summary_file = output_dir / "visualization_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("🇩🇰 Denmark Data Visualizations Summary\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Players analyzed: {len(all_results)}\n")
        f.write(f"Visualizations created: {len(visualizations)}\n\n")
        
        f.write("📊 Visualization Types:\n")
        for viz_name in visualizations.keys():
            f.write(f"   • {viz_name}\n")
        
        f.write(f"\n📁 Files saved: {len(saved_files)}\n")
        for filename in saved_files:
            f.write(f"   • {filename}\n")
    
    print(f"✅ Summary saved: {summary_file}")
    
    # Step 6: Final report
    print("\n🎉 Visualization Creation Complete!")
    print("=" * 50)
    print(f"✅ Created {len(visualizations)} visualizations")
    print(f"✅ Saved {len(saved_files)} files")
    print(f"📁 Output directory: {output_dir}")
    print(f"📊 Players analyzed: {len(all_results)}")
    
    # List all files in output directory
    print(f"\n📋 All files in output directory:")
    for file_path in output_dir.iterdir():
        if file_path.is_file():
            size_kb = file_path.stat().st_size / 1024
            print(f"   • {file_path.name} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    main() 