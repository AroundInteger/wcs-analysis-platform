"""
Visualization Module for WCS Analysis Platform

Handles creation of interactive charts and graphs for GPS data analysis.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import streamlit as st


def add_wcs_annotations(fig, wcs_results, colors, annotation_positions):
    """
    Add WCS annotations with intelligent positioning to avoid overlaps
    
    Args:
        fig: Plotly figure object
        wcs_results: List of WCS results
        colors: List of colors for different epochs
        annotation_positions: List of annotation positions to cycle through
        
    Returns:
        Updated figure with annotations
    """
    if not wcs_results:
        return fig
    
    # Valid Plotly annotation positions
    valid_positions = ['top left', 'top right', 'bottom left', 'bottom right']
    
    for i, epoch_result in enumerate(wcs_results):
        if len(epoch_result) >= 8:
            # Default threshold period
            th0_start = epoch_result[2] / 10  # Convert to seconds
            th0_end = epoch_result[3] / 10
            th0_distance = epoch_result[0]
            
            # Choose position to avoid overlap (use only valid positions)
            th0_pos = valid_positions[i % len(valid_positions)]
            
            fig.add_vrect(
                x0=th0_start, x1=th0_end,
                fillcolor=colors[i % len(colors)],
                opacity=0.2,
                layer="below",
                line_width=0,
                annotation_text=f"Default: {th0_distance:.1f}m",
                annotation_position=th0_pos,
                annotation=dict(
                    font=dict(size=10, color="white"),
                    bgcolor="rgba(0,0,0,0.8)",
                    bordercolor="rgba(255,255,255,0.3)",
                    borderwidth=1
                )
            )
            
            # Threshold 1 period
            th1_start = epoch_result[6] / 10
            th1_end = epoch_result[7] / 10
            th1_distance = epoch_result[4]
            
            # Choose different position for Threshold 1 to avoid overlap
            th1_pos = valid_positions[(i + 2) % len(valid_positions)]
            
            fig.add_vrect(
                x0=th1_start, x1=th1_end,
                fillcolor=colors[(i + 1) % len(colors)],
                opacity=0.3,
                layer="below",
                line_width=0,
                annotation_text=f"TH_1: {th1_distance:.1f}m",
                annotation_position=th1_pos,
                annotation=dict(
                    font=dict(size=10, color="white"),
                    bgcolor="rgba(0,0,0,0.8)",
                    bordercolor="rgba(255,255,255,0.3)",
                    borderwidth=1
                )
            )
    
    return fig


def create_kinematic_visualization(df: pd.DataFrame, 
                                 metadata: Dict[str, Any],
                                 wcs_results: Optional[List] = None) -> go.Figure:
    """
    Create comprehensive kinematic parameters visualization
    
    Args:
        df: DataFrame with velocity, acceleration, and distance data
        metadata: File metadata
        wcs_results: Optional WCS analysis results
        
    Returns:
        Plotly figure object
    """
    try:
        # Check which kinematic parameters are available
        has_acceleration = 'Acceleration' in df.columns
        has_distance = 'Distance' in df.columns
        has_power = 'Power' in df.columns
        
        # Determine number of subplots
        num_plots = 1  # Velocity is always available
        if has_acceleration:
            num_plots += 1
        if has_distance:
            num_plots += 1
        if has_power:
            num_plots += 1
        
        # Create subplots
        subplot_titles = ['Velocity Time Series']
        if has_acceleration:
            subplot_titles.append('Acceleration Time Series')
        if has_distance:
            subplot_titles.append('Cumulative Distance')
        if has_power:
            subplot_titles.append('Instantaneous Power')
        
        fig = make_subplots(
            rows=num_plots, cols=1,
            subplot_titles=subplot_titles,
            vertical_spacing=0.15,  # Increased spacing between subplots for better separation
            row_heights=[1.0] * num_plots
        )
        
        # Time data
        if 'Seconds' in df.columns:
            time_data = df['Seconds']
        else:
            time_data = np.arange(len(df)) / 10  # Assume 10Hz
        
        current_row = 1
        
        # Velocity plot
        fig.add_trace(
            go.Scatter(
                x=time_data,
                y=df['Velocity'],
                mode='lines',
                name='Velocity',
                line=dict(color='blue', width=1),
                hovertemplate='Time: %{x:.1f}s<br>Velocity: %{y:.2f} m/s<extra></extra>'
            ),
            row=current_row, col=1
        )
        
        # Add smoothed velocity if available
        if 'Velocity_Smooth' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=time_data,
                    y=df['Velocity_Smooth'],
                    mode='lines',
                    name='Velocity (Smoothed)',
                    line=dict(color='red', width=2, dash='dash'),
                    hovertemplate='Time: %{x:.1f}s<br>Velocity: %{y:.2f} m/s<extra></extra>'
                ),
                row=current_row, col=1
            )
        
        current_row += 1
        
        # Acceleration plot
        if has_acceleration:
            fig.add_trace(
                go.Scatter(
                    x=time_data,
                    y=df['Acceleration'],
                    mode='lines',
                    name='Acceleration',
                    line=dict(color='green', width=1),
                    hovertemplate='Time: %{x:.1f}s<br>Acceleration: %{y:.2f} m/s²<extra></extra>'
                ),
                row=current_row, col=1
            )
            
            # Add smoothed acceleration if available
            if 'Acceleration_Smooth' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=time_data,
                        y=df['Acceleration_Smooth'],
                        mode='lines',
                        name='Acceleration (Smoothed)',
                        line=dict(color='orange', width=2, dash='dash'),
                        hovertemplate='Time: %{x:.1f}s<br>Acceleration: %{y:.2f} m/s²<extra></extra>'
                    ),
                    row=current_row, col=1
                )
            
            current_row += 1
        
        # Distance plot
        if has_distance:
            fig.add_trace(
                go.Scatter(
                    x=time_data,
                    y=df['Distance'],
                    mode='lines',
                    name='Cumulative Distance',
                    line=dict(color='purple', width=2),
                    hovertemplate='Time: %{x:.1f}s<br>Distance: %{y:.1f} m<extra></extra>'
                ),
                row=current_row, col=1
            )
            current_row += 1
        
        # Power plot
        if has_power:
            fig.add_trace(
                go.Scatter(
                    x=time_data,
                    y=df['Power'],
                    mode='lines',
                    name='Instantaneous Power',
                    line=dict(color='brown', width=1),
                    hovertemplate='Time: %{x:.1f}s<br>Power: %{y:.2f} W<extra></extra>'
                ),
                row=current_row, col=1
            )
        
        # Add WCS periods to velocity plot if available
        if wcs_results:
            colors = ['red', 'orange', 'green', 'purple', 'brown']
            fig = add_wcs_annotations(fig, wcs_results, colors, [])
        
        # Update layout with better spacing
        fig.update_layout(
            title=f"Kinematic Analysis - {metadata.get('player_name', 'Unknown')}",
            height=300 * num_plots,  # Increased height for better spacing
            showlegend=True,
            legend=dict(
                x=1.02,  # Position legend outside the plot
                y=1.0,
                xanchor='left',
                yanchor='top',
                bgcolor='rgba(0,0,0,0.8)',
                bordercolor='rgba(255,255,255,0.3)',
                borderwidth=1,
                font=dict(color='white')
            ),
            hovermode='x unified',
            margin=dict(l=80, r=120, t=120, b=120),  # Increased margins for better spacing
            title_x=0.5,  # Center the title
            title_font_size=16
        )
        
        # Update axes labels with better formatting
        for i in range(1, num_plots + 1):
            fig.update_xaxes(
                title_text="Time (seconds)", 
                row=i, col=1,
                title_font_size=12,
                tickfont_size=10
            )
            if i == 1:
                fig.update_yaxes(
                    title_text="Velocity (m/s)", 
                    row=i, col=1,
                    title_font_size=12,
                    tickfont_size=10
                )
            elif i == 2 and has_acceleration:
                fig.update_yaxes(
                    title_text="Acceleration (m/s²)", 
                    row=i, col=1,
                    title_font_size=12,
                    tickfont_size=10
                )
            elif i == 3 and has_distance:
                fig.update_yaxes(
                    title_text="Distance (m)", 
                    row=i, col=1,
                    title_font_size=12,
                    tickfont_size=10
                )
            elif i == 4 and has_power:
                fig.update_yaxes(
                    title_text="Power (W)", 
                    row=i, col=1,
                    title_font_size=12,
                    tickfont_size=10
                )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating kinematic visualization: {str(e)}")
        return None


def create_velocity_visualization(df: pd.DataFrame, 
                                metadata: Dict[str, Any],
                                wcs_results: Optional[List] = None) -> go.Figure:
    """
    Create comprehensive velocity visualization
    
    Args:
        df: DataFrame with velocity data
        metadata: File metadata
        wcs_results: Optional WCS analysis results
        
    Returns:
        Plotly figure object
    """
    try:
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Velocity Time Series', 'Velocity Distribution'),
            vertical_spacing=0.15,  # Increased spacing between subplots
            row_heights=[0.7, 0.3]
        )
        
        # Time series plot
        if 'Seconds' in df.columns:
            time_data = df['Seconds']
        else:
            time_data = np.arange(len(df)) / 10  # Assume 10Hz
        
        # Add velocity time series
        fig.add_trace(
            go.Scatter(
                x=time_data,
                y=df['Velocity'],
                mode='lines',
                name='Velocity',
                line=dict(color='blue', width=1),
                hovertemplate='Time: %{x:.1f}s<br>Velocity: %{y:.2f} m/s<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Add WCS periods if available
        if wcs_results:
            colors = ['red', 'orange', 'green', 'purple', 'brown']
            fig = add_wcs_annotations(fig, wcs_results, colors, [])
        
        # Add velocity distribution histogram
        fig.add_trace(
            go.Histogram(
                x=df['Velocity'],
                nbinsx=50,
                name='Velocity Distribution',
                marker_color='lightblue',
                opacity=0.7,
                hovertemplate='Velocity: %{x:.2f} m/s<br>Count: %{y}<extra></extra>'
            ),
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            title=f"Velocity Analysis - {metadata.get('player_name', 'Unknown')}",
            xaxis_title="Time (seconds)",
            yaxis_title="Velocity (m/s)",
            height=700,  # Increased height for better spacing
            showlegend=True,
            legend=dict(
                x=1.02,  # Position legend outside the plot
                y=1.0,
                xanchor='left',
                yanchor='top',
                bgcolor='rgba(0,0,0,0.8)',
                bordercolor='rgba(255,255,255,0.3)',
                borderwidth=1,
                font=dict(color='white')
            ),
            hovermode='x unified',
            margin=dict(l=80, r=120, t=100, b=80),  # Increased right margin for legend
            title_x=0.5,  # Center the title
            title_font_size=16
        )
        
        # Update axes
        fig.update_xaxes(title_text="Time (seconds)", row=1, col=1)
        fig.update_yaxes(title_text="Velocity (m/s)", row=1, col=1)
        fig.update_xaxes(title_text="Velocity (m/s)", row=2, col=1)
        fig.update_yaxes(title_text="Count", row=2, col=1)
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating velocity visualization: {str(e)}")
        return None


def create_wcs_comparison_chart(wcs_results: List[List], 
                               epoch_durations: List[float]) -> go.Figure:
    """
    Create WCS comparison chart for different epoch durations
    
    Args:
        wcs_results: List of WCS results
        epoch_durations: List of epoch durations
        
    Returns:
        Plotly figure object
    """
    try:
        # Extract data
        th0_distances = [result[0] for result in wcs_results]
        th1_distances = [result[4] for result in wcs_results]
        
        # Create figure
        fig = go.Figure()
        
        # Add Default threshold distances
        fig.add_trace(
            go.Bar(
                x=[f"{dur:.1f}min" for dur in epoch_durations],
                y=th0_distances,
                name='Default Threshold Distance',
                marker_color='lightcoral',
                hovertemplate='Epoch: %{x}<br>Distance: %{y:.1f} m<extra></extra>'
            )
        )
        
        # Add Threshold 1 distances
        fig.add_trace(
            go.Bar(
                x=[f"{dur:.1f}min" for dur in epoch_durations],
                y=th1_distances,
                name='Threshold 1 Distance',
                marker_color='lightblue',
                hovertemplate='Epoch: %{x}<br>Distance: %{y:.1f} m<extra></extra>'
            )
        )
        
        # Update layout
        fig.update_layout(
            title="WCS Distance by Epoch Duration",
            xaxis_title="Epoch Duration",
            yaxis_title="Distance (m)",
            barmode='group',
            height=400
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating WCS comparison chart: {str(e)}")
        return None


def create_performance_metrics_dashboard(velocity_stats: Dict[str, Any],
                                       wcs_summary: Dict[str, Any]) -> go.Figure:
    """
    Create performance metrics dashboard
    
    Args:
        velocity_stats: Velocity statistics
        wcs_summary: WCS summary statistics
        
    Returns:
        Plotly figure object
    """
    try:
        # Create subplots for different metrics
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Velocity Statistics', 'WCS Distances', 'WCS Times', 'Performance Summary'),
            specs=[[{"type": "indicator"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "indicator"}]]
        )
        
        # Velocity statistics gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=velocity_stats.get('mean', 0),
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Mean Velocity (m/s)"},
                delta={'reference': 5.0},
                gauge={
                    'axis': {'range': [None, 15]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 5], 'color': "lightgray"},
                        {'range': [5, 10], 'color': "yellow"},
                        {'range': [10, 15], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 12
                    }
                }
            ),
            row=1, col=1
        )
        
        # WCS distances bar chart
        fig.add_trace(
            go.Bar(
                x=['Default Threshold Max', 'Threshold 1 Max'],
                y=[wcs_summary.get('th0_max_distance', 0), wcs_summary.get('th1_max_distance', 0)],
                marker_color=['lightcoral', 'lightblue'],
                name='Max Distances'
            ),
            row=1, col=2
        )
        
        # WCS times bar chart
        fig.add_trace(
            go.Bar(
                x=['Default Threshold Max', 'Threshold 1 Max'],
                y=[wcs_summary.get('th0_max_time', 0), wcs_summary.get('th1_max_time', 0)],
                marker_color=['orange', 'green'],
                name='Max Times'
            ),
            row=2, col=1
        )
        
        # Performance summary indicator
        performance_score = min(100, (velocity_stats.get('max', 0) / 15) * 100)
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=performance_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Performance Score (%)"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 75], 'color': "yellow"},
                        {'range': [75, 100], 'color': "green"}
                    ]
                }
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title="Performance Metrics Dashboard",
            height=600,
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating performance metrics dashboard: {str(e)}")
        return None


def create_batch_comparison_chart(batch_results: List[Dict[str, Any]]) -> go.Figure:
    """
    Create batch comparison chart for multiple files
    
    Args:
        batch_results: List of results from batch processing
        
    Returns:
        Plotly figure object
    """
    try:
        # Extract data
        player_names = []
        mean_velocities = []
        peak_velocities = []
        th0_distances = []
        th1_distances = []
        
        for result in batch_results:
            metadata = result['metadata']
            velocity_stats = result['results'].get('velocity_stats', {})
            wcs_results = result['results'].get('wcs_results', [])
            
            player_names.append(metadata.get('player_name', 'Unknown'))
            mean_velocities.append(velocity_stats.get('mean', 0))
            peak_velocities.append(velocity_stats.get('max', 0))
            
            # Get first epoch results
            if wcs_results:
                th0_distances.append(wcs_results[0][0] if len(wcs_results[0]) > 0 else 0)
                th1_distances.append(wcs_results[0][4] if len(wcs_results[0]) > 4 else 0)
            else:
                th0_distances.append(0)
                th1_distances.append(0)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Mean Velocity', 'Peak Velocity', 'Default Threshold Distance', 'TH_1 Distance'),
            vertical_spacing=0.1
        )
        
        # Mean velocity
        fig.add_trace(
            go.Bar(x=player_names, y=mean_velocities, name='Mean Velocity', marker_color='lightblue'),
            row=1, col=1
        )
        
        # Peak velocity
        fig.add_trace(
            go.Bar(x=player_names, y=peak_velocities, name='Peak Velocity', marker_color='orange'),
            row=1, col=2
        )
        
        # Default threshold distance
        fig.add_trace(
            go.Bar(x=player_names, y=th0_distances, name='Default Threshold Distance', marker_color='lightcoral'),
            row=2, col=1
        )
        
        # TH_1 distance
        fig.add_trace(
            go.Bar(x=player_names, y=th1_distances, name='TH_1 Distance', marker_color='lightgreen'),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title="Batch Comparison Results",
            height=600,
            showlegend=False
        )
        
        # Update axes
        fig.update_xaxes(tickangle=45)
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating batch comparison chart: {str(e)}")
        return None


def create_enhanced_wcs_visualization(df: pd.DataFrame, 
                                    metadata: Dict[str, Any],
                                    wcs_results: Optional[List] = None) -> go.Figure:
    """
    Create enhanced WCS visualization with sophisticated period highlighting
    
    Args:
        df: DataFrame with velocity data
        metadata: File metadata
        wcs_results: Optional WCS analysis results
        
    Returns:
        Plotly figure object
    """
    try:
        # Create subplots with better spacing
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Velocity with WCS Periods', 'WCS Period Timeline', 'Performance Intensity'),
            vertical_spacing=0.15,  # Increased from 0.08 to 0.15 for better spacing
            row_heights=[0.5, 0.25, 0.25],
            specs=[[{"secondary_y": False}],
                   [{"secondary_y": False}],
                   [{"secondary_y": False}]]
        )
        
        # Time data
        if 'Seconds' in df.columns:
            time_data = df['Seconds']
        else:
            time_data = np.arange(len(df)) / 10  # Assume 10Hz
        
        # Main velocity plot with enhanced WCS periods
        fig.add_trace(
            go.Scatter(
                x=time_data,
                y=df['Velocity'],
                mode='lines',
                name='Velocity',
                line=dict(color='#2E86AB', width=1.5),
                hovertemplate='<b>Time:</b> %{x:.1f}s<br><b>Velocity:</b> %{y:.2f} m/s<extra></extra>',
                fill='tonexty',
                fillcolor='rgba(46, 134, 171, 0.1)'
            ),
            row=1, col=1
        )
        
        # Add WCS periods with enhanced styling
        if wcs_results:
            fig = add_enhanced_wcs_periods(fig, wcs_results, time_data, row=1)
        
        # WCS Period Timeline
        if wcs_results:
            fig = create_wcs_timeline(fig, wcs_results, row=2)
        
        # Performance Intensity Heatmap
        if wcs_results:
            fig = create_performance_intensity(fig, df, wcs_results, row=3)
        

        
        # Update layout with better spacing
        fig.update_layout(
            title=f"Enhanced WCS Analysis - {metadata.get('player_name', 'Unknown')}",
            height=900,  # Increased height to accommodate better spacing
            showlegend=True,  # Re-enable legend for colored markers
            legend=dict(
                x=1.02,
                y=1.0,
                xanchor='left',
                yanchor='top',
                bgcolor='rgba(0,0,0,0.8)',
                bordercolor='rgba(255,255,255,0.3)',
                borderwidth=1,
                font=dict(color='white', size=10)
            ),
            hovermode='x unified',
            margin=dict(l=80, r=120, t=120, b=120),  # Increased top and bottom margins
            title_x=0.5,
            title_font_size=18,
            font=dict(size=12)
        )
        
        # Update axes with better spacing
        fig.update_xaxes(
            title_text="Time (seconds)", 
            row=1, col=1,
            title_font_size=12,
            tickfont_size=10
        )
        fig.update_yaxes(
            title_text="Velocity (m/s)", 
            row=1, col=1,
            title_font_size=12,
            tickfont_size=10,
            range=[0, 10]  # Set y-axis maximum to 10 m/s
        )
        
        fig.update_xaxes(
            title_text="Time (seconds)", 
            row=2, col=1,
            title_font_size=12,
            tickfont_size=10
        )
        fig.update_yaxes(
            title_text="Period Type", 
            row=2, col=1,
            title_font_size=12,
            tickfont_size=10
        )
        
        fig.update_xaxes(
            title_text="Time (seconds)", 
            row=3, col=1,
            title_font_size=12,
            tickfont_size=10
        )
        fig.update_yaxes(
            title_text="Intensity", 
            row=3, col=1,
            title_font_size=12,
            tickfont_size=10
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating enhanced WCS visualization: {str(e)}")
        return None


def add_enhanced_wcs_periods(fig, wcs_results, time_data, row=1):
    """
    Add clean, elegant WCS periods with minimal visual clutter
    
    Args:
        fig: Plotly figure object
        wcs_results: List of WCS results
        time_data: Time data array
        row: Subplot row number
        
    Returns:
        Updated figure with clean WCS periods
    """
    colors = {
        'th0': '#FF6B6B',  # Single color for consistency
        'th1': '#4ECDC4'   # Single color for consistency
    }
    
    # Create legend entries for the periods (specific to velocity plot)
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=15, color=colors['th0'], symbol='square'),
            name='Default Threshold Periods',
            showlegend=True,
            legendgroup='velocity_periods'
        ),
        row=row, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=15, color=colors['th1'], symbol='square'),
            name='Threshold 1 Periods',
            showlegend=True,
            legendgroup='velocity_periods'
        ),
        row=row, col=1
    )
    
    # Get y-axis range for proper shape positioning
    y_min = 0
    y_max = 10  # Set to 10 m/s as requested
    
    for i, epoch_result in enumerate(wcs_results):
        if len(epoch_result) >= 8:
            # Default threshold period - clean background highlight only
            th0_start = epoch_result[2] / 10
            th0_end = epoch_result[3] / 10
            
            # Use add_shape instead of add_vrect for better control
            fig.add_shape(
                type="rect",
                x0=th0_start, x1=th0_end,
                y0=y_min, y1=y_max,
                fillcolor=colors['th0'],
                opacity=0.15,  # Very subtle background
                layer="below",
                line_width=0,  # No border
                visible=True,
                xref=f"x{row}" if row > 1 else "x",
                yref=f"y{row}" if row > 1 else "y"
            )
            
            # Threshold 1 period - clean background highlight only
            th1_start = epoch_result[6] / 10
            th1_end = epoch_result[7] / 10
            
            fig.add_shape(
                type="rect",
                x0=th1_start, x1=th1_end,
                y0=y_min, y1=y_max,
                fillcolor=colors['th1'],
                opacity=0.2,  # Slightly more visible
                layer="below",
                line_width=0,  # No border
                visible=True,
                xref=f"x{row}" if row > 1 else "x",
                yref=f"y{row}" if row > 1 else "y"
            )
    
    return fig


def create_wcs_timeline(fig, wcs_results, row=2):
    """
    Create clean WCS period timeline visualization
    
    Args:
        fig: Plotly figure object
        wcs_results: List of WCS results
        row: Subplot row number
        
    Returns:
        Updated figure with timeline
    """
    colors = {'th0': '#FF6B6B', 'th1': '#4ECDC4'}
    
    # Create summary data for timeline
    th0_periods = []
    th1_periods = []
    
    for i, epoch_result in enumerate(wcs_results):
        if len(epoch_result) >= 8:
            # Default threshold period
            th0_start = epoch_result[2] / 10
            th0_end = epoch_result[3] / 10
            th0_distance = epoch_result[0]
            th0_duration = th0_end - th0_start
            
            th0_periods.append({
                'start': th0_start,
                'end': th0_end,
                'distance': th0_distance,
                'duration': th0_duration,
                'epoch': i + 1
            })
            
            # Threshold 1 period
            th1_start = epoch_result[6] / 10
            th1_end = epoch_result[7] / 10
            th1_distance = epoch_result[4]
            th1_duration = th1_end - th1_start
            
            th1_periods.append({
                'start': th1_start,
                'end': th1_end,
                'distance': th1_distance,
                'duration': th1_duration,
                'epoch': i + 1
            })
    
    # Add Default Threshold periods
    if th0_periods:
        fig.add_trace(
            go.Scatter(
                x=[p['start'] for p in th0_periods] + [p['end'] for p in th0_periods],
                y=['Default Threshold'] * len(th0_periods) * 2,
                mode='markers',
                name='Default Threshold',
                marker=dict(
                    color=colors['th0'],
                    size=8,
                    symbol='circle'
                ),
                hovertemplate='<b>Default Threshold</b><br>Distance: %{customdata[0]:.1f}m<br>Duration: %{customdata[1]:.1f}s<br>Epoch: %{customdata[2]}<extra></extra>',
                customdata=[[p['distance'], p['duration'], p['epoch']] for p in th0_periods] * 2,
                showlegend=False
            ),
            row=row, col=1
        )
    
    # Add Threshold 1 periods
    if th1_periods:
        fig.add_trace(
            go.Scatter(
                x=[p['start'] for p in th1_periods] + [p['end'] for p in th1_periods],
                y=['Threshold 1'] * len(th1_periods) * 2,
                mode='markers',
                name='Threshold 1',
                marker=dict(
                    color=colors['th1'],
                    size=8,
                    symbol='circle'
                ),
                hovertemplate='<b>Threshold 1</b><br>Distance: %{customdata[0]:.1f}m<br>Duration: %{customdata[1]:.1f}s<br>Epoch: %{customdata[2]}<extra></extra>',
                customdata=[[p['distance'], p['duration'], p['epoch']] for p in th1_periods] * 2,
                showlegend=False
            ),
            row=row, col=1
        )
    
    return fig


def create_performance_intensity(fig, df, wcs_results, row=3):
    """
    Create clean performance intensity visualization
    
    Args:
        fig: Plotly figure object
        df: DataFrame with velocity data
        wcs_results: List of WCS results
        row: Subplot row number
        
    Returns:
        Updated figure with intensity visualization
    """
    # Create intensity array based on velocity
    time_data = df['Seconds'] if 'Seconds' in df.columns else np.arange(len(df)) / 10
    velocity_data = df['Velocity']
    
    # Normalize velocity to intensity (0-1)
    intensity = (velocity_data - velocity_data.min()) / (velocity_data.max() - velocity_data.min())
    
    # Add clean intensity trace
    fig.add_trace(
        go.Scatter(
            x=time_data,
            y=intensity,
            mode='lines',
            name='Performance Intensity',
            line=dict(color='#2E86AB', width=1.5),
            fill='tonexty',
            fillcolor='rgba(46, 134, 171, 0.2)',
            hovertemplate='<b>Time:</b> %{x:.1f}s<br><b>Intensity:</b> %{y:.2f}<br><b>Velocity:</b> %{customdata:.2f} m/s<extra></extra>',
            customdata=velocity_data
        ),
        row=row, col=1
    )
    
    # Add subtle WCS period highlights
    colors_wcs = {'th0': '#FF6B6B', 'th1': '#4ECDC4'}
    
    # Get y-axis range for intensity plot
    y_min = 0
    y_max = 1  # Intensity is normalized to 0-1
    
    for i, epoch_result in enumerate(wcs_results):
        if len(epoch_result) >= 8:
            # Default threshold intensity highlight
            th0_start = epoch_result[2] / 10
            th0_end = epoch_result[3] / 10
            
            fig.add_shape(
                type="rect",
                x0=th0_start, x1=th0_end,
                y0=y_min, y1=y_max,
                fillcolor=colors_wcs['th0'],
                opacity=0.1,  # Very subtle
                layer="below",
                line_width=0,
                visible=True,
                xref=f"x{row}" if row > 1 else "x",
                yref=f"y{row}" if row > 1 else "y"
            )
            
            # Threshold 1 intensity highlight
            th1_start = epoch_result[6] / 10
            th1_end = epoch_result[7] / 10
            
            fig.add_shape(
                type="rect",
                x0=th1_start, x1=th1_end,
                y0=y_min, y1=y_max,
                fillcolor=colors_wcs['th1'],
                opacity=0.1,  # Very subtle
                layer="below",
                line_width=0,
                visible=True,
                xref=f"x{row}" if row > 1 else "x",
                yref=f"y{row}" if row > 1 else "y"
            )
    
    return fig


def create_wcs_period_details(wcs_results: List[List], epoch_durations: Optional[List[float]] = None) -> pd.DataFrame:
    """
    Create detailed WCS period information table
    
    Args:
        wcs_results: List of WCS results
        epoch_durations: List of epoch durations in minutes
        
    Returns:
        DataFrame with detailed period information
    """
    try:
        period_data = []
        
        # Default epoch names if not provided (in minutes)
        if epoch_durations is None:
            epoch_names = ['0.5min', '1.0min', '1.5min', '2.0min', '3.0min', '5.0min']
        else:
            epoch_names = [f"{dur:.1f}min" for dur in epoch_durations]
        
        for i, epoch_result in enumerate(wcs_results):
            if len(epoch_result) >= 8:
                epoch_name = epoch_names[i] if i < len(epoch_names) else f"Epoch {i+1}"
                
                # Default threshold details
                th0_distance = epoch_result[0]
                th0_start = epoch_result[2] / 10
                th0_end = epoch_result[3] / 10
                th0_duration = th0_end - th0_start
                th0_avg_velocity = th0_distance / th0_duration if th0_duration > 0 else 0
                
                period_data.append({
                    'Epoch': epoch_name,
                    'Period': 'Default Threshold',
                    'Distance (m)': f"{th0_distance:.1f}",
                    'Duration (s)': f"{th0_duration:.1f}",
                    'Start Time (s)': f"{th0_start:.1f}",
                    'End Time (s)': f"{th0_end:.1f}",
                    'Avg Velocity (m/s)': f"{th0_avg_velocity:.2f}",
                    'Performance Level': 'High Intensity' if th0_avg_velocity > 5 else 'Moderate Intensity'
                })
                
                # Threshold 1 details
                th1_distance = epoch_result[4]
                th1_start = epoch_result[6] / 10
                th1_end = epoch_result[7] / 10
                th1_duration = th1_end - th1_start
                th1_avg_velocity = th1_distance / th1_duration if th1_duration > 0 else 0
                
                period_data.append({
                    'Epoch': epoch_name,
                    'Period': 'Threshold 1',
                    'Distance (m)': f"{th1_distance:.1f}",
                    'Duration (s)': f"{th1_duration:.1f}",
                    'Start Time (s)': f"{th1_start:.1f}",
                    'End Time (s)': f"{th1_end:.1f}",
                    'Avg Velocity (m/s)': f"{th1_avg_velocity:.2f}",
                    'Performance Level': 'Peak Performance' if th1_avg_velocity > 7 else 'High Performance'
                })
        
        df = pd.DataFrame(period_data)
        
        # Sort by Period first (Default Threshold, then Threshold 1), then by Epoch
        period_order = ['Default Threshold', 'Threshold 1']
        df['Period'] = pd.Categorical(df['Period'], categories=period_order, ordered=True)
        df = df.sort_values(['Period', 'Epoch'])
        
        return df
        
    except Exception as e:
        st.error(f"Error creating WCS period details: {str(e)}")
        return pd.DataFrame()


def create_summary_statistics_table(velocity_stats: Dict[str, Any], 
                                   kinematic_stats: Optional[Dict[str, Any]] = None,
                                   wcs_summary: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Create a summary statistics table for display
    
    Args:
        velocity_stats: Velocity statistics dictionary
        kinematic_stats: Optional kinematic statistics dictionary
        wcs_summary: Optional WCS analysis summary
        
    Returns:
        DataFrame formatted for display
    """
    try:
        # Create summary data
        summary_data = []
        
        # Velocity statistics
        if velocity_stats:
            summary_data.append({
                'Metric': 'Max Velocity',
                'Value': f"{velocity_stats.get('max_velocity', 0):.2f} m/s",
                'Category': 'Velocity'
            })
            summary_data.append({
                'Metric': 'Mean Velocity',
                'Value': f"{velocity_stats.get('mean_velocity', 0):.2f} m/s",
                'Category': 'Velocity'
            })
            summary_data.append({
                'Metric': 'Min Velocity',
                'Value': f"{velocity_stats.get('min_velocity', 0):.2f} m/s",
                'Category': 'Velocity'
            })
            summary_data.append({
                'Metric': 'Velocity Std Dev',
                'Value': f"{velocity_stats.get('velocity_std', 0):.2f} m/s",
                'Category': 'Velocity'
            })
        
        # Kinematic statistics
        if kinematic_stats:
            if 'max_acceleration' in kinematic_stats:
                summary_data.append({
                    'Metric': 'Max Acceleration',
                    'Value': f"{kinematic_stats.get('max_acceleration', 0):.2f} m/s²",
                    'Category': 'Kinematics'
                })
                summary_data.append({
                    'Metric': 'Min Acceleration',
                    'Value': f"{kinematic_stats.get('min_acceleration', 0):.2f} m/s²",
                    'Category': 'Kinematics'
                })
                summary_data.append({
                    'Metric': 'Mean Acceleration',
                    'Value': f"{kinematic_stats.get('mean_acceleration', 0):.2f} m/s²",
                    'Category': 'Kinematics'
                })
            
            if 'total_distance' in kinematic_stats:
                summary_data.append({
                    'Metric': 'Total Distance',
                    'Value': f"{kinematic_stats.get('total_distance', 0):.1f} m",
                    'Category': 'Kinematics'
                })
            
            if 'max_power' in kinematic_stats:
                summary_data.append({
                    'Metric': 'Max Power',
                    'Value': f"{kinematic_stats.get('max_power', 0):.1f} W",
                    'Category': 'Kinematics'
                })
                summary_data.append({
                    'Metric': 'Mean Power',
                    'Value': f"{kinematic_stats.get('mean_power', 0):.1f} W",
                    'Category': 'Kinematics'
                })
        
        # WCS statistics
        if wcs_summary:
            if 'th0_distance' in wcs_summary:
                summary_data.append({
                    'Metric': 'Default Threshold Distance',
                    'Value': f"{wcs_summary.get('th0_distance', 0):.1f} m",
                    'Category': 'WCS Analysis'
                })
                summary_data.append({
                    'Metric': 'Default Threshold Duration',
                    'Value': f"{wcs_summary.get('th0_duration', 0):.1f} s",
                    'Category': 'WCS Analysis'
                })
            
            if 'th1_distance' in wcs_summary:
                summary_data.append({
                    'Metric': 'Threshold 1 Distance',
                    'Value': f"{wcs_summary.get('th1_distance', 0):.1f} m",
                    'Category': 'WCS Analysis'
                })
                summary_data.append({
                    'Metric': 'Threshold 1 Duration',
                    'Value': f"{wcs_summary.get('th1_duration', 0):.1f} s",
                    'Category': 'WCS Analysis'
                })
        
        # Create DataFrame
        df = pd.DataFrame(summary_data)
        
        # Sort by category and metric
        category_order = ['Velocity', 'Kinematics', 'WCS Analysis']
        df['Category'] = pd.Categorical(df['Category'], categories=category_order, ordered=True)
        df = df.sort_values(['Category', 'Metric'])
        
        return df
        
    except Exception as e:
        st.error(f"Error creating summary statistics table: {str(e)}")
        return pd.DataFrame()


def display_visualization(fig: go.Figure, title: str = "Chart"):
    """
    Display visualization in Streamlit
    
    Args:
        fig: Plotly figure object
        title: Chart title
    """
    try:
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"Could not create {title}")
    except Exception as e:
        st.error(f"Error displaying {title}: {str(e)}") 