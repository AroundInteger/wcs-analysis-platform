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
from data_export import export_data_matlab_format, get_export_formats


def main():
    """Main Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title="WCS Analysis Platform",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="collapsed"
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
    .config-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e9ecef;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🔥 WCS Analysis Platform</h1>', unsafe_allow_html=True)
    st.markdown("### Professional Worst Case Scenario Analysis for GPS Data")
    
    # Top configuration bar
    st.markdown("### ⚙️ Configuration")
    
    # Configuration in horizontal layout
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
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
                    "📁 Upload GPS CSV files",
                    type=['csv'],
                    accept_multiple_files=True,
                    help="Drag and drop multiple CSV files or click to browse. Supports StatSport, Catapult, and Generic GPS formats."
                )
                
                # Debug information
                if uploaded_files:
                    st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
                    for i, file in enumerate(uploaded_files):
                        st.info(f"📄 {file.name}")
                
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
                        st.success(f"✅ Found {len(csv_files)} CSV files")
                        
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
    
    with col2:
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
    
    with col3:
        with st.expander("🎯 Threshold Parameters", expanded=True):
            # Default threshold is always 0-100 m/s
            th0_min = 0.0
            th0_max = 100.0
            st.info("🎯 **Default Threshold**: 0.0 - 100.0 m/s (all velocities)")
            
            th1_min = st.number_input("Threshold 1 Min Velocity (m/s)", 0.0, 10.0, 5.0, 0.1, help="Used for contiguous WCS analysis only. Rolling WCS uses all velocities (no thresholding).")
            th1_max = st.number_input("Threshold 1 Max Velocity (m/s)", 0.0, 100.0, 100.0, 0.1, help="Used for contiguous WCS analysis only. Rolling WCS uses all velocities (no thresholding).")
    
    with col4:
        with st.expander("📊 Analysis Options", expanded=True):
            # Note: WCS Analysis now calculates both rolling and contiguous methods automatically
            st.info("🔄 **Dual WCS Analysis**: Both rolling (accumulated work) and contiguous (best continuous period) methods are calculated automatically")
            
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
            st.metric("Threshold 1 Range", f"{th1_min}-{th1_max} m/s")
        
        # Analysis execution
        if st.button("🚀 Run WCS Analysis", type="primary", use_container_width=True):
            with st.spinner("🔄 Processing files..."):
                # Process files
                all_results = []
                
                for i, file_path in enumerate(selected_files):
                    # Get filename for display
                    if isinstance(file_path, str):
                        # File from folder
                        filename = os.path.basename(file_path)
                    else:
                        # Uploaded file
                        filename = file_path.name
                    
                    st.info(f"📊 Processing file {i+1}/{len(selected_files)}: {filename}")
                    
                    try:
                        # Read and validate data
                        if isinstance(file_path, str):
                            # File from folder
                            df, metadata, file_type_info = read_csv_with_metadata(file_path)
                        else:
                            # Uploaded file
                            df, metadata, file_type_info = read_csv_with_metadata(file_path)
                        
                        # Validate velocity data
                        if not validate_velocity_data(df):
                            st.error(f"❌ Invalid velocity data in {filename}")
                            continue
                        
                        # Prepare parameters dictionary
                        parameters = {
                            'sampling_rate': sampling_rate,
                            'epoch_duration': epoch_duration,
                            'epoch_durations': [epoch_duration] + epoch_durations,  # Include primary + additional
                            'th0_min': th0_min,
                            'th0_max': th0_max,
                            'th1_min': th1_min,
                            'th1_max': th1_max,
                        }
                        
                        # Perform WCS analysis
                        results = perform_wcs_analysis(
                            df, 
                            metadata, 
                            file_type_info, 
                            parameters
                        )
                        
                        # Store results with metadata
                        all_results.append({
                            'file_path': file_path,
                            'metadata': metadata,
                            'results': results
                        })
                        
                        st.success(f"✅ Successfully processed {filename}")
                        
                    except Exception as e:
                        st.error(f"❌ Error processing {filename}: {str(e)}")
                        continue
                
                if all_results:
                    st.success(f"🎉 Analysis complete! Processed {len(all_results)} file(s)")
                    
                    # Store results in session state
                    st.session_state['all_results'] = all_results
                    st.session_state['analysis_complete'] = True
                    
                    # Automatic MATLAB format export for batch mode
                    if batch_mode and len(all_results) > 1:
                        try:
                            export_path = export_data_matlab_format(all_results, "OUTPUT", "xlsx")
                            st.success(f"✅ **Automatic MATLAB Format Export**: Data exported to Excel with multiple sheets!")
                            st.info(f"📁 **File saved to**: `{export_path}`")
                            st.info("💡 **Note**: This Excel file contains WCS Report, Summary Maximum Values, and Binned Data sheets matching your MATLAB workflow format.")
                        except Exception as e:
                            st.warning(f"⚠️ Automatic export failed: {str(e)}. You can still export manually using the Export tab.")
                    
                    # Display results based on mode
                    if batch_mode and len(all_results) > 1:
                        # Create tabs for better organization
                        tab1, tab2, tab3 = st.tabs(["📊 Results", "📈 Visualizations", "📤 Export"])
                        
                        with tab1:
                            st.markdown("### 📋 Analysis Results")
                            display_batch_summary(all_results)
                        
                        with tab2:
                            st.markdown("### 📈 Analysis Visualizations")
                            # Combined visualizations for multiple files
                            if len(all_results) > 1:
                                st.markdown("#### 📊 Combined Analysis Visualizations")
                                
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
                                        st.markdown("#### 👤 Individual Player Analysis")
                                        st.info("📊 **Note**: Showing analysis for the first 3 players only to prevent overlapping. Use the heatmap above for all players.")
                                        st.plotly_chart(combined_viz['individual_player_grid'], use_container_width=True)
                            else:
                                st.info("📊 Upload multiple files to see combined visualizations")
                        
                        with tab3:
                            st.markdown("### 📤 Export Options")
                            # Export functionality
                            if include_export:
                                st.markdown("#### 🎯 **MATLAB-Compatible Export (Recommended)**")
                                st.info("💡 **MATLAB Format**: Exports data in the exact format used by your existing MATLAB workflow, including WCS Report, Summary Maximum Values, and Binned Data sheets.")
                                
                                # MATLAB format export options
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    if st.button("📊 Excel (MATLAB Format)", help="Export to Excel with multiple sheets matching MATLAB output"):
                                        try:
                                            export_path = export_data_matlab_format(all_results, "OUTPUT", "xlsx")
                                            st.success(f"✅ MATLAB format Excel exported successfully!")
                                            st.info(f"📁 File saved to: `{export_path}`")
                                        except Exception as e:
                                            st.error(f"❌ Export failed: {str(e)}")
                                
                                with col2:
                                    if st.button("📄 CSV (MATLAB Format)", help="Export WCS Report to CSV in MATLAB format"):
                                        try:
                                            export_path = export_data_matlab_format(all_results, "OUTPUT", "csv")
                                            st.success(f"✅ MATLAB format CSV exported successfully!")
                                            st.info(f"📁 File saved to: `{export_path}`")
                                        except Exception as e:
                                            st.error(f"❌ Export failed: {str(e)}")
                                
                                with col3:
                                    if st.button("📋 JSON (MATLAB Format)", help="Export to JSON with structured data"):
                                        try:
                                            export_path = export_data_matlab_format(all_results, "OUTPUT", "json")
                                            st.success(f"✅ MATLAB format JSON exported successfully!")
                                            st.info(f"📁 File saved to: `{export_path}`")
                                        except Exception as e:
                                            st.error(f"❌ Export failed: {str(e)}")
                                
                                st.markdown("---")
                                st.markdown("#### 📊 **Standard Export Options**")
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    if st.button("📊 Standard CSV Export", help="Export all WCS analysis results to a CSV file in the OUTPUT folder"):
                                        export_path = export_wcs_data_to_csv(all_results)
                                        if export_path:
                                            st.success(f"✅ Standard CSV exported successfully!")
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
                        # Display individual results
                        for result in all_results:
                            display_wcs_results(result['results'], result['metadata'], include_visualizations, enhanced_wcs_viz)
                else:
                    st.error("❌ No files were successfully processed")
    
    # Display results if analysis was previously completed
    elif st.session_state.get('analysis_complete', False):
        all_results = st.session_state.get('all_results', [])
        if all_results:
            st.success("📊 Previous analysis results found")
            
            # Display results based on mode
            if batch_mode and len(all_results) > 1:
                # Create tabs for better organization
                tab1, tab2, tab3 = st.tabs(["📊 Results", "📈 Visualizations", "📤 Export"])
                
                with tab1:
                    st.markdown("### 📋 Analysis Results")
                    display_batch_summary(all_results)
                
                with tab2:
                    st.markdown("### 📈 Analysis Visualizations")
                    # Combined visualizations for multiple files
                    if len(all_results) > 1:
                        st.markdown("#### 📊 Combined Analysis Visualizations")
                        
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
                                st.markdown("#### 👤 Individual Player Analysis")
                                st.info("📊 **Note**: Showing analysis for the first 3 players only to prevent overlapping. Use the heatmap above for all players.")
                                st.plotly_chart(combined_viz['individual_player_grid'], use_container_width=True)
                    else:
                        st.info("📊 Upload multiple files to see combined visualizations")
                
                with tab3:
                    st.markdown("### 📤 Export Options")
                    # Export functionality
                    if include_export:
                        st.markdown("#### 🎯 **MATLAB-Compatible Export (Recommended)**")
                        st.info("💡 **MATLAB Format**: Exports data in the exact format used by your existing MATLAB workflow, including WCS Report, Summary Maximum Values, and Binned Data sheets.")
                        
                        # MATLAB format export options
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("📊 Excel (MATLAB Format)", help="Export to Excel with multiple sheets matching MATLAB output"):
                                try:
                                    export_path = export_data_matlab_format(all_results, "OUTPUT", "xlsx")
                                    st.success(f"✅ MATLAB format Excel exported successfully!")
                                    st.info(f"📁 File saved to: `{export_path}`")
                                except Exception as e:
                                    st.error(f"❌ Export failed: {str(e)}")
                        
                        with col2:
                            if st.button("📄 CSV (MATLAB Format)", help="Export WCS Report to CSV in MATLAB format"):
                                try:
                                    export_path = export_data_matlab_format(all_results, "OUTPUT", "csv")
                                    st.success(f"✅ MATLAB format CSV exported successfully!")
                                    st.info(f"📁 File saved to: `{export_path}`")
                                except Exception as e:
                                    st.error(f"❌ Export failed: {str(e)}")
                        
                        with col3:
                            if st.button("📋 JSON (MATLAB Format)", help="Export to JSON with structured data"):
                                try:
                                    export_path = export_data_matlab_format(all_results, "OUTPUT", "json")
                                    st.success(f"✅ MATLAB format JSON exported successfully!")
                                    st.info(f"📁 File saved to: `{export_path}`")
                                except Exception as e:
                                    st.error(f"❌ Export failed: {str(e)}")
                        
                        st.markdown("---")
                        st.markdown("#### 📊 **Standard Export Options**")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("📊 Standard CSV Export", help="Export all WCS analysis results to a CSV file in the OUTPUT folder"):
                                export_path = export_wcs_data_to_csv(all_results)
                                if export_path:
                                    st.success(f"✅ Standard CSV exported successfully!")
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
                # Display individual results
                for result in all_results:
                    display_wcs_results(result['results'], result['metadata'], include_visualizations, enhanced_wcs_viz)
    
    # Instructions when no files are selected
    else:
        st.markdown("---")
        st.markdown("### 📋 Getting Started")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **1. Upload or Select Files**
            - Use the **Data Input** section above
            - Drag & drop multiple CSV files
            - Or select from a folder
            
            **2. Configure Parameters**
            - Set epoch durations for analysis
            - Adjust velocity thresholds
            - Choose analysis options
            """)
        
        with col2:
            st.markdown("""
            **3. Run Analysis**
            - Click **Run WCS Analysis** button
            - View results and visualizations
            - Export data as needed
            
            **Supported Formats:**
            - StatSport CSV files
            - Catapult CSV files  
            - Generic GPS CSV files
            """)
        
        # Show sample data info
        if os.path.exists("data/test_data"):
            st.info("💡 **Tip**: Sample data is available in the `data/test_data` folder for testing")


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
                    'mean_acceleration': ks['acceleration']['mean_positive'],  # Mean of positive acceleration only
                    'mean_deceleration_from_accel': ks['acceleration']['mean_negative'],  # Mean of negative acceleration
                    'acceleration_events': ks['acceleration']['positive_count'],
                    'deceleration_events': ks['acceleration']['negative_count']
                })
            
            if 'deceleration' in ks:
                kinematic_stats.update({
                    'max_deceleration': ks['deceleration']['max'],
                    'mean_deceleration': ks['deceleration']['mean'],
                    'deceleration_events': ks['deceleration']['count']
                })
            
            if 'distance' in ks:
                kinematic_stats['total_distance'] = ks['distance']['total']
            
            if 'power' in ks:
                kinematic_stats.update({
                    'max_power': ks['power']['max'],
                    'mean_power': ks['power']['mean']
                })
        
        # Prepare WCS summary for both methods
        wcs_summary = None
        rolling_wcs_results = results.get('rolling_wcs_results', [])
        contiguous_wcs_results = results.get('contiguous_wcs_results', [])
        
        if rolling_wcs_results and len(rolling_wcs_results) > 0:
            epoch_data = rolling_wcs_results[0]  # Use first epoch for summary
            wcs_summary = {
                'rolling_th0_distance': epoch_data[0] if len(epoch_data) > 0 else 0,
                'rolling_th0_duration': epoch_data[1] if len(epoch_data) > 1 else 0,
                'rolling_th1_distance': epoch_data[4] if len(epoch_data) > 4 else 0,
                'rolling_th1_duration': epoch_data[5] if len(epoch_data) > 5 else 0
            }
            
            # Add contiguous results if available
            if contiguous_wcs_results and len(contiguous_wcs_results) > 0:
                cont_epoch_data = contiguous_wcs_results[0]
                wcs_summary.update({
                    'contiguous_th0_distance': cont_epoch_data[0] if len(cont_epoch_data) > 0 else 0,
                    'contiguous_th0_duration': cont_epoch_data[1] if len(cont_epoch_data) > 1 else 0,
                    'contiguous_th1_distance': cont_epoch_data[4] if len(cont_epoch_data) > 4 else 0,
                    'contiguous_th1_duration': cont_epoch_data[5] if len(cont_epoch_data) > 5 else 0
                })
        
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
    
    # Display WCS metrics for both methods
    rolling_wcs_results = results.get('rolling_wcs_results', [])
    contiguous_wcs_results = results.get('contiguous_wcs_results', [])
    
    if rolling_wcs_results or contiguous_wcs_results:
        st.markdown("### 🔥 WCS Analysis Results")
        
        # Create WCS results table for both methods
        wcs_data = []
        
        # Get epoch durations from the analysis results or use defaults
        epoch_durations = results.get('epoch_durations', [0.5, 1.0, 1.5, 2.0, 3.0, 5.0])
        epoch_names = [f"{dur:.1f}min" for dur in epoch_durations]
        
        for i, epoch_name in enumerate(epoch_names):
            row_data = {'Epoch': epoch_name}
            
            # Add rolling results
            if i < len(rolling_wcs_results):
                epoch_data = rolling_wcs_results[i]
                row_data.update({
                    'Rolling Default Distance (m)': f"{epoch_data[0] if len(epoch_data) > 0 else 0:.1f}",
                    'Rolling Default Duration (s)': f"{epoch_data[1] if len(epoch_data) > 1 else 0:.1f}",
                    'Rolling Threshold 1 Distance (m)': f"{epoch_data[4] if len(epoch_data) > 4 else 0:.1f}",
                    'Rolling Threshold 1 Duration (s)': f"{epoch_data[5] if len(epoch_data) > 5 else 0:.1f}"
                })
            else:
                row_data.update({
                    'Rolling Default Distance (m)': 'N/A',
                    'Rolling Default Duration (s)': 'N/A',
                    'Rolling Threshold 1 Distance (m)': 'N/A',
                    'Rolling Threshold 1 Duration (s)': 'N/A'
                })
            
            # Add contiguous results
            if i < len(contiguous_wcs_results):
                epoch_data = contiguous_wcs_results[i]
                row_data.update({
                    'Contiguous Default Distance (m)': f"{epoch_data[0] if len(epoch_data) > 0 else 0:.1f}",
                    'Contiguous Default Duration (s)': f"{epoch_data[1] if len(epoch_data) > 1 else 0:.1f}",
                    'Contiguous Threshold 1 Distance (m)': f"{epoch_data[4] if len(epoch_data) > 4 else 0:.1f}",
                    'Contiguous Threshold 1 Duration (s)': f"{epoch_data[5] if len(epoch_data) > 5 else 0:.1f}"
                })
            else:
                row_data.update({
                    'Contiguous Default Distance (m)': 'N/A',
                    'Contiguous Default Duration (s)': 'N/A',
                    'Contiguous Threshold 1 Distance (m)': 'N/A',
                    'Contiguous Threshold 1 Duration (s)': 'N/A'
                })
            
            wcs_data.append(row_data)
        
        if wcs_data:
            wcs_df = pd.DataFrame(wcs_data)
            st.dataframe(
                wcs_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No WCS results available")
    
    # Display visualizations
    if 'processed_data' in results and include_visualizations:
        # Import visualization functions
        from visualization import (create_enhanced_wcs_visualization, create_wcs_period_details, 
                                 create_kinematic_visualization, create_dual_wcs_velocity_visualization)
        
        # Display dual WCS velocity visualization
        st.markdown("### 🔥 Dual WCS Velocity Analysis (Rolling: Accumulated Work | Contiguous: Best Continuous Period)")
        dual_wcs_fig = create_dual_wcs_velocity_visualization(
            results['processed_data'], 
            metadata, 
            rolling_wcs_results,
            contiguous_wcs_results
        )
        
        if dual_wcs_fig:
            st.plotly_chart(dual_wcs_fig, use_container_width=True)
        else:
            st.warning("Could not create dual WCS velocity visualization")
        
        if enhanced_wcs_viz:
            st.markdown("### 🔥 Enhanced WCS Analysis Visualizations")
            
            # Create enhanced WCS visualization (using rolling method for display)
            enhanced_wcs_fig = create_enhanced_wcs_visualization(
                results['processed_data'], 
                metadata, 
                rolling_wcs_results,
                'rolling'
            )
            
            if enhanced_wcs_fig:
                st.plotly_chart(enhanced_wcs_fig, use_container_width=True)
            else:
                st.warning("Could not create enhanced WCS visualization")
            
            # Display detailed WCS period information
            if rolling_wcs_results or contiguous_wcs_results:
                st.markdown("### 📋 Detailed WCS Period Information")
                
                # Get epoch durations from the analysis results
                epoch_durations = results.get('epoch_durations', [0.5, 1.0, 1.5, 2.0, 3.0, 5.0])
                
                # Create detailed tables for both methods
                if rolling_wcs_results:
                    st.markdown("#### Rolling WCS Periods (Accumulated Work)")
                    rolling_details_df = create_wcs_period_details(rolling_wcs_results, epoch_durations, 'rolling')
                    if not rolling_details_df.empty:
                        st.dataframe(
                            rolling_details_df,
                            use_container_width=True,
                            hide_index=True
                        )
                
                if contiguous_wcs_results:
                    st.markdown("#### Contiguous WCS Periods")
                    contiguous_details_df = create_wcs_period_details(contiguous_wcs_results, epoch_durations, 'contiguous')
                    if not contiguous_details_df.empty:
                        st.dataframe(
                            contiguous_details_df,
                            use_container_width=True,
                            hide_index=True
                        )
        
        # Display kinematic visualizations
        st.markdown("### 📈 Kinematic Analysis Visualizations")
        
        # Create kinematic visualization
        kinematic_fig = create_kinematic_visualization(
            results['processed_data'], 
            metadata, 
            rolling_wcs_results  # Use rolling results for kinematic visualization
        )
        
        if kinematic_fig:
            st.plotly_chart(kinematic_fig, use_container_width=True)
        else:
            st.warning("Could not create kinematic visualization")
    else:
        st.markdown("### 📈 Standard Kinematic Analysis Visualizations")


def display_batch_summary(all_results: list):
    """Display batch processing summary"""
    st.markdown("### 📊 Batch Processing Summary")
    
    if not all_results:
        st.warning("No results to display")
        return
    
    # Create summary table
    summary_data = []
    for result in all_results:
        metadata = result.get('metadata', {})
        
        # Handle different result structures
        if 'results' in result:
            results_data = result['results']
            # Get velocity stats - handle both old and new structure
            if isinstance(results_data, dict):
                velocity_stats = results_data.get('velocity_stats', {})
                kinematic_stats = results_data.get('kinematic_stats', {})
            else:
                # Fallback for old structure
                velocity_stats = {}
                kinematic_stats = {}
        else:
            # Direct structure
            velocity_stats = result.get('velocity_stats', {})
            kinematic_stats = result.get('kinematic_stats', {})
        
        # Handle both file path types
        file_path = result.get('file_path', 'Unknown')
        if isinstance(file_path, str):
            file_name = os.path.basename(file_path)
        else:
            file_name = getattr(file_path, 'name', 'Unknown')
        
        # Get kinematic stats for distance
        distance_info = kinematic_stats.get('distance', {}) if isinstance(kinematic_stats, dict) else {}
        total_distance = distance_info.get('total', 0) if distance_info else 0
        
        # Get additional player information
        position = metadata.get('position', 'Unknown')
        competition = metadata.get('competition', 'Unknown')
        matchday = metadata.get('matchday', 'Unknown')
        
        summary_data.append({
            'File': file_name,
            'Player': metadata.get('player_name', 'Unknown'),
            'Position': position,
            'Competition': competition,
            'Match Day': matchday,
            'Records': metadata.get('total_records', 0),
            'Duration (min)': round(metadata.get('duration_minutes', 0), 1),
            'Mean Velocity (m/s)': round(velocity_stats.get('mean', 0), 2),
            'Max Velocity (m/s)': round(velocity_stats.get('max', 0), 2),
            'Total Distance (m)': round(total_distance, 1)
        })
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Files", len(summary_data))
        with col2:
            total_records = sum(row['Records'] for row in summary_data)
            st.metric("Total Records", f"{total_records:,}")
        with col3:
            total_duration = sum(row['Duration (min)'] for row in summary_data)
            st.metric("Total Duration", f"{total_duration:.1f} min")
    else:
        st.warning("No results to display")


if __name__ == "__main__":
    main() 