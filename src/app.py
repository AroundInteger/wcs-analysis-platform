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
from .file_ingestion import read_csv_with_metadata, validate_velocity_data
from .wcs_analysis import perform_wcs_analysis
from .visualization import create_velocity_visualization


def main():
    """Main Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title="WCS Analysis Platform",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for professional appearance
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
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
            help="Upload a single file or select from a folder"
        )
        
        if input_method == "Upload File":
            uploaded_file = st.file_uploader(
                "Upload GPS CSV file",
                type=['csv'],
                help="Upload a GPS data file in CSV format"
            )
            selected_files = [uploaded_file] if uploaded_file else []
        else:
            # Folder selection
            data_folder = st.text_input(
                "Data folder path:",
                value="data/sample_data",
                help="Enter the path to your data folder"
            )
            
            if data_folder and os.path.exists(data_folder):
                csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
                if csv_files:
                    selected_files = st.multiselect(
                        "Select files to analyze:",
                        csv_files,
                        help="Choose one or more CSV files for analysis"
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
        # Process files
        all_results = []
        
        for file_input in selected_files:
            try:
                st.markdown(f"### 📄 Processing: {os.path.basename(file_input) if isinstance(file_input, str) else file_input.name}")
                
                # Read file
                if isinstance(file_input, str):
                    # File path
                    with open(file_input, 'r') as f:
                        df, metadata, file_type_info = read_csv_with_metadata(f)
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
                            if isinstance(file_input, str):
                                # For file paths, we need to create a file-like object
                                import tempfile
                                with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as tmp_file:
                                    with open(file_input, 'rb') as f:
                                        tmp_file.write(f.read())
                                    tmp_file_path = tmp_file.name
                                
                                # Create a mock uploaded file
                                class MockUploadedFile:
                                    def __init__(self, file_path):
                                        self.file_path = file_path
                                        self.name = os.path.basename(file_path)
                                    
                                    def getvalue(self):
                                        with open(self.file_path, 'rb') as f:
                                            return f.read()
                                
                                mock_file = MockUploadedFile(tmp_file_path)
                                results = perform_wcs_analysis(mock_file, parameters)
                                
                                # Clean up
                                os.unlink(tmp_file_path)
                            else:
                                # For uploaded files
                                results = perform_wcs_analysis(file_input, parameters)
                        
                        if results:
                            # Display results
                            display_wcs_results(results, metadata)
                            
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
        with st.expander("📋 Sample Data Information"):
            st.markdown("""
            **Sample data files are available in the `data/sample_data/` folder:**
            - `statsport_sample.csv` - StatSport format example
            - `catapult_sample.csv` - Catapult format example
            - `generic_sample.csv` - Generic GPS format example
            
            Use these files to test the application functionality.
            """)


def display_wcs_results(results: Dict[str, Any], metadata: Dict[str, Any]):
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
    
    # Display processed velocity statistics
    if 'processed_data' in results:
        processed_df = results['processed_data']
        
        st.markdown("### 📊 Processed Velocity Statistics (10Hz)")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Mean Velocity", f"{processed_df['Velocity'].mean():.2f} m/s")
        with col2:
            st.metric("Peak Velocity", f"{processed_df['Velocity'].max():.2f} m/s")
        with col3:
            st.metric("Min Velocity", f"{processed_df['Velocity'].min():.2f} m/s")
        with col4:
            st.metric("Velocity Std Dev", f"{processed_df['Velocity'].std():.2f} m/s")
    
    # Display WCS metrics
    st.markdown("### 🔥 WCS Analysis Results")
    
    if 'wcs_results' in results:
        wcs_results = results['wcs_results']
        
        # Display WCS results for different epochs
        st.markdown("**WCS Results by Epoch Duration:**")
        
        epoch_names = ['30s', '60s', '90s']
        for i, epoch_name in enumerate(epoch_names):
            if i < len(wcs_results):
                epoch_data = wcs_results[i]
                st.markdown(f"**{epoch_name} Epoch:**")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("TH_0 Distance", f"{epoch_data[0] if len(epoch_data) > 0 else 0:.1f} m")
                with col2:
                    st.metric("TH_0 Time", f"{epoch_data[1] if len(epoch_data) > 1 else 0:.1f} s")
                with col3:
                    st.metric("TH_1 Distance", f"{epoch_data[3] if len(epoch_data) > 3 else 0:.1f} m")
                with col4:
                    st.metric("TH_1 Time", f"{epoch_data[4] if len(epoch_data) > 4 else 0:.1f} s")
    
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