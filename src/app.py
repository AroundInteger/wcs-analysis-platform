"""
WCS Analysis Platform - Main Streamlit Application

A professional application for Worst Case Scenario analysis of GPS data.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Import our modules
from file_ingestion import read_csv_with_metadata, validate_velocity_data
from wcs_analysis import perform_wcs_analysis
from visualization import create_velocity_visualization
from batch_processing import process_batch_files, export_wcs_data_to_csv, create_combined_visualizations, create_combined_wcs_dataframe


def main():
    """Main Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title="WCS Analysis Platform",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for professional appearance with reduced font sizes
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stDataFrame {
        font-size: 0.9rem;
    }
    .stMetric {
        font-size: 0.9rem;
    }
    h3 {
        font-size: 1.3rem;
        margin-bottom: 0.5rem;
    }
    h4 {
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🔥 WCS Analysis Platform</h1>', unsafe_allow_html=True)
    st.markdown("### Professional Worst Case Scenario Analysis for GPS Data")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Data input options
        with st.expander("📁 Data Input", expanded=True):
            input_method = st.radio(
                "Choose input method:",
                ["Upload File", "Select from Folder"],
                help="Upload multiple files or select from a folder"
            )
        
        # Instructions for multiple file upload
        if input_method == "Upload File":
            st.info("💡 **Tip**: You can drag and drop multiple CSV files at once, or use Ctrl+Click (Cmd+Click on Mac) to select multiple files.")
        
        if input_method == "Upload File":
            uploaded_files = st.file_uploader(
                "📁 Upload GPS CSV files (drag & drop multiple files)",
                type=['csv'],
                accept_multiple_files=True,
                help="Drag and drop multiple CSV files or click to browse. Supports StatSport, Catapult, and Generic GPS formats."
            )
            
            # Debug information
            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully")
                for i, file in enumerate(uploaded_files):
                    st.info(f"📄 File {i+1}: {file.name} ({file.size} bytes)")
            
            selected_files = uploaded_files if uploaded_files else []
        else:
            # Folder selection
            data_folder = st.text_input(
                "Data folder path:",
                value="data/test_data",
                help="Enter the path to your data folder (e.g., data/test_data)"
            )
            
            if data_folder and os.path.exists(data_folder):
                csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
                if csv_files:
                    st.success(f"✅ Found {len(csv_files)} CSV files in folder")
                    
                    # Add "Select All" option
                    select_all = st.checkbox(
                        f"📁 Select All Files ({len(csv_files)} files)",
                        help="Check this to select all CSV files in the folder"
                    )
                    
                    if select_all:
                        # Select all files
                        selected_files = csv_files
                        st.info(f"✅ All {len(csv_files)} files selected")
                    else:
                        # Manual selection
                        selected_files = st.multiselect(
                            "Select files to analyze:",
                            csv_files,
                            help=f"Choose one or more CSV files for analysis (found {len(csv_files)} files)"
                        )
                    
                    selected_files = [os.path.join(data_folder, f) for f in selected_files]
                else:
                    st.warning("No CSV files found in the specified folder")
                    selected_files = []
            else:
                st.warning("Please enter a valid folder path")
                selected_files = []
        
        # Analysis parameters
        with st.expander("🔧 WCS Parameters", expanded=True):
            # Epoch durations
            epoch_duration = st.selectbox(
                "Primary Epoch Duration (minutes)",
                [0.5, 1.0, 1.5, 2.0, 3.0, 5.0],
                index=1,  # Default to 1.0 minute
                help="Primary duration for WCS analysis (will be included in all analyses)"
            )
            
            epoch_durations = st.multiselect(
                "Additional Epoch Durations",
                [0.5, 1.0, 1.5, 2.0, 3.0, 5.0],
                default=[2.0, 5.0],  # Removed 1.0 since it's the default primary
                help="Additional epoch durations for comprehensive analysis (duplicates with primary will be automatically removed)"
            )
            
            # Show warning if user selects the same duration in both fields
            if epoch_duration in epoch_durations:
                st.warning(f"⚠️ **Note**: {epoch_duration} minute duration is selected in both fields. Duplicates will be automatically removed during analysis.")
            
            # Sampling rate (fixed at 10Hz for all files)
            sampling_rate = 10
            st.info(f"📊 **Sampling Rate**: Fixed at {sampling_rate} Hz for all files")
        
        # Threshold parameters
        with st.expander("🎯 Threshold Parameters", expanded=True):
            # Default threshold is always 0-100 m/s
            th0_min = 0.0
            th0_max = 100.0
            st.info("🎯 **Default Threshold**: 0.0 - 100.0 m/s (all velocities)")
            
            th1_min = st.number_input("Threshold 1 Min Velocity (m/s)", 0.0, 10.0, 5.0, 0.1)
            th1_max = st.number_input("Threshold 1 Max Velocity (m/s)", 0.0, 100.0, 100.0, 0.1)
        
        # Analysis options
        with st.expander("📊 Analysis Options", expanded=False):
            batch_mode = st.checkbox("Batch Processing Mode", value=False, help="Enable for multiple files - shows combined analysis and exports only")
            
            if batch_mode:
                st.info("🔄 **Batch Mode**: Individual visualizations disabled. Focus on combined analysis and exports.")
                include_visualizations = False
                enhanced_wcs_viz = False
                include_export = True
            else:
                include_visualizations = st.checkbox("Include Visualizations", value=True)
                enhanced_wcs_viz = st.checkbox("Enhanced WCS Visualizations", value=True, help="Use new enhanced WCS period visualizations with timeline and intensity maps")
                include_export = st.checkbox("Include Export Options", value=True)
    
    # Main content area
    if selected_files:
        # Summary cards at the top
        st.markdown("### 📊 Analysis Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Files to Process", len(selected_files))
        with col2:
            st.metric("Primary Epoch", f"{epoch_duration} min")
        with col3:
            st.metric("Additional Epochs", len(epoch_durations))
        with col4:
            st.metric("Mode", "Batch" if batch_mode else "Individual")
        
        st.info(f"🔄 Processing {len(selected_files)} file(s)...")
        
        # Prepare parameters - deduplicate epoch durations to avoid redundant analysis
        all_epoch_durations = [epoch_duration] + epoch_durations
        unique_epoch_durations = list(dict.fromkeys(all_epoch_durations))  # Preserve order while removing duplicates
        
        # Show user which epochs will be analyzed
        if len(all_epoch_durations) != len(unique_epoch_durations):
            st.info(f"🔄 **Optimization**: Removed duplicate epoch duration(s). Analyzing: {unique_epoch_durations} minutes")
        
        parameters = {
            'sampling_rate': sampling_rate,
            'epoch_duration': epoch_duration,
            'epoch_durations': unique_epoch_durations,
            'th0_min': th0_min,
            'th0_max': th0_max,
            'th1_min': th1_min,
            'th1_max': th1_max
        }
        
        # Process all files using batch processing
        all_results = process_batch_files(selected_files, parameters)
        
        # Processing summary
        if len(selected_files) > 1:
            st.success(f"✅ Successfully processed {len(all_results)} out of {len(selected_files)} files")
        
        # Batch processing features
        if all_results:
            # Create tabs for better organization
            tab1, tab2, tab3 = st.tabs(["📊 Results", "📈 Visualizations", "📤 Export"])
            
            with tab1:
                st.markdown("### 📋 Analysis Results")
                # Display individual results if not in batch mode
                if not batch_mode and all_results:
                    for result in all_results:
                        with st.expander(f"📄 {result['file_name']}", expanded=False):
                            # Display file information
                            with st.expander(f"📋 File Information - {result['metadata'].get('player_name', 'Unknown')}", expanded=False):
                                st.json(result['metadata'])
                            
                            display_wcs_results(result, result['metadata'], include_visualizations, enhanced_wcs_viz)
                
                # Batch mode summary
                if batch_mode and all_results:
                    st.markdown("### 📊 Batch Processing Summary")
                    display_batch_summary(all_results)
            
            with tab2:
                st.markdown("### 📈 Analysis Visualizations")
                # Combined visualizations for multiple files
                if len(all_results) > 1 and (batch_mode or include_visualizations):
                    if batch_mode:
                        st.markdown("#### 📊 Combined Analysis Visualizations")
                    else:
                        st.markdown("#### 📊 Multi-File Comparison Visualizations")
                    
                    # Create combined visualizations
                    combined_viz = create_combined_visualizations(all_results)
                    
                    if combined_viz:
                        # Display each visualization
                        if 'wcs_distance_distribution' in combined_viz:
                            st.markdown("#### 📈 WCS Distance Distribution by Epoch")
                            st.plotly_chart(combined_viz['wcs_distance_distribution'], use_container_width=True)
                        
                        if 'mean_wcs_distance_trend' in combined_viz:
                            st.markdown("#### 📈 Mean WCS Distance vs Epoch Duration")
                            st.plotly_chart(combined_viz['mean_wcs_distance_trend'], use_container_width=True)
                        
                        if 'player_comparison' in combined_viz:
                            st.markdown("#### 🏃‍♂️ Average WCS Distance by Player")
                            st.plotly_chart(combined_viz['player_comparison'], use_container_width=True)
                        
                        if 'player_epoch_heatmap' in combined_viz:
                            st.markdown("#### 🔥 WCS Distance Heatmap by Player and Epoch")
                            st.plotly_chart(combined_viz['player_epoch_heatmap'], use_container_width=True)
                        
                        if 'individual_player_grid' in combined_viz:
                            with st.expander("👤 Individual Player Analysis (Click to expand)", expanded=False):
                                st.info("📊 **Note**: Showing analysis for the first 3 players only to prevent overlapping. Use the heatmap above for all players.")
                                st.plotly_chart(combined_viz['individual_player_grid'], use_container_width=True)
                else:
                    st.info("📊 Upload multiple files to see combined visualizations")
            
            with tab3:
                st.markdown("### 📤 Export Options")
                # Export functionality
                if include_export:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("📊 Export WCS Data to CSV", help="Export all WCS analysis results to a CSV file in the OUTPUT folder"):
                            export_path = export_wcs_data_to_csv(all_results)
                            if export_path:
                                st.success(f"✅ Data exported successfully!")
                                st.info(f"📁 File saved to: `{export_path}`")
                    
                    with col2:
                        if st.button("📋 Download Combined Data", help="Download the combined WCS data as a CSV file"):
                            combined_df = create_combined_wcs_dataframe(all_results)
                            if not combined_df.empty:
                                csv_data = combined_df.to_csv(index=False)
                                st.download_button(
                                    label="💾 Download CSV",
                                    data=csv_data,
                                    file_name=f"WCS_Analysis_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv"
                                )
            

    
    else:
        # Welcome message
        st.markdown("""
        ## 🎯 Welcome to WCS Analysis Platform
        
        This application helps you analyze GPS data to identify **Worst Case Scenario (WCS)** periods - 
        the maximum intensity windows in athletic performance data.
        
        ### 📁 **Supported File Formats:**
        - **StatSport**: CSV files with velocity data
        - **Catapult**: GPS data with metadata headers  
        - **Generic GPS**: Standard CSV format
        
        ### 🚀 **Getting Started:**
        1. **Upload a file** or **select from folder** using the sidebar
        2. **Configure WCS parameters** (epoch duration, thresholds)
        3. **Run analysis** to identify peak performance periods
        4. **View results** and export data
        
        ### 📊 **What is WCS Analysis?**
        WCS analysis identifies the time windows with the highest cumulative distance 
        within specified velocity thresholds, helping coaches and analysts understand 
        maximum performance periods.
        """)
        
        # Sample data information
        with st.expander("📋 Test Data Information"):
            st.markdown("""
            **Test data files are available in the `data/test_data/` folder:**
            - `BR_EC_18s(MD1).csv` - StatSport format (4.8 MB)
            - `BR_EC_18s(MD2).csv` - StatSport format (10.2 MB)
            - `Aaron Ramsey_2024-09-09_Raw Data 09.09.24 MD vs Montenegro.csv` - Catapult format (7.0 MB)
            - `3A-NT-GP-LSG-10x10-70x60 Export for Michael Obafemi 22346.csv` - Catapult format (1.1 MB)
            
            Use these files to test the application functionality. You can select "Select from Folder" 
            and enter `data/test_data` to access all files at once.
            """)


def display_wcs_results(results: Dict[str, Any], metadata: Dict[str, Any], include_visualizations: bool = True, enhanced_wcs_viz: bool = True):
    """Display WCS analysis results"""
    
    if not results:
        st.error("No WCS results to display")
        return
    
    # Display metadata
    st.markdown("### 📋 File Information")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Player", metadata.get('player_name', 'Unknown'))
    with col2:
        st.metric("File Type", metadata.get('file_type', 'Unknown'))
    with col3:
        st.metric("Records", f"{metadata.get('total_records', 0):,}")
    with col4:
        st.metric("Duration", f"{metadata.get('duration_minutes', 0):.1f} min")
    
    # Display summary statistics in a clean table format
    if 'processed_data' in results:
        processed_df = results['processed_data']
        
        # Prepare velocity statistics
        velocity_stats = {
            'max_velocity': processed_df['Velocity'].max(),
            'mean_velocity': processed_df['Velocity'].mean(),
            'min_velocity': processed_df['Velocity'].min(),
            'velocity_std': processed_df['Velocity'].std()
        }
        
        # Prepare kinematic statistics
        kinematic_stats = None
        if 'kinematic_stats' in results and results['kinematic_stats']:
            ks = results['kinematic_stats']
            kinematic_stats = {}
            
            if 'acceleration' in ks:
                kinematic_stats.update({
                    'max_acceleration': ks['acceleration']['max'],
                    'min_acceleration': ks['acceleration']['min'],
                    'mean_acceleration': ks['acceleration']['mean']
                })
            
            if 'distance' in ks:
                kinematic_stats['total_distance'] = ks['distance']['total']
            
            if 'power' in ks:
                kinematic_stats.update({
                    'max_power': ks['power']['max'],
                    'mean_power': ks['power']['mean']
                })
        
        # Prepare WCS summary
        wcs_summary = None
        if 'wcs_results' in results and results['wcs_results']:
            wcs_results = results['wcs_results']
            if len(wcs_results) > 0:
                epoch_data = wcs_results[0]  # Use first epoch for summary
                wcs_summary = {
                    'th0_distance': epoch_data[0] if len(epoch_data) > 0 else 0,
                    'th0_duration': epoch_data[1] if len(epoch_data) > 1 else 0,
                    'th1_distance': epoch_data[4] if len(epoch_data) > 4 else 0,
                    'th1_duration': epoch_data[5] if len(epoch_data) > 5 else 0
                }
        
        # Create and display summary table
        from visualization import create_summary_statistics_table
        
        st.markdown("### 📊 Summary Statistics")
        summary_table = create_summary_statistics_table(velocity_stats, kinematic_stats, wcs_summary)
        
        if not summary_table.empty:
            # Display table with smaller font and better formatting
            st.dataframe(
                summary_table,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Category": st.column_config.TextColumn("Category", width="medium"),
                    "Metric": st.column_config.TextColumn("Metric", width="medium"),
                    "Value": st.column_config.TextColumn("Value", width="small")
                }
            )
        else:
            st.warning("No summary statistics available")
    
    # Display WCS metrics in a compact format
    if 'wcs_results' in results:
        wcs_results = results['wcs_results']
        
        st.markdown("### 🔥 WCS Analysis Results")
        
        # Create WCS results table
        wcs_data = []
        
        # Get epoch durations from the analysis results or use defaults
        epoch_durations = results.get('epoch_durations', [0.5, 1.0, 1.5, 2.0, 3.0, 5.0])
        epoch_names = [f"{dur:.1f}min" for dur in epoch_durations]
        
        for i, epoch_name in enumerate(epoch_names):
            if i < len(wcs_results):
                epoch_data = wcs_results[i]
                wcs_data.append({
                    'Epoch': epoch_name,
                    'Default Threshold Distance (m)': f"{epoch_data[0] if len(epoch_data) > 0 else 0:.1f}",
                    'Default Threshold Duration (s)': f"{epoch_data[1] if len(epoch_data) > 1 else 0:.1f}",
                    'Threshold 1 Distance (m)': f"{epoch_data[4] if len(epoch_data) > 4 else 0:.1f}",
                    'Threshold 1 Duration (s)': f"{epoch_data[5] if len(epoch_data) > 5 else 0:.1f}"
                })
        
        if wcs_data:
            wcs_df = pd.DataFrame(wcs_data)
            st.dataframe(
                wcs_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Epoch": st.column_config.TextColumn("Epoch", width="small"),
                                "Default Threshold Distance (m)": st.column_config.TextColumn("Default Threshold Distance (m)", width="medium"),
            "Default Threshold Duration (s)": st.column_config.TextColumn("Default Threshold Duration (s)", width="medium"),
            "Threshold 1 Distance (m)": st.column_config.TextColumn("Threshold 1 Distance (m)", width="medium"),
            "Threshold 1 Duration (s)": st.column_config.TextColumn("Threshold 1 Duration (s)", width="medium")
                }
            )
        else:
            st.warning("No WCS results available")
    
            # Display enhanced WCS visualizations
        if 'processed_data' in results and include_visualizations:
            # Import visualization functions
            from visualization import create_enhanced_wcs_visualization, create_wcs_period_details, create_kinematic_visualization
            
            if enhanced_wcs_viz:
                st.markdown("### 🔥 Enhanced WCS Analysis Visualizations")
            
            # Create enhanced WCS visualization
            enhanced_wcs_fig = create_enhanced_wcs_visualization(
                results['processed_data'], 
                metadata, 
                results.get('wcs_results', [])
            )
            
            if enhanced_wcs_fig:
                st.plotly_chart(enhanced_wcs_fig, use_container_width=True)
            else:
                st.warning("Could not create enhanced WCS visualization")
            
            # Display detailed WCS period information
            if 'wcs_results' in results and results['wcs_results']:
                st.markdown("### 📋 Detailed WCS Period Information")
                
                # Get epoch durations from the analysis results
                epoch_durations = results.get('epoch_durations', [0.5, 1.0, 1.5, 2.0, 3.0, 5.0])
                wcs_details_df = create_wcs_period_details(results['wcs_results'], epoch_durations)
                
                if not wcs_details_df.empty:
                    st.dataframe(
                        wcs_details_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Epoch": st.column_config.TextColumn("Epoch", width="small"),
                            "Period": st.column_config.TextColumn("Period", width="small"),
                            "Distance (m)": st.column_config.TextColumn("Distance (m)", width="medium"),
                            "Duration (s)": st.column_config.TextColumn("Duration (s)", width="medium"),
                            "Start Time (s)": st.column_config.TextColumn("Start Time (s)", width="medium"),
                            "End Time (s)": st.column_config.TextColumn("End Time (s)", width="medium"),
                            "Avg Velocity (m/s)": st.column_config.TextColumn("Avg Velocity (m/s)", width="medium"),
                            "Performance Level": st.column_config.TextColumn("Performance Level", width="medium")
                        }
                    )
                else:
                    st.warning("No detailed WCS period information available")
        else:
            st.markdown("### 📈 Standard Kinematic Analysis Visualizations")
        
        # Display kinematic visualizations as well
        st.markdown("### 📈 Kinematic Analysis Visualizations")
        
        # Import visualization function
        from visualization import create_kinematic_visualization
        
        # Create kinematic visualization
        kinematic_fig = create_kinematic_visualization(
            results['processed_data'], 
            metadata, 
            results.get('wcs_results', [])
        )
        
        if kinematic_fig:
            st.plotly_chart(kinematic_fig, use_container_width=True)
        else:
            st.warning("Could not create kinematic visualization")
    
    elif 'velocity_stats' in results:
        velocity_stats = results['velocity_stats']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Mean Velocity", f"{velocity_stats.get('mean', 0):.2f} m/s")
        with col2:
            st.metric("Peak Velocity", f"{velocity_stats.get('max', 0):.2f} m/s")
        with col3:
            st.metric("Min Velocity", f"{velocity_stats.get('min', 0):.2f} m/s")
        with col4:
            st.metric("Velocity Std Dev", f"{velocity_stats.get('std', 0):.2f} m/s")


def display_batch_summary(all_results: list):
    """Display batch processing summary"""
    
    if not all_results:
        return
    
    # Create summary table
    summary_data = []
    for result in all_results:
        metadata = result['metadata']
        velocity_stats = result.get('velocity_stats', {})
        
        summary_data.append({
            'File': result['file_name'],
            'Player': metadata.get('player_name', 'Unknown'),
            'Records': metadata.get('total_records', 0),
            'Duration (min)': f"{metadata.get('duration_minutes', 0):.1f}",
            'Mean Velocity (m/s)': f"{velocity_stats.get('mean', 0):.2f}",
            'Peak Velocity (m/s)': f"{velocity_stats.get('max', 0):.2f}"
        })
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)


if __name__ == "__main__":
    main() 