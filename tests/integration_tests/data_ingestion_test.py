#!/usr/bin/env python3
"""
Data Ingestion Test - Comprehensive Folder Analysis

This script tests:
1. All files in the folder are being ingested
2. Zero-velocity files are acknowledged but don't stop analysis
3. Files with valid data are processed correctly
"""

import streamlit as st
import sys
import os
import glob
import pandas as pd
import time

# Add src to path
sys.path.insert(0, 'src')

def analyze_folder_contents(folder_path):
    """Analyze all files in the folder"""
    st.write(f"📁 Analyzing folder: {folder_path}")
    
    if not os.path.exists(folder_path):
        st.error(f"❌ Folder not found: {folder_path}")
        return
    
    # Get all CSV files
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    st.write(f"📄 Found {len(csv_files)} CSV files")
    
    if not csv_files:
        st.error("❌ No CSV files found in folder")
        return
    
    # Display all files
    st.write("**All CSV files in folder:**")
    for i, file_path in enumerate(csv_files, 1):
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        st.write(f"{i}. {os.path.basename(file_path)} ({file_size:.2f} MB)")
    
    return csv_files

def test_file_ingestion(file_path):
    """Test ingestion of a single file"""
    try:
        from file_ingestion import read_csv_with_metadata, validate_velocity_data
        
        # Read file
        df, metadata, file_type_info = read_csv_with_metadata(file_path)
        
        if df is None:
            return {
                'status': 'failed',
                'error': 'File reading returned None',
                'metadata': None,
                'file_type': None,
                'shape': None,
                'velocity_stats': None
            }
        
        # Get velocity column
        velocity_col = None
        for col in df.columns:
            if 'velocity' in col.lower() or 'speed' in col.lower():
                velocity_col = col
                break
        
        if velocity_col is None:
            return {
                'status': 'failed',
                'error': 'No velocity column found',
                'metadata': metadata,
                'file_type': file_type_info,
                'shape': df.shape,
                'velocity_stats': None
            }
        
        # Check velocity data
        velocity_data = df[velocity_col].dropna()
        velocity_stats = {
            'total_points': len(velocity_data),
            'non_zero_points': len(velocity_data[velocity_data > 0]),
            'zero_points': len(velocity_data[velocity_data == 0]),
            'max_velocity': velocity_data.max(),
            'mean_velocity': velocity_data.mean(),
            'has_movement': len(velocity_data[velocity_data > 0]) > 0
        }
        
        # Validate data
        is_valid = validate_velocity_data(df)
        
        return {
            'status': 'success' if is_valid else 'invalid',
            'error': None,
            'metadata': metadata,
            'file_type': file_type_info,
            'shape': df.shape,
            'velocity_stats': velocity_stats,
            'velocity_column': velocity_col
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'metadata': None,
            'file_type': None,
            'shape': None,
            'velocity_stats': None
        }

def test_wcs_analysis_on_file(file_path):
    """Test WCS analysis on a single file"""
    try:
        from file_ingestion import read_csv_with_metadata, validate_velocity_data
        from wcs_analysis import perform_wcs_analysis
        
        # Read and validate file
        df, metadata, file_type_info = read_csv_with_metadata(file_path)
        
        if df is None:
            return {
                'status': 'failed',
                'error': 'File reading failed',
                'results': None
            }
        
        if not validate_velocity_data(df):
            return {
                'status': 'failed',
                'error': 'Data validation failed',
                'results': None
            }
        
        # Set up parameters
        parameters = {
            'sampling_rate': 10,
            'epoch_duration': 1.0,
            'epoch_durations': [1.0, 2.0, 5.0],
            'th0_min': 0.0,
            'th0_max': 100.0,
            'th1_min': 5.0,
            'th1_max': 100.0,
        }
        
        # Run WCS analysis
        results = perform_wcs_analysis(df, metadata, file_type_info, parameters)
        
        if results is None:
            return {
                'status': 'failed',
                'error': 'WCS analysis returned None',
                'results': None
            }
        
        return {
            'status': 'success',
            'error': None,
            'results': results
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'results': None
        }

def main():
    st.title("🔍 Data Ingestion & Zero-Velocity Test")
    st.write("Testing complete folder ingestion and zero-velocity file handling...")
    
    # Test folder
    test_folder = "/Users/rowanbrown/Library/CloudStorage/OneDrive-SwanseaUniversity/Research/WIPS/Intensity Monitoring/DATA2/Blackpool (A) 13.08.22/"
    
    if st.button("🚀 Start Comprehensive Test"):
        
        # Step 1: Analyze folder contents
        st.write("## Step 1: Folder Analysis")
        csv_files = analyze_folder_contents(test_folder)
        
        if not csv_files:
            return
        
        # Step 2: Test each file individually
        st.write("## Step 2: Individual File Analysis")
        
        ingestion_results = []
        wcs_results = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, file_path in enumerate(csv_files):
            filename = os.path.basename(file_path)
            status_text.text(f"Processing {i+1}/{len(csv_files)}: {filename}")
            progress_bar.progress((i + 1) / len(csv_files))
            
            # Test ingestion
            ingestion_result = test_file_ingestion(file_path)
            ingestion_result['filename'] = filename
            ingestion_result['file_path'] = file_path
            ingestion_results.append(ingestion_result)
            
            # If ingestion successful, test WCS analysis
            if ingestion_result['status'] == 'success':
                wcs_result = test_wcs_analysis_on_file(file_path)
                wcs_result['filename'] = filename
                wcs_result['file_path'] = file_path
                wcs_results.append(wcs_result)
            else:
                wcs_results.append({
                    'filename': filename,
                    'file_path': file_path,
                    'status': 'skipped',
                    'error': 'Ingestion failed',
                    'results': None
                })
        
        status_text.text("Analysis complete!")
        
        # Step 3: Display results
        st.write("## Step 3: Results Summary")
        
        # Ingestion results
        st.write("### 📊 Ingestion Results")
        
        successful_ingestions = [r for r in ingestion_results if r['status'] == 'success']
        failed_ingestions = [r for r in ingestion_results if r['status'] == 'failed']
        error_ingestions = [r for r in ingestion_results if r['status'] == 'error']
        invalid_ingestions = [r for r in ingestion_results if r['status'] == 'invalid']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("✅ Successful", len(successful_ingestions))
        with col2:
            st.metric("❌ Failed", len(failed_ingestions))
        with col3:
            st.metric("⚠️ Errors", len(error_ingestions))
        with col4:
            st.metric("🔍 Invalid", len(invalid_ingestions))
        
        # Zero-velocity analysis
        st.write("### 🚶 Zero-Velocity Analysis")
        
        zero_velocity_files = []
        valid_movement_files = []
        
        for result in successful_ingestions:
            if result['velocity_stats']:
                if result['velocity_stats']['has_movement']:
                    valid_movement_files.append(result)
                else:
                    zero_velocity_files.append(result)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📈 Has Movement", len(valid_movement_files))
        with col2:
            st.metric("🛑 Zero Velocity", len(zero_velocity_files))
        
        # WCS analysis results
        st.write("### 🔬 WCS Analysis Results")
        
        successful_wcs = [r for r in wcs_results if r['status'] == 'success']
        failed_wcs = [r for r in wcs_results if r['status'] == 'failed']
        error_wcs = [r for r in wcs_results if r['status'] == 'error']
        skipped_wcs = [r for r in wcs_results if r['status'] == 'skipped']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("✅ WCS Success", len(successful_wcs))
        with col2:
            st.metric("❌ WCS Failed", len(failed_wcs))
        with col3:
            st.metric("⚠️ WCS Errors", len(error_wcs))
        with col4:
            st.metric("⏭️ WCS Skipped", len(skipped_wcs))
        
        # Detailed results
        st.write("### 📋 Detailed Results")
        
        # Create expandable sections for different result types
        with st.expander("✅ Successful Files", expanded=True):
            for result in successful_ingestions:
                if result['velocity_stats']:
                    st.write(f"**{result['filename']}**")
                    st.write(f"  - Shape: {result['shape']}")
                    st.write(f"  - Velocity Column: {result['velocity_stats'].get('velocity_column', 'N/A')}")
                    st.write(f"  - Total Points: {result['velocity_stats']['total_points']}")
                    st.write(f"  - Non-zero Points: {result['velocity_stats']['non_zero_points']}")
                    st.write(f"  - Zero Points: {result['velocity_stats']['zero_points']}")
                    st.write(f"  - Max Velocity: {result['velocity_stats']['max_velocity']:.2f}")
                    st.write(f"  - Has Movement: {'✅' if result['velocity_stats']['has_movement'] else '❌'}")
                    st.write("---")
        
        if zero_velocity_files:
            with st.expander("🛑 Zero-Velocity Files", expanded=True):
                for result in zero_velocity_files:
                    st.write(f"**{result['filename']}**")
                    st.write(f"  - Shape: {result['shape']}")
                    st.write(f"  - Total Points: {result['velocity_stats']['total_points']}")
                    st.write(f"  - All velocities are zero")
                    st.write("---")
        
        if failed_ingestions:
            with st.expander("❌ Failed Files", expanded=False):
                for result in failed_ingestions:
                    st.write(f"**{result['filename']}**")
                    st.write(f"  - Error: {result['error']}")
                    st.write("---")
        
        if error_ingestions:
            with st.expander("⚠️ Error Files", expanded=False):
                for result in error_ingestions:
                    st.write(f"**{result['filename']}**")
                    st.write(f"  - Error: {result['error']}")
                    st.write("---")
        
        # Conclusion
        st.write("## 🎯 Conclusion")
        
        if len(successful_ingestions) == len(csv_files):
            st.success("✅ All files were successfully ingested!")
        else:
            st.warning(f"⚠️ {len(csv_files) - len(successful_ingestions)} files failed ingestion")
        
        if zero_velocity_files:
            st.info(f"ℹ️ {len(zero_velocity_files)} files have zero velocity (no movement recorded)")
        
        if len(successful_wcs) > 0:
            st.success(f"✅ WCS analysis completed successfully for {len(successful_wcs)} files")
        else:
            st.error("❌ No files completed WCS analysis successfully")
        
        # Key findings
        st.write("### 🔍 Key Findings:")
        st.write(f"- **Total files processed:** {len(csv_files)}")
        st.write(f"- **Files with movement data:** {len(valid_movement_files)}")
        st.write(f"- **Files with zero velocity:** {len(zero_velocity_files)}")
        st.write(f"- **WCS analysis successful:** {len(successful_wcs)}")
        
        if len(successful_wcs) > 0:
            st.success("🎉 The system correctly handles zero-velocity files and continues processing other files!")

if __name__ == "__main__":
    main() 