#!/usr/bin/env python3
"""
Diagnostic test to compare file handling between drag-and-drop and file explorer modes
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
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    st.error(f"Import error: {e}")
    st.stop()

def main():
    st.title("File Handling Comparison Test")
    st.write("Testing file handling differences between drag-and-drop and file explorer modes")
    
    # Test with sample data
    test_data_path = "data/test_data"
    
    if not os.path.exists(test_data_path):
        st.error(f"Test data path not found: {test_data_path}")
        return
    
    # Get test files using the file browser method
    st.write("### Testing File Browser Method")
    st.write(f"Looking for CSV files in: {test_data_path}")
    
    try:
        csv_files = get_csv_files_from_folder(test_data_path)
        st.write(f"✅ File browser found {len(csv_files)} CSV files:")
        for file in csv_files:
            st.write(f"  - {file}")
    except Exception as e:
        st.error(f"❌ File browser method failed: {str(e)}")
        return
    
    if not csv_files:
        st.error("No CSV files found using file browser method")
        return
    
    # Test file processing for each method
    st.write("---")
    st.write("### Testing File Processing")
    
    # Method 1: File browser method (simulating what happens in explorer)
    st.write("**Method 1: File Browser (Explorer Mode)**")
    all_results_explorer = []
    
    for i, file_path in enumerate(csv_files[:2]):  # Test with first 2 files
        filename = os.path.basename(file_path)
        st.write(f"Processing {i+1}/2: {filename}")
        st.write(f"  File path: {file_path}")
        st.write(f"  Path type: {type(file_path)}")
        st.write(f"  Path exists: {os.path.exists(file_path)}")
        
        try:
            # Read and validate data
            df, metadata, file_type_info = read_csv_with_metadata(file_path)
            st.write(f"  ✅ File read successfully")
            st.write(f"  DataFrame shape: {df.shape}")
            st.write(f"  Metadata keys: {list(metadata.keys())}")
            
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
                all_results_explorer.append({
                    'file_path': file_path,
                    'metadata': metadata,
                    'results': results
                })
                
            else:
                st.write(f"  ❌ Velocity data validation failed")
                
        except Exception as e:
            st.error(f"  ❌ Error processing {filename}: {str(e)}")
            continue
    
    st.write(f"**Explorer method results: {len(all_results_explorer)} files processed**")
    
    # Method 2: Simulate drag-and-drop (file objects)
    st.write("---")
    st.write("**Method 2: Drag-and-drop Simulation**")
    all_results_dragdrop = []
    
    for i, file_path in enumerate(csv_files[:2]):  # Test with first 2 files
        filename = os.path.basename(file_path)
        st.write(f"Processing {i+1}/2: {filename}")
        
        try:
            # Simulate file object (like drag-and-drop creates)
            class MockFileObject:
                def __init__(self, file_path):
                    self.name = os.path.basename(file_path)
                    self.file_path = file_path
                
                def __str__(self):
                    return self.file_path
            
            mock_file = MockFileObject(file_path)
            st.write(f"  Mock file object: {mock_file}")
            st.write(f"  Mock file name: {mock_file.name}")
            
            # Read and validate data
            df, metadata, file_type_info = read_csv_with_metadata(file_path)
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
                all_results_dragdrop.append({
                    'file_path': mock_file,
                    'metadata': metadata,
                    'results': results
                })
                
            else:
                st.write(f"  ❌ Velocity data validation failed")
                
        except Exception as e:
            st.error(f"  ❌ Error processing {filename}: {str(e)}")
            continue
    
    st.write(f"**Drag-and-drop method results: {len(all_results_dragdrop)} files processed**")
    
    # Summary
    st.write("---")
    st.write("### Summary")
    st.write(f"**Explorer method**: {len(all_results_explorer)} files processed successfully")
    st.write(f"**Drag-and-drop method**: {len(all_results_dragdrop)} files processed successfully")
    
    if len(all_results_explorer) != len(all_results_dragdrop):
        st.warning("⚠️ Different number of files processed between methods!")
    else:
        st.success("✅ Both methods processed the same number of files")

if __name__ == "__main__":
    main() 