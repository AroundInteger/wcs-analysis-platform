# WCS Analysis Implementation Guide

## Overview

The Work Capacity Score (WCS) analysis is a key feature of the sports performance platform that identifies periods of maximum accumulated work over specified time windows. This document provides comprehensive implementation details for both rolling and contiguous WCS methods with thresholding capabilities.

## Table of Contents

1. [WCS Theory](#wcs-theory)
2. [Implementation Methods](#implementation-methods)
3. [Thresholding Options](#thresholding-options)
4. [Key Functions](#key-functions)
5. [Integration with App](#integration-with-app)
6. [Testing and Validation](#testing-and-validation)
7. [Configuration Parameters](#configuration-parameters)

## WCS Theory

### Definition
WCS calculates the maximum accumulated work (distance) over a specified time window by integrating velocity over time:

```
WCS = ∫ v(t) dt
```

Where:
- `v(t)` = velocity at time t
- `dt` = time step (1/sampling_rate)
- Integration is performed over the specified epoch duration

### Sports Science Relevance
- Identifies peak performance periods
- Measures high-intensity work capacity
- Provides objective performance metrics
- Enables comparison across sessions and athletes

## Implementation Methods

### 1. Rolling WCS
**Purpose**: Flexible window positioning to find optimal work periods

**Characteristics**:
- Window can start at any sample position
- More adaptive to actual performance peaks
- Generally finds higher WCS values
- Better for identifying true performance maxima

**Algorithm**:
```python
def calculate_wcs_period_rolling(velocity_data, epoch_duration, sampling_rate, threshold_min=0.0, threshold_max=100.0):
    # Convert epoch duration to samples
    epoch_samples = int(epoch_duration * 60 * sampling_rate)
    
    # Slide window through all possible positions
    for i in range(len(velocity_data) - epoch_samples + 1):
        window_data = velocity_data[i:i + epoch_samples]
        
        # Apply thresholding
        threshold_mask = (window_data >= threshold_min) & (window_data <= threshold_max)
        window_data_thresholded = window_data[threshold_mask]
        
        # Calculate distance
        time_per_sample = 1.0 / sampling_rate
        window_distance = np.sum(window_data_thresholded * time_per_sample)
        
        # Track maximum
        if window_distance > max_distance:
            max_distance = window_distance
            start_index = i
            end_index = i + epoch_samples
```

### 2. Contiguous WCS
**Purpose**: Fixed epoch alignment for standardized analysis

**Characteristics**:
- Windows align with fixed epoch boundaries
- More structured and consistent
- Better for standardized comparisons
- Useful for time-based analysis

**Algorithm**:
```python
def calculate_wcs_period_contiguous(velocity_data, epoch_duration, sampling_rate, threshold_min=0.0, threshold_max=100.0):
    # Convert epoch duration to samples
    epoch_samples = int(epoch_duration * 60 * sampling_rate)
    
    # Calculate number of complete epochs
    num_complete_epochs = len(velocity_data) // epoch_samples
    
    # Check each complete epoch
    for epoch_idx in range(num_complete_epochs):
        start_idx = epoch_idx * epoch_samples
        end_idx = start_idx + epoch_samples
        
        window_data = velocity_data[start_idx:end_idx]
        
        # Apply thresholding and calculate distance
        threshold_mask = (window_data >= threshold_min) & (window_data <= threshold_max)
        window_data_thresholded = window_data[threshold_mask]
        
        time_per_sample = 1.0 / sampling_rate
        window_distance = np.sum(window_data_thresholded * time_per_sample)
        
        # Track maximum
        if window_distance > max_distance:
            max_distance = window_distance
            start_index = start_idx
            end_index = end_idx
```

## Thresholding Options

### 1. Velocity Thresholding
**Purpose**: Focus on high-intensity velocity ranges

**Implementation**:
```python
# Apply velocity threshold
threshold_mask = (velocity_data >= velocity_min) & (velocity_data <= velocity_max)
thresholded_velocity = velocity_data[threshold_mask]
```

**Example**: `velocity_min = 5.0 m/s` filters out low-intensity periods

### 2. Acceleration Thresholding
**Purpose**: Focus on dynamic periods with significant acceleration/deceleration

**Implementation**:
```python
# Calculate acceleration
acceleration = calculate_acceleration(velocity_data, sampling_rate)

# Apply acceleration threshold
accel_threshold = 0.5  # m/s²
threshold_mask = np.abs(acceleration) >= accel_threshold

# Set both velocity and acceleration to zero where threshold not met
thresholded_velocity = np.where(threshold_mask, velocity_data, 0.0)
thresholded_acceleration = np.where(threshold_mask, acceleration, 0.0)
```

**Example**: `|acceleration| >= 0.5 m/s²` focuses on dynamic periods

## Key Functions

### Core WCS Functions

#### `calculate_wcs_period_rolling()`
```python
def calculate_wcs_period_rolling(velocity_data, epoch_duration, sampling_rate, threshold_min=0.0, threshold_max=100.0):
    """
    Calculate WCS using rolling window approach
    
    Args:
        velocity_data: Array of velocity values
        epoch_duration: Duration of epoch in minutes
        sampling_rate: Sampling rate in Hz
        threshold_min: Minimum velocity threshold
        threshold_max: Maximum velocity threshold
        
    Returns:
        Tuple of (max_distance, max_time, start_index, end_index)
    """
```

#### `calculate_wcs_period_contiguous()`
```python
def calculate_wcs_period_contiguous(velocity_data, epoch_duration, sampling_rate, threshold_min=0.0, threshold_max=100.0):
    """
    Calculate WCS using contiguous epoch approach
    
    Args:
        velocity_data: Array of velocity values
        epoch_duration: Duration of epoch in minutes
        sampling_rate: Sampling rate in Hz
        threshold_min: Minimum velocity threshold
        threshold_max: Maximum velocity threshold
        
    Returns:
        Tuple of (max_distance, max_time, start_index, end_index)
    """
```

#### `calculate_acceleration()`
```python
def calculate_acceleration(velocity_data, sampling_rate):
    """
    Calculate acceleration using central difference method
    
    Args:
        velocity_data: Array of velocity values
        sampling_rate: Sampling rate in Hz
        
    Returns:
        Array of acceleration values
    """
```

### Main Analysis Function

#### `perform_wcs_analysis()`
```python
def perform_wcs_analysis(df, metadata, file_type_info, parameters):
    """
    Perform complete WCS analysis on processed DataFrame
    
    Args:
        df: Processed DataFrame with velocity data
        metadata: File metadata dictionary
        file_type_info: File type information
        parameters: Analysis parameters dictionary
        
    Returns:
        Dictionary containing rolling and contiguous WCS results
    """
```

## Integration with App

### 1. App Configuration
Add WCS parameters to the app configuration:

```yaml
# config/app_config.yaml
wcs_analysis:
  default_epoch_duration: 20.0  # seconds
  default_velocity_threshold_min: 0.0  # m/s
  default_velocity_threshold_max: 100.0  # m/s
  default_acceleration_threshold: 0.5  # m/s²
  enable_acceleration_thresholding: true
  enable_velocity_thresholding: true
```

### 2. Streamlit UI Components

#### WCS Settings Panel
```python
def render_wcs_settings():
    st.subheader("WCS Analysis Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        epoch_duration = st.slider(
            "Epoch Duration (seconds)",
            min_value=5.0,
            max_value=60.0,
            value=20.0,
            step=5.0,
            help="Duration of WCS analysis window"
        )
        
        velocity_threshold_min = st.number_input(
            "Min Velocity Threshold (m/s)",
            min_value=0.0,
            max_value=20.0,
            value=0.0,
            step=0.5,
            help="Minimum velocity for inclusion in WCS calculation"
        )
    
    with col2:
        velocity_threshold_max = st.number_input(
            "Max Velocity Threshold (m/s)",
            min_value=0.0,
            max_value=50.0,
            value=100.0,
            step=1.0,
            help="Maximum velocity for inclusion in WCS calculation"
        )
        
        acceleration_threshold = st.number_input(
            "Acceleration Threshold (m/s²)",
            min_value=0.0,
            max_value=10.0,
            value=0.5,
            step=0.1,
            help="Minimum acceleration magnitude for inclusion"
        )
    
    return {
        'epoch_duration': epoch_duration / 60.0,  # Convert to minutes
        'velocity_threshold_min': velocity_threshold_min,
        'velocity_threshold_max': velocity_threshold_max,
        'acceleration_threshold': acceleration_threshold
    }
```

#### WCS Results Display
```python
def render_wcs_results(wcs_results):
    st.subheader("WCS Analysis Results")
    
    if not wcs_results:
        st.warning("No WCS results available")
        return
    
    # Create tabs for different methods
    tab1, tab2 = st.tabs(["Rolling WCS", "Contiguous WCS"])
    
    with tab1:
        rolling_results = wcs_results.get('rolling_wcs_results', [])
        if rolling_results:
            display_wcs_table(rolling_results, "Rolling WCS")
        else:
            st.info("No rolling WCS results available")
    
    with tab2:
        contiguous_results = wcs_results.get('contiguous_wcs_results', [])
        if contiguous_results:
            display_wcs_table(contiguous_results, "Contiguous WCS")
        else:
            st.info("No contiguous WCS results available")
```

### 3. Data Processing Pipeline

#### Main App Integration
```python
def process_files_with_wcs(uploaded_files, wcs_parameters):
    """
    Process uploaded files with WCS analysis
    
    Args:
        uploaded_files: List of uploaded files
        wcs_parameters: WCS analysis parameters
        
    Returns:
        Dictionary containing processed results
    """
    results = []
    
    for file in uploaded_files:
        # Process file
        df, metadata, file_type_info = process_single_file(file)
        
        # Perform WCS analysis
        wcs_results = perform_wcs_analysis(df, metadata, file_type_info, wcs_parameters)
        
        # Store results
        results.append({
            'filename': file.name,
            'metadata': metadata,
            'wcs_results': wcs_results
        })
    
    return results
```

## Testing and Validation

### 1. Test Data Generation
```python
def create_test_velocity_data():
    """Create synthetic velocity data for testing"""
    sampling_rate = 10  # Hz
    duration_seconds = 120
    num_samples = duration_seconds * sampling_rate
    time_seconds = np.linspace(0, duration_seconds, num_samples)
    
    # Create smooth velocity profile with known characteristics
    velocities = np.zeros(num_samples)
    
    for i, t in enumerate(time_seconds):
        baseline = 2.0
        
        # Dynamic phases with smooth transitions
        if 20 <= t <= 40:
            phase_progress = (t - 20) / 20
            intensity = 6.0 * phase_progress ** 2
        elif 40 < t <= 60:
            phase_progress = (60 - t) / 20
            intensity = 6.0 * phase_progress ** 2
        elif 70 <= t <= 90:
            envelope = np.exp(-0.5 * ((t - 80) / 8) ** 2)
            oscillation = np.sin((t - 70) * np.pi / 10) ** 2
            intensity = 4.0 * envelope * oscillation
        else:
            intensity = 0
        
        velocities[i] = baseline + intensity
    
    return velocities, time_seconds, sampling_rate
```

### 2. Validation Tests
```python
def test_wcs_implementation():
    """Test WCS implementation with synthetic data"""
    
    # Create test data
    velocities, time_seconds, sampling_rate = create_test_velocity_data()
    
    # Test parameters
    epoch_duration = 20.0 / 60.0  # 20 seconds in minutes
    
    # Test rolling WCS
    rolling_distance, rolling_time, rolling_start, rolling_end = calculate_wcs_period_rolling(
        velocities, epoch_duration, sampling_rate, 0.0, 100.0
    )
    
    # Test contiguous WCS
    contiguous_distance, contiguous_time, contiguous_start, contiguous_end = calculate_wcs_period_contiguous(
        velocities, epoch_duration, sampling_rate, 0.0, 100.0
    )
    
    # Validate results
    assert rolling_distance > 0, "Rolling WCS should find positive distance"
    assert contiguous_distance > 0, "Contiguous WCS should find positive distance"
    assert rolling_distance >= contiguous_distance, "Rolling WCS should be >= contiguous WCS"
    
    print(f"✅ WCS Implementation Test Passed")
    print(f"   Rolling WCS: {rolling_distance:.1f}m at t={time_seconds[rolling_start + (rolling_end - rolling_start) // 2]:.1f}s")
    print(f"   Contiguous WCS: {contiguous_distance:.1f}m at t={time_seconds[contiguous_start + (contiguous_end - contiguous_start) // 2]:.1f}s")
```

## Configuration Parameters

### Default Parameters
```python
DEFAULT_WCS_PARAMETERS = {
    'epoch_duration': 20.0 / 60.0,  # 20 seconds in minutes
    'velocity_threshold_min': 0.0,  # m/s
    'velocity_threshold_max': 100.0,  # m/s
    'acceleration_threshold': 0.5,  # m/s²
    'enable_velocity_thresholding': False,
    'enable_acceleration_thresholding': False
}
```

### Parameter Validation
```python
def validate_wcs_parameters(parameters):
    """
    Validate WCS analysis parameters
    
    Args:
        parameters: Dictionary of WCS parameters
        
    Returns:
        Boolean indicating if parameters are valid
    """
    required_keys = ['epoch_duration', 'velocity_threshold_min', 'velocity_threshold_max']
    
    # Check required keys
    for key in required_keys:
        if key not in parameters:
            return False
    
    # Validate ranges
    if parameters['epoch_duration'] <= 0:
        return False
    
    if parameters['velocity_threshold_min'] < 0:
        return False
    
    if parameters['velocity_threshold_max'] <= parameters['velocity_threshold_min']:
        return False
    
    return True
```

## Best Practices

### 1. Data Quality
- Ensure smooth velocity data (no discontinuities)
- Use appropriate sampling rates (10 Hz minimum)
- Validate input data ranges

### 2. Parameter Selection
- Choose epoch duration based on sport requirements
- Set realistic velocity thresholds
- Use acceleration thresholding for dynamic sports

### 3. Performance Optimization
- Pre-allocate arrays for large datasets
- Use vectorized operations where possible
- Consider parallel processing for batch analysis

### 4. Error Handling
- Validate all input parameters
- Handle edge cases (insufficient data, all-zero velocities)
- Provide meaningful error messages

## Troubleshooting

### Common Issues

1. **Zero WCS Results**
   - Check if velocity thresholds are too restrictive
   - Verify data contains non-zero velocities
   - Ensure epoch duration is appropriate

2. **Identical Rolling and Contiguous Results**
   - This is normal when optimal window aligns with epoch boundaries
   - Check if data has clear performance peaks

3. **High Memory Usage**
   - Reduce sampling rate for large datasets
   - Process files in batches
   - Use streaming for very large files

### Debug Mode
```python
def enable_wcs_debug_mode():
    """Enable debug mode for WCS analysis"""
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Add debug prints to key functions
    # Log intermediate calculations
    # Save intermediate results for inspection
```

## Conclusion

This WCS analysis implementation provides a robust foundation for sports performance analysis. The combination of rolling and contiguous methods with flexible thresholding options enables comprehensive performance assessment across different sports and analysis requirements.

Key success factors:
- Proper parameter selection
- Data quality validation
- Comprehensive testing
- Clear user interface
- Robust error handling

The implementation is ready for integration into the main application with appropriate UI components and configuration options. 