"""
Batch Processing Module for WCS Analysis Platform

Handles processing of multiple files, CSV export, and combined visualizations.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import streamlit as st
from src.file_ingestion import read_csv_with_metadata, validate_velocity_data
from src.wcs_analysis import perform_wcs_analysis
from src.visualization import create_enhanced_wcs_visualization, create_kinematic_visualization


def process_batch_files(file_inputs: List, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process multiple files and return combined results
    
    Args:
        file_inputs: List of file inputs (paths or uploaded files)
        parameters: Analysis parameters
        
    Returns:
        List of results dictionaries for each file
    """
    all_results = []
    
    for i, file_input in enumerate(file_inputs):
        try:
            st.markdown(f"### 📄 Processing File {i+1}/{len(file_inputs)}: {os.path.basename(file_input) if isinstance(file_input, str) else file_input.name}")
            
            # Progress bar for multiple files
            if len(file_inputs) > 1:
                progress = (i + 1) / len(file_inputs)
                st.progress(progress)
            
            # Read file
            if isinstance(file_input, str):
                # File path - pass directly to the function
                df, metadata, file_type_info = read_csv_with_metadata(file_input)
            else:
                # Uploaded file
                df, metadata, file_type_info = read_csv_with_metadata(file_input)
            
            if df is not None and metadata is not None:
                # Validate velocity data
                if validate_velocity_data(df):
                    st.success("✅ Velocity data validated successfully")
                    
                    # Process WCS analysis
                    with st.spinner("Running WCS analysis..."):
                        results = perform_wcs_analysis(df, metadata, file_type_info, parameters)
                    
                    if results:
                        # Add file information to results
                        results['file_name'] = os.path.basename(file_input) if isinstance(file_input, str) else file_input.name
                        results['file_path'] = file_input if isinstance(file_input, str) else file_input.name
                        
                        all_results.append(results)
                        st.success(f"✅ Successfully processed {results['file_name']}")
                    else:
                        st.error("❌ WCS analysis failed")
                else:
                    st.error("❌ Velocity data validation failed")
            else:
                st.error("❌ Failed to read file")
                
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
    
    return all_results


def create_combined_wcs_dataframe(all_results: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Create a combined DataFrame with all WCS results (both rolling and contiguous)
    
    Args:
        all_results: List of results from batch processing
        
    Returns:
        Combined DataFrame with all WCS data
    """
    combined_data = []
    
    for result in all_results:
        metadata = result['metadata']
        wcs_results = result['results']
        
        # Get data from the results structure
        rolling_wcs_results = wcs_results.get('rolling_wcs_results', [])
        contiguous_wcs_results = wcs_results.get('contiguous_wcs_results', [])
        epoch_durations = wcs_results.get('epoch_durations', [])
        velocity_stats = wcs_results.get('velocity_stats', {})
        
        player_name = metadata.get('player_name', 'Unknown')
        file_name = result.get('file_name', 'Unknown')
        
        # If file_name is not in result, get it from file_path
        if file_name == 'Unknown':
            file_path = result.get('file_path', 'Unknown')
            if isinstance(file_path, str):
                file_name = os.path.basename(file_path)
            else:
                file_name = file_path.name if hasattr(file_path, 'name') else 'Unknown'
        
        # Process rolling WCS results
        for i, epoch_result in enumerate(rolling_wcs_results):
            if len(epoch_result) >= 8:
                epoch_duration = epoch_durations[i] if i < len(epoch_durations) else f"Epoch_{i+1}"
                
                # Default threshold data (rolling)
                th0_distance = epoch_result[0]
                th0_duration = epoch_result[1]
                th0_start = epoch_result[2] / 10
                th0_end = epoch_result[3] / 10
                th0_avg_velocity = th0_distance / th0_duration if th0_duration > 0 else 0
                
                combined_data.append({
                    'File_Name': file_name,
                    'Player_Name': player_name,
                    'Epoch_Duration_Minutes': epoch_duration,
                    'WCS_Method': 'Rolling',
                    'Threshold_Type': 'Default Threshold',
                    'WCS_Distance_m': th0_distance,
                    'WCS_Duration_s': th0_duration,
                    'Start_Time_s': th0_start,
                    'End_Time_s': th0_end,
                    'Avg_Velocity_m_s': th0_avg_velocity,
                    'File_Mean_Velocity_m_s': velocity_stats.get('mean', 0),
                    'File_Max_Velocity_m_s': velocity_stats.get('max', 0),
                    'File_Min_Velocity_m_s': velocity_stats.get('min', 0),
                    'File_Velocity_Std_m_s': velocity_stats.get('std', 0),
                    'Total_Records': metadata.get('total_records', 0),
                    'Duration_Minutes': metadata.get('duration_minutes', 0),
                    'Processing_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
                # Threshold 1 data (rolling)
                th1_distance = epoch_result[4]
                th1_duration = epoch_result[5]
                th1_start = epoch_result[6] / 10
                th1_end = epoch_result[7] / 10
                th1_avg_velocity = th1_distance / th1_duration if th1_duration > 0 else 0
                
                combined_data.append({
                    'File_Name': file_name,
                    'Player_Name': player_name,
                    'Epoch_Duration_Minutes': epoch_duration,
                    'WCS_Method': 'Rolling',
                    'Threshold_Type': 'Threshold 1',
                    'WCS_Distance_m': th1_distance,
                    'WCS_Duration_s': th1_duration,
                    'Start_Time_s': th1_start,
                    'End_Time_s': th1_end,
                    'Avg_Velocity_m_s': th1_avg_velocity,
                    'File_Mean_Velocity_m_s': velocity_stats.get('mean', 0),
                    'File_Max_Velocity_m_s': velocity_stats.get('max', 0),
                    'File_Min_Velocity_m_s': velocity_stats.get('min', 0),
                    'File_Velocity_Std_m_s': velocity_stats.get('std', 0),
                    'Total_Records': metadata.get('total_records', 0),
                    'Duration_Minutes': metadata.get('duration_minutes', 0),
                    'Processing_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # Process contiguous WCS results
        for i, epoch_result in enumerate(contiguous_wcs_results):
            if len(epoch_result) >= 8:
                epoch_duration = epoch_durations[i] if i < len(epoch_durations) else f"Epoch_{i+1}"
                
                # Default threshold data (contiguous)
                th0_distance = epoch_result[0]
                th0_duration = epoch_result[1]
                th0_start = epoch_result[2] / 10
                th0_end = epoch_result[3] / 10
                th0_avg_velocity = th0_distance / th0_duration if th0_duration > 0 else 0
                
                combined_data.append({
                    'File_Name': file_name,
                    'Player_Name': player_name,
                    'Epoch_Duration_Minutes': epoch_duration,
                    'WCS_Method': 'Contiguous',
                    'Threshold_Type': 'Default Threshold',
                    'WCS_Distance_m': th0_distance,
                    'WCS_Duration_s': th0_duration,
                    'Start_Time_s': th0_start,
                    'End_Time_s': th0_end,
                    'Avg_Velocity_m_s': th0_avg_velocity,
                    'File_Mean_Velocity_m_s': velocity_stats.get('mean', 0),
                    'File_Max_Velocity_m_s': velocity_stats.get('max', 0),
                    'File_Min_Velocity_m_s': velocity_stats.get('min', 0),
                    'File_Velocity_Std_m_s': velocity_stats.get('std', 0),
                    'Total_Records': metadata.get('total_records', 0),
                    'Duration_Minutes': metadata.get('duration_minutes', 0),
                    'Processing_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
                # Threshold 1 data (contiguous)
                th1_distance = epoch_result[4]
                th1_duration = epoch_result[5]
                th1_start = epoch_result[6] / 10
                th1_end = epoch_result[7] / 10
                th1_avg_velocity = th1_distance / th1_duration if th1_duration > 0 else 0
                
                combined_data.append({
                    'File_Name': file_name,
                    'Player_Name': player_name,
                    'Epoch_Duration_Minutes': epoch_duration,
                    'WCS_Method': 'Contiguous',
                    'Threshold_Type': 'Threshold 1',
                    'WCS_Distance_m': th1_distance,
                    'WCS_Duration_s': th1_duration,
                    'Start_Time_s': th1_start,
                    'End_Time_s': th1_end,
                    'Avg_Velocity_m_s': th1_avg_velocity,
                    'File_Mean_Velocity_m_s': velocity_stats.get('mean', 0),
                    'File_Max_Velocity_m_s': velocity_stats.get('max', 0),
                    'File_Min_Velocity_m_s': velocity_stats.get('min', 0),
                    'File_Velocity_Std_m_s': velocity_stats.get('std', 0),
                    'Total_Records': metadata.get('total_records', 0),
                    'Duration_Minutes': metadata.get('duration_minutes', 0),
                    'Processing_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
    
    return pd.DataFrame(combined_data)


def export_wcs_data_to_csv(all_results: List[Dict[str, Any]], output_folder: str = "OUTPUT") -> str:
    """
    Export all WCS data to a CSV file
    
    Args:
        all_results: List of results from batch processing
        output_folder: Folder to save the CSV file
        
    Returns:
        Path to the exported CSV file
    """
    try:
        # Create combined DataFrame
        combined_df = create_combined_wcs_dataframe(all_results)
        
        if combined_df.empty:
            st.warning("No WCS data to export")
            return None
        
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"WCS_Analysis_Results_{timestamp}.csv"
        filepath = os.path.join(output_folder, filename)
        
        # Export to CSV
        combined_df.to_csv(filepath, index=False)
        
        st.success(f"✅ WCS data exported to: `{filepath}`")
        st.info(f"📊 Exported {len(combined_df)} records from {len(all_results)} files")
        
        return filepath
        
    except Exception as e:
        st.error(f"❌ Error exporting WCS data: {str(e)}")
        return None


def create_combined_visualizations(all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create combined visualizations for multiple files
    
    Args:
        all_results: List of results from batch processing
        
    Returns:
        Dictionary containing visualization figures
    """
    try:
        if len(all_results) < 2:
            st.warning("Combined visualizations require at least 2 files")
            return {}
        
        # Create combined DataFrame
        combined_df = create_combined_wcs_dataframe(all_results)
        
        if combined_df.empty:
            st.warning("No data available for combined visualizations")
            return {}
        
        # Import visualization functions
        from src.visualization import (
            create_wcs_comparison_chart, 
            create_batch_comparison_chart,
            create_performance_metrics_dashboard
        )
        
        # Create different types of combined visualizations
        visualizations = {}
        
        # 1. WCS Distance Distribution by Epoch (Box Plot)
        fig_box = create_wcs_distance_distribution(combined_df)
        if fig_box:
            visualizations['wcs_distance_distribution'] = fig_box
        
        # 2. Mean WCS Distance vs Epoch Duration (Line Plot)
        fig_line = create_mean_wcs_distance_trend(combined_df)
        if fig_line:
            visualizations['mean_wcs_distance_trend'] = fig_line
        
        # 3. Average WCS Distance by Player (Bar Chart)
        fig_bar = create_player_comparison(combined_df)
        if fig_bar:
            visualizations['player_comparison'] = fig_bar
        
        # 4. WCS Distance Heatmap by Player and Epoch
        fig_heatmap = create_player_epoch_heatmap(combined_df)
        if fig_heatmap:
            visualizations['player_epoch_heatmap'] = fig_heatmap
        
        # 5. Individual Player Analysis Grid
        fig_grid = create_individual_player_grid(all_results)
        if fig_grid:
            visualizations['individual_player_grid'] = fig_grid
        
        return visualizations
        
    except Exception as e:
        st.error(f"❌ Error creating combined visualizations: {str(e)}")
        return {}


def create_wcs_distance_distribution(combined_df: pd.DataFrame):
    """Create WCS distance distribution box plot"""
    try:
        import plotly.graph_objects as go
        
        # Filter for Default Threshold only for cleaner visualization
        df_filtered = combined_df[combined_df['Threshold_Type'] == 'Default Threshold']
        
        # Create box plot
        fig = go.Figure()
        
        epochs = sorted(df_filtered['Epoch_Duration_Minutes'].unique())
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        for i, epoch in enumerate(epochs):
            epoch_data = df_filtered[df_filtered['Epoch_Duration_Minutes'] == epoch]['WCS_Distance_m']
            
            fig.add_trace(go.Box(
                y=epoch_data,
                name=f"{epoch}min",
                marker_color=colors[i % len(colors)],
                boxpoints='outliers',
                hovertemplate='Epoch: %{fullData.name}<br>Distance: %{y:.1f}m<extra></extra>'
            ))
        
        fig.update_layout(
            title="WCS Distance Distribution by Epoch",
            yaxis_title="WCS Distance (m)",
            xaxis_title="Epoch Duration",
            height=400,
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating WCS distance distribution: {str(e)}")
        return None


def create_mean_wcs_distance_trend(combined_df: pd.DataFrame):
    """Create mean WCS distance trend line plot"""
    try:
        import plotly.graph_objects as go
        
        # Filter for Default Threshold only
        df_filtered = combined_df[combined_df['Threshold_Type'] == 'Default Threshold']
        
        # Calculate mean and std for each epoch
        epoch_stats = df_filtered.groupby('Epoch_Duration_Minutes')['WCS_Distance_m'].agg(['mean', 'std']).reset_index()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=epoch_stats['Epoch_Duration_Minutes'],
            y=epoch_stats['mean'],
            mode='lines+markers',
            name='Mean WCS Distance',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=8),
            error_y=dict(type='data', array=epoch_stats['std'], visible=True),
            hovertemplate='Epoch: %{x}min<br>Mean Distance: %{y:.1f}m<br>Std: %{error_y.array:.1f}m<extra></extra>'
        ))
        
        fig.update_layout(
            title="Mean WCS Distance vs Epoch Duration",
            xaxis_title="Epoch Duration (minutes)",
            yaxis_title="Mean WCS Distance (m)",
            height=400
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating mean WCS distance trend: {str(e)}")
        return None


def create_player_comparison(combined_df: pd.DataFrame):
    """Create player comparison bar chart"""
    try:
        import plotly.graph_objects as go
        
        # Calculate average WCS distance per player across all epochs
        player_stats = combined_df.groupby('Player_Name')['WCS_Distance_m'].mean().sort_values(ascending=False)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=player_stats.index,
            y=player_stats.values,
            marker_color='#4ECDC4',
            hovertemplate='Player: %{x}<br>Avg Distance: %{y:.1f}m<extra></extra>'
        ))
        
        fig.update_layout(
            title="Average WCS Distance by Player (All Epochs)",
            xaxis_title="Player",
            yaxis_title="Mean WCS Distance (m)",
            height=400,
            xaxis_tickangle=-45
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating player comparison: {str(e)}")
        return None


def create_player_epoch_heatmap(combined_df: pd.DataFrame):
    """Create player vs epoch heatmap"""
    try:
        import plotly.graph_objects as go
        
        # Filter for Default Threshold only
        df_filtered = combined_df[combined_df['Threshold_Type'] == 'Default Threshold']
        
        # Create pivot table
        pivot_df = df_filtered.pivot_table(
            values='WCS_Distance_m',
            index='Player_Name',
            columns='Epoch_Duration_Minutes',
            aggfunc='mean'
        )
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            colorscale='RdYlBu_r',
            hovertemplate='Player: %{y}<br>Epoch: %{x}min<br>Distance: %{z:.1f}m<extra></extra>'
        ))
        
        fig.update_layout(
            title="WCS Distance Heatmap by Player and Epoch",
            xaxis_title="Epoch Duration (minutes)",
            yaxis_title="Player",
            height=400
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating player epoch heatmap: {str(e)}")
        return None


def create_individual_player_grid(all_results: List[Dict[str, Any]]):
    """Create individual player analysis grid"""
    try:
        from plotly.subplots import make_subplots
        import plotly.graph_objects as go
        
        # Limit to first 3 players for better readability and prevent overlapping
        max_players = min(3, len(all_results))
        selected_results = all_results[:max_players]
        
        # Create subplots with better spacing
        fig = make_subplots(
            rows=max_players, cols=2,
            subplot_titles=[f"{result['metadata'].get('player_name', 'Unknown')} - Velocity Profile" for result in selected_results] +
                          [f"{result['metadata'].get('player_name', 'Unknown')} - Epoch Comparison" for result in selected_results],
            vertical_spacing=0.15,  # Increased spacing
            horizontal_spacing=0.15,  # Increased spacing
            specs=[[{"secondary_y": False}, {"secondary_y": False}] for _ in range(max_players)]
        )
        
        for i, result in enumerate(selected_results):
            row = i + 1
            player_name = result['metadata'].get('player_name', 'Unknown')
            
            # Get data from the correct structure
            results_data = result['results']
            if isinstance(results_data, dict):
                processed_data = results_data.get('processed_data')
                wcs_results = results_data.get('wcs_results', [])
                epoch_durations = results_data.get('epoch_durations', [])
            else:
                # Fallback for old structure
                processed_data = result.get('processed_data')
                wcs_results = result.get('wcs_results', [])
                epoch_durations = result.get('epoch_durations', [])
            
            # Velocity profile (left column)
            if processed_data is not None:
                df = processed_data
                time_data = df['Seconds'] if 'Seconds' in df.columns else np.arange(len(df)) / 10
                
                # Limit time range for better visibility (first 10 minutes)
                max_time = min(600, time_data.max())  # 10 minutes = 600 seconds
                mask = time_data <= max_time
                
                fig.add_trace(
                    go.Scatter(
                        x=time_data[mask],
                        y=df['Velocity'][mask],
                        mode='lines',
                        name=f'{player_name} - Velocity',
                        line=dict(color='#2E86AB', width=1),
                        showlegend=False
                    ),
                    row=row, col=1
                )
                
                # Add WCS period highlights (only if within time range)
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
                
                for j, epoch_result in enumerate(wcs_results):
                    if len(epoch_result) >= 8:
                        th0_start = epoch_result[2] / 10
                        th0_end = epoch_result[3] / 10
                        th0_distance = epoch_result[0]
                        
                        # Only show highlights if they're within the displayed time range
                        if th0_start <= max_time:
                            fig.add_vrect(
                                x0=th0_start, x1=min(th0_end, max_time),
                                fillcolor=colors[j % len(colors)],
                                opacity=0.3,
                                layer="below",
                                line_width=0,
                                row=row, col=1
                            )
            
            # Epoch comparison (right column)
            
            if wcs_results:
                distances = [epoch_result[0] for epoch_result in wcs_results if len(epoch_result) >= 8]
                epoch_labels = [f"{dur:.1f}min" for dur in epoch_durations[:len(distances)]]
                
                fig.add_trace(
                    go.Bar(
                        x=epoch_labels,
                        y=distances,
                        name=f'{player_name} - Epochs',
                        marker_color=colors[:len(distances)],
                        showlegend=False,
                        hovertemplate='Epoch: %{x}<br>Distance: %{y:.1f}m<extra></extra>'
                    ),
                    row=row, col=2
                )
        
        fig.update_layout(
            title="Individual Player Analysis (Top 3 Players)",
            height=300 * max_players,  # Increased height per player
            showlegend=False,
            margin=dict(l=50, r=50, t=80, b=50),  # Better margins
            font=dict(size=10)  # Smaller font for better fit
        )
        
        # Update subplot titles to be more compact
        for i in range(len(fig.layout.annotations)):
            fig.layout.annotations[i].font.size = 11
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating individual player grid: {str(e)}")
        return None 