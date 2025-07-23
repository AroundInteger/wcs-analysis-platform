# WCS Analysis App Integration Guide

## Quick Start Integration

This guide provides step-by-step instructions for integrating WCS analysis into the existing Streamlit app.

## 1. Update App Configuration

### Add WCS Settings to `config/app_config.yaml`

```yaml
# Add this section to your existing config
wcs_analysis:
  # Default parameters
  default_epoch_duration: 20.0  # seconds
  default_velocity_threshold_min: 0.0  # m/s
  default_velocity_threshold_max: 100.0  # m/s
  default_acceleration_threshold: 0.5  # m/s²
  
  # Feature flags
  enable_velocity_thresholding: true
  enable_acceleration_thresholding: true
  enable_rolling_wcs: true
  enable_contiguous_wcs: true
  
  # UI settings
  show_wcs_settings_panel: true
  show_wcs_results_tab: true
  show_wcs_visualizations: true
```

## 2. Add WCS UI Components

### Create `src/wcs_ui.py`

```python
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Any, List

def render_wcs_settings_panel() -> Dict[str, Any]:
    """
    Render WCS analysis settings panel
    
    Returns:
        Dictionary of WCS parameters
    """
    st.subheader("🔬 WCS Analysis Settings")
    
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Window Settings**")
        epoch_duration = st.slider(
            "Epoch Duration (seconds)",
            min_value=5.0,
            max_value=60.0,
            value=20.0,
            step=5.0,
            help="Duration of WCS analysis window"
        )
        
        st.markdown("**Velocity Thresholds**")
        velocity_threshold_min = st.number_input(
            "Min Velocity (m/s)",
            min_value=0.0,
            max_value=20.0,
            value=0.0,
            step=0.5,
            help="Minimum velocity for inclusion in WCS calculation"
        )
        
        velocity_threshold_max = st.number_input(
            "Max Velocity (m/s)",
            min_value=0.0,
            max_value=50.0,
            value=100.0,
            step=1.0,
            help="Maximum velocity for inclusion in WCS calculation"
        )
    
    with col2:
        st.markdown("**Acceleration Threshold**")
        acceleration_threshold = st.number_input(
            "Min Acceleration (m/s²)",
            min_value=0.0,
            max_value=10.0,
            value=0.5,
            step=0.1,
            help="Minimum acceleration magnitude for inclusion"
        )
        
        st.markdown("**Analysis Methods**")
        enable_rolling = st.checkbox(
            "Enable Rolling WCS",
            value=True,
            help="Flexible window positioning"
        )
        
        enable_contiguous = st.checkbox(
            "Enable Contiguous WCS", 
            value=True,
            help="Fixed epoch alignment"
        )
        
        st.markdown("**Thresholding Options**")
        enable_velocity_thresholding = st.checkbox(
            "Apply Velocity Thresholding",
            value=False,
            help="Filter velocities outside threshold range"
        )
        
        enable_acceleration_thresholding = st.checkbox(
            "Apply Acceleration Thresholding",
            value=False,
            help="Focus on dynamic periods only"
        )
    
    # Return parameters
    return {
        'epoch_duration': epoch_duration / 60.0,  # Convert to minutes
        'velocity_threshold_min': velocity_threshold_min,
        'velocity_threshold_max': velocity_threshold_max,
        'acceleration_threshold': acceleration_threshold,
        'enable_rolling': enable_rolling,
        'enable_contiguous': enable_contiguous,
        'enable_velocity_thresholding': enable_velocity_thresholding,
        'enable_acceleration_thresholding': enable_acceleration_thresholding
    }

def render_wcs_results(wcs_results: Dict[str, Any], file_metadata: Dict[str, Any]):
    """
    Render WCS analysis results
    
    Args:
        wcs_results: WCS analysis results dictionary
        file_metadata: File metadata information
    """
    if not wcs_results:
        st.warning("⚠️ No WCS results available")
        return
    
    st.subheader("📊 WCS Analysis Results")
    
    # Display file information
    with st.expander("📁 File Information", expanded=False):
        st.write(f"**Filename:** {file_metadata.get('filename', 'Unknown')}")
        st.write(f"**Duration:** {file_metadata.get('duration', 0):.1f} seconds")
        st.write(f"**Sampling Rate:** {file_metadata.get('sampling_rate', 0)} Hz")
    
    # Create tabs for different methods
    tab_labels = []
    if wcs_results.get('rolling_wcs_results'):
        tab_labels.append("🔄 Rolling WCS")
    if wcs_results.get('contiguous_wcs_results'):
        tab_labels.append("📏 Contiguous WCS")
    
    if not tab_labels:
        st.info("ℹ️ No WCS results available for display")
        return
    
    tabs = st.tabs(tab_labels)
    
    # Rolling WCS Tab
    if wcs_results.get('rolling_wcs_results') and len(tab_labels) > 0:
        with tabs[0]:
            display_wcs_method_results(wcs_results['rolling_wcs_results'], "Rolling WCS")
    
    # Contiguous WCS Tab
    if wcs_results.get('contiguous_wcs_results') and len(tab_labels) > 1:
        with tabs[1]:
            display_wcs_method_results(wcs_results['contiguous_wcs_results'], "Contiguous WCS")

def display_wcs_method_results(wcs_data: List[List], method_name: str):
    """
    Display results for a specific WCS method
    
    Args:
        wcs_data: WCS results data
        method_name: Name of the WCS method
    """
    if not wcs_data:
        st.info(f"ℹ️ No {method_name} results available")
        return
    
    # Extract the best WCS result
    best_wcs = wcs_data[0] if wcs_data else None
    
    if best_wcs:
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🏃‍♂️ Max Distance",
                value=f"{best_wcs[0]:.1f} m",
                help="Maximum accumulated distance in the WCS window"
            )
        
        with col2:
            st.metric(
                label="⏱️ Time",
                value=f"{best_wcs[1]:.1f} s",
                help="Time duration of the WCS window"
            )
        
        with col3:
            center_time = best_wcs[2] if len(best_wcs) > 2 else 0
            st.metric(
                label="🎯 Center Time",
                value=f"{center_time:.1f} s",
                help="Center time of the WCS window"
            )
        
        with col4:
            avg_velocity = best_wcs[0] / best_wcs[1] if best_wcs[1] > 0 else 0
            st.metric(
                label="⚡ Avg Velocity",
                value=f"{avg_velocity:.1f} m/s",
                help="Average velocity in the WCS window"
            )
    
    # Display detailed results table
    st.markdown("**📋 Detailed Results**")
    
    if len(wcs_data) > 1:
        # Create DataFrame for multiple results
        df_results = pd.DataFrame(wcs_data, columns=[
            'Distance (m)', 'Time (s)', 'Start Time (s)', 'End Time (s)'
        ])
        st.dataframe(df_results, use_container_width=True)
    else:
        # Display single result
        st.write(f"**Distance:** {best_wcs[0]:.1f} m")
        st.write(f"**Time:** {best_wcs[1]:.1f} s")
        st.write(f"**Start Time:** {best_wcs[2]:.1f} s")
        st.write(f"**End Time:** {best_wcs[3]:.1f} s")

def render_wcs_comparison(batch_results: List[Dict[str, Any]]):
    """
    Render WCS comparison across multiple files
    
    Args:
        batch_results: List of results from multiple files
    """
    if not batch_results or len(batch_results) < 2:
        return
    
    st.subheader("📈 WCS Comparison Across Files")
    
    # Extract WCS data for comparison
    comparison_data = []
    
    for result in batch_results:
        filename = result.get('filename', 'Unknown')
        wcs_results = result.get('wcs_results', {})
        
        # Get rolling WCS if available
        rolling_wcs = wcs_results.get('rolling_wcs_results', [])
        rolling_distance = rolling_wcs[0][0] if rolling_wcs else 0
        
        # Get contiguous WCS if available
        contiguous_wcs = wcs_results.get('contiguous_wcs_results', [])
        contiguous_distance = contiguous_wcs[0][0] if contiguous_wcs else 0
        
        comparison_data.append({
            'Filename': filename,
            'Rolling WCS (m)': rolling_distance,
            'Contiguous WCS (m)': contiguous_distance
        })
    
    if comparison_data:
        df_comparison = pd.DataFrame(comparison_data)
        
        # Display comparison table
        st.dataframe(df_comparison, use_container_width=True)
        
        # Create comparison chart
        if len(comparison_data) > 1:
            st.markdown("**📊 WCS Comparison Chart**")
            
            # Create bar chart
            chart_data = df_comparison.set_index('Filename')
            st.bar_chart(chart_data)
```

## 3. Update Main App File

### Modify `src/app.py`

Add these imports at the top:

```python
from src.wcs_ui import render_wcs_settings_panel, render_wcs_results, render_wcs_comparison
```

Add WCS processing to the main processing function:

```python
def process_uploaded_files(uploaded_files):
    """Process uploaded files with WCS analysis"""
    
    # Get WCS settings from UI
    wcs_parameters = render_wcs_settings_panel()
    
    results = []
    
    for uploaded_file in uploaded_files:
        try:
            # Process file (existing code)
            df, metadata, file_type_info = process_single_file(uploaded_file)
            
            # Perform WCS analysis
            if wcs_parameters.get('enable_rolling') or wcs_parameters.get('enable_contiguous'):
                wcs_results = perform_wcs_analysis(df, metadata, file_type_info, wcs_parameters)
            else:
                wcs_results = {}
            
            # Store results
            results.append({
                'filename': uploaded_file.name,
                'data': df,
                'metadata': metadata,
                'file_type_info': file_type_info,
                'wcs_results': wcs_results
            })
            
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
    
    return results
```

Add WCS results display to the main app:

```python
def main():
    # ... existing code ...
    
    if uploaded_files:
        # Process files
        results = process_uploaded_files(uploaded_files)
        
        # Display results in tabs
        if len(results) == 1:
            # Single file analysis
            result = results[0]
            
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Results", "📈 Visualizations", "🔬 WCS Analysis", "📋 Advanced Analytics", "💾 Export"
            ])
            
            with tab1:
                # Existing results display
                display_results(result)
            
            with tab2:
                # Existing visualizations
                display_visualizations(result)
            
            with tab3:
                # WCS Analysis
                render_wcs_results(result['wcs_results'], result['metadata'])
            
            with tab4:
                # Existing advanced analytics
                display_advanced_analytics(result)
            
            with tab5:
                # Existing export functionality
                display_export_options(result)
        
        else:
            # Batch analysis
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Batch Results", "🔬 WCS Comparison", "📈 Visualizations", "💾 Export"
            ])
            
            with tab1:
                # Existing batch results
                display_batch_results(results)
            
            with tab2:
                # WCS comparison
                render_wcs_comparison(results)
            
            with tab3:
                # Existing batch visualizations
                display_batch_visualizations(results)
            
            with tab4:
                # Existing batch export
                display_batch_export(results)
```

## 4. Update Export Functionality

### Modify `src/batch_processing.py`

Add WCS data to export:

```python
def create_combined_wcs_dataframe(batch_results):
    """Create combined DataFrame with WCS results"""
    
    wcs_data = []
    
    for result in batch_results:
        filename = result.get('filename', 'Unknown')
        wcs_results = result.get('wcs_results', {})
        
        # Extract rolling WCS
        rolling_wcs = wcs_results.get('rolling_wcs_results', [])
        if rolling_wcs:
            rolling_data = rolling_wcs[0]
            wcs_data.append({
                'Filename': filename,
                'Method': 'Rolling WCS',
                'Distance (m)': rolling_data[0],
                'Time (s)': rolling_data[1],
                'Start Time (s)': rolling_data[2],
                'End Time (s)': rolling_data[3]
            })
        
        # Extract contiguous WCS
        contiguous_wcs = wcs_results.get('contiguous_wcs_results', [])
        if contiguous_wcs:
            contiguous_data = contiguous_wcs[0]
            wcs_data.append({
                'Filename': filename,
                'Method': 'Contiguous WCS',
                'Distance (m)': contiguous_data[0],
                'Time (s)': contiguous_data[1],
                'Start Time (s)': contiguous_data[2],
                'End Time (s)': contiguous_data[3]
            })
    
    return pd.DataFrame(wcs_data) if wcs_data else pd.DataFrame()

def export_wcs_data_to_excel(batch_results, output_path):
    """Export WCS data to Excel file"""
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Export WCS results
        wcs_df = create_combined_wcs_dataframe(batch_results)
        if not wcs_df.empty:
            wcs_df.to_excel(writer, sheet_name='WCS Analysis', index=False)
        
        # Export other data (existing functionality)
        # ... existing export code ...
```

## 5. Add Configuration Loading

### Create `src/config_loader.py`

```python
import yaml
from typing import Dict, Any

def load_wcs_config() -> Dict[str, Any]:
    """Load WCS configuration from config file"""
    
    try:
        with open('config/app_config.yaml', 'r') as file:
            config = yaml.safe_load(file)
            return config.get('wcs_analysis', {})
    except FileNotFoundError:
        # Return default configuration
        return {
            'default_epoch_duration': 20.0,
            'default_velocity_threshold_min': 0.0,
            'default_velocity_threshold_max': 100.0,
            'default_acceleration_threshold': 0.5,
            'enable_velocity_thresholding': True,
            'enable_acceleration_thresholding': True,
            'enable_rolling_wcs': True,
            'enable_contiguous_wcs': True
        }

def get_wcs_defaults() -> Dict[str, Any]:
    """Get default WCS parameters"""
    
    config = load_wcs_config()
    
    return {
        'epoch_duration': config.get('default_epoch_duration', 20.0) / 60.0,
        'velocity_threshold_min': config.get('default_velocity_threshold_min', 0.0),
        'velocity_threshold_max': config.get('default_velocity_threshold_max', 100.0),
        'acceleration_threshold': config.get('default_acceleration_threshold', 0.5),
        'enable_velocity_thresholding': config.get('enable_velocity_thresholding', False),
        'enable_acceleration_thresholding': config.get('enable_acceleration_thresholding', False),
        'enable_rolling': config.get('enable_rolling_wcs', True),
        'enable_contiguous': config.get('enable_contiguous_wcs', True)
    }
```

## 6. Testing the Integration

### Create Test Script

```python
# test_wcs_integration.py
import sys
import os
sys.path.append('.')

from src.wcs_analysis import perform_wcs_analysis
from src.wcs_ui import render_wcs_settings_panel, render_wcs_results
import pandas as pd
import numpy as np

def test_wcs_integration():
    """Test WCS integration with sample data"""
    
    # Create sample data
    sampling_rate = 10
    duration = 120
    time = np.linspace(0, duration, duration * sampling_rate)
    
    # Create velocity data with peaks
    velocities = 2.0 + 6.0 * np.exp(-0.5 * ((time - 60) / 20) ** 2)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Time': time,
        'Velocity': velocities
    })
    
    # Test WCS analysis
    metadata = {'sampling_rate': sampling_rate, 'duration': duration}
    file_type_info = {'type': 'test'}
    parameters = {
        'epoch_duration': 20.0 / 60.0,
        'velocity_threshold_min': 0.0,
        'velocity_threshold_max': 100.0,
        'acceleration_threshold': 0.5,
        'enable_rolling': True,
        'enable_contiguous': True
    }
    
    # Perform analysis
    wcs_results = perform_wcs_analysis(df, metadata, file_type_info, parameters)
    
    print("✅ WCS Integration Test Results:")
    print(f"Rolling WCS: {wcs_results.get('rolling_wcs_results', [])}")
    print(f"Contiguous WCS: {wcs_results.get('contiguous_wcs_results', [])}")

if __name__ == "__main__":
    test_wcs_integration()
```

## 7. Deployment Checklist

- [ ] Update `config/app_config.yaml` with WCS settings
- [ ] Add `src/wcs_ui.py` file
- [ ] Modify `src/app.py` to include WCS processing
- [ ] Update `src/batch_processing.py` for WCS export
- [ ] Add `src/config_loader.py` for configuration management
- [ ] Test WCS integration with sample data
- [ ] Verify UI components render correctly
- [ ] Test export functionality with WCS data
- [ ] Update documentation

## 8. User Guide

### For End Users

1. **Upload Files**: Select velocity data files
2. **Configure WCS Settings**: Adjust epoch duration and thresholds
3. **Run Analysis**: Process files with WCS analysis
4. **View Results**: Check WCS Analysis tab for results
5. **Export Data**: Download results including WCS metrics

### For Developers

1. **Configuration**: Modify `config/app_config.yaml` for default settings
2. **UI Customization**: Edit `src/wcs_ui.py` for interface changes
3. **Algorithm Tuning**: Modify `src/wcs_analysis.py` for analysis changes
4. **Testing**: Use test scripts to validate changes

This integration provides a complete WCS analysis solution within the existing app framework, maintaining consistency with current functionality while adding powerful new analysis capabilities. 