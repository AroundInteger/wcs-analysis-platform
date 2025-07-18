"""
WCS Analysis Module for WCS Analysis Platform

Implements MATLAB-equivalent Worst Case Scenario analysis algorithms
for GPS velocity data processing.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import streamlit as st


def process_velocity_data(df: pd.DataFrame, sampling_rate: int = 10) -> pd.DataFrame:
    """
    Process velocity data to 10Hz sampling rate
    
    Args:
        df: DataFrame with velocity data
        sampling_rate: Target sampling rate (default 10Hz)
        
    Returns:
        Processed DataFrame with standardized velocity data
    """
    try:
        # Ensure we have required columns
        if 'Velocity' not in df.columns:
            st.error("Velocity column not found in data")
            return df
        
        # Create time index if not present
        if 'Seconds' not in df.columns:
            # Create time index based on row number and sampling rate
            df['Seconds'] = np.arange(len(df)) / sampling_rate
        
        # Ensure velocity data is numeric
        df['Velocity'] = pd.to_numeric(df['Velocity'], errors='coerce')
        
        # Remove any NaN values
        df = df.dropna(subset=['Velocity'])
        
        # Reset index for clean processing
        df = df.reset_index(drop=True)
        
        # Create standardized time index
        df['Seconds'] = np.arange(len(df)) / sampling_rate
        
        return df
        
    except Exception as e:
        st.error(f"Error processing velocity data: {str(e)}")
        return df


def calculate_wcs_period(velocity_data: np.ndarray, 
                        epoch_duration: float, 
                        sampling_rate: int = 10,
                        threshold_min: float = 0.0,
                        threshold_max: float = 100.0) -> Tuple[float, float, int, int]:
    """
    Calculate WCS period for given epoch duration and threshold
    
    Args:
        velocity_data: Array of velocity values
        epoch_duration: Duration of epoch in minutes
        sampling_rate: Sampling rate in Hz
        threshold_min: Minimum velocity threshold
        threshold_max: Maximum velocity threshold
        
    Returns:
        Tuple of (max_distance, max_time, start_index, end_index)
    """
    try:
        # Convert epoch duration to samples
        epoch_samples = int(epoch_duration * 60 * sampling_rate)
        
        if len(velocity_data) < epoch_samples:
            # If data is shorter than epoch, use all available data
            epoch_samples = len(velocity_data)
        
        # Apply velocity threshold
        threshold_mask = (velocity_data >= threshold_min) & (velocity_data <= threshold_max)
        
        # Calculate cumulative distance for each window
        max_distance = 0
        max_time = 0
        start_index = 0
        end_index = 0
        
        # Slide window through data
        for i in range(len(velocity_data) - epoch_samples + 1):
            window_data = velocity_data[i:i + epoch_samples]
            window_mask = threshold_mask[i:i + epoch_samples]
            
            # Calculate distance for this window (velocity * time)
            # Each sample represents 1/sampling_rate seconds
            time_per_sample = 1.0 / sampling_rate
            window_distance = np.sum(window_data[window_mask] * time_per_sample)
            
            # Calculate time within threshold
            window_time = np.sum(window_mask) * time_per_sample
            
            # Update maximum if this window has higher distance
            if window_distance > max_distance:
                max_distance = window_distance
                max_time = window_time
                start_index = i
                end_index = i + epoch_samples
        
        return max_distance, max_time, start_index, end_index
        
    except Exception as e:
        st.error(f"Error calculating WCS period: {str(e)}")
        return 0.0, 0.0, 0, 0


def perform_wcs_analysis(uploaded_file, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Perform complete WCS analysis on uploaded file
    
    Args:
        uploaded_file: Streamlit uploaded file or file path
        parameters: Analysis parameters dictionary
        
    Returns:
        Dictionary containing analysis results
    """
    try:
        # Import file ingestion function
        from .file_ingestion import read_csv_with_metadata, validate_velocity_data
        
        # Read file
        df, metadata, file_type_info = read_csv_with_metadata(uploaded_file)
        
        if df is None or metadata is None:
            st.error("Failed to read file")
            return None
        
        # Validate velocity data
        if not validate_velocity_data(df):
            st.error("Velocity data validation failed")
            return None
        
        # Process velocity data to 10Hz
        sampling_rate = parameters.get('sampling_rate', 10)
        processed_df = process_velocity_data(df, sampling_rate)
        
        # Extract velocity data
        velocity_data = processed_df['Velocity'].values
        
        # Calculate velocity statistics
        velocity_stats = {
            'mean': float(np.mean(velocity_data)),
            'max': float(np.max(velocity_data)),
            'min': float(np.min(velocity_data)),
            'std': float(np.std(velocity_data)),
            'total_samples': len(velocity_data),
            'duration_seconds': len(velocity_data) / sampling_rate
        }
        
        # Perform WCS analysis for different epoch durations
        epoch_durations = parameters.get('epoch_durations', [1.0])
        th0_min = parameters.get('th0_min', 0.0)
        th0_max = parameters.get('th0_max', 100.0)
        th1_min = parameters.get('th1_min', 5.0)
        th1_max = parameters.get('th1_max', 100.0)
        
        wcs_results = []
        
        for epoch_duration in epoch_durations:
            # Calculate WCS for TH_0 threshold
            th0_distance, th0_time, th0_start, th0_end = calculate_wcs_period(
                velocity_data, epoch_duration, sampling_rate, th0_min, th0_max
            )
            
            # Calculate WCS for TH_1 threshold
            th1_distance, th1_time, th1_start, th1_end = calculate_wcs_period(
                velocity_data, epoch_duration, sampling_rate, th1_min, th1_max
            )
            
            # Store results for this epoch
            epoch_results = [
                th0_distance, th0_time, th0_start, th0_end,
                th1_distance, th1_time, th1_start, th1_end,
                epoch_duration
            ]
            wcs_results.append(epoch_results)
        
        # Prepare final results
        results = {
            'processed_data': processed_df,
            'velocity_stats': velocity_stats,
            'wcs_results': wcs_results,
            'parameters': parameters,
            'metadata': metadata,
            'file_type_info': file_type_info
        }
        
        return results
        
    except Exception as e:
        st.error(f"Error in WCS analysis: {str(e)}")
        return None


def calculate_summary_statistics(wcs_results: List[List]) -> Dict[str, Any]:
    """
    Calculate summary statistics from WCS results
    
    Args:
        wcs_results: List of WCS results for different epochs
        
    Returns:
        Dictionary of summary statistics
    """
    try:
        if not wcs_results:
            return {}
        
        # Extract distances and times
        th0_distances = [result[0] for result in wcs_results]
        th0_times = [result[1] for result in wcs_results]
        th1_distances = [result[4] for result in wcs_results]
        th1_times = [result[5] for result in wcs_results]
        
        summary = {
            'th0_max_distance': max(th0_distances) if th0_distances else 0,
            'th0_max_time': max(th0_times) if th0_times else 0,
            'th1_max_distance': max(th1_distances) if th1_distances else 0,
            'th1_max_time': max(th1_times) if th1_times else 0,
            'th0_mean_distance': np.mean(th0_distances) if th0_distances else 0,
            'th1_mean_distance': np.mean(th1_distances) if th1_distances else 0,
            'total_epochs': len(wcs_results)
        }
        
        return summary
        
    except Exception as e:
        st.error(f"Error calculating summary statistics: {str(e)}")
        return {}


def validate_parameters(parameters: Dict[str, Any]) -> bool:
    """
    Validate analysis parameters
    
    Args:
        parameters: Dictionary of analysis parameters
        
    Returns:
        True if parameters are valid, False otherwise
    """
    try:
        required_keys = ['sampling_rate', 'epoch_duration', 'th0_min', 'th0_max', 'th1_min', 'th1_max']
        
        for key in required_keys:
            if key not in parameters:
                st.error(f"Missing required parameter: {key}")
                return False
        
        # Validate ranges
        if parameters['th0_min'] >= parameters['th0_max']:
            st.error("TH_0 minimum must be less than TH_0 maximum")
            return False
        
        if parameters['th1_min'] >= parameters['th1_max']:
            st.error("TH_1 minimum must be less than TH_1 maximum")
            return False
        
        if parameters['sampling_rate'] <= 0:
            st.error("Sampling rate must be positive")
            return False
        
        if parameters['epoch_duration'] <= 0:
            st.error("Epoch duration must be positive")
            return False
        
        return True
        
    except Exception as e:
        st.error(f"Error validating parameters: {str(e)}")
        return False 