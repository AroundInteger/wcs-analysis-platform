"""
WCS Analysis Module for WCS Analysis Platform

Implements MATLAB-equivalent Worst Case Scenario analysis algorithms
for GPS velocity data processing.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import streamlit as st


def calculate_acceleration(velocity_data: np.ndarray, sampling_rate: int = 10) -> np.ndarray:
    """
    Calculate acceleration by differentiating velocity signal
    
    Args:
        velocity_data: Array of velocity values (m/s)
        sampling_rate: Sampling rate in Hz
        
    Returns:
        Array of acceleration values (m/s²)
    """
    try:
        if len(velocity_data) < 2:
            return np.array([])
        
        # Calculate time step
        dt = 1.0 / sampling_rate
        
        # Use central difference for interior points
        acceleration = np.zeros_like(velocity_data)
        
        # Forward difference for first point
        if len(velocity_data) > 1:
            acceleration[0] = (velocity_data[1] - velocity_data[0]) / dt
        
        # Central difference for interior points
        for i in range(1, len(velocity_data) - 1):
            acceleration[i] = (velocity_data[i + 1] - velocity_data[i - 1]) / (2 * dt)
        
        # Backward difference for last point
        if len(velocity_data) > 1:
            acceleration[-1] = (velocity_data[-1] - velocity_data[-2]) / dt
        
        return acceleration
        
    except Exception as e:
        # st.error(f"Error calculating acceleration: {str(e)}")  # Removed to avoid UI issues
        return np.zeros_like(velocity_data)


def calculate_distance(velocity_data: np.ndarray, sampling_rate: int = 10) -> np.ndarray:
    """
    Calculate cumulative distance by integrating velocity signal
    
    Args:
        velocity_data: Array of velocity values (m/s)
        sampling_rate: Sampling rate in Hz
        
    Returns:
        Array of cumulative distance values (m)
    """
    try:
        if len(velocity_data) == 0:
            return np.array([])
        
        # Calculate time step
        dt = 1.0 / sampling_rate
        
        # Use trapezoidal integration for better accuracy
        distance = np.zeros_like(velocity_data)
        
        # First point (no distance yet)
        distance[0] = 0.0
        
        # Integrate using trapezoidal rule
        for i in range(1, len(velocity_data)):
            # Average velocity between points * time step
            avg_velocity = (velocity_data[i] + velocity_data[i-1]) / 2
            distance[i] = distance[i-1] + avg_velocity * dt
        
        return distance
        
    except Exception as e:
        # st.error(f"Error calculating distance: {str(e)}")  # Removed to avoid UI issues
        return np.zeros_like(velocity_data)


def calculate_kinematic_parameters(velocity_data: np.ndarray, sampling_rate: int = 10) -> Dict[str, np.ndarray]:
    """
    Calculate comprehensive kinematic parameters from velocity signal
    
    Args:
        velocity_data: Array of velocity values (m/s)
        sampling_rate: Sampling rate in Hz
        
    Returns:
        Dictionary containing acceleration, distance, and other kinematic parameters
    """
    try:
        # Calculate acceleration
        acceleration = calculate_acceleration(velocity_data, sampling_rate)
        
        # Calculate cumulative distance
        distance = calculate_distance(velocity_data, sampling_rate)
        
        # Calculate time array
        time = np.arange(len(velocity_data)) / sampling_rate
        
        # Calculate additional parameters
        # Instantaneous power (P = F*v = m*|a|*v, assuming m=1 for relative comparison)
        # Using absolute acceleration ensures power is always positive and meaningful
        power = np.abs(acceleration) * velocity_data
        
        # Deceleration (negative acceleration) - useful for sports analysis
        deceleration = np.where(acceleration < 0, -acceleration, 0)
        
        # Rate of change of acceleration (jerk)
        jerk = calculate_acceleration(acceleration, sampling_rate) if len(acceleration) > 2 else np.zeros_like(acceleration)
        
        # Calculate moving averages for smoothing
        window_size = min(5, len(velocity_data) // 10)  # Adaptive window size
        if window_size > 1:
            velocity_smooth = np.convolve(velocity_data, np.ones(window_size)/window_size, mode='same')
            acceleration_smooth = np.convolve(acceleration, np.ones(window_size)/window_size, mode='same')
        else:
            velocity_smooth = velocity_data
            acceleration_smooth = acceleration
        
        kinematic_params = {
            'time': time,
            'velocity': velocity_data,
            'velocity_smooth': velocity_smooth,
            'acceleration': acceleration,
            'acceleration_smooth': acceleration_smooth,
            'deceleration': deceleration,
            'distance': distance,
            'power': power,
            'jerk': jerk,
            'sampling_rate': sampling_rate
        }
        
        return kinematic_params
        
    except Exception as e:
        # st.error(f"Error calculating kinematic parameters: {str(e)}")  # Removed to avoid UI issues
        return {}


def process_velocity_data(df: pd.DataFrame, sampling_rate: int = 10) -> pd.DataFrame:
    """
    Process velocity data to 10Hz sampling rate and calculate kinematic parameters
    
    Args:
        df: DataFrame with velocity data
        sampling_rate: Target sampling rate (default 10Hz)
        
    Returns:
        Processed DataFrame with standardized velocity data and kinematic parameters
    """
    try:
        # Ensure we have required columns
        if 'Velocity' not in df.columns:
            # st.error("Velocity column not found in data")  # Removed to avoid UI issues
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
        
        # Calculate kinematic parameters
        velocity_data = df['Velocity'].values
        kinematic_params = calculate_kinematic_parameters(velocity_data, sampling_rate)
        
        # Add kinematic parameters to DataFrame
        if kinematic_params:
            df['Acceleration'] = kinematic_params['acceleration']
            df['Deceleration'] = kinematic_params['deceleration']
            df['Distance'] = kinematic_params['distance']
            df['Power'] = kinematic_params['power']
            df['Jerk'] = kinematic_params['jerk']
            df['Velocity_Smooth'] = kinematic_params['velocity_smooth']
            df['Acceleration_Smooth'] = kinematic_params['acceleration_smooth']
        
        return df
        
    except Exception as e:
        # st.error(f"Error processing velocity data: {str(e)}")  # Removed to avoid UI issues
        return df


def calculate_wcs_period_rolling(velocity_data: np.ndarray, 
                                epoch_duration: float, 
                                sampling_rate: int = 10,
                                threshold_min: float = 0.0,
                                threshold_max: float = 100.0) -> Tuple[float, float, int, int]:
    """
    Calculate WCS period using rolling window approach with central point focus
    
    This method uses the central point of each window as the focal point,
    and calculates the maximum accumulated work (area under the curve) over the specified time period.
    
    IMPORTANT: Rolling WCS applies thresholding to only include velocity data points
    that are within the threshold range (>= threshold_min and <= threshold_max).
    
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
        
        # Calculate cumulative distance for each window
        max_distance = 0
        max_time = 0
        start_index = 0
        end_index = 0
        
        # Calculate half-window size for central point focus
        half_window = epoch_samples // 2
        
        # Slide window through data with central point focus
        for i in range(half_window, len(velocity_data) - half_window):
            # Window is centered on point i
            window_start = i - half_window
            window_end = i + half_window + (1 if epoch_samples % 2 == 1 else 0)  # Handle odd window sizes
            
            window_data = velocity_data[window_start:window_end]
            
            # Apply velocity threshold - only include data points within threshold range
            threshold_mask = (window_data >= threshold_min) & (window_data <= threshold_max)
            window_data_thresholded = window_data[threshold_mask]
            
            # Calculate distance for this window (velocity * time)
            # Each sample represents 1/sampling_rate seconds
            time_per_sample = 1.0 / sampling_rate
            window_distance = np.sum(window_data_thresholded * time_per_sample)
            
            # Calculate time within threshold
            window_time = len(window_data_thresholded) * time_per_sample
            
            # Update maximum if this window has higher distance AND has data within threshold
            if window_distance > max_distance and len(window_data_thresholded) > 0:
                max_distance = window_distance
                max_time = window_time
                start_index = window_start
                end_index = window_end
        
        return max_distance, max_time, start_index, end_index
        
    except Exception as e:
        # st.error(f"Error calculating WCS period (rolling): {str(e)}")  # Removed to avoid UI issues
        return 0.0, 0.0, 0, 0


def calculate_wcs_period_contiguous(velocity_data: np.ndarray, 
                                   epoch_duration: float, 
                                   sampling_rate: int = 10,
                                   threshold_min: float = 0.0,
                                   threshold_max: float = 100.0) -> Tuple[float, float, int, int]:
    """
    Calculate WCS period using contiguous epoch approach
    
    This finds the best continuous period of exactly the specified duration,
    rather than using a rolling window approach.
    
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
        
        # Find best contiguous period using fixed epoch boundaries
        # Calculate how many complete epochs fit in the data
        num_complete_epochs = len(velocity_data) // epoch_samples
        
        for epoch_idx in range(num_complete_epochs):
            # Calculate start and end indices for this epoch
            start_idx = epoch_idx * epoch_samples
            end_idx = start_idx + epoch_samples
            
            window_data = velocity_data[start_idx:end_idx]
            window_mask = threshold_mask[start_idx:end_idx]
            
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
                start_index = start_idx
                end_index = end_idx
        
        return max_distance, max_time, start_index, end_index
        
    except Exception as e:
        # st.error(f"Error calculating WCS period (contiguous): {str(e)}")  # Removed to avoid UI issues
        return 0.0, 0.0, 0, 0


def calculate_wcs_period(velocity_data: np.ndarray, 
                        epoch_duration: float, 
                        sampling_rate: int = 10,
                        threshold_min: float = 0.0,
                        threshold_max: float = 100.0,
                        method: str = 'rolling') -> Tuple[float, float, int, int]:
    """
    Calculate WCS period for given epoch duration and threshold
    
    Args:
        velocity_data: Array of velocity values
        epoch_duration: Duration of epoch in minutes
        sampling_rate: Sampling rate in Hz
        threshold_min: Minimum velocity threshold
        threshold_max: Maximum velocity threshold
        method: Analysis method - 'rolling' or 'contiguous'
        
    Returns:
        Tuple of (max_distance, max_time, start_index, end_index)
    """
    if method == 'contiguous':
        return calculate_wcs_period_contiguous(velocity_data, epoch_duration, sampling_rate, threshold_min, threshold_max)
    else:
        return calculate_wcs_period_rolling(velocity_data, epoch_duration, sampling_rate, threshold_min, threshold_max)


def perform_wcs_analysis(df: pd.DataFrame, metadata: Dict[str, Any], file_type_info: Dict[str, Any], parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Perform complete WCS analysis on processed DataFrame
    
    Args:
        df: Processed DataFrame with velocity data
        metadata: File metadata dictionary
        file_type_info: File type information
        parameters: Analysis parameters dictionary
        
    Returns:
        Dictionary containing analysis results
    """
    try:
        # Validate velocity data
        from src.file_ingestion import validate_velocity_data
        
        if not validate_velocity_data(df):
            # st.error("Velocity data validation failed")  # Removed to avoid UI issues
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
        
        # Calculate kinematic statistics
        kinematic_stats = {}
        if 'Acceleration' in processed_df.columns:
            accel_data = processed_df['Acceleration'].values
            # Calculate mean acceleration (positive values only)
            positive_accel = accel_data[accel_data > 0]
            # Calculate mean deceleration (negative values only, but store as positive)
            negative_accel = accel_data[accel_data < 0]
            
            kinematic_stats['acceleration'] = {
                'mean_positive': float(np.mean(positive_accel)) if len(positive_accel) > 0 else 0.0,
                'mean_negative': float(np.mean(negative_accel)) if len(negative_accel) > 0 else 0.0,
                'mean_overall': float(np.mean(accel_data)),  # Overall mean (should be close to 0)
                'max': float(np.max(accel_data)),
                'min': float(np.min(accel_data)),
                'std': float(np.std(accel_data)),
                'positive_count': len(positive_accel),
                'negative_count': len(negative_accel),
                'total_samples': len(accel_data)
            }
        
        if 'Deceleration' in processed_df.columns:
            decel_data = processed_df['Deceleration'].values
            # Only calculate mean over non-zero deceleration periods
            non_zero_decel = decel_data[decel_data > 0]
            kinematic_stats['deceleration'] = {
                'mean': float(np.mean(non_zero_decel)) if len(non_zero_decel) > 0 else 0.0,
                'max': float(np.max(decel_data)),
                'std': float(np.std(non_zero_decel)) if len(non_zero_decel) > 0 else 0.0,
                'count': len(non_zero_decel),  # Number of deceleration events
                'total_samples': len(decel_data)
            }
        
        if 'Distance' in processed_df.columns:
            distance_data = processed_df['Distance'].values
            kinematic_stats['distance'] = {
                'total': float(distance_data[-1]) if len(distance_data) > 0 else 0.0,
                'mean_rate': float(distance_data[-1] / (len(velocity_data) / sampling_rate)) if len(velocity_data) > 0 else 0.0
            }
        
        if 'Power' in processed_df.columns:
            power_data = processed_df['Power'].values
            kinematic_stats['power'] = {
                'mean': float(np.mean(power_data)),
                'max': float(np.max(power_data)),
                'min': float(np.min(power_data)),
                'std': float(np.std(power_data))
            }
        
        # Perform WCS analysis for different epoch durations
        epoch_durations = parameters.get('epoch_durations', [1.0])
        th0_min = parameters.get('th0_min', 0.0)
        th0_max = parameters.get('th0_max', 100.0)
        th1_min = parameters.get('th1_min', 5.0)
        th1_max = parameters.get('th1_max', 100.0)
        
        # Apply thresholding if enabled
        enable_thresholding = parameters.get('enable_thresholding', False)
        if enable_thresholding:
            # Store original velocity data for comparison
            velocity_data_original = velocity_data.copy()
            
            threshold_type = parameters.get('threshold_type')
            
            if threshold_type == "Velocity":
                velocity_threshold = parameters.get('velocity_threshold', 5.0)
                # Apply velocity thresholding
                threshold_condition = velocity_data > velocity_threshold
                velocity_data = np.where(threshold_condition, velocity_data, 0.0)
                
            elif threshold_type == "Acceleration":
                acceleration_threshold = parameters.get('acceleration_threshold', 0.5)
                # Calculate acceleration and apply thresholding
                acceleration_data = calculate_acceleration(velocity_data, sampling_rate)
                threshold_condition = np.abs(acceleration_data) > acceleration_threshold
                velocity_data = np.where(threshold_condition, velocity_data, 0.0)
        
        # Log which epoch durations will be analyzed (commented out to avoid UI issues)
        # st.info(f"📊 **Analyzing {len(epoch_durations)} epoch duration(s)**: {epoch_durations} minutes")
        # st.info(f"🔍 **WCS Methods**: Rolling and Contiguous window analysis")
        
        # Calculate both rolling and contiguous WCS results
        rolling_wcs_results = []
        contiguous_wcs_results = []
        
        for epoch_duration in epoch_durations:
            # Calculate WCS for Default threshold (rolling)
            th0_distance_rolling, th0_time_rolling, th0_start_rolling, th0_end_rolling = calculate_wcs_period(
                velocity_data, epoch_duration, sampling_rate, th0_min, th0_max, 'rolling'
            )
            
            # Calculate WCS for Threshold 1 (rolling)
            th1_distance_rolling, th1_time_rolling, th1_start_rolling, th1_end_rolling = calculate_wcs_period(
                velocity_data, epoch_duration, sampling_rate, th1_min, th1_max, 'rolling'
            )
            
            # Calculate WCS for Default threshold (contiguous)
            th0_distance_contiguous, th0_time_contiguous, th0_start_contiguous, th0_end_contiguous = calculate_wcs_period(
                velocity_data, epoch_duration, sampling_rate, th0_min, th0_max, 'contiguous'
            )
            
            # Calculate WCS for Threshold 1 (contiguous)
            th1_distance_contiguous, th1_time_contiguous, th1_start_contiguous, th1_end_contiguous = calculate_wcs_period(
                velocity_data, epoch_duration, sampling_rate, th1_min, th1_max, 'contiguous'
            )
            
            # Store rolling results for this epoch
            rolling_epoch_results = [
                th0_distance_rolling, th0_time_rolling, th0_start_rolling, th0_end_rolling,
                th1_distance_rolling, th1_time_rolling, th1_start_rolling, th1_end_rolling,
                epoch_duration
            ]
            rolling_wcs_results.append(rolling_epoch_results)
            
            # Store contiguous results for this epoch
            contiguous_epoch_results = [
                th0_distance_contiguous, th0_time_contiguous, th0_start_contiguous, th0_end_contiguous,
                th1_distance_contiguous, th1_time_contiguous, th1_start_contiguous, th1_end_contiguous,
                epoch_duration
            ]
            contiguous_wcs_results.append(contiguous_epoch_results)
        
        # Prepare final results
        results = {
            'processed_data': processed_df,
            'velocity_stats': velocity_stats,
            'kinematic_stats': kinematic_stats,
            'rolling_wcs_results': rolling_wcs_results,
            'contiguous_wcs_results': contiguous_wcs_results,
            'epoch_durations': epoch_durations,
            'parameters': parameters,
            'metadata': metadata,
            'file_type_info': file_type_info
        }
        
        # Add thresholding information to results
        if enable_thresholding:
            results['thresholding_info'] = {
                'enabled': True,
                'type': threshold_type,
                'threshold_value': parameters.get('velocity_threshold') if threshold_type == "Velocity" else parameters.get('acceleration_threshold'),
                'data_reduction_percent': calculate_data_reduction_percent(velocity_data_original, velocity_data) if 'velocity_data_original' in locals() else 0.0
            }
        else:
            results['thresholding_info'] = {
                'enabled': False
            }
        
        return results
        
    except Exception as e:
        # st.error(f"Error in WCS analysis: {str(e)}")  # Removed to avoid UI issues
        return None


def calculate_summary_statistics(rolling_wcs_results: List[List], contiguous_wcs_results: List[List]) -> Dict[str, Any]:
    """
    Calculate summary statistics from both rolling and contiguous WCS results
    
    Args:
        rolling_wcs_results: List of rolling WCS results for different epochs
        contiguous_wcs_results: List of contiguous WCS results for different epochs
        
    Returns:
        Dictionary of summary statistics
    """
    try:
        summary = {}
        
        # Process rolling WCS results
        if rolling_wcs_results:
            # Extract distances and times for rolling
            th0_distances_rolling = [result[0] for result in rolling_wcs_results]
            th0_times_rolling = [result[1] for result in rolling_wcs_results]
            th1_distances_rolling = [result[4] for result in rolling_wcs_results]
            th1_times_rolling = [result[5] for result in rolling_wcs_results]
            
            summary.update({
                'rolling_th0_max_distance': max(th0_distances_rolling) if th0_distances_rolling else 0,
                'rolling_th0_max_time': max(th0_times_rolling) if th0_times_rolling else 0,
                'rolling_th1_max_distance': max(th1_distances_rolling) if th1_distances_rolling else 0,
                'rolling_th1_max_time': max(th1_times_rolling) if th1_times_rolling else 0,
                'rolling_th0_mean_distance': np.mean(th0_distances_rolling) if th0_distances_rolling else 0,
                'rolling_th1_mean_distance': np.mean(th1_distances_rolling) if th1_distances_rolling else 0,
            })
        
        # Process contiguous WCS results
        if contiguous_wcs_results:
            # Extract distances and times for contiguous
            th0_distances_contiguous = [result[0] for result in contiguous_wcs_results]
            th0_times_contiguous = [result[1] for result in contiguous_wcs_results]
            th1_distances_contiguous = [result[4] for result in contiguous_wcs_results]
            th1_times_contiguous = [result[5] for result in contiguous_wcs_results]
            
            summary.update({
                'contiguous_th0_max_distance': max(th0_distances_contiguous) if th0_distances_contiguous else 0,
                'contiguous_th0_max_time': max(th0_times_contiguous) if th0_times_contiguous else 0,
                'contiguous_th1_max_distance': max(th1_distances_contiguous) if th1_distances_contiguous else 0,
                'contiguous_th1_max_time': max(th1_times_contiguous) if th1_times_contiguous else 0,
                'contiguous_th0_mean_distance': np.mean(th0_distances_contiguous) if th0_distances_contiguous else 0,
                'contiguous_th1_mean_distance': np.mean(th1_distances_contiguous) if th1_distances_contiguous else 0,
            })
        
        # Add total epochs count
        summary['total_epochs'] = max(len(rolling_wcs_results) if rolling_wcs_results else 0, 
                                    len(contiguous_wcs_results) if contiguous_wcs_results else 0)
        
        return summary
        
    except Exception as e:
        # st.error(f"Error calculating summary statistics: {str(e)}")  # Removed to avoid UI issues
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
                # st.error(f"Missing required parameter: {key}")  # Removed to avoid UI issues
                return False
        
        # Validate ranges
        if parameters['th0_min'] >= parameters['th0_max']:
            # st.error("Default threshold minimum must be less than maximum")  # Removed to avoid UI issues
            return False
        
        if parameters['th1_min'] >= parameters['th1_max']:
            # st.error("Threshold 1 minimum must be less than maximum")  # Removed to avoid UI issues
            return False
        
        if parameters['sampling_rate'] <= 0:
            # st.error("Sampling rate must be positive")  # Removed to avoid UI issues
            return False
        
        if parameters['epoch_duration'] <= 0:
            # st.error("Epoch duration must be positive")  # Removed to avoid UI issues
            return False
        
        return True
        
    except Exception as e:
        # st.error(f"Error validating parameters: {str(e)}")  # Removed to avoid UI issues
        return False


def calculate_data_reduction_percent(original_data: np.ndarray, thresholded_data: np.ndarray) -> float:
    """
    Calculate percentage of data reduced by thresholding
    
    Args:
        original_data: Original velocity data array
        thresholded_data: Thresholded velocity data array
        
    Returns:
        Percentage of data reduction (0-100)
    """
    try:
        original_nonzero = np.sum(original_data > 0)
        thresholded_nonzero = np.sum(thresholded_data > 0)
        
        if original_nonzero == 0:
            return 0.0
        
        reduction_percent = ((original_nonzero - thresholded_nonzero) / original_nonzero) * 100
        return reduction_percent
        
    except Exception as e:
        return 0.0 