# WCS Thresholding Documentation

## Overview

This document explicitly defines how thresholding works in the Work Capacity Score (WCS) analysis. Thresholding is a key feature that allows filtering of data based on specific parameter criteria before calculating WCS.

## Thresholding Process Definition

### Basic Concept

Given a dataset with N data points (indices 0 to N-1), each containing velocity (V), acceleration (a), and odometer values, thresholding works as follows:

1. **Original Data**: `V[0:N-1]`, `a[0:N-1]`, `odometer[0:N-1]`
2. **Threshold Application**: Apply threshold condition to one parameter
3. **Data Modification**: Where threshold condition is TRUE, retain original values; where FALSE, set to zero
4. **WCS Calculation**: Apply rolling and contiguous WCS methods to the modified dataset

### Mathematical Definition

For a threshold condition on parameter P (where P can be V, a, or odometer):

```
Modified_P[i] = {
    P[i]    if threshold_condition(P[i]) is TRUE
    0       if threshold_condition(P[i]) is FALSE
}
```

Where `i` ranges from 0 to N-1.

## Specific Thresholding Examples

### 1. Velocity Thresholding: V > 5 m/s

**Condition**: `V[i] > 5.0`

**Result**:
```
Modified_V[i] = {
    V[i]    if V[i] > 5.0 m/s
    0       if V[i] ≤ 5.0 m/s
}
```

**Effect**: Only high-velocity periods contribute to WCS calculation.

### 2. Acceleration Thresholding: |a| > 0.5 m/s²

**Condition**: `|a[i]| > 0.5`

**Result**:
```
Modified_V[i] = {
    V[i]    if |a[i]| > 0.5 m/s²
    0       if |a[i]| ≤ 0.5 m/s²
}

Modified_a[i] = {
    a[i]    if |a[i]| > 0.5 m/s²
    0       if |a[i]| ≤ 0.5 m/s²
}
```

**Effect**: Only dynamic periods (high acceleration/deceleration) contribute to WCS calculation.

### 3. Odometer Thresholding: Distance > 100 m

**Condition**: `odometer[i] > 100.0`

**Result**:
```
Modified_V[i] = {
    V[i]    if odometer[i] > 100.0 m
    0       if odometer[i] ≤ 100.0 m
}
```

**Effect**: Only periods after 100m distance contribute to WCS calculation.

## Multiple Threshold Implementation

When multiple thresholds need to be considered:

1. **Reinitialize**: Start with original parameter values for each new threshold
2. **Apply Threshold**: Apply the new threshold condition to the specified parameter
3. **Calculate WCS**: Use the modified dataset for WCS calculation
4. **Repeat**: For each additional threshold, repeat steps 1-3

### Example: Testing Multiple Acceleration Thresholds

```python
# Original data
V_original = [v0, v1, v2, ..., vN-1]
a_original = [a0, a1, a2, ..., aN-1]

# Test threshold 1: |a| > 0.3 m/s²
V_modified_1 = [v0 if |a0| > 0.3 else 0, v1 if |a1| > 0.3 else 0, ...]
WCS_1 = calculate_wcs(V_modified_1)

# Test threshold 2: |a| > 0.5 m/s² (reinitialize with original)
V_modified_2 = [v0 if |a0| > 0.5 else 0, v1 if |a1| > 0.5 else 0, ...]
WCS_2 = calculate_wcs(V_modified_2)

# Test threshold 3: |a| > 1.0 m/s² (reinitialize with original)
V_modified_3 = [v0 if |a0| > 1.0 else 0, v1 if |a1| > 1.0 else 0, ...]
WCS_3 = calculate_wcs(V_modified_3)
```

## Implementation in Code

### Threshold Application Function

```python
def apply_threshold(data, threshold_condition):
    """
    Apply threshold condition to data array
    
    Args:
        data: Original data array [0:N-1]
        threshold_condition: Boolean array indicating where condition is TRUE
    
    Returns:
        Modified data array with zeros where condition is FALSE
    """
    return np.where(threshold_condition, data, 0.0)
```

### Velocity Thresholding Example

```python
def apply_velocity_threshold(velocities, threshold_value):
    """Apply velocity threshold: V > threshold_value"""
    threshold_condition = velocities > threshold_value
    return apply_threshold(velocities, threshold_condition)
```

### Acceleration Thresholding Example

```python
def apply_acceleration_threshold(velocities, accelerations, threshold_value):
    """Apply acceleration threshold: |a| > threshold_value"""
    threshold_condition = np.abs(accelerations) > threshold_value
    modified_velocities = apply_threshold(velocities, threshold_condition)
    modified_accelerations = apply_threshold(accelerations, threshold_condition)
    return modified_velocities, modified_accelerations
```

## WCS Calculation with Thresholding

### Process Flow

1. **Load Original Data**: `V[0:N-1]`, `a[0:N-1]`, `odometer[0:N-1]`
2. **Define Threshold**: Choose parameter and threshold condition
3. **Apply Threshold**: Create modified dataset
4. **Calculate WCS**: Apply both rolling and contiguous methods
5. **Analyze Results**: Compare with non-thresholded WCS

### Code Example

```python
def calculate_wcs_with_thresholding(velocities, accelerations, threshold_type, threshold_value):
    """
    Calculate WCS with thresholding applied
    
    Args:
        velocities: Original velocity data
        accelerations: Original acceleration data
        threshold_type: 'velocity' or 'acceleration'
        threshold_value: Threshold value to apply
    
    Returns:
        Dictionary with rolling and contiguous WCS results
    """
    if threshold_type == 'velocity':
        modified_velocities = apply_velocity_threshold(velocities, threshold_value)
    elif threshold_type == 'acceleration':
        modified_velocities, _ = apply_acceleration_threshold(velocities, accelerations, threshold_value)
    
    # Calculate WCS on modified data
    rolling_wcs = calculate_wcs_period_rolling(modified_velocities, ...)
    contiguous_wcs = calculate_wcs_period_contiguous(modified_velocities, ...)
    
    return {
        'rolling': rolling_wcs,
        'contiguous': contiguous_wcs,
        'data_reduction': calculate_data_reduction(velocities, modified_velocities)
    }
```

## Data Reduction Analysis

### Definition

Data reduction measures how much the thresholding affects the dataset:

```
Data Reduction (%) = ((Original_NonZero - Thresholded_NonZero) / Original_NonZero) × 100
```

### Example

```python
def calculate_data_reduction(original_data, thresholded_data):
    """Calculate percentage of data reduced by thresholding"""
    original_nonzero = np.sum(original_data > 0)
    thresholded_nonzero = np.sum(thresholded_data > 0)
    
    if original_nonzero == 0:
        return 0.0
    
    reduction_percent = ((original_nonzero - thresholded_nonzero) / original_nonzero) * 100
    return reduction_percent
```

## Practical Applications

### 1. High-Intensity Focus
- **Threshold**: V > 5 m/s
- **Purpose**: Focus on sprint/high-speed periods
- **Use Case**: Sprint performance analysis

### 2. Dynamic Movement Focus
- **Threshold**: |a| > 0.5 m/s²
- **Purpose**: Focus on acceleration/deceleration periods
- **Use Case**: Change of direction analysis

### 3. Distance-Based Analysis
- **Threshold**: Distance > 100 m
- **Purpose**: Focus on later stages of activity
- **Use Case**: Endurance performance analysis

## Validation and Testing

### Test Scenarios

1. **No Thresholding**: Baseline WCS calculation
2. **Single Threshold**: One parameter threshold applied
3. **Multiple Thresholds**: Different threshold values tested
4. **Combined Thresholds**: Multiple parameters thresholded simultaneously

### Expected Behaviors

1. **Data Reduction**: Higher thresholds = more data reduction
2. **WCS Changes**: Thresholding should affect WCS magnitude and timing
3. **Method Differences**: Rolling and contiguous WCS may respond differently to thresholding
4. **Optimal Threshold**: Balance between data retention and meaningful filtering

## Summary

Thresholding in WCS analysis is a systematic process where:

1. **Original data** is preserved for each new threshold test
2. **Threshold conditions** are applied to specific parameters
3. **Data modification** occurs: TRUE conditions retain values, FALSE conditions become zero
4. **WCS calculation** uses the modified dataset
5. **Analysis** compares results across different threshold levels

This approach allows for focused analysis of specific performance characteristics while maintaining the integrity of the original WCS methodology. 