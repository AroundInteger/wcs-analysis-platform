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
from src.file_ingestion import read_csv_with_metadata, validate_velocity_data
from src.wcs_analysis import perform_wcs_analysis
from src.visualization import create_velocity_visualization
from src.batch_processing import process_batch_files, export_wcs_data_to_csv, create_combined_visualizations, create_combined_wcs_dataframe
from src.data_export import export_data_matlab_format, get_export_formats
from src.advanced_analytics import analyze_cohort_performance, create_cohort_report, export_cohort_analysis
from src.advanced_visualizations import (
    create_comprehensive_dashboard,
    create_individual_player_dashboard,
    create_performance_insights_dashboard,
    save_dashboard_visualizations
)
from src.file_browser import create_simple_folder_picker, get_csv_files_from_folder


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
    st.markdown('<h4 class="subsection-header">Output Settings</h4>', unsafe_allow_html=True)
    
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
        page_icon="📊",
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
    
    /* Custom subtitle styling for better visibility */
    .subtitle-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #f59e0b !important;
        text-align: center;
        margin-bottom: 1.5rem;
        padding: 0.5rem 1rem;
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-radius: 8px;
        border: 2px solid #f59e0b;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Enhanced section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e40af !important;
        margin-bottom: 1rem;
        padding: 0.75rem 1rem;
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-radius: 8px;
        border-left: 4px solid #2563eb;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Subsection headers */
    .subsection-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #374151 !important;
        margin-bottom: 0.75rem;
        padding: 0.5rem 0;
        border-bottom: 2px solid #e5e7eb;
        text-shadow: 0 1px 1px rgba(0,0,0,0.05);
    }
    
    /* Button text wrapping - prevent word splitting */
    .stButton > button,
    .stButton > button > div,
    .stButton > button > span,
    .stButton > button > p {
        white-space: normal !important;
        word-wrap: break-word !important;
        word-break: keep-all !important;
    }
    
    /* Force all text in Streamlit metrics to be visible */
    .stMetric,
    .stMetric *,
    .stMetric > div,
    .stMetric > div > div,
    .stMetric > div > div > div,
    .stMetric > div > div > div > div,
    .stMetric > div > div > div > div > div {
        color: #1e293b !important;
        background-color: transparent !important;
    }
    
    /* Force all text in metric cards to be visible */
    .metric-card,
    .metric-card *,
    .metric-card h4,
    .metric-card div,
    .metric-card span,
    .metric-card p {
        color: #1e293b !important;
        background-color: transparent !important;
    }
    
    /* Override any white text */
    div[style*="color: white"],
    div[style*="color: #fff"],
    div[style*="color: #ffffff"],
    h4[style*="color: white"],
    h4[style*="color: #fff"],
    h4[style*="color: #ffffff"] {
        color: #1e293b !important;
    }
    
    /* Ensure all text elements have proper color */
    .stMarkdown,
    .stMarkdown *,
    .stMarkdown > div,
    .stMarkdown > div > div {
        color: #1e293b !important;
    }
    
    /* Target specific problematic elements */
    .stMetric > div > div > div > div > div {
        color: #1e293b !important;
    }
    
    /* Ensure metric cards have proper colors */
    .metric-card h4 {
        color: #64748b !important;
    }
    
    .metric-card div[style*="font-size: 2rem"],
    .metric-card div[style*="font-size: 1.5rem"] {
        color: #2563eb !important;
    }
    
    /* Override any remaining white text */
    div[style*="color: white"],
    div[style*="color: #fff"],
    div[style*="color: #ffffff"],
    span[style*="color: white"],
    span[style*="color: #fff"],
    span[style*="color: #ffffff"] {
        color: #1e293b !important;
    }
        overflow-wrap: break-word !important;
        hyphens: none !important;
        line-height: 1.2 !important;
        text-align: center !important;
    }
    
    /* Button container styling */
    .stButton > button {
        min-height: 44px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0.5rem 1rem !important;
    }
    
    /* Ensure button text doesn't get cut off */
    .stButton > button > div {
        white-space: normal !important;
        word-wrap: break-word !important;
        word-break: keep-all !important;
        overflow-wrap: break-word !important;
        hyphens: none !important;
        max-width: 100% !important;
    }
    
    /* Override any Streamlit default button text styling */
    .stButton > button * {
        white-space: normal !important;
        word-wrap: break-word !important;
        word-break: keep-all !important;
        overflow-wrap: break-word !important;
        hyphens: none !important;
    }
    
    /* Force button text to wrap properly */
    .stButton > button {
        white-space: normal !important;
        overflow-wrap: break-word !important;
        word-break: keep-all !important;
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
    st.markdown('<h1 class="main-header">WCS Analysis Platform</h1>', unsafe_allow_html=True)
    st.markdown('<h3 class="subtitle-header">Professional Worst Case Scenario Analysis for GPS Data</h3>', unsafe_allow_html=True)
    
    # Enhanced configuration section with better visual hierarchy
    st.markdown("---")
    st.markdown('<h3 class="section-header">Configuration</h3>', unsafe_allow_html=True)
    
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
                # Use the new simple folder picker
                data_folder = create_simple_folder_picker(
                    title="📁 Select Data Folder",
                    default_path="data/test_data"
                )
                
                # Get CSV files from the selected folder
                if data_folder:
                    if data_folder == "UPLOADED_FILES":
                        # Handle uploaded files
                        selected_files = st.session_state.get('uploaded_files', [])
                        if selected_files:
                            st.success(f"✅ Using {len(selected_files)} uploaded files")
                    else:
                        # Check for selected files in session state (from file explorer)
                        selected_files_explorer = st.session_state.get('selected_files_explorer', [])
                        selected_files_quick = st.session_state.get('selected_files_quick', [])
                        
                        if selected_files_explorer:
                            selected_files = selected_files_explorer
                            st.success(f"✅ Using {len(selected_files)} files selected via file explorer")
                        elif selected_files_quick:
                            selected_files = selected_files_quick
                            st.success(f"✅ Using {len(selected_files)} files selected via quick access")
                        else:
                            # Fallback: Get all CSV files from the selected folder
                            selected_files = get_csv_files_from_folder(data_folder)
                            
                            if selected_files:
                                st.success(f"✅ Found {len(selected_files)} CSV files in {data_folder}")
                                st.info("💡 **Tip**: Use the file explorer to select specific files for analysis")
                            else:
                                st.warning(f"⚠️ No CSV files found in {data_folder}")
                else:
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
            st.info(f"**Sampling Rate**: Fixed at {sampling_rate} Hz for all files")
    
    with col3:
        with st.expander("WCS Algorithm Parameters", expanded=True):
            # Default threshold is always 0-100 m/s
            th0_min = 0.0
            th0_max = 100.0
            st.info("**WCS Distance Threshold**: 0.0 - 100.0 m/s (all velocities)")
            
            th1_min = st.number_input("Contiguous WCS Min Velocity (m/s)", 0.0, 10.0, 5.0, 0.1, help="Minimum velocity for contiguous WCS analysis. Rolling WCS uses all velocities.")
            th1_max = st.number_input("Contiguous WCS Max Velocity (m/s)", 0.0, 100.0, 100.0, 0.1, help="Maximum velocity for contiguous WCS analysis. Rolling WCS uses all velocities.")
    
    with col4:
        st.markdown("### 🔍 Data Filtering")
        st.markdown("**Filter input data to focus on specific performance zones**")
        
        # Predefined threshold options
        threshold_options = {
            "No Threshold (V > 0)": {"type": "Velocity", "value": 0.0, "description": "All velocities contribute to WCS"},
            "High Speed (V > 5.5 m/s)": {"type": "Velocity", "value": 5.5, "description": "Focus on high-speed periods"},
            "Sprint (V > 7.0 m/s)": {"type": "Velocity", "value": 7.0, "description": "Focus on sprint/peak performance"},
            "Dynamic Movement (|a| > 3.0 m/s²)": {"type": "Acceleration", "value": 3.0, "description": "Focus on high acceleration/deceleration"}
        }
        
        # Threshold selection
        selected_threshold = st.selectbox(
            "Select Threshold Option",
            list(threshold_options.keys()),
            help="Choose from predefined threshold options optimized for different analysis types"
        )
        
        # Display selected threshold info
        threshold_info = threshold_options[selected_threshold]
        threshold_type = threshold_info["type"]
        threshold_value = threshold_info["value"]
        
        # Show threshold effect
        if threshold_type == "Velocity":
            if threshold_value == 0.0:
                st.info(f"**Effect**: {threshold_info['description']} - All velocity data will be used")
            else:
                st.info(f"**Effect**: {threshold_info['description']} - Only velocities > {threshold_value} m/s will contribute to WCS")
        else:
            st.info(f"**Effect**: {threshold_info['description']} - Only accelerations |a| > {threshold_value} m/s² will contribute to WCS")
        
        # Custom threshold override
        st.markdown("---")
        st.markdown("**🔧 Custom Threshold Value**")
        
        use_custom = st.checkbox("Override with custom value", value=False, help="Use a custom threshold instead of the predefined option")
        
        if use_custom:
            if threshold_type == "Velocity":
                custom_value = st.number_input(
                    "Custom Velocity Threshold (m/s)",
                    min_value=0.0,
                    max_value=20.0,
                    value=threshold_value,
                    step=0.1,
                    help="V > threshold: retain data, V ≤ threshold: set to zero"
                )
                threshold_value = custom_value
                st.info(f"**Custom Effect**: Only velocities > {threshold_value} m/s will contribute to WCS")
            else:
                custom_value = st.number_input(
                    "Custom Acceleration Threshold (m/s²)",
                    min_value=0.0,
                    max_value=10.0,
                    value=threshold_value,
                    step=0.1,
                    help="|a| > threshold: retain data, |a| ≤ threshold: set to zero"
                )
                threshold_value = custom_value
                st.info(f"**Custom Effect**: Only accelerations |a| > {threshold_value} m/s² will contribute to WCS")
        
        # Show thresholding explanation
        with st.expander("ℹ️ How Thresholding Works"):
            st.markdown("""
            **Thresholding Process**:
            1. **Original Data**: V[0:N-1], a[0:N-1] (N data points)
            2. **Apply Threshold**: Where condition is TRUE, retain values; where FALSE, set to zero
            3. **WCS Calculation**: Use modified dataset for both rolling and contiguous methods
            
            **Predefined Options**:
            - **No Threshold**: All data contributes (baseline analysis)
            - **High Speed (V > 5.5 m/s)**: Focus on moderate-high intensity periods
            - **Sprint (V > 7.0 m/s)**: Focus on peak performance periods
            - **Dynamic Movement (|a| > 3.0 m/s²)**: Focus on acceleration/deceleration events
            
            **Example**: V > 5.5 m/s threshold
            - Original: [2, 3, 8, 7, 4, 1, 6, 9, 5, 2] m/s
            - Modified: [0, 0, 8, 7, 0, 0, 6, 9, 0, 0] m/s
            - Effect: Only high-velocity periods contribute to WCS
            """)
        
        # Set enable_thresholding to True by default
        enable_thresholding = True
    
    # Analysis Options in a separate section
    st.markdown("---")
    with st.expander("🔧 Analysis Options", expanded=True):
            # Note: WCS Analysis now calculates both rolling and contiguous methods automatically
            st.info("🔄 **Dual WCS Analysis**: Both rolling (accumulated work) and contiguous (best continuous period) methods are calculated automatically")
            
            batch_mode = st.checkbox("Batch Processing Mode", value=True, help="Enable for multiple files - shows combined analysis and exports")
            
            # Smart individual analysis options based on file count
            if len(selected_files) == 1:
                # Single file: Always enable individual analysis
                include_individual_analysis = True
                include_visualizations = True
                enhanced_wcs_viz = True
                st.info("**Single File Mode**: Individual analysis enabled for detailed results.")
            else:
                # Multiple files: User can choose to see individual analysis
                include_individual_analysis = st.checkbox("Include Individual File Analysis", value=False, help="Show detailed analysis for each individual file")
                include_visualizations = include_individual_analysis
                enhanced_wcs_viz = include_individual_analysis
            
            # Export options
            include_export = st.checkbox("Include Export Options", value=True)
            
            # Store analysis options in session state
            st.session_state['include_individual_analysis'] = include_individual_analysis
            st.session_state['include_visualizations'] = include_visualizations
            st.session_state['enhanced_wcs_viz'] = enhanced_wcs_viz
            st.session_state['include_export'] = include_export
    
    # Output settings section
    st.markdown("---")
    output_path = display_output_settings(input_method, data_folder if input_method == "Select from Folder" else None)
    
    # Main content area
    if selected_files:
        # Enhanced summary cards with better visual design
        st.markdown("---")
        st.markdown('<h3 class="section-header">Analysis Overview</h3>', unsafe_allow_html=True)
        
        # Create metric cards with Streamlit's native metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Files to Process", len(selected_files))
        
        with col2:
            st.metric("Primary Epoch", f"{epoch_duration} min")
        
        with col3:
            st.metric("Additional Epochs", len(epoch_durations))
        
        with col4:
            st.metric("Threshold 1 Range", f"{th1_min}-{th1_max} m/s")
        
        # Enhanced analysis execution with better progress tracking
        st.markdown("---")
        
        # Analysis button with enhanced styling
        if st.button("Run WCS Analysis", type="primary", use_container_width=True):
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
                    
                    # Simple file processing feedback
                    st.write(f"Processing file {i+1}/{len(selected_files)}: {filename}")
                    
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
                        
                        # Add thresholding parameters if enabled
                        if enable_thresholding:
                            parameters['enable_thresholding'] = True
                            parameters['threshold_type'] = threshold_type
                            if threshold_type == "Velocity":
                                parameters['velocity_threshold'] = threshold_value
                            elif threshold_type == "Acceleration":
                                parameters['acceleration_threshold'] = threshold_value
                        else:
                            parameters['enable_thresholding'] = False
                        
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
                        
                        # Simple success message
                        st.write(f"✅ Successfully processed {filename}")
                        
                    except Exception as e:
                        # Simple error message
                        st.error(f"❌ Error processing {filename}: {str(e)}")
                        continue
                
                if all_results:
                    # Simple completion message
                    st.success(f"🎉 Analysis Complete! Successfully processed {len(all_results)} file(s)")
                    
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
                    if len(all_results) >= 3:
                        st.markdown(f"""
                        <div class="progress-container" style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-color: #d97706;">
                            <h4 style="margin: 0; color: #92400e;">Advanced Analytics Available!</h4>
                            <p style="margin: 0.5rem 0 0 0; color: #92400e;">With {len(all_results)} files, you now have access to comprehensive cohort analysis!</p>
                            <p style="margin: 0.25rem 0 0 0; color: #92400e; font-size: 0.9rem;"><strong>Features:</strong> Statistical comparisons, performance distributions, outlier detection, and group insights</p>
                            <p style="margin: 0.25rem 0 0 0; color: #92400e; font-size: 0.9rem;"><strong>Access:</strong> Use the "Advanced Analytics" tab below for detailed cohort analysis</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Display results based on mode
                    if batch_mode and len(all_results) > 1:
                        # Create tabs for better organization
                        if len(all_results) >= 3:
                            # Advanced analytics for large batches
                            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Results", "Visualizations", "Dashboards", "Advanced Analytics", "Export"])
                        elif len(all_results) >= 2:
                            # Dashboard analytics for medium batches
                            tab1, tab2, tab3, tab4 = st.tabs(["Results", "Visualizations", "Dashboards", "Export"])
                        else:
                            tab1, tab2, tab3 = st.tabs(["Results", "Visualizations", "Export"])
                        
                        with tab1:
                            st.markdown('<h4 class="subsection-header">Analysis Results</h4>', unsafe_allow_html=True)
                            display_batch_summary(all_results)
                            
                            # Add individual WCS results when enabled
                            if include_individual_analysis:
                                st.markdown("---")
                                st.markdown('<h4 class="subsection-header">Individual WCS Results</h4>', unsafe_allow_html=True)
                                
                                for i, result in enumerate(all_results):
                                    if result and 'metadata' in result and 'results' in result:
                                        st.markdown(f"### 📊 {result['metadata'].get('player_name', f'File {i+1}')}")
                                        display_wcs_results(result['results'], result['metadata'], include_visualizations, enhanced_wcs_viz)
                        
                        with tab2:
                            st.markdown("### Analysis Visualizations")
                            # Combined visualizations for multiple files (now for any batch > 1)
                            if len(all_results) > 1:
                                st.markdown("#### Combined Analysis Visualizations")
                                
                                # Create combined visualizations
                                combined_viz = create_combined_visualizations(all_results)
                                
                                if combined_viz:
                                    # Display each visualization
                                    if 'wcs_distance_distribution' in combined_viz:
                                        st.markdown("#### WCS Distance Distribution by Epoch")
                                        st.plotly_chart(combined_viz['wcs_distance_distribution'], use_container_width=True)
                                    
                                    if 'mean_wcs_distance_trend' in combined_viz:
                                        st.markdown("#### Mean WCS Distance vs Epoch Duration")
                                        st.plotly_chart(combined_viz['mean_wcs_distance_trend'], use_container_width=True)
                                    
                                    if 'player_comparison' in combined_viz:
                                        st.markdown("#### Average WCS Distance by Player")
                                        st.plotly_chart(combined_viz['player_comparison'], use_container_width=True)
                                    
                                    if 'player_epoch_heatmap' in combined_viz:
                                        st.markdown("#### WCS Distance Heatmap by Player and Epoch")
                                        st.plotly_chart(combined_viz['player_epoch_heatmap'], use_container_width=True)
                                    
                                    if 'individual_player_grid' in combined_viz:
                                        st.markdown("#### Individual Player Analysis")
                                        st.info("**Note**: Showing analysis for the first 3 players only to prevent overlapping. Use the heatmap above for all players.")
                                        st.plotly_chart(combined_viz['individual_player_grid'], use_container_width=True)
                            else:
                                st.info("Upload multiple files to see combined visualizations")
                        
                        # Note: Export functionality moved to tab5 for 3+ files
                        
                        # Dashboard Tab (for 2+ files)
                        if len(all_results) >= 2:
                            with tab3:
                                display_dashboard_visualizations(all_results, output_path)
                        
                        # Export Tab (for 2 files)
                        if len(all_results) == 2:
                            with tab4:
                                st.markdown("### Export Options")
                                # Export functionality
                                if include_export:
                                    st.markdown("#### **MATLAB-Compatible Export (Recommended)**")
                                    st.info("**MATLAB Format**: Exports data in the exact format used by your existing MATLAB workflow, including WCS Report, Summary Maximum Values, and Binned Data sheets.")
                                    
                                    # MATLAB format export options
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        if st.button("Excel (MATLAB Format)", help="Export to Excel with multiple sheets matching MATLAB output"):
                                            try:
                                                export_path = export_data_matlab_format(all_results, output_path, "xlsx")
                                                st.success("MATLAB format Excel exported successfully!")
                                                st.info(f"File saved to: `{export_path}`")
                                            except Exception as e:
                                                st.error(f"Export failed: {str(e)}")
                                    
                                    with col2:
                                        if st.button("CSV (MATLAB Format)", help="Export WCS Report to CSV in MATLAB format"):
                                            try:
                                                export_path = export_data_matlab_format(all_results, output_path, "csv")
                                                st.success("MATLAB format CSV exported successfully!")
                                                st.info(f"File saved to: `{export_path}`")
                                            except Exception as e:
                                                st.error(f"Export failed: {str(e)}")
                                    
                                    with col3:
                                        if st.button("JSON (MATLAB Format)", help="Export to JSON with structured data"):
                                            try:
                                                export_path = export_data_matlab_format(all_results, output_path, "json")
                                                st.success("MATLAB format JSON exported successfully!")
                                                st.info(f"File saved to: `{export_path}`")
                                            except Exception as e:
                                                st.error(f"Export failed: {str(e)}")
                                    
                                    st.markdown("---")
                                    st.markdown("#### **Standard Export Options**")
                                    
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        if st.button("Standard CSV Export", help="Export all WCS analysis results to a CSV file"):
                                            export_path = export_wcs_data_to_csv(all_results, output_path)
                                            if export_path:
                                                st.success(f"Standard CSV exported successfully!")
                                                st.info(f"File saved to: `{export_path}`")
                                    
                                    with col2:
                                        if st.button("Download Combined Data", help="Download the combined WCS data as a CSV file"):
                                            combined_df = create_combined_wcs_dataframe(all_results)
                                            if not combined_df.empty:
                                                csv_data = combined_df.to_csv(index=False)
                                                st.download_button(
                                                    label="Download CSV",
                                                    data=csv_data,
                                                    file_name=f"WCS_Analysis_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                                    mime="text/csv"
                                                )
                        
                        # Export Tab (for 1 file)
                        if len(all_results) == 1:
                            with tab3:
                                st.markdown("### Export Options")
                                # Export functionality
                                if include_export:
                                    st.markdown("#### **MATLAB-Compatible Export (Recommended)**")
                                    st.info("**MATLAB Format**: Exports data in the exact format used by your existing MATLAB workflow, including WCS Report, Summary Maximum Values, and Binned Data sheets.")
                                    
                                    # MATLAB format export options
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        if st.button("Excel (MATLAB Format)", help="Export to Excel with multiple sheets matching MATLAB output"):
                                            try:
                                                export_path = export_data_matlab_format(all_results, output_path, "xlsx")
                                                st.success("MATLAB format Excel exported successfully!")
                                                st.info(f"File saved to: `{export_path}`")
                                            except Exception as e:
                                                st.error(f"Export failed: {str(e)}")
                                    
                                    with col2:
                                        if st.button("CSV (MATLAB Format)", help="Export WCS Report to CSV in MATLAB format"):
                                            try:
                                                export_path = export_data_matlab_format(all_results, output_path, "csv")
                                                st.success("MATLAB format CSV exported successfully!")
                                                st.info(f"File saved to: `{export_path}`")
                                            except Exception as e:
                                                st.error(f"Export failed: {str(e)}")
                                    
                                    with col3:
                                        if st.button("JSON (MATLAB Format)", help="Export to JSON with structured data"):
                                            try:
                                                export_path = export_data_matlab_format(all_results, output_path, "json")
                                                st.success("MATLAB format JSON exported successfully!")
                                                st.info(f"File saved to: `{export_path}`")
                                            except Exception as e:
                                                st.error(f"Export failed: {str(e)}")
                                    
                                    st.markdown("---")
                                    st.markdown("#### **Standard Export Options**")
                                    
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        if st.button("Standard CSV Export", help="Export all WCS analysis results to a CSV file"):
                                            export_path = export_wcs_data_to_csv(all_results, output_path)
                                            if export_path:
                                                st.success(f"Standard CSV exported successfully!")
                                                st.info(f"File saved to: `{export_path}`")
                                    
                                    with col2:
                                        if st.button("Download Combined Data", help="Download the combined WCS data as a CSV file"):
                                            combined_df = create_combined_wcs_dataframe(all_results)
                                            if not combined_df.empty:
                                                csv_data = combined_df.to_csv(index=False)
                                                st.download_button(
                                                    label="Download CSV",
                                                    data=csv_data,
                                                    file_name=f"WCS_Analysis_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                                    mime="text/csv"
                                                )
                        
                        # Advanced Analytics Tab (only for 3+ files)
                        if len(all_results) >= 3:
                            with tab4:
                                display_advanced_analytics(all_results, output_path)
                        
                        # Export Tab (for 3+ files)
                        if len(all_results) >= 3:
                            with tab5:
                                st.markdown("### Export Options")
                                # Export functionality
                                if include_export:
                                    st.markdown("#### **MATLAB-Compatible Export (Recommended)**")
                                    st.info("**MATLAB Format**: Exports data in the exact format used by your existing MATLAB workflow, including WCS Report, Summary Maximum Values, and Binned Data sheets.")
                                    
                                    # MATLAB format export options
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        if st.button("Excel (MATLAB Format)", help="Export to Excel with multiple sheets matching MATLAB output"):
                                            try:
                                                export_path = export_data_matlab_format(all_results, output_path, "xlsx")
                                                st.success("MATLAB format Excel exported successfully!")
                                                st.info(f"File saved to: `{export_path}`")
                                            except Exception as e:
                                                st.error(f"Export failed: {str(e)}")
                                    
                                    with col2:
                                        if st.button("CSV (MATLAB Format)", help="Export WCS Report to CSV in MATLAB format"):
                                            try:
                                                export_path = export_data_matlab_format(all_results, output_path, "csv")
                                                st.success("MATLAB format CSV exported successfully!")
                                                st.info(f"File saved to: `{export_path}`")
                                            except Exception as e:
                                                st.error(f"Export failed: {str(e)}")
                                    
                                    with col3:
                                        if st.button("JSON (MATLAB Format)", help="Export to JSON with structured data"):
                                            try:
                                                export_path = export_data_matlab_format(all_results, output_path, "json")
                                                st.success("MATLAB format JSON exported successfully!")
                                                st.info(f"File saved to: `{export_path}`")
                                            except Exception as e:
                                                st.error(f"Export failed: {str(e)}")
                                    
                                    st.markdown("---")
                                    st.markdown("#### **Standard Export Options**")
                                    
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        if st.button("Standard CSV Export", help="Export all WCS analysis results to a CSV file"):
                                            export_path = export_wcs_data_to_csv(all_results, output_path)
                                            if export_path:
                                                st.success(f"Standard CSV exported successfully!")
                                                st.info(f"File saved to: `{export_path}`")
                                    
                                    with col2:
                                        if st.button("Download Combined Data", help="Download the combined WCS data as a CSV file"):
                                            combined_df = create_combined_wcs_dataframe(all_results)
                                            if not combined_df.empty:
                                                csv_data = combined_df.to_csv(index=False)
                                                st.download_button(
                                                    label="Download CSV",
                                                    data=csv_data,
                                                    file_name=f"WCS_Analysis_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                                    mime="text/csv"
                                                )
                    else:
                        # Display individual results
                        for result in all_results:
                            display_wcs_results(result['results'], result['metadata'], include_visualizations, enhanced_wcs_viz)
                    
                    # Add individual analysis layer when enabled
                    if include_individual_analysis:
                        st.markdown("---")
                        st.markdown('<h3 class="section-header">Individual File Analysis</h3>', unsafe_allow_html=True)
                        
                        for i, result in enumerate(all_results):
                            st.markdown(f"### 📊 {result['metadata'].get('player_name', f'File {i+1}')}")
                            display_wcs_results(result['results'], result['metadata'], include_visualizations, enhanced_wcs_viz)
                else:
                    st.error("❌ No files were successfully processed")
    
    # Display results if analysis was previously completed
    elif st.session_state.get('analysis_complete', False):
        all_results = st.session_state.get('all_results', [])
        if all_results:
            st.success("Previous analysis results found")
            
            # Retrieve analysis options from session state
            include_individual_analysis = st.session_state.get('include_individual_analysis', False)
            include_visualizations = st.session_state.get('include_visualizations', True)
            enhanced_wcs_viz = st.session_state.get('enhanced_wcs_viz', True)
            include_export = st.session_state.get('include_export', True)
            
            # Display results based on mode
            if batch_mode and len(all_results) > 1:
                # Create tabs for better organization
                if len(all_results) >= 3:
                    # Advanced analytics for large batches
                    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Results", "Visualizations", "Dashboards", "Advanced Analytics", "Export"])
                elif len(all_results) >= 2:
                    # Dashboard analytics for medium batches
                    tab1, tab2, tab3, tab4 = st.tabs(["Results", "Visualizations", "Dashboards", "Export"])
                else:
                    tab1, tab2, tab3 = st.tabs(["Results", "Visualizations", "Export"])
                
                with tab1:
                    st.markdown('<h4 class="subsection-header">Analysis Results</h4>', unsafe_allow_html=True)
                    display_batch_summary(all_results)
                    
                    # Add individual WCS results when enabled
                    if include_individual_analysis:
                        st.markdown("---")
                        st.markdown('<h4 class="subsection-header">Individual WCS Results</h4>', unsafe_allow_html=True)
                        
                        for i, result in enumerate(all_results):
                            if result and 'metadata' in result and 'results' in result:
                                st.markdown(f"### 📊 {result['metadata'].get('player_name', f'File {i+1}')}")
                                display_wcs_results(result['results'], result['metadata'], include_visualizations, enhanced_wcs_viz)
                
                with tab2:
                    st.markdown("### Analysis Visualizations")
                    # Combined visualizations for multiple files
                    if len(all_results) > 1:
                        st.markdown("#### Combined Analysis Visualizations")
                        
                        # Create combined visualizations
                        combined_viz = create_combined_visualizations(all_results)
                        
                        if combined_viz:
                            # Display each visualization
                            if 'wcs_distance_distribution' in combined_viz:
                                st.markdown("#### WCS Distance Distribution by Epoch")
                                st.plotly_chart(combined_viz['wcs_distance_distribution'], use_container_width=True)
                            
                            if 'mean_wcs_distance_trend' in combined_viz:
                                st.markdown("#### Mean WCS Distance vs Epoch Duration")
                                st.plotly_chart(combined_viz['mean_wcs_distance_trend'], use_container_width=True)
                            
                            if 'player_comparison' in combined_viz:
                                st.markdown("#### Average WCS Distance by Player")
                                st.plotly_chart(combined_viz['player_comparison'], use_container_width=True)
                            
                            if 'player_epoch_heatmap' in combined_viz:
                                st.markdown("#### WCS Distance Heatmap by Player and Epoch")
                                st.plotly_chart(combined_viz['player_epoch_heatmap'], use_container_width=True)
                            
                            if 'individual_player_grid' in combined_viz:
                                st.markdown("#### Individual Player Analysis")
                                st.info("**Note**: Showing analysis for the first 3 players only to prevent overlapping. Use the heatmap above for all players.")
                                st.plotly_chart(combined_viz['individual_player_grid'], use_container_width=True)
                    else:
                        st.info("Upload multiple files to see combined visualizations")
                
                # Note: Export functionality moved to tab5 for 3+ files
                
                # Dashboard Tab (for 2+ files)
                if len(all_results) >= 2:
                    with tab3:
                        display_dashboard_visualizations(all_results, output_path)
                
                # Advanced Analytics Tab (only for 3+ files)
                if len(all_results) >= 3:
                    with tab4:
                        display_advanced_analytics(all_results, output_path)
                
                # Export Tab (for 3+ files)
                if len(all_results) >= 3:
                    with tab5:
                        st.markdown("### Export Options")
                        # Export functionality
                        if include_export:
                            st.markdown("#### **MATLAB-Compatible Export (Recommended)**")
                            st.info("**MATLAB Format**: Exports data in the exact format used by your existing MATLAB workflow, including WCS Report, Summary Maximum Values, and Binned Data sheets.")
                            
                            # MATLAB format export options
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                if st.button("Excel (MATLAB Format)", help="Export to Excel with multiple sheets matching MATLAB output"):
                                    try:
                                        export_path = export_data_matlab_format(all_results, output_path, "xlsx")
                                        st.success(f"MATLAB format Excel exported successfully!")
                                        st.info(f"File saved to: `{export_path}`")
                                    except Exception as e:
                                        st.error(f"Export failed: {str(e)}")
                            
                            with col2:
                                if st.button("CSV (MATLAB Format)", help="Export WCS Report to CSV in MATLAB format"):
                                    try:
                                        export_path = export_data_matlab_format(all_results, output_path, "csv")
                                        st.success(f"MATLAB format CSV exported successfully!")
                                        st.info(f"File saved to: `{export_path}`")
                                    except Exception as e:
                                        st.error(f"Export failed: {str(e)}")
                            
                            with col3:
                                if st.button("JSON (MATLAB Format)", help="Export to JSON with structured data"):
                                    try:
                                        export_path = export_data_matlab_format(all_results, output_path, "json")
                                        st.success(f"MATLAB format JSON exported successfully!")
                                        st.info(f"File saved to: `{export_path}`")
                                    except Exception as e:
                                        st.error(f"Export failed: {str(e)}")
                            
                            st.markdown("---")
                            st.markdown("#### **Standard Export Options**")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.button("Standard CSV Export", help="Export all WCS analysis results to a CSV file"):
                                    export_path = export_wcs_data_to_csv(all_results, output_path)
                                    if export_path:
                                        st.success(f"Standard CSV exported successfully!")
                                        st.info(f"File saved to: `{export_path}`")
                            
                            with col2:
                                if st.button("Download Combined Data", help="Download the combined WCS data as a CSV file"):
                                    combined_df = create_combined_wcs_dataframe(all_results)
                                    if not combined_df.empty:
                                        csv_data = combined_df.to_csv(index=False)
                                        st.download_button(
                                            label="Download CSV",
                                            data=csv_data,
                                            file_name=f"WCS_Analysis_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                            mime="text/csv"
                                        )
            else:
                # Display individual results
                for result in all_results:
                    display_wcs_results(result['results'], result['metadata'], include_visualizations, enhanced_wcs_viz)
                
                # Add individual analysis layer when enabled
                if include_individual_analysis:
                    st.markdown("---")
                    st.markdown('<h3 class="section-header">Individual File Analysis</h3>', unsafe_allow_html=True)
                    
                    for i, result in enumerate(all_results):
                        st.markdown(f"### 📊 {result['metadata'].get('player_name', f'File {i+1}')}")
                        display_wcs_results(result['results'], result['metadata'], include_visualizations, enhanced_wcs_viz)
    
    # Instructions when no files are selected
    else:
        st.markdown("---")
        st.markdown('<h4 class="subsection-header">Getting Started</h4>', unsafe_allow_html=True)
        
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


def display_dashboard_visualizations(all_results: list, output_path: str):
    """Display advanced dashboard visualizations for batch processing (5+ files)"""
    
    st.markdown("### Advanced Dashboard Visualizations")
    st.info("**Professional Dashboards**: Comprehensive multi-panel visualizations providing insights across all players and epochs in a single view.")
    
    # Check if we have enough data for dashboard analysis
    if len(all_results) < 5:
        st.warning("Dashboard visualizations require at least 5 files for meaningful analysis")
        return
    
    # Dashboard selection
    st.markdown("#### Choose Dashboard Type")
    
    dashboard_type = st.selectbox(
        "Select Dashboard:",
        ["Comprehensive Overview", "Individual Players", "Performance Insights"],
        help="Choose the type of dashboard visualization to display"
    )
    
    # Smart recommendation
    if len(all_results) >= 3:
        st.success("**Recommended**: Comprehensive Overview (best for large datasets)")
    elif len(all_results) >= 7:
        st.info("**Recommended**: Individual Players (good for medium datasets)")
    else:
        st.info("**Recommended**: Performance Insights (ideal for smaller datasets)")
    
    # Create and display selected dashboard
    with st.spinner(f"Creating {dashboard_type} dashboard..."):
        try:
            if dashboard_type == "Comprehensive Overview":
                fig = create_comprehensive_dashboard(all_results, "WCS Analysis - Comprehensive Dashboard")
            elif dashboard_type == "Individual Players":
                max_players = min(5, len(all_results))
                fig = create_individual_player_dashboard(all_results, max_players)
            else:  # Performance Insights
                fig = create_performance_insights_dashboard(all_results)
            
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                
                # Dashboard export options
                st.markdown("---")
                st.markdown("#### Export Dashboard")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Export as HTML", help="Export dashboard as interactive HTML file"):
                        try:
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            filename = f"dashboard_{dashboard_type.lower().replace(' ', '_')}_{timestamp}.html"
                            filepath = os.path.join(output_path, filename)
                            fig.write_html(filepath)
                            st.success("Dashboard exported successfully!")
                            st.info(f"File saved to: `{filepath}`")
                        except Exception as e:
                            st.error(f"Export failed: {str(e)}")
                
                with col2:
                    if st.button("Download Dashboard", help="Download dashboard as HTML file"):
                        try:
                            html_content = fig.to_html(include_plotlyjs=True, full_html=True)
                            st.download_button(
                                label="Download HTML",
                                data=html_content,
                                file_name=f"dashboard_{dashboard_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                                mime="text/html"
                            )
                        except Exception as e:
                            st.error(f"Download failed: {str(e)}")
                
                # Dashboard insights
                st.markdown("---")
                st.markdown("#### Dashboard Insights")
                
                if dashboard_type == "Comprehensive Overview":
                    st.markdown("""
                    **What This Dashboard Shows:**
                    - **Top Left**: WCS Distance vs Mean Velocity correlation by epoch
                    - **Top Right**: Correlation matrix of all key metrics
                    - **Bottom Left**: Epoch efficiency (distance per second)
                    - **Bottom Right**: WCS distance distribution patterns
                    """)
                elif dashboard_type == "Individual Players":
                    st.markdown("""
                    **What This Dashboard Shows:**
                    - **Left Panels**: Simulated velocity profiles for top performers
                    - **Right Panels**: Epoch comparison charts for each player
                    - **Performance Ranking**: Based on average WCS distance
                    """)
                else:  # Performance Insights
                    st.markdown("""
                    **What This Dashboard Shows:**
                    - **Top Left**: Player performance ranking by 1-min WCS
                    - **Top Right**: Velocity vs WCS distance correlation
                    - **Bottom Left**: Performance consistency analysis
                    - **Bottom Right**: Epoch duration optimization insights
                    """)
        except Exception as e:
            st.error(f"Error creating dashboard: {str(e)}")
            st.info("Try selecting a different dashboard type or check your data")


def display_advanced_analytics(all_results: list, output_path: str):
    """Display advanced analytics for large batch processing (10+ files)"""
    
    st.markdown("### Advanced Analytics")
    st.info("**Advanced Analytics**: Comprehensive group/cohort analysis for large datasets with statistical comparisons, performance distributions, and insights.")
    
    # Check if we have enough data for advanced analytics
    if len(all_results) < 3:
        st.warning("Advanced analytics require at least 3 files for meaningful cohort analysis")
        return
    
    # Perform cohort analysis
    with st.spinner("Performing cohort analysis..."):
        try:
            cohort_analysis = analyze_cohort_performance(all_results)
            
            if cohort_analysis and 'error' not in cohort_analysis:
                # Display cohort performance summary
                st.markdown("#### Cohort Performance Summary")
                
                # Get statistics from the analysis
                stats = cohort_analysis.get('statistics', {})
                overall_stats = stats.get('overall', {})
                
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Total Players",
                        overall_stats.get('total_players', len(all_results)),
                        help="Number of players in the cohort"
                    )
                
                with col2:
                    st.metric(
                        "Avg WCS Distance",
                        f"{overall_stats.get('mean_distance', 0):.2f} m",
                        help="Average WCS distance across all players"
                    )
                
                with col3:
                    st.metric(
                        "Std Dev WCS",
                        f"{overall_stats.get('std_distance', 0):.2f} m",
                        help="Standard deviation of WCS distances"
                    )
                
                with col4:
                    wcs_range = overall_stats.get('max_distance', 0) - overall_stats.get('min_distance', 0)
                    st.metric(
                        "Performance Range",
                        f"{wcs_range:.2f} m",
                        help="Range between min and max WCS distances"
                    )
                
                # Performance distribution
                st.markdown("#### Performance Distribution")
                
                visualizations = cohort_analysis.get('visualizations', {})
                if 'distance_distribution' in visualizations:
                    st.plotly_chart(visualizations['distance_distribution'], use_container_width=True)
                elif 'performance_histogram' in visualizations:
                    st.plotly_chart(visualizations['performance_histogram'], use_container_width=True)
                
                # Player ranking
                st.markdown("#### Player Performance Ranking")
                
                rankings = cohort_analysis.get('rankings', {})
                if 'player_rankings' in rankings:
                    ranking_df = rankings['player_rankings']
                    st.dataframe(ranking_df, use_container_width=True)
                
                # Statistical analysis
                st.markdown("#### Statistical Analysis")
                
                if 'correlation_heatmap' in visualizations:
                    st.plotly_chart(visualizations['correlation_heatmap'], use_container_width=True)
                
                # Performance insights
                st.markdown("#### Performance Insights")
                
                outliers = cohort_analysis.get('outliers', {})
                insights = outliers.get('insights', [])
                if insights:
                    for insight in insights:
                        st.info(insight)
                else:
                    st.info("No significant outliers or trends detected in this cohort.")
                
                # Additional visualizations
                if 'epoch_comparison' in visualizations:
                    st.markdown("#### Performance by Epoch Duration")
                    st.plotly_chart(visualizations['epoch_comparison'], use_container_width=True)
                
                if 'player_comparison' in visualizations:
                    st.markdown("#### Player Performance Comparison")
                    st.plotly_chart(visualizations['player_comparison'], use_container_width=True)
                
                # Export options
                st.markdown("---")
                st.markdown("#### Export Cohort Data")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Export Cohort Data", help="Export cohort analysis data to CSV"):
                        try:
                            export_path = export_cohort_analysis(cohort_analysis, output_path)
                            if 'error' not in export_path:
                                st.success("Cohort data exported successfully!")
                                for file_type, file_path in export_path.items():
                                    st.info(f"📁 {file_type}: {file_path}")
                            else:
                                st.error(f"❌ Export failed: {export_path['error']}")
                        except Exception as e:
                            st.error(f"Export failed: {str(e)}")
                
                with col2:
                    if st.button("Download Cohort Report", help="Download comprehensive cohort analysis report"):
                        try:
                            report_content = create_cohort_report(cohort_analysis)
                            st.download_button(
                                label="Download Report",
                                data=report_content,
                                file_name=f"cohort_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain"
                            )
                        except Exception as e:
                            st.error(f"Report generation failed: {str(e)}")
                
            else:
                error_msg = cohort_analysis.get('error', 'Unknown error in cohort analysis') if cohort_analysis else 'No cohort analysis data available'
                st.error(f"❌ Cohort analysis failed: {error_msg}")
                
        except Exception as e:
            st.error(f"❌ Error performing cohort analysis: {str(e)}")
            st.exception(e)


def display_wcs_results(results: Dict[str, Any], metadata: Dict[str, Any], include_visualizations: bool = True, enhanced_wcs_viz: bool = True):
    """Display WCS analysis results for a single file"""
    
    # Summary statistics
    st.markdown("### Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", metadata.get('total_records', 0))
    
    with col2:
        duration = metadata.get('duration_minutes', 0)
        st.metric("Duration", f"{duration:.1f} min")
    
    with col3:
        if 'wcs_rolling' in results and results['wcs_rolling']:
            max_rolling = max([epoch['distance'] for epoch in results['wcs_rolling']])
            st.metric("Max Rolling WCS", f"{max_rolling:.2f} m")
        else:
            st.metric("Max Rolling WCS", "N/A")
    
    with col4:
        if 'wcs_contiguous' in results and results['wcs_contiguous']:
            max_contiguous = max([epoch['distance'] for epoch in results['wcs_contiguous']])
            st.metric("Max Contiguous WCS", f"{max_contiguous:.2f} m")
        else:
            st.metric("Max Contiguous WCS", "N/A")
    
    # Thresholding Information
    if 'thresholding_info' in results and results['thresholding_info']['enabled']:
        st.markdown("### 🔍 Thresholding Information")
        
        threshold_info = results['thresholding_info']
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Threshold Type", threshold_info['type'])
        
        with col2:
            threshold_value = threshold_info['threshold_value']
            if threshold_info['type'] == "Velocity":
                st.metric("Velocity Threshold", f"{threshold_value} m/s")
            else:
                st.metric("Acceleration Threshold", f"{threshold_value} m/s²")
        
        with col3:
            data_reduction = threshold_info['data_reduction_percent']
            st.metric("Data Reduction", f"{data_reduction:.1f}%")
        
        # Thresholding explanation
        if threshold_info['type'] == "Velocity" and threshold_value == 0.0:
            st.info(f"📊 **No Thresholding Applied**: All velocity data contributed to WCS calculation (baseline analysis).")
        elif threshold_info['type'] == "Velocity":
            st.info(f"📊 **Velocity Thresholding Applied**: Only velocities > {threshold_value} m/s contributed to WCS calculation. {data_reduction:.1f}% of data was filtered out.")
        else:
            st.info(f"📊 **Acceleration Thresholding Applied**: Only accelerations |a| > {threshold_value} m/s² contributed to WCS calculation. {data_reduction:.1f}% of data was filtered out.")
    
    # WCS Analysis Results
    st.markdown('<h4 class="subsection-header">WCS Analysis Results</h4>', unsafe_allow_html=True)
    
    # Rolling WCS Results
    if 'wcs_rolling' in results and results['wcs_rolling']:
        st.markdown("#### Rolling WCS Analysis (Accumulated Work)")
        
        rolling_df = pd.DataFrame(results['wcs_rolling'])
        rolling_df['epoch_duration'] = rolling_df['epoch_duration'].round(1)
        rolling_df['distance'] = rolling_df['distance'].round(2)
        rolling_df['mean_velocity'] = rolling_df['mean_velocity'].round(2)
        
        st.dataframe(rolling_df[['epoch_duration', 'distance', 'mean_velocity', 'start_time', 'end_time']], 
                    use_container_width=True, hide_index=True)
    
    # Contiguous WCS Results
    if 'wcs_contiguous' in results and results['wcs_contiguous']:
        st.markdown("#### Contiguous WCS Analysis (Best Continuous Period)")
        
        contiguous_df = pd.DataFrame(results['wcs_contiguous'])
        contiguous_df['epoch_duration'] = contiguous_df['epoch_duration'].round(1)
        contiguous_df['distance'] = contiguous_df['distance'].round(2)
        contiguous_df['mean_velocity'] = contiguous_df['mean_velocity'].round(2)
        
        st.dataframe(contiguous_df[['epoch_duration', 'distance', 'mean_velocity', 'start_time', 'end_time']], 
                    use_container_width=True, hide_index=True)
    
    # Visualizations
    if include_visualizations:
        st.markdown("### Dual WCS Velocity Analysis (Rolling: Accumulated Work | Contiguous: Best Continuous Period)")
        
        # Create dual WCS velocity visualization
        if 'velocity_data' in results and results['velocity_data'] is not None:
            dual_viz = create_dual_wcs_velocity_visualization(
                results['velocity_data'],
                results.get('wcs_rolling', []),
                results.get('wcs_contiguous', []),
                metadata.get('player_name', 'Unknown')
            )
            if dual_viz:
                st.plotly_chart(dual_viz, use_container_width=True)
        
        # Enhanced WCS visualizations
        if enhanced_wcs_viz:
            st.markdown("### Enhanced WCS Analysis Visualizations")
            
            # Create enhanced WCS visualization
            if 'velocity_data' in results and results['velocity_data'] is not None:
                enhanced_viz = create_enhanced_wcs_visualization(
                    results['velocity_data'],
                    results.get('wcs_rolling', []),
                    results.get('wcs_contiguous', []),
                    metadata.get('player_name', 'Unknown')
                )
                if enhanced_viz:
                    st.plotly_chart(enhanced_viz, use_container_width=True)
            
            # WCS period details
            if 'wcs_rolling' in results and results['wcs_rolling']:
                period_viz = create_wcs_period_details(
                    results['velocity_data'],
                    results['wcs_rolling'],
                    metadata.get('player_name', 'Unknown'),
                    "Rolling WCS Periods"
                )
                if period_viz:
                    st.plotly_chart(period_viz, use_container_width=True)


def display_batch_summary(all_results: list):
    """Display a summary of batch processing results"""
    
    st.markdown('<h4 class="subsection-header">Batch Processing Summary</h4>', unsafe_allow_html=True)
    
    # Calculate summary statistics
    total_files = len(all_results)
    successful_files = len([r for r in all_results if r and 'metadata' in r and 'results' in r])
    failed_files = total_files - successful_files
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Files", total_files)
    
    with col2:
        st.metric("Successful", successful_files)
    
    with col3:
        st.metric("Failed", failed_files)
    
    with col4:
        success_rate = (successful_files / total_files * 100) if total_files > 0 else 0
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    # Display file details
    st.markdown("#### File Details")
    
    file_details = []
    for i, result in enumerate(all_results, 1):
        if result and 'metadata' in result and 'results' in result:
            metadata = result['metadata']
            file_details.append({
                'File': i,
                'Player': metadata.get('player_name', 'Unknown'),
                'Type': metadata.get('file_type', 'Unknown'),
                'Records': metadata.get('total_records', 0),
                'Duration (min)': f"{metadata.get('duration_minutes', 0):.1f}",
                'Status': 'Success'
            })
        else:
            file_details.append({
                'File': i,
                'Player': 'Unknown',
                'Type': 'Unknown',
                'Records': 0,
                'Duration (min)': '0.0',
                'Status': 'Failed'
            })
    
    if file_details:
        df = pd.DataFrame(file_details)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Display any errors
    if failed_files > 0:
        st.markdown("#### Processing Errors")
        for i, result in enumerate(all_results):
            if result and 'error' in result:
                st.error(f"File {i+1}: {result['error']}")
    
    # Add WCS summary statistics
    if successful_files > 0:
        st.markdown("#### WCS Analysis Summary")
        
        # Calculate WCS statistics across all files
        total_wcs_distance = 0
        total_wcs_periods = 0
        
        for result in all_results:
            if result and 'results' in result:
                wcs_results = result['results']
                if 'wcs_rolling' in wcs_results:
                    for period in wcs_results['wcs_rolling']:
                        if isinstance(period, list) and len(period) >= 8:
                            # Distance is at index 0 for default threshold
                            total_wcs_distance += period[0]
                            total_wcs_periods += 1
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total WCS Distance", f"{total_wcs_distance:.1f} m")
        
        with col2:
            st.metric("Total WCS Periods", total_wcs_periods)
        
        with col3:
            avg_distance = (total_wcs_distance / total_wcs_periods) if total_wcs_periods > 0 else 0
            st.metric("Average WCS Distance", f"{avg_distance:.1f} m")


if __name__ == "__main__":
    main() 