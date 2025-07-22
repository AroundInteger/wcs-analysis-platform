#!/usr/bin/env python3
"""
Test Advanced Dashboard Visualizations

This script demonstrates the new multi-panel dashboard visualizations
using the Denmark data test results.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from advanced_visualizations import (
    create_comprehensive_dashboard,
    create_individual_player_dashboard,
    create_performance_insights_dashboard,
    save_dashboard_visualizations
)

def load_denmark_results():
    """Load the Denmark test results from CSV"""
    
    csv_file = Path("OUTPUT/denmark_test_20250721_21-07-44/WCS_Analysis_Results_20250721_210744.csv")
    
    if not csv_file.exists():
        print(f"❌ CSV file not found: {csv_file}")
        return None
    
    print(f"📁 Loading results from: {csv_file}")
    
    # Load CSV data
    df = pd.read_csv(csv_file)
    print(f"✅ Loaded {len(df)} data rows")
    
    return df

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

def main():
    """Main function to test advanced dashboard visualizations"""
    
    print("🎯 Testing Advanced Dashboard Visualizations")
    print("=" * 60)
    
    # Step 1: Load data
    print("\n📁 Step 1: Loading Denmark test results...")
    
    df = load_denmark_results()
    if df is None:
        return
    
    # Step 2: Create results structure
    print("\n🔄 Step 2: Converting data structure...")
    
    all_results = create_results_structure(df)
    print(f"✅ Created results structure for {len(all_results)} players")
    
    # Step 3: Create output directory
    output_dir = Path("OUTPUT/denmark_test_20250721_21-07-44")
    
    # Step 4: Test individual dashboard functions
    print("\n📊 Step 3: Testing individual dashboard functions...")
    
    # Test 1: Comprehensive Dashboard
    print("   Creating comprehensive dashboard...")
    try:
        fig1 = create_comprehensive_dashboard(all_results, "Denmark WCS Analysis - Comprehensive Dashboard")
        if fig1:
            file1 = output_dir / "denmark_comprehensive_dashboard.html"
            fig1.write_html(str(file1))
            print(f"   ✅ Saved: {file1}")
        else:
            print("   ❌ Failed to create comprehensive dashboard")
    except Exception as e:
        print(f"   ❌ Error creating comprehensive dashboard: {str(e)}")
    
    # Test 2: Individual Player Dashboard
    print("   Creating individual player dashboard...")
    try:
        fig2 = create_individual_player_dashboard(all_results, max_players=5)
        if fig2:
            file2 = output_dir / "denmark_individual_players.html"
            fig2.write_html(str(file2))
            print(f"   ✅ Saved: {file2}")
        else:
            print("   ❌ Failed to create individual player dashboard")
    except Exception as e:
        print(f"   ❌ Error creating individual player dashboard: {str(e)}")
    
    # Test 3: Performance Insights Dashboard
    print("   Creating performance insights dashboard...")
    try:
        fig3 = create_performance_insights_dashboard(all_results)
        if fig3:
            file3 = output_dir / "denmark_performance_insights.html"
            fig3.write_html(str(file3))
            print(f"   ✅ Saved: {file3}")
        else:
            print("   ❌ Failed to create performance insights dashboard")
    except Exception as e:
        print(f"   ❌ Error creating performance insights dashboard: {str(e)}")
    
    # Step 5: Test batch save function
    print("\n💾 Step 4: Testing batch save function...")
    
    try:
        saved_files = save_dashboard_visualizations(
            all_results, 
            str(output_dir), 
            "Denmark_Advanced"
        )
        
        print(f"✅ Batch save completed. Saved {len(saved_files)} files:")
        for viz_type, file_path in saved_files.items():
            print(f"   • {viz_type}: {file_path}")
            
    except Exception as e:
        print(f"❌ Batch save failed: {str(e)}")
    
    # Step 6: Create summary
    print("\n📋 Step 5: Creating dashboard summary...")
    
    summary_file = output_dir / "advanced_dashboards_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("🎯 Advanced Dashboard Visualizations Summary\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Players analyzed: {len(all_results)}\n")
        f.write(f"Dashboard types: 3\n\n")
        
        f.write("📊 Dashboard Types:\n")
        f.write("   1. Comprehensive Dashboard (4-panel)\n")
        f.write("      • WCS Distance vs Mean Velocity by Epoch\n")
        f.write("      • Correlation Matrix\n")
        f.write("      • Epoch Efficiency (Distance per Second)\n")
        f.write("      • WCS Distance Distribution by Epoch\n\n")
        
        f.write("   2. Individual Player Dashboard\n")
        f.write("      • Velocity profiles for top 5 players\n")
        f.write("      • Epoch comparison charts\n")
        f.write("      • Individual performance analysis\n\n")
        
        f.write("   3. Performance Insights Dashboard\n")
        f.write("      • Player performance ranking\n")
        f.write("      • Velocity vs WCS correlation\n")
        f.write("      • Performance consistency analysis\n")
        f.write("      • Top performers by epoch duration\n\n")
        
        f.write("🎯 Key Benefits:\n")
        f.write("   • Comprehensive overview in single view\n")
        f.write("   • Professional dashboard presentation\n")
        f.write("   • Multiple insights simultaneously\n")
        f.write("   • Interactive exploration capabilities\n")
        f.write("   • Perfect for reports and presentations\n")
    
    print(f"✅ Summary saved: {summary_file}")
    
    # Step 7: Final report
    print("\n🎉 Advanced Dashboard Testing Complete!")
    print("=" * 60)
    print(f"✅ Tested 3 dashboard types")
    print(f"✅ Created comprehensive multi-panel visualizations")
    print(f"📁 Output directory: {output_dir}")
    print(f"📊 Players analyzed: {len(all_results)}")
    
    # List all files in output directory
    print(f"\n📋 All files in output directory:")
    dashboard_files = [f for f in output_dir.iterdir() if f.is_file() and 'dashboard' in f.name.lower()]
    for file_path in dashboard_files:
        size_kb = file_path.stat().st_size / 1024
        print(f"   • {file_path.name} ({size_kb:.1f} KB)")
    
    print(f"\n🚀 Next Steps:")
    print(f"   • Integrate dashboards into main Streamlit app")
    print(f"   • Add dashboard selection options for users")
    print(f"   • Create dashboard export functionality")
    print(f"   • Add real-time velocity profile data")

if __name__ == "__main__":
    main() 