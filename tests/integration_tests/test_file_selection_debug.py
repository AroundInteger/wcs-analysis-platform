#!/usr/bin/env python3
"""
Diagnostic test to debug file selection and processing issues
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Test imports
try:
    from src.file_ingestion import read_csv_with_metadata, validate_velocity_data
    from src.wcs_analysis import perform_wcs_analysis
    from src.file_browser import get_csv_files_from_folder
    from src.data_export import export_data_matlab_format
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    st.error(f"Import error: {e}")
    st.stop()

def main():
    st.title("File Selection & Processing Debug Test")
    st.write("Debugging file selection and processing issues")
    
    # Check session state
    st.write("### Session State Debug")
    st.write("**Current session state keys:**")
    for key in st.session_state.keys():
        value = st.session_state[key]
        if isinstance(value, list):
            st.write(f"  - {key}: {len(value)} items")
            if len(value) > 0:
                st.write(f"    First item: {value[0]}")
        else:
            st.write(f"  - {key}: {value}")
    
    # Check specific session state variables
    st.write("### File Selection Debug")
    
    selected_files_explorer = st.session_state.get('selected_files_explorer', [])
    selected_files_quick = st.session_state.get('selected_files_quick', [])
    uploaded_files = st.session_state.get('uploaded_files', [])
    
    st.write(f"**selected_files_explorer**: {len(selected_files_explorer)} files")
    if selected_files_explorer:
        for i, file in enumerate(selected_files_explorer[:3]):
            st.write(f"  {i+1}. {file}")
    
    st.write(f"**selected_files_quick**: {len(selected_files_quick)} files")
    if selected_files_quick:
        for i, file in enumerate(selected_files_quick[:3]):
            st.write(f"  {i+1}. {file}")
    
    st.write(f"**uploaded_files**: {len(uploaded_files)} files")
    if uploaded_files:
        for i, file in enumerate(uploaded_files[:3]):
            st.write(f"  {i+1}. {file.name if hasattr(file, 'name') else str(file)}")
    
    # Test file processing
    st.write("### File Processing Test")
    
    # Get test files
    test_data_path = "data/test_data"
    if os.path.exists(test_data_path):
        csv_files = get_csv_files_from_folder(test_data_path)
        st.write(f"Found {len(csv_files)} CSV files in test data")
        
        if csv_files:
            # Test processing first file
            test_file = csv_files[0]
            st.write(f"Testing file: {test_file}")
            
            try:
                # Read and validate data
                df, metadata, file_type_info = read_csv_with_metadata(test_file)
                st.write(f"✅ File read successfully")
                st.write(f"  DataFrame shape: {df.shape}")
                st.write(f"  Metadata keys: {list(metadata.keys())}")
                
                # Validate velocity data
                if validate_velocity_data(df):
                    st.write(f"✅ Velocity data validated")
                    
                    # Prepare parameters
                    parameters = {
                        'sampling_rate': 10,
                        'epoch_duration': 5,
                        'epoch_durations': [5, 10, 15],
                        'th0_min': 0,
                        'th0_max': 20,
                        'th1_min': 5,
                        'th1_max': 20,
                    }
                    
                    # Perform WCS analysis
                    results = perform_wcs_analysis(df, metadata, file_type_info, parameters)
                    st.write(f"✅ WCS analysis completed")
                    
                    # Test export
                    st.write("### Export Test")
                    all_results = [{
                        'file_path': test_file,
                        'metadata': metadata,
                        'results': results,
                        'analysis_successful': True
                    }]
                    
                    try:
                        export_path = export_data_matlab_format(all_results, "OUTPUT", "xlsx")
                        st.success(f"✅ Export successful: {export_path}")
                    except Exception as e:
                        st.error(f"❌ Export failed: {str(e)}")
                        st.write(f"Error type: {type(e)}")
                        
                else:
                    st.write(f"❌ Velocity data validation failed")
                    
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
                st.write(f"Error type: {type(e)}")
    
    # Manual file selection test
    st.write("### Manual File Selection Test")
    
    uploaded_files_test = st.file_uploader(
        "Upload test files:",
        type=['csv'],
        accept_multiple_files=True,
        key="debug_uploader"
    )
    
    if uploaded_files_test:
        st.write(f"Uploaded {len(uploaded_files_test)} files")
        
        # Process uploaded files
        all_results = []
        for i, file in enumerate(uploaded_files_test):
            st.write(f"Processing {i+1}/{len(uploaded_files_test)}: {file.name}")
            
            try:
                # Read and validate data
                df, metadata, file_type_info = read_csv_with_metadata(file)
                st.write(f"  ✅ File read successfully")
                
                # Validate velocity data
                if validate_velocity_data(df):
                    st.write(f"  ✅ Velocity data validated")
                    
                    # Prepare parameters
                    parameters = {
                        'sampling_rate': 10,
                        'epoch_duration': 5,
                        'epoch_durations': [5, 10, 15],
                        'th0_min': 0,
                        'th0_max': 20,
                        'th1_min': 5,
                        'th1_max': 20,
                    }
                    
                    # Perform WCS analysis
                    results = perform_wcs_analysis(df, metadata, file_type_info, parameters)
                    st.write(f"  ✅ WCS analysis completed")
                    
                    # Store results
                    all_results.append({
                        'file_path': file,
                        'metadata': metadata,
                        'results': results,
                        'analysis_successful': True
                    })
                    
                else:
                    st.write(f"  ❌ Velocity data validation failed")
                    
            except Exception as e:
                st.error(f"  ❌ Error processing {file.name}: {str(e)}")
                continue
        
        if all_results:
            st.success(f"✅ Successfully processed {len(all_results)} files")
            
            # Test export
            try:
                export_path = export_data_matlab_format(all_results, "OUTPUT", "xlsx")
                st.success(f"✅ Export successful: {export_path}")
            except Exception as e:
                st.error(f"❌ Export failed: {str(e)}")
                st.write(f"Error type: {type(e)}")
                st.write(f"Error details: {e}")
        else:
            st.warning("⚠️ No files were successfully processed")

if __name__ == "__main__":
    main() 