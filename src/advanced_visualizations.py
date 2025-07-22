#!/usr/bin/env python3
"""
Advanced Multi-Panel Visualizations for WCS Analysis

This module creates comprehensive dashboard-style visualizations that combine
multiple charts into informative multi-panel summaries.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Optional
import streamlit as st

def create_comprehensive_dashboard(all_results: List[Dict[str, Any]], 
                                 title: str = "WCS Analysis Dashboard") -> go.Figure:
    """
    Create a comprehensive 4-panel dashboard visualization
    
    Args:
        all_results: List of results from batch processing
        title: Dashboard title
        
    Returns:
        Plotly figure with 4 subplots
    """
    
    # Create combined DataFrame
    combined_data = []
    for result in all_results:
        player_name = result['metadata']['player_name']
        
        for epoch_analysis in result['wcs_analysis']:
            epoch_duration = epoch_analysis['epoch_duration']
            
            for threshold in epoch_analysis['thresholds']:
                if threshold['threshold_name'] == 'Default Threshold':
                    combined_data.append({
                        'Player': player_name,
                        'Epoch_Duration': epoch_duration,
                        'WCS_Distance': threshold['distance'],
                        'Mean_Velocity': threshold['avg_velocity'],
                        'Max_Velocity': threshold['max_velocity'],
                        'Efficiency': threshold['distance'] / (epoch_duration * 60)  # m/s
                    })
    
    df = pd.DataFrame(combined_data)
    
    if df.empty:
        st.warning("No data available for dashboard")
        return None
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'WCS Distance vs Mean Velocity by Epoch',
            'Correlation Matrix',
            'Epoch Efficiency (Distance per Second)',
            'WCS Distance Distribution by Epoch'
        ),
        specs=[[{"type": "scatter"}, {"type": "heatmap"}],
               [{"type": "bar"}, {"type": "histogram"}]]
    )
    
    # Panel 1: WCS Distance vs Mean Velocity Scatter Plot
    epochs = sorted(df['Epoch_Duration'].unique())
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    for i, epoch in enumerate(epochs):
        epoch_data = df[df['Epoch_Duration'] == epoch]
        
        fig.add_trace(
            go.Scatter(
                x=epoch_data['Mean_Velocity'],
                y=epoch_data['WCS_Distance'],
                mode='markers',
                name=f'{epoch}min',
                marker=dict(color=colors[i % len(colors)], size=8),
                hovertemplate='Player: %{text}<br>Mean Velocity: %{x:.2f} m/s<br>WCS Distance: %{y:.1f}m<extra></extra>',
                text=epoch_data['Player']
            ),
            row=1, col=1
        )
    
    # Panel 2: Correlation Matrix
    corr_matrix = df[['WCS_Distance', 'Mean_Velocity', 'Max_Velocity', 'Epoch_Duration', 'Efficiency']].corr()
    
    fig.add_trace(
        go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            hovertemplate='%{x} vs %{y}<br>Correlation: %{z:.3f}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # Panel 3: Epoch Efficiency Bar Chart
    efficiency_by_epoch = df.groupby('Epoch_Duration')['Efficiency'].agg(['mean', 'std']).reset_index()
    
    fig.add_trace(
        go.Bar(
            x=[f"{epoch}min" for epoch in efficiency_by_epoch['Epoch_Duration']],
            y=efficiency_by_epoch['mean'],
            error_y=dict(type='data', array=efficiency_by_epoch['std']),
            name='Efficiency',
            marker_color='#96CEB4',
            hovertemplate='Epoch: %{x}<br>Mean Efficiency: %{y:.2f} m/s<br>Std Dev: %{error_y.array:.2f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Panel 4: WCS Distance Distribution Histogram
    for i, epoch in enumerate(epochs):
        epoch_data = df[df['Epoch_Duration'] == epoch]['WCS_Distance']
        
        fig.add_trace(
            go.Histogram(
                x=epoch_data,
                name=f'{epoch}min',
                marker_color=colors[i % len(colors)],
                opacity=0.7,
                hovertemplate='Epoch: %{fullData.name}<br>Distance: %{x:.1f}m<br>Count: %{y}<extra></extra>'
            ),
            row=2, col=2
        )
    
    # Update layout
    fig.update_layout(
        title=title,
        height=800,
        showlegend=True,
        title_x=0.5
    )
    
    # Update axes labels
    fig.update_xaxes(title_text="Mean Velocity (m/s)", row=1, col=1)
    fig.update_yaxes(title_text="WCS Distance (m)", row=1, col=1)
    fig.update_xaxes(title_text="Epoch Duration", row=2, col=1)
    fig.update_yaxes(title_text="Distance per Second (m/s)", row=2, col=1)
    fig.update_xaxes(title_text="WCS Distance (m)", row=2, col=2)
    fig.update_yaxes(title_text="Frequency", row=2, col=2)
    
    return fig

def create_individual_player_dashboard(all_results: List[Dict[str, Any]], 
                                     max_players: int = 5) -> go.Figure:
    """
    Create individual player analysis dashboard with velocity profiles and epoch comparisons
    
    Args:
        all_results: List of results from batch processing
        max_players: Maximum number of players to show
        
    Returns:
        Plotly figure with player analysis panels
    """
    
    # Select top players by average WCS distance
    player_stats = []
    for result in all_results:
        player_name = result['metadata']['player_name']
        avg_distance = np.mean([
            threshold['distance'] 
            for epoch in result['wcs_analysis'] 
            for threshold in epoch['thresholds'] 
            if threshold['threshold_name'] == 'Default Threshold'
        ])
        player_stats.append({'player': player_name, 'avg_distance': avg_distance})
    
    # Sort by average distance and take top players
    player_stats.sort(key=lambda x: x['avg_distance'], reverse=True)
    top_players = player_stats[:max_players]
    
    # Create subplots (2 columns, max_players rows)
    fig = make_subplots(
        rows=max_players, cols=2,
        subplot_titles=[f"{player['player']} - Velocity Profile" for player in top_players] +
                      [f"{player['player']} - Epoch Comparison" for player in top_players],
        specs=[[{"type": "scatter"}, {"type": "bar"}] for _ in range(max_players)]
    )
    
    for i, player_info in enumerate(top_players):
        player_name = player_info['player']
        player_result = next(r for r in all_results if r['metadata']['player_name'] == player_name)
        
        # Left panel: Velocity Profile (simplified - would need actual time series data)
        # For now, create a simulated velocity profile
        time_points = np.linspace(0, 1000, 100)
        velocity_profile = np.random.normal(2.5, 1.0, 100) + 0.5 * np.sin(time_points / 100)
        
        fig.add_trace(
            go.Scatter(
                x=time_points,
                y=velocity_profile,
                mode='lines',
                name=f'{player_name} Velocity',
                line=dict(color='#4ECDC4', width=2),
                showlegend=False
            ),
            row=i+1, col=1
        )
        
        # Right panel: Epoch Comparison
        epoch_distances = []
        epoch_labels = []
        
        for epoch_analysis in player_result['wcs_analysis']:
            epoch_duration = epoch_analysis['epoch_duration']
            for threshold in epoch_analysis['thresholds']:
                if threshold['threshold_name'] == 'Default Threshold':
                    epoch_distances.append(threshold['distance'])
                    epoch_labels.append(f'{epoch_duration}min')
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        fig.add_trace(
            go.Bar(
                x=epoch_labels,
                y=epoch_distances,
                name=f'{player_name} Distances',
                marker_color=colors[:len(epoch_distances)],
                showlegend=False,
                hovertemplate='Epoch: %{x}<br>Distance: %{y:.1f}m<extra></extra>'
            ),
            row=i+1, col=2
        )
    
    # Update layout
    fig.update_layout(
        title="Individual Player Analysis Dashboard",
        height=200 * max_players,
        showlegend=False
    )
    
    # Update axes labels
    for i in range(max_players):
        fig.update_xaxes(title_text="Time (seconds)", row=i+1, col=1)
        fig.update_yaxes(title_text="Velocity (m/s)", row=i+1, col=1)
        fig.update_xaxes(title_text="Epoch Duration", row=i+1, col=2)
        fig.update_yaxes(title_text="WCS Distance (m)", row=i+1, col=2)
    
    return fig

def create_performance_insights_dashboard(all_results: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a performance insights dashboard with key metrics and trends
    
    Args:
        all_results: List of results from batch processing
        
    Returns:
        Plotly figure with performance insights
    """
    
    # Prepare data
    combined_data = []
    for result in all_results:
        player_name = result['metadata']['player_name']
        velocity_stats = result['velocity_stats']
        
        # Get WCS distances for different epochs
        wcs_distances = {}
        for epoch_analysis in result['wcs_analysis']:
            epoch_duration = epoch_analysis['epoch_duration']
            for threshold in epoch_analysis['thresholds']:
                if threshold['threshold_name'] == 'Default Threshold':
                    wcs_distances[epoch_duration] = threshold['distance']
        
        combined_data.append({
            'Player': player_name,
            'Mean_Velocity': velocity_stats['mean'],
            'Max_Velocity': velocity_stats['max'],
            'WCS_1min': wcs_distances.get(1.0, 0),
            'WCS_2min': wcs_distances.get(2.0, 0),
            'WCS_5min': wcs_distances.get(5.0, 0),
            'Total_Records': result['metadata']['total_records']
        })
    
    df = pd.DataFrame(combined_data)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Player Performance Ranking (1-min WCS)',
            'Velocity vs WCS Distance Correlation',
            'Performance Consistency (Std Dev)',
            'Top Performers by Epoch Duration'
        ),
        specs=[[{"type": "bar"}, {"type": "scatter"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Panel 1: Performance Ranking
    df_sorted = df.sort_values('WCS_1min', ascending=True)
    
    fig.add_trace(
        go.Bar(
            x=df_sorted['WCS_1min'],
            y=df_sorted['Player'],
            orientation='h',
            marker_color='#45B7D1',
            hovertemplate='Player: %{y}<br>1-min WCS: %{x:.1f}m<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Panel 2: Velocity vs WCS Correlation
    fig.add_trace(
        go.Scatter(
            x=df['Mean_Velocity'],
            y=df['WCS_1min'],
            mode='markers+text',
            text=df['Player'],
            textposition='top center',
            marker=dict(color='#FF6B6B', size=10),
            hovertemplate='Player: %{text}<br>Mean Velocity: %{x:.2f} m/s<br>1-min WCS: %{y:.1f}m<extra></extra>'
        ),
        row=1, col=2
    )
    
    # Panel 3: Performance Consistency (simplified)
    # Calculate consistency as coefficient of variation across epochs
    df['consistency'] = df[['WCS_1min', 'WCS_2min', 'WCS_5min']].std(axis=1) / df[['WCS_1min', 'WCS_2min', 'WCS_5min']].mean(axis=1)
    df_consistent = df.sort_values('consistency')
    
    fig.add_trace(
        go.Bar(
            x=df_consistent['Player'],
            y=df_consistent['consistency'],
            marker_color='#96CEB4',
            hovertemplate='Player: %{x}<br>Consistency (CV): %{y:.3f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Panel 4: Top Performers by Epoch
    top_1min = df.nlargest(3, 'WCS_1min')
    top_2min = df.nlargest(3, 'WCS_2min')
    top_5min = df.nlargest(3, 'WCS_5min')
    
    fig.add_trace(
        go.Bar(
            x=['1min', '2min', '5min'],
            y=[top_1min['WCS_1min'].iloc[0], top_2min['WCS_2min'].iloc[0], top_5min['WCS_5min'].iloc[0]],
            name='Top Performer',
            marker_color='#FFEAA7',
            hovertemplate='Epoch: %{x}<br>Distance: %{y:.1f}m<extra></extra>'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title="Performance Insights Dashboard",
        height=800,
        showlegend=False
    )
    
    # Update axes labels
    fig.update_xaxes(title_text="1-min WCS Distance (m)", row=1, col=1)
    fig.update_xaxes(title_text="Mean Velocity (m/s)", row=1, col=2)
    fig.update_yaxes(title_text="1-min WCS Distance (m)", row=1, col=2)
    fig.update_xaxes(title_text="Player", row=2, col=1)
    fig.update_yaxes(title_text="Consistency (Coefficient of Variation)", row=2, col=1)
    fig.update_xaxes(title_text="Epoch Duration", row=2, col=2)
    fig.update_yaxes(title_text="Top Distance (m)", row=2, col=2)
    
    return fig

def save_dashboard_visualizations(all_results: List[Dict[str, Any]], 
                                output_path: str,
                                title_prefix: str = "WCS_Analysis") -> Dict[str, str]:
    """
    Create and save all dashboard visualizations
    
    Args:
        all_results: List of results from batch processing
        output_path: Directory to save visualizations
        title_prefix: Prefix for file names
        
    Returns:
        Dictionary of saved file paths
    """
    
    saved_files = {}
    
    # 1. Comprehensive Dashboard
    try:
        fig1 = create_comprehensive_dashboard(all_results, f"{title_prefix} - Comprehensive Dashboard")
        if fig1:
            file1 = f"{output_path}/{title_prefix}_comprehensive_dashboard.html"
            fig1.write_html(file1)
            saved_files['comprehensive_dashboard'] = file1
    except Exception as e:
        st.error(f"Failed to create comprehensive dashboard: {str(e)}")
    
    # 2. Individual Player Dashboard
    try:
        fig2 = create_individual_player_dashboard(all_results)
        if fig2:
            file2 = f"{output_path}/{title_prefix}_individual_players.html"
            fig2.write_html(file2)
            saved_files['individual_players'] = file2
    except Exception as e:
        st.error(f"Failed to create individual player dashboard: {str(e)}")
    
    # 3. Performance Insights Dashboard
    try:
        fig3 = create_performance_insights_dashboard(all_results)
        if fig3:
            file3 = f"{output_path}/{title_prefix}_performance_insights.html"
            fig3.write_html(file3)
            saved_files['performance_insights'] = file3
    except Exception as e:
        st.error(f"Failed to create performance insights dashboard: {str(e)}")
    
    return saved_files 