#!/usr/bin/env python3
"""
Simple Denmark Data Visualizations

Create basic visualizations for Denmark data test results.
"""

import sys
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from pathlib import Path

def load_denmark_data():
    """Load Denmark test results"""
    csv_file = Path("OUTPUT/denmark_test_20250721_21-07-44/WCS_Analysis_Results_20250721_210744.csv")
    
    if not csv_file.exists():
        print(f"❌ CSV file not found: {csv_file}")
        return None
    
    df = pd.read_csv(csv_file)
    print(f"✅ Loaded {len(df)} data rows")
    return df

def create_wcs_distance_comparison(df):
    """Create WCS distance comparison by player and epoch"""
    
    # Filter for Default Threshold only
    df_filtered = df[df['Threshold_Type'] == 'Default Threshold']
    
    fig = go.Figure()
    
    # Get unique epochs and players
    epochs = sorted(df_filtered['Epoch_Duration_Minutes'].unique())
    players = df_filtered['Player_Name'].unique()
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
    
    for i, epoch in enumerate(epochs):
        epoch_data = df_filtered[df_filtered['Epoch_Duration_Minutes'] == epoch]
        
        fig.add_trace(go.Bar(
            x=epoch_data['Player_Name'],
            y=epoch_data['WCS_Distance_m'],
            name=f'{epoch}min',
            marker_color=colors[i % len(colors)],
            hovertemplate='Player: %{x}<br>Distance: %{y:.1f}m<br>Epoch: %{fullData.name}<extra></extra>'
        ))
    
    fig.update_layout(
        title="WCS Distance Comparison by Player and Epoch Duration",
        xaxis_title="Player",
        yaxis_title="WCS Distance (m)",
        barmode='group',
        height=600,
        showlegend=True
    )
    
    return fig

def create_velocity_analysis(df):
    """Create velocity analysis visualization"""
    
    # Get unique players and their velocity stats
    players = df['Player_Name'].unique()
    
    fig = go.Figure()
    
    # Add mean velocity bars
    mean_velocities = []
    for player in players:
        player_data = df[df['Player_Name'] == player].iloc[0]  # Take first row for stats
        mean_velocities.append(player_data['File_Mean_Velocity_m_s'])
    
    fig.add_trace(go.Bar(
        x=players,
        y=mean_velocities,
        name='Mean Velocity',
        marker_color='#4ECDC4',
        hovertemplate='Player: %{x}<br>Mean Velocity: %{y:.2f} m/s<extra></extra>'
    ))
    
    # Add max velocity line
    max_velocities = []
    for player in players:
        player_data = df[df['Player_Name'] == player].iloc[0]
        max_velocities.append(player_data['File_Max_Velocity_m_s'])
    
    fig.add_trace(go.Scatter(
        x=players,
        y=max_velocities,
        mode='lines+markers',
        name='Max Velocity',
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=8),
        hovertemplate='Player: %{x}<br>Max Velocity: %{y:.2f} m/s<extra></extra>'
    ))
    
    fig.update_layout(
        title="Player Velocity Analysis",
        xaxis_title="Player",
        yaxis_title="Velocity (m/s)",
        height=500,
        showlegend=True
    )
    
    return fig

def create_epoch_performance_heatmap(df):
    """Create performance heatmap by epoch duration"""
    
    # Filter for Default Threshold
    df_filtered = df[df['Threshold_Type'] == 'Default Threshold']
    
    # Pivot data for heatmap
    pivot_data = df_filtered.pivot_table(
        values='WCS_Distance_m',
        index='Player_Name',
        columns='Epoch_Duration_Minutes',
        aggfunc='mean'
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='Viridis',
        hovertemplate='Player: %{y}<br>Epoch: %{x}min<br>Distance: %{z:.1f}m<extra></extra>'
    ))
    
    fig.update_layout(
        title="WCS Performance Heatmap by Player and Epoch Duration",
        xaxis_title="Epoch Duration (minutes)",
        yaxis_title="Player",
        height=600
    )
    
    return fig

def create_performance_ranking(df):
    """Create performance ranking chart"""
    
    # Filter for 1-minute epoch, Default Threshold
    df_filtered = df[
        (df['Threshold_Type'] == 'Default Threshold') & 
        (df['Epoch_Duration_Minutes'] == 1.0)
    ]
    
    # Sort by WCS distance
    df_sorted = df_filtered.sort_values('WCS_Distance_m', ascending=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_sorted['WCS_Distance_m'],
        y=df_sorted['Player_Name'],
        orientation='h',
        marker_color='#45B7D1',
        hovertemplate='Player: %{y}<br>WCS Distance: %{x:.1f}m<extra></extra>'
    ))
    
    fig.update_layout(
        title="Player Performance Ranking (1-minute WCS Distance)",
        xaxis_title="WCS Distance (m)",
        yaxis_title="Player",
        height=600
    )
    
    return fig

def save_visualizations(visualizations, output_dir):
    """Save all visualizations"""
    
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
            
        except Exception as e:
            print(f"❌ Failed to save {viz_name}: {str(e)}")
    
    return saved_files

def main():
    """Main function"""
    
    print("🇩🇰 Creating Simple Denmark Data Visualizations")
    print("=" * 50)
    
    # Load data
    df = load_denmark_data()
    if df is None:
        return
    
    # Create output directory
    output_dir = Path("OUTPUT/denmark_test_20250721_21-07-44")
    
    # Create visualizations
    print("\n📈 Creating visualizations...")
    
    visualizations = {}
    
    # 1. WCS Distance Comparison
    print("   Creating WCS distance comparison...")
    fig1 = create_wcs_distance_comparison(df)
    visualizations['wcs_distance_comparison'] = fig1
    
    # 2. Velocity Analysis
    print("   Creating velocity analysis...")
    fig2 = create_velocity_analysis(df)
    visualizations['velocity_analysis'] = fig2
    
    # 3. Performance Heatmap
    print("   Creating performance heatmap...")
    fig3 = create_epoch_performance_heatmap(df)
    visualizations['performance_heatmap'] = fig3
    
    # 4. Performance Ranking
    print("   Creating performance ranking...")
    fig4 = create_performance_ranking(df)
    visualizations['performance_ranking'] = fig4
    
    print(f"✅ Created {len(visualizations)} visualizations")
    
    # Save visualizations
    saved_files = save_visualizations(visualizations, output_dir)
    
    # Create summary
    print("\n📋 Creating summary...")
    
    summary_file = output_dir / "denmark_visualizations_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("🇩🇰 Denmark Data Visualizations Summary\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Players analyzed: {len(df['Player_Name'].unique())}\n")
        f.write(f"Visualizations created: {len(visualizations)}\n\n")
        
        f.write("📊 Visualization Types:\n")
        for viz_name in visualizations.keys():
            f.write(f"   • {viz_name}\n")
        
        f.write(f"\n📁 Files saved: {len(saved_files)}\n")
        for filename in saved_files:
            f.write(f"   • {filename}\n")
    
    print(f"✅ Summary saved: {summary_file}")
    
    # Final report
    print("\n🎉 Visualization Creation Complete!")
    print("=" * 50)
    print(f"✅ Created {len(visualizations)} visualizations")
    print(f"✅ Saved {len(saved_files)} files")
    print(f"📁 Output directory: {output_dir}")
    
    # List all files
    print(f"\n📋 All files in output directory:")
    for file_path in output_dir.iterdir():
        if file_path.is_file():
            size_kb = file_path.stat().st_size / 1024
            print(f"   • {file_path.name} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    main() 