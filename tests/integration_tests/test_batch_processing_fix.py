#!/usr/bin/env python3
"""
Test script to verify batch processing and WCS analysis is working
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
    from src.data_export import export_data_matlab_format
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    st.error(f"Import error: {e}")
    st.stop()

def main():
    st.title("Batch Processing Test")
    st.write("Testing if batch processing and WCS analysis works correctly")
    
    # Test with sample data
    test_data_path = "data/test_data"
    
    if not os.path.exists(test_data_path):
        st.error(f"Test data path not found: {test_data_path}")
        return
    
    # Get test files
    test_files = []
    for file in os.listdir(test_data_path):
        if file.endswith('.csv'):
            test_files.append(os.path.join(test_data_path, file))
    
    if not test_files:
        st.error("No CSV files found in test data directory")
        return
    
    st.write(f"Found {len(test_files)} test files")
    
    if st.button("Test Batch Processing"):
        st.write("Starting batch processing test...")
        
        all_results = []
        
        for i, file_path in enumerate(test_files[:3]):  # Test with first 3 files
            filename = os.path.basename(file_path)
            st.write(f"Processing {i+1}/3: {filename}")
            
            try:
                # Read and validate data
                df, metadata, file_type_info = read_csv_with_metadata(file_path)
                
                # Validate velocity data
                if not validate_velocity_data(df):
                    st.warning(f"Invalid velocity data in {filename}")
                    continue
                
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
                
                # Store results
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
            st.success(f"🎉 Batch processing test successful! Processed {len(all_results)} files")
            
            # Test export
            try:
                output_path = "test_output"
                os.makedirs(output_path, exist_ok=True)
                export_path = export_data_matlab_format(all_results, output_path, "xlsx")
                st.success(f"✅ Export test successful! File: {export_path}")
            except Exception as e:
                st.error(f"❌ Export test failed: {str(e)}")
        else:
            st.error("❌ No files were successfully processed")

if __name__ == "__main__":
    main() 