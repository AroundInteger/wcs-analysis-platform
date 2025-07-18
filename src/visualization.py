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
            # TH_0 period
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
                annotation_text=f"TH_0: {th0_distance:.1f}m",
                annotation_position=th0_pos,
                annotation=dict(
                    font=dict(size=10, color="black"),
                    bgcolor="rgba(255,255,255,0.9)",
                    bordercolor="rgba(0,0,0,0.3)",
                    borderwidth=1
                )
            )
            
            # TH_1 period
            th1_start = epoch_result[6] / 10
            th1_end = epoch_result[7] / 10
            th1_distance = epoch_result[4]
            
            # Choose different position for TH_1 to avoid overlap
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
                    font=dict(size=10, color="black"),
                    bgcolor="rgba(255,255,255,0.9)",
                    bordercolor="rgba(0,0,0,0.3)",
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
            vertical_spacing=0.12,  # Increased spacing between subplots
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
        
        # Update layout
        fig.update_layout(
            title=f"Kinematic Analysis - {metadata.get('player_name', 'Unknown')}",
            height=250 * num_plots,  # Increased height for better spacing
            showlegend=True,
            legend=dict(
                x=1.02,  # Position legend outside the plot
                y=1.0,
                xanchor='left',
                yanchor='top',
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='rgba(0,0,0,0.3)',
                borderwidth=1
            ),
            hovermode='x unified',
            margin=dict(l=80, r=120, t=100, b=80),  # Increased right margin for legend
            title_x=0.5,  # Center the title
            title_font_size=16
        )
        
        # Update axes labels
        for i in range(1, num_plots + 1):
            fig.update_xaxes(title_text="Time (seconds)", row=i, col=1)
            if i == 1:
                fig.update_yaxes(title_text="Velocity (m/s)", row=i, col=1)
            elif i == 2 and has_acceleration:
                fig.update_yaxes(title_text="Acceleration (m/s²)", row=i, col=1)
            elif i == 3 and has_distance:
                fig.update_yaxes(title_text="Distance (m)", row=i, col=1)
            elif i == 4 and has_power:
                fig.update_yaxes(title_text="Power (W)", row=i, col=1)
        
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
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='rgba(0,0,0,0.3)',
                borderwidth=1
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
        
        # Add TH_0 distances
        fig.add_trace(
            go.Bar(
                x=[f"{dur:.1f}min" for dur in epoch_durations],
                y=th0_distances,
                name='TH_0 Distance',
                marker_color='lightcoral',
                hovertemplate='Epoch: %{x}<br>Distance: %{y:.1f} m<extra></extra>'
            )
        )
        
        # Add TH_1 distances
        fig.add_trace(
            go.Bar(
                x=[f"{dur:.1f}min" for dur in epoch_durations],
                y=th1_distances,
                name='TH_1 Distance',
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
                x=['TH_0 Max', 'TH_1 Max'],
                y=[wcs_summary.get('th0_max_distance', 0), wcs_summary.get('th1_max_distance', 0)],
                marker_color=['lightcoral', 'lightblue'],
                name='Max Distances'
            ),
            row=1, col=2
        )
        
        # WCS times bar chart
        fig.add_trace(
            go.Bar(
                x=['TH_0 Max', 'TH_1 Max'],
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
            subplot_titles=('Mean Velocity', 'Peak Velocity', 'TH_0 Distance', 'TH_1 Distance'),
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
        
        # TH_0 distance
        fig.add_trace(
            go.Bar(x=player_names, y=th0_distances, name='TH_0 Distance', marker_color='lightcoral'),
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
                    'Metric': 'TH_0 Distance',
                    'Value': f"{wcs_summary.get('th0_distance', 0):.1f} m",
                    'Category': 'WCS Analysis'
                })
                summary_data.append({
                    'Metric': 'TH_0 Duration',
                    'Value': f"{wcs_summary.get('th0_duration', 0):.1f} s",
                    'Category': 'WCS Analysis'
                })
            
            if 'th1_distance' in wcs_summary:
                summary_data.append({
                    'Metric': 'TH_1 Distance',
                    'Value': f"{wcs_summary.get('th1_distance', 0):.1f} m",
                    'Category': 'WCS Analysis'
                })
                summary_data.append({
                    'Metric': 'TH_1 Duration',
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