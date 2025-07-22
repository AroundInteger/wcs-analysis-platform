#!/usr/bin/env python3
"""
Debug script to test batch mode data ingestion step by step
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import traceback

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

def test_single_file_processing(file_path):
    """Test processing a single file"""
    st.write(f"🔍 Testing single file: {os.path.basename(file_path)}")
    
    try:
        # Step 1: Read file
        st.write("📖 Step 1: Reading file...")
        df, metadata, file_type_info = read_csv_with_metadata(file_path)
        
        if df is None:
            st.error("❌ Failed to read file - df is None")
            return False
            
        st.success(f"✅ File read successfully! Shape: {df.shape}")
        st.write(f"📊 Metadata keys: {list(metadata.keys())}")
        st.write(f"🏷️ File type: {file_type_info}")
        
        # Step 2: Validate velocity data
        st.write("🔍 Step 2: Validating velocity data...")
        is_valid = validate_velocity_data(df)
        
        if not is_valid:
            st.warning("⚠️ Velocity data validation failed")
            return False
            
        st.success("✅ Velocity data validated successfully!")
        
        # Step 3: Prepare parameters
        st.write("⚙️ Step 3: Preparing parameters...")
        parameters = {
            'sampling_rate': 10,
            'epoch_duration': 5,
            'epoch_durations': [5, 10, 15],
            'th0_min': 0,
            'th0_max': 20,
            'th1_min': 5,
            'th1_max': 20,
        }
        st.success("✅ Parameters prepared successfully!")
        
        # Step 4: Perform WCS analysis
        st.write("🧮 Step 4: Performing WCS analysis...")
        results = perform_wcs_analysis(df, metadata, file_type_info, parameters)
        
        if results is None:
            st.error("❌ WCS analysis failed - results is None")
            return False
            
        st.success("✅ WCS analysis completed successfully!")
        st.write(f"📈 Results keys: {list(results.keys())}")
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.code(traceback.format_exc())
        return False

def test_batch_processing():
    """Test batch processing with multiple files"""
    st.title("Batch Processing Debug Test")
    st.write("Testing batch mode data ingestion step by step")
    
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
    
    st.write(f"📁 Found {len(test_files)} test files")
    
    # Test individual files first
    st.markdown("---")
    st.markdown("### 🔍 Individual File Testing")
    
    successful_files = []
    for i, file_path in enumerate(test_files[:3]):  # Test with first 3 files
        filename = os.path.basename(file_path)
        st.markdown(f"#### Testing File {i+1}/3: {filename}")
        
        if test_single_file_processing(file_path):
            successful_files.append(file_path)
            st.success(f"✅ {filename} processed successfully!")
        else:
            st.error(f"❌ {filename} failed!")
        
        st.markdown("---")
    
    # Test batch processing
    if successful_files:
        st.markdown("### 🚀 Batch Processing Test")
        st.write(f"Testing batch processing with {len(successful_files)} successful files")
        
        all_results = []
        
        for i, file_path in enumerate(successful_files):
            filename = os.path.basename(file_path)
            st.write(f"Processing {i+1}/{len(successful_files)}: {filename}")
            
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
                st.code(traceback.format_exc())
                continue
        
        if all_results:
            st.success(f"🎉 Batch processing test successful! Processed {len(all_results)} files")
            
            # Test export
            try:
                st.write("📤 Testing export functionality...")
                output_path = "test_output"
                os.makedirs(output_path, exist_ok=True)
                export_path = export_data_matlab_format(all_results, output_path, "xlsx")
                st.success(f"✅ Export test successful! File: {export_path}")
            except Exception as e:
                st.error(f"❌ Export test failed: {str(e)}")
                st.code(traceback.format_exc())
        else:
            st.error("❌ No files were successfully processed in batch mode")
    else:
        st.error("❌ No individual files processed successfully - cannot test batch mode")

def main():
    st.set_page_config(page_title="Batch Processing Debug", layout="wide")
    
    if st.button("Start Debug Test"):
        test_batch_processing()

if __name__ == "__main__":
    main() 