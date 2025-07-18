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
        st.subheader("📁 Data Input")
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
        st.subheader("🔧 WCS Parameters")
        
        # Epoch durations
        epoch_duration = st.selectbox(
            "Epoch Duration (minutes)",
            [0.5, 1.0, 1.5, 2.0, 3.0, 5.0],
            index=1,  # Default to 1.0 minute
            help="Duration of the WCS analysis window"
        )
        
        epoch_durations = st.multiselect(
            "Additional Epoch Durations",
            [0.5, 1.0, 1.5, 2.0, 3.0, 5.0],
            default=[1.0, 2.0, 5.0],
            help="Additional epoch durations for comprehensive analysis"
        )
        
        # Sampling rate (fixed at 10Hz for all files)
        sampling_rate = 10
        st.info(f"📊 **Sampling Rate**: Fixed at {sampling_rate} Hz for all files")
        
        # Threshold parameters
        st.subheader("🎯 Threshold Parameters")
        
        th0_min = st.number_input("TH_0 Min Velocity (m/s)", 0.0, 10.0, 0.0, 0.1)
        th0_max = st.number_input("TH_0 Max Velocity (m/s)", 0.0, 100.0, 100.0, 0.1)
        
        th1_min = st.number_input("TH_1 Min Velocity (m/s)", 0.0, 10.0, 5.0, 0.1)
        th1_max = st.number_input("TH_1 Max Velocity (m/s)", 0.0, 100.0, 100.0, 0.1)
        
        # Analysis options
        st.subheader("📊 Analysis Options")
        
        include_visualizations = st.checkbox("Include Visualizations", value=True)
        include_export = st.checkbox("Include Export Options", value=True)
        batch_mode = st.checkbox("Batch Processing Mode", value=False)
    
    # Main content area
    if selected_files:
        st.info(f"🔄 Processing {len(selected_files)} file(s)...")
        # Process files
        all_results = []
        
        for i, file_input in enumerate(selected_files):
            try:
                st.markdown(f"### 📄 Processing File {i+1}/{len(selected_files)}: {os.path.basename(file_input) if isinstance(file_input, str) else file_input.name}")
                
                # Progress bar for multiple files
                if len(selected_files) > 1:
                    progress = (i + 1) / len(selected_files)
                    st.progress(progress)
                
                # Read file
                if isinstance(file_input, str):
                    # File path - pass directly to the function
                    df, metadata, file_type_info = read_csv_with_metadata(file_input)
                else:
                    # Uploaded file
                    df, metadata, file_type_info = read_csv_with_metadata(file_input)
                
                if df is not None and metadata is not None:
                    # Display file information
                    with st.expander(f"📋 File Information - {metadata.get('player_name', 'Unknown')}"):
                        st.json(metadata)
                        st.info(f"📁 **File Type**: {file_type_info['type'].title()} (Confidence: {file_type_info['confidence']:.1%})")
                    
                    # Validate velocity data
                    if validate_velocity_data(df):
                        st.success("✅ Velocity data validated successfully")
                        
                        # Prepare parameters
                        parameters = {
                            'sampling_rate': sampling_rate,
                            'epoch_duration': epoch_duration,
                            'epoch_durations': [epoch_duration] + epoch_durations,
                            'th0_min': th0_min,
                            'th0_max': th0_max,
                            'th1_min': th1_min,
                            'th1_max': th1_max
                        }
                        
                        # Process WCS analysis
                        with st.spinner("Running WCS analysis..."):
                            # Pass the already-processed DataFrame to WCS analysis
                            results = perform_wcs_analysis(df, metadata, file_type_info, parameters)
                        
                        if results:
                            # Display results
                            display_wcs_results(results, metadata, include_visualizations)
                            
                            # Add to batch results
                            all_results.append({
                                'file_name': os.path.basename(file_input) if isinstance(file_input, str) else file_input.name,
                                'results': results,
                                'metadata': metadata
                            })
                        else:
                            st.error("❌ WCS analysis failed")
                    else:
                        st.error("❌ Velocity data validation failed")
                else:
                    st.error("❌ Failed to read file")
                    
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
        
        # Processing summary
        if len(selected_files) > 1:
            st.success(f"✅ Successfully processed {len(all_results)} out of {len(selected_files)} files")
        
        # Batch processing summary
        if batch_mode and all_results:
            st.markdown("### 📊 Batch Processing Summary")
            display_batch_summary(all_results)
    
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


def display_wcs_results(results: Dict[str, Any], metadata: Dict[str, Any], include_visualizations: bool = True):
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
        epoch_names = ['30s', '60s', '90s', '120s', '180s', '300s']
        
        for i, epoch_name in enumerate(epoch_names):
            if i < len(wcs_results):
                epoch_data = wcs_results[i]
                wcs_data.append({
                    'Epoch': epoch_name,
                    'TH_0 Distance (m)': f"{epoch_data[0] if len(epoch_data) > 0 else 0:.1f}",
                    'TH_0 Duration (s)': f"{epoch_data[1] if len(epoch_data) > 1 else 0:.1f}",
                    'TH_1 Distance (m)': f"{epoch_data[4] if len(epoch_data) > 4 else 0:.1f}",
                    'TH_1 Duration (s)': f"{epoch_data[5] if len(epoch_data) > 5 else 0:.1f}"
                })
        
        if wcs_data:
            wcs_df = pd.DataFrame(wcs_data)
            st.dataframe(
                wcs_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Epoch": st.column_config.TextColumn("Epoch", width="small"),
                    "TH_0 Distance (m)": st.column_config.TextColumn("TH_0 Distance (m)", width="medium"),
                    "TH_0 Duration (s)": st.column_config.TextColumn("TH_0 Duration (s)", width="medium"),
                    "TH_1 Distance (m)": st.column_config.TextColumn("TH_1 Distance (m)", width="medium"),
                    "TH_1 Duration (s)": st.column_config.TextColumn("TH_1 Duration (s)", width="medium")
                }
            )
        else:
            st.warning("No WCS results available")
    
    # Display kinematic visualizations
    if 'processed_data' in results and include_visualizations:
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
        velocity_stats = result['results'].get('velocity_stats', {})
        
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