# Rolling WCS Theory and Implementation

## Overview

This document outlines the mathematical foundation and implementation principles for Rolling Worst Case Scenario (WCS) analysis in GPS velocity data.

## Mathematical Foundation

### Core Principle

Rolling WCS finds the window position that **maximizes the integral** (area under the curve) over a specified time period:

```
WCS = max(∫ velocity(t) dt) over all possible window positions
```

### Discrete Implementation

For discrete velocity data with sampling rate `fs`:

```
WCS = max(Σ velocity[i] * Δt) over all possible window centers
```

Where:
- `velocity[i]` = velocity at sample i
- `Δt = 1/fs` = time per sample
- Window spans `[center - half_window, center + half_window]`

## Key Insights

### 1. WCS ≠ Maximum Velocity Peak

**Important**: The rolling WCS epoch does NOT necessarily correspond to the highest velocity peak. Instead, it identifies the window that captures the **maximum accumulated work** over the specified time period.

**Example**: In our 3-peak test:
- Peak 2: Highest velocity (8.5 m/s) but NOT maximum WCS
- Peak 3: Lower velocity (7.0 m/s) but WINS the WCS competition
- Reason: Peak 3 is broader and has better baseline integration

### 2. Area Under the Curve Matters

The WCS is determined by the **total area under the velocity curve** within the window, not just peak values. This makes it physiologically relevant for:
- Sustained high-intensity periods
- Accumulated metabolic demand
- Total work output over time

### 3. Window Characteristics

- **Broad peaks** often beat narrow peaks due to sustained activity
- **Baseline velocity** contributes to total work done
- **Window duration** affects which type of activity pattern wins

## Implementation Requirements

### 1. Thresholding Applied

**Critical**: Rolling WCS applies velocity thresholds to only include data points within the specified range:

```python
# CORRECT - Apply thresholding to focus on relevant performance zones
threshold_mask = (window_data >= threshold_min) & (window_data <= threshold_max)
window_data_thresholded = window_data[threshold_mask]
window_distance = np.sum(window_data_thresholded * time_per_sample)

# INCORRECT - Including all velocities regardless of performance relevance
window_distance = np.sum(window_data * time_per_sample)
```

### 2. Why Apply Thresholding?

Thresholding provides several benefits:
- **Performance focus**: Concentrates on relevant velocity ranges for sports analysis
- **Training specificity**: Allows analysis of specific performance zones
- **Reduced noise**: Excludes low-intensity periods that don't contribute to high-performance analysis
- **Sports relevance**: Focuses on intensities that matter for competition and training

### 3. Window Centering

The window should be **centered** on each data point to ensure proper integration:

```python
for i in range(len(velocity)):
    window_start = max(0, i - half_window)
    window_end = min(len(velocity), i + half_window + (1 if epoch_samples % 2 == 1 else 0))
    window_data = velocity[window_start:window_end]
    window_distance = np.sum(window_data * time_per_sample)
```

## Test Results Validation

### Single Peak Test (Normal Distribution)
- **Peak at t=90s**: Maximum WCS occurs exactly at velocity peak
- **Smooth curve**: No artifacts or discontinuities
- **Intuitive behavior**: WCS follows velocity profile naturally

### Three Peak Test (Complex System)
- **Peak 1**: 6.0 m/s at 30s (narrow) → WCS: 141.073 m
- **Peak 2**: 8.5 m/s at 120s (medium) → WCS: 198.531 m  
- **Peak 3**: 7.0 m/s at 210s (broad) → WCS: 201.723 m (WINNER)
- **Maximum WCS**: 201.725 m at t=213.3s (near Peak 3)

**Key Insight**: Peak 3 wins despite lower velocity because it has the largest area under the curve within the 1-minute window.

## Comparison: With vs Without Thresholding

### With Thresholding (Correct)
- **Performance focus**: Concentrates on relevant velocity ranges
- **Sports specificity**: Analyzes performance zones that matter for training
- **Reduced noise**: Excludes low-intensity periods from high-performance analysis
- **Training relevance**: Focuses on intensities relevant to competition

### Without Thresholding (Incorrect for sports analysis)
- **Includes all velocities**: Even low-intensity periods contribute to WCS
- **Reduced specificity**: Doesn't focus on performance-relevant zones
- **Noise inclusion**: Low-intensity periods may mask high-performance periods
- **Less sports-specific**: Doesn't distinguish between different performance intensities

## Real-World Applications

### Sports Science Relevance

Rolling WCS identifies periods of **sustained high work output**, which is often more physiologically relevant than peak performance alone:

1. **Metabolic demand**: Sustained high-intensity periods create greater metabolic stress
2. **Recovery planning**: Understanding accumulated work helps with training load management
3. **Performance analysis**: Identifies periods of sustained excellence vs. brief spikes
4. **Injury prevention**: High accumulated work periods may indicate increased injury risk

### Training Applications

- **Interval training**: Identify optimal work:rest ratios
- **Match analysis**: Find periods of sustained high performance
- **Fitness assessment**: Measure ability to maintain high work output
- **Recovery monitoring**: Track accumulated work over time

## Implementation Checklist

When implementing rolling WCS, ensure:

- [ ] **Thresholding applied**: Only include velocity data points within the specified threshold range
- [ ] **Proper windowing**: Centered windows with correct edge handling
- [ ] **Performance focus**: Concentrate on relevant velocity ranges for sports analysis
- [ ] **Smooth transitions**: WCS curve should follow velocity profile naturally within threshold
- [ ] **Peak alignment**: Maximum WCS should occur near the most productive velocity regions within threshold
- [ ] **Sports relevance**: Results should reflect accumulated work in performance-relevant zones

## Future Considerations

### Potential Enhancements

1. **Multiple epoch durations**: Analyze different time windows simultaneously
2. **Weighted contributions**: Consider physiological factors in work calculation
3. **Peak detection**: Identify and analyze multiple WCS periods
4. **Trend analysis**: Track WCS changes over training periods
5. **Comparative analysis**: Compare WCS across different sessions/athletes

### Validation Methods

1. **Synthetic data tests**: Use known velocity profiles to verify results
2. **Physiological correlation**: Compare WCS with heart rate, lactate, etc.
3. **Performance correlation**: Relate WCS to actual performance outcomes
4. **Cross-validation**: Test with different sports and activity types

---

**Last Updated**: July 18, 2025  
**Version**: 1.0  
**Status**: Validated through comprehensive testing 