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
from advanced_analytics import analyze_cohort_performance, create_cohort_report, export_cohort_analysis


def get_smart_output_path(input_method: str, data_folder: str = None, uploaded_files = None) -> str:
    """
    Determine the optimal output path based on input method and user preferences
    
    Args:
        input_method: "Upload File" or "Select from Folder"
        data_folder: Path to the data folder (if using folder selection)
        uploaded_files: List of uploaded files (if using file upload)
    
    Returns:
        Path to the output directory
    """
    from datetime import datetime
    
    # Create timestamp for session organization
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    if input_method == "Select from Folder" and data_folder:
        # Create OUTPUT folder in the selected data directory
        output_base = os.path.join(data_folder, "OUTPUT")
        output_path = os.path.join(output_base, timestamp)
        
        # Create the directory structure
        os.makedirs(output_path, exist_ok=True)
        
        return output_path
    
    else:
        # For uploaded files, use project root with session organization
        output_base = "OUTPUT"
        output_path = os.path.join(output_base, timestamp)
        
        # Create the directory structure
        os.makedirs(output_path, exist_ok=True)
        
        return output_path


def display_output_settings(input_method: str, data_folder: str = None) -> str:
    """
    Display output settings and allow user to customize output location
    
    Args:
        input_method: Current input method
        data_folder: Current data folder (if applicable)
    
    Returns:
        Selected output path
    """
    st.markdown("### 📁 Output Settings")
    
    # Get default output path
    default_output_path = get_smart_output_path(input_method, data_folder)
    
    # Show current output location
    st.markdown(f"""
    <div class="status-badge status-success">
        📁 Default output location: {os.path.abspath(default_output_path)}
    </div>
    """, unsafe_allow_html=True)
    
    # Output customization options
    output_option = st.radio(
        "Output location:",
        ["Use default location", "Custom output folder"],
        help="Choose where to save analysis results"
    )
    
    if output_option == "Custom output folder":
        custom_output = st.text_input(
            "Enter custom output folder path:",
            value=default_output_path,
            help="Enter the full path where you want to save analysis results"
        )
        
        if custom_output:
            # Create the custom directory
            try:
                os.makedirs(custom_output, exist_ok=True)
                st.markdown(f"""
                <div class="status-badge status-success">
                    ✅ Custom output folder created: {os.path.abspath(custom_output)}
                </div>
                """, unsafe_allow_html=True)
                return custom_output
            except Exception as e:
                st.markdown(f"""
                <div class="status-badge status-error">
                    ❌ Error creating custom folder: {str(e)}
                </div>
                """, unsafe_allow_html=True)
                return default_output_path
    else:
        return default_output_path


def main():
    """Main Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title="WCS Analysis Platform",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Enhanced CSS for modern, professional appearance
    st.markdown("""
    <style>
    /* Modern color palette */
    :root {
        --primary-color: #2563eb;
        --secondary-color: #64748b;
        --success-color: #059669;
        --warning-color: #d97706;
        --error-color: #dc2626;
        --background-light: #f8fafc;
        --border-color: #e2e8f0;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
    }
    
    /* Main header with gradient */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Enhanced metric cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    /* Configuration sections */
    .config-section {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .config-section:hover {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Enhanced typography */
    h3 {
        font-size: 1.4rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.75rem;
        border-bottom: 2px solid var(--primary-color);
        padding-bottom: 0.5rem;
    }
    
    h4 {
        font-size: 1.2rem;
        font-weight: 500;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    /* Improved data frames */
    .stDataFrame {
        font-size: 0.9rem;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Enhanced metrics */
    .stMetric {
        font-size: 0.95rem;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
    }
    
    /* Progress indicators */
    .progress-container {
        background: var(--background-light);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .status-success {
        background-color: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
    }
    
    .status-warning {
        background-color: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
    }
    
    .status-error {
        background-color: #fee2e2;
        color: #991b1b;
        border: 1px solid #fecaca;
    }
    
    /* Responsive design improvements */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .config-section {
            padding: 1rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
    }
    
    /* Loading animations */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid var(--primary-color);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: var(--background-light);
        border-radius: 8px 8px 0 0;
        border: 1px solid var(--border-color);
        border-bottom: none;
        padding: 12px 24px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color);
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🔥 WCS Analysis Platform</h1>', unsafe_allow_html=True)
    st.markdown("### Professional Worst Case Scenario Analysis for GPS Data")
    
    # Enhanced configuration section with better visual hierarchy
    st.markdown("---")
    st.markdown("### ⚙️ Configuration")
    
    # Configuration in a more balanced layout
    col1, col2, col3, col4 = st.columns([2.5, 2, 2, 1.5])
    
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
                
                # Enhanced file upload feedback
                if uploaded_files:
                    st.markdown(f"""
                    <div class="status-badge status-success">
                        ✅ {len(uploaded_files)} file(s) uploaded
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show uploaded files in a compact list without nested expander
                    st.markdown("**📄 Uploaded Files:**")
                    file_list = "\n".join([f"• {file.name}" for file in uploaded_files])
                    st.text(file_list)
                
                selected_files = uploaded_files if uploaded_files else []
            else:
                # Enhanced folder selection with navigation
                st.markdown("**📁 Folder Selection**")
                
                # Quick access to common folders
                common_folders = {
                    "📂 Project Data": "data",
                    "📂 Test Data": "data/test_data", 
                    "📂 Sample Data": "data/sample_data",
                    "📂 Current Directory": ".",
                    "📂 Home Directory": os.path.expanduser("~")
                }
                
                # Quick folder selection
                quick_folder = st.selectbox(
                    "Quick access to common folders:",
                    ["Custom path..."] + list(common_folders.keys()),
                    help="Select a common folder or choose 'Custom path...' to browse"
                )
                
                if quick_folder == "Custom path...":
                    # Custom path input
                    data_folder = st.text_input(
                        "Enter custom folder path:",
                        value="data/test_data",
                        help="Enter the full path to your data folder"
                    )
                else:
                    data_folder = common_folders[quick_folder]
                
                # Folder navigation and file browsing
                if data_folder and os.path.exists(data_folder):
                    # Show current folder info
                    st.markdown(f"""
                    <div class="status-badge status-success">
                        📁 Current folder: {os.path.abspath(data_folder)}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # List subdirectories for navigation
                    try:
                        items = os.listdir(data_folder)
                        subdirs = [item for item in items if os.path.isdir(os.path.join(data_folder, item))]
                        
                        if subdirs:
                            st.markdown("**📂 Available subdirectories:**")
                            for subdir in sorted(subdirs):
                                subdir_path = os.path.join(data_folder, subdir)
                                if st.button(f"📁 {subdir}", key=f"subdir_{subdir}"):
                                    data_folder = subdir_path
                                    st.rerun()
                    
                    except PermissionError:
                        st.warning("⚠️ Permission denied accessing some directories")
                    
                    # Find CSV files in current folder
                    csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
                    
                    if csv_files:
                        st.markdown(f"""
                        <div class="status-badge status-success">
                            ✅ Found {len(csv_files)} CSV files
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # File selection options (without nested columns)
                        # Add "Select All" option with better styling
                        select_all = st.checkbox(
                            f"📁 Select All Files ({len(csv_files)} files)",
                            help="Check this to select all CSV files in the folder"
                        )
                        
                        # Show file count
                        st.info(f"📊 {len(csv_files)} CSV files available")
                        
                        if select_all:
                            # Select all files
                            selected_files = csv_files
                            st.markdown(f"""
                            <div class="status-badge status-success">
                                ✅ All {len(csv_files)} files selected
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            # Manual selection with file preview
                            st.markdown("**📄 Select files to analyze:**")
                            
                            # Show file list with sizes
                            file_info = []
                            for file in sorted(csv_files):
                                file_path = os.path.join(data_folder, file)
                                try:
                                    size = os.path.getsize(file_path)
                                    size_str = f"{size:,} bytes" if size < 1024*1024 else f"{size/1024/1024:.1f} MB"
                                    file_info.append(f"📄 {file} ({size_str})")
                                except:
                                    file_info.append(f"📄 {file}")
                            
                            selected_files = st.multiselect(
                                "Choose files:",
                                csv_files,
                                help=f"Select one or more CSV files for analysis"
                            )
                            
                            # Show selected files
                            if selected_files:
                                st.markdown("**✅ Selected files:**")
                                for file in selected_files:
                                    st.markdown(f"• {file}")
                        
                        selected_files = [os.path.join(data_folder, f) for f in selected_files]
                    else:
                        st.markdown("""
                        <div class="status-badge status-warning">
                            ⚠️ No CSV files found in this folder
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show what files are available
                        try:
                            all_files = os.listdir(data_folder)
                            if all_files:
                                st.markdown("**📄 Files in this folder:**")
                                for file in sorted(all_files)[:10]:  # Show first 10 files
                                    st.markdown(f"• {file}")
                                if len(all_files) > 10:
                                    st.markdown(f"*... and {len(all_files) - 10} more files*")
                        except:
                            pass
                        
                        selected_files = []
                else:
                    st.markdown("""
                    <div class="status-badge status-error">
                        ❌ Please enter a valid folder path
                    </div>
                    """, unsafe_allow_html=True)
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
    
    # Output settings section
    st.markdown("---")
    output_path = display_output_settings(input_method, data_folder if input_method == "Select from Folder" else None)
    
    # Main content area
    if selected_files:
        # Enhanced summary cards with better visual design
        st.markdown("---")
        st.markdown("### 📊 Analysis Overview")
        
        # Create metric cards with enhanced styling
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="margin: 0; color: var(--text-secondary);">Files to Process</h4>
                <div style="font-size: 2rem; font-weight: 700; color: var(--primary-color);">{len(selected_files)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="margin: 0; color: var(--text-secondary);">Primary Epoch</h4>
                <div style="font-size: 2rem; font-weight: 700; color: var(--primary-color);">{epoch_duration} min</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="margin: 0; color: var(--text-secondary);">Additional Epochs</h4>
                <div style="font-size: 2rem; font-weight: 700; color: var(--primary-color);">{len(epoch_durations)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="margin: 0; color: var(--text-secondary);">Threshold 1 Range</h4>
                <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary-color);">{th1_min}-{th1_max} m/s</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced analysis execution with better progress tracking
        st.markdown("---")
        
        # Analysis button with enhanced styling
        if st.button("🚀 Run WCS Analysis", type="primary", use_container_width=True):
            # Create a progress container
            progress_container = st.container()
            
            with progress_container:
                st.markdown("""
                <div class="progress-container">
                    <h4 style="margin: 0 0 1rem 0;">🔄 Processing Files</h4>
                    <div class="loading-spinner"></div>
                    <span style="margin-left: 0.5rem;">Initializing analysis...</span>
                </div>
                """, unsafe_allow_html=True)
            
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
                    
                    # Enhanced file processing feedback
                    progress_text = f"📊 Processing file {i+1}/{len(selected_files)}: {filename}"
                    st.markdown(f"""
                    <div class="progress-container">
                        <h4 style="margin: 0 0 0.5rem 0;">{progress_text}</h4>
                        <div class="loading-spinner"></div>
                        <span style="margin-left: 0.5rem;">Reading data and performing analysis...</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
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
                        
                        # Enhanced success message
                        st.markdown(f"""
                        <div class="status-badge status-success">
                            ✅ Successfully processed {filename}
                        </div>
                        """, unsafe_allow_html=True)
                        
                    except Exception as e:
                        # Enhanced error message
                        st.markdown(f"""
                        <div class="status-badge status-error">
                            ❌ Error processing {filename}: {str(e)}
                        </div>
                        """, unsafe_allow_html=True)
                        continue
                
                if all_results:
                    # Enhanced completion message
                    st.markdown(f"""
                    <div class="progress-container" style="background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); border-color: #059669;">
                        <h4 style="margin: 0; color: #166534;">🎉 Analysis Complete!</h4>
                        <p style="margin: 0.5rem 0 0 0; color: #166534; font-weight: 500;">Successfully processed {len(all_results)} file(s)</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Store results in session state
                    st.session_state['all_results'] = all_results
                    st.session_state['analysis_complete'] = True
                    
                    # Automatic MATLAB format export for batch mode
                    if batch_mode and len(all_results) > 1:
                        try:
                            export_path = export_data_matlab_format(all_results, output_path, "xlsx")
                            st.markdown(f"""
                            <div class="progress-container" style="background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); border-color: #2563eb;">
                                <h4 style="margin: 0; color: #1e40af;">✅ Automatic MATLAB Format Export</h4>
                                <p style="margin: 0.5rem 0 0 0; color: #1e40af;">Data exported to Excel with multiple sheets!</p>
                                <p style="margin: 0.25rem 0 0 0; color: #1e40af; font-size: 0.9rem;"><strong>File saved to:</strong> {export_path}</p>
                                <p style="margin: 0.25rem 0 0 0; color: #1e40af; font-size: 0.9rem;">💡 This Excel file contains WCS Report, Summary Maximum Values, and Binned Data sheets matching your MATLAB workflow format.</p>
                            </div>
                            """, unsafe_allow_html=True)
                        except Exception as e:
                            st.markdown(f"""
                            <div class="status-badge status-warning">
                                ⚠️ Automatic export failed: {str(e)}. You can still export manually using the Export tab.
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Advanced analytics notification for large batches
                    if len(all_results) >= 10:
                        st.markdown(f"""
                        <div class="progress-container" style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-color: #d97706;">
                            <h4 style="margin: 0; color: #92400e;">🔬 Advanced Analytics Available!</h4>
                            <p style="margin: 0.5rem 0 0 0; color: #92400e;">With {len(all_results)} files, you now have access to comprehensive cohort analysis!</p>
                            <p style="margin: 0.25rem 0 0 0; color: #92400e; font-size: 0.9rem;">📊 <strong>Features:</strong> Statistical comparisons, performance distributions, outlier detection, and group insights</p>
                            <p style="margin: 0.25rem 0 0 0; color: #92400e; font-size: 0.9rem;">💡 <strong>Access:</strong> Use the "🔬 Advanced Analytics" tab below for detailed cohort analysis</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Display results based on mode
                    if batch_mode and len(all_results) > 1:
                        # Create tabs for better organization
                        if len(all_results) >= 10:
                            # Advanced analytics for large batches
                            tab1, tab2, tab3, tab4 = st.tabs(["📊 Results", "📈 Visualizations", "🔬 Advanced Analytics", "📤 Export"])
                        else:
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
                                            export_path = export_data_matlab_format(all_results, output_path, "xlsx")
                                            st.success(f"✅ MATLAB format Excel exported successfully!")
                                            st.info(f"📁 File saved to: `{export_path}`")
                                        except Exception as e:
                                            st.error(f"❌ Export failed: {str(e)}")
                                
                                with col2:
                                    if st.button("📄 CSV (MATLAB Format)", help="Export WCS Report to CSV in MATLAB format"):
                                        try:
                                            export_path = export_data_matlab_format(all_results, output_path, "csv")
                                            st.success(f"✅ MATLAB format CSV exported successfully!")
                                            st.info(f"📁 File saved to: `{export_path}`")
                                        except Exception as e:
                                            st.error(f"❌ Export failed: {str(e)}")
                                
                                with col3:
                                    if st.button("📋 JSON (MATLAB Format)", help="Export to JSON with structured data"):
                                        try:
                                            export_path = export_data_matlab_format(all_results, output_path, "json")
                                            st.success(f"✅ MATLAB format JSON exported successfully!")
                                            st.info(f"📁 File saved to: `{export_path}`")
                                        except Exception as e:
                                            st.error(f"❌ Export failed: {str(e)}")
                                
                                st.markdown("---")
                                st.markdown("#### 📊 **Standard Export Options**")
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    if st.button("📊 Standard CSV Export", help="Export all WCS analysis results to a CSV file"):
                                        export_path = export_wcs_data_to_csv(all_results, output_path)
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
                                    export_path = export_data_matlab_format(all_results, output_path, "xlsx")
                                    st.success(f"✅ MATLAB format Excel exported successfully!")
                                    st.info(f"📁 File saved to: `{export_path}`")
                                except Exception as e:
                                    st.error(f"❌ Export failed: {str(e)}")
                        
                        with col2:
                            if st.button("📄 CSV (MATLAB Format)", help="Export WCS Report to CSV in MATLAB format"):
                                try:
                                    export_path = export_data_matlab_format(all_results, output_path, "csv")
                                    st.success(f"✅ MATLAB format CSV exported successfully!")
                                    st.info(f"📁 File saved to: `{export_path}`")
                                except Exception as e:
                                    st.error(f"❌ Export failed: {str(e)}")
                        
                        with col3:
                            if st.button("📋 JSON (MATLAB Format)", help="Export to JSON with structured data"):
                                try:
                                    export_path = export_data_matlab_format(all_results, output_path, "json")
                                    st.success(f"✅ MATLAB format JSON exported successfully!")
                                    st.info(f"📁 File saved to: `{export_path}`")
                                except Exception as e:
                                    st.error(f"❌ Export failed: {str(e)}")
                        
                        st.markdown("---")
                        st.markdown("#### 📊 **Standard Export Options**")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("📊 Standard CSV Export", help="Export all WCS analysis results to a CSV file"):
                                export_path = export_wcs_data_to_csv(all_results, output_path)
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
                        
                        # Advanced Analytics Tab (only for large batches)
                        if len(all_results) >= 10:
                            with tab4:
                                display_advanced_analytics(all_results, output_path)
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


def display_advanced_analytics(all_results: list, output_path: str):
    """Display advanced analytics for large batch processing (>10 files)"""
    
    st.markdown("### 🔬 Advanced Analytics & Cohort Analysis")
    st.info("🎯 **Advanced Analytics**: Comprehensive group/cohort analysis for large datasets with statistical comparisons, performance distributions, and insights.")
    
    # Check if we have enough data for cohort analysis
    if len(all_results) < 10:
        st.warning("⚠️ Advanced analytics require at least 10 files for meaningful cohort analysis")
        return
    
    # Perform cohort analysis
    with st.spinner("🔬 Performing advanced cohort analysis..."):
        try:
            cohort_analysis = analyze_cohort_performance(all_results)
            
            if 'error' in cohort_analysis:
                st.error(f"❌ Cohort analysis failed: {cohort_analysis['error']}")
                return
            
            # Display cohort summary
            st.markdown("#### 📊 Cohort Performance Summary")
            summary = cohort_analysis['summary']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Players", summary['total_players'])
            with col2:
                st.metric("Total Observations", summary['total_observations'])
            with col3:
                st.metric("Avg Distance", f"{summary['distance_range']['mean']:.1f} m")
            with col4:
                st.metric("Distance Range", f"{summary['distance_range']['min']:.1f} - {summary['distance_range']['max']:.1f} m")
            
            # Display key insights
            if summary['insights']:
                st.markdown("#### 💡 Key Insights")
                for insight in summary['insights']:
                    st.info(f"• {insight}")
            
            # Display top performers
            st.markdown("#### 🏆 Top Performers")
            top_performers_df = pd.DataFrame([
                {'Player': player, 'Avg Distance (m)': distance}
                for player, distance in summary['top_performers'].items()
            ])
            st.dataframe(top_performers_df, use_container_width=True, hide_index=True)
            
            # Display visualizations
            st.markdown("#### 📈 Advanced Visualizations")
            
            if 'visualizations' in cohort_analysis:
                viz = cohort_analysis['visualizations']
                
                # Performance Distribution
                if 'performance_distribution' in viz:
                    st.markdown("**Performance Distribution by Player**")
                    st.plotly_chart(viz['performance_distribution'], use_container_width=True)
                
                # Performance Heatmap
                if 'performance_heatmap' in viz:
                    st.markdown("**Performance Heatmap (Distance by Player & Epoch)**")
                    st.plotly_chart(viz['performance_heatmap'], use_container_width=True)
                
                # Threshold Comparison
                if 'threshold_comparison' in viz:
                    st.markdown("**Performance by Threshold**")
                    st.plotly_chart(viz['threshold_comparison'], use_container_width=True)
                
                # Player Radar Chart
                if 'player_radar' in viz:
                    st.markdown("**Player Performance Comparison (Normalized)**")
                    st.plotly_chart(viz['player_radar'], use_container_width=True)
                
                # Performance Scatter
                if 'performance_scatter' in viz:
                    st.markdown("**WCS Distance vs Average Velocity**")
                    st.plotly_chart(viz['performance_scatter'], use_container_width=True)
            
            # Display statistical analysis
            st.markdown("#### 📊 Statistical Analysis")
            
            if 'statistics' in cohort_analysis:
                stats = cohort_analysis['statistics']
                
                # Overall statistics
                if 'overall' in stats:
                    overall_stats = stats['overall']
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Mean Distance", f"{overall_stats['mean_distance']:.2f} m")
                    with col2:
                        st.metric("Std Distance", f"{overall_stats['std_distance']:.2f} m")
                    with col3:
                        st.metric("IQR Distance", f"{overall_stats['iqr_distance']:.2f} m")
                
                # Player statistics table
                if 'by_player' in stats:
                    st.markdown("**Player Statistics**")
                    player_stats = stats['by_player']
                    st.dataframe(player_stats, use_container_width=True)
            
            # Display rankings
            st.markdown("#### 🏅 Performance Rankings")
            
            if 'rankings' in cohort_analysis:
                rankings = cohort_analysis['rankings']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'overall' in rankings:
                        st.markdown("**Overall Performance Ranking**")
                        overall_rank = rankings['overall'].head(10)
                        st.dataframe(overall_rank, use_container_width=True, hide_index=True)
                
                with col2:
                    if 'consistency' in rankings:
                        st.markdown("**Consistency Ranking (Lowest Std Dev)**")
                        consistency_rank = rankings['consistency'].head(10)
                        st.dataframe(consistency_rank, use_container_width=True, hide_index=True)
            
            # Export options for advanced analytics
            st.markdown("#### 📤 Export Advanced Analytics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Export Cohort Data", help="Export cohort analysis data to CSV"):
                    try:
                        exported_files = export_cohort_analysis(cohort_analysis, output_path)
                        if 'error' not in exported_files:
                            st.success("✅ Cohort data exported successfully!")
                            for file_type, file_path in exported_files.items():
                                st.info(f"📁 {file_type}: {file_path}")
                        else:
                            st.error(f"❌ Export failed: {exported_files['error']}")
                    except Exception as e:
                        st.error(f"❌ Export failed: {str(e)}")
            
            with col2:
                if st.button("📋 Download Report", help="Download comprehensive cohort analysis report"):
                    try:
                        report_text = create_cohort_report(cohort_analysis)
                        st.download_button(
                            label="💾 Download Report",
                            data=report_text,
                            file_name=f"Cohort_Analysis_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                    except Exception as e:
                        st.error(f"❌ Report generation failed: {str(e)}")
            
            with col3:
                if st.button("📈 Export Visualizations", help="Export all cohort visualizations as HTML"):
                    try:
                        # Create a combined HTML file with all visualizations
                        html_content = "<html><head><title>Cohort Analysis Visualizations</title></head><body>"
                        html_content += "<h1>Cohort Analysis Visualizations</h1>"
                        
                        if 'visualizations' in cohort_analysis:
                            for viz_name, viz_fig in cohort_analysis['visualizations'].items():
                                html_content += f"<h2>{viz_name.replace('_', ' ').title()}</h2>"
                                html_content += viz_fig.to_html(full_html=False)
                                html_content += "<hr>"
                        
                        html_content += "</body></html>"
                        
                        st.download_button(
                            label="💾 Download Visualizations",
                            data=html_content,
                            file_name=f"Cohort_Visualizations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                            mime="text/html"
                        )
                    except Exception as e:
                        st.error(f"❌ Visualization export failed: {str(e)}")
        
        except Exception as e:
            st.error(f"❌ Advanced analytics failed: {str(e)}")
            st.exception(e)


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