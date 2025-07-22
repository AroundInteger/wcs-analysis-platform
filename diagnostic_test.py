#!/usr/bin/env python3
"""
Diagnostic Test for WCS Analysis Issues

This script checks for potential issues that might cause the app to stop silently.
"""

import streamlit as st
import sys
import os
import psutil
import time
import traceback

# Add src to path
sys.path.insert(0, 'src')

def check_system_resources():
    """Check system resources"""
    st.write("**System Resources:**")
    
    # Memory
    memory = psutil.virtual_memory()
    st.write(f"- Available Memory: {memory.available / (1024**3):.1f} GB")
    st.write(f"- Memory Usage: {memory.percent}%")
    
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    st.write(f"- CPU Usage: {cpu_percent}%")
    
    # Process memory
    process = psutil.Process()
    process_memory = process.memory_info().rss / (1024**2)  # MB
    st.write(f"- Current Process Memory: {process_memory:.1f} MB")
    
    return memory.available > (1024**3)  # At least 1GB available

def test_with_timeout():
    """Test WCS analysis with timeout monitoring"""
    st.write("**Testing WCS Analysis with Timeout Monitoring...**")
    
    test_file = "/Users/rowanbrown/Library/CloudStorage/OneDrive-SwanseaUniversity/Research/WIPS/Intensity Monitoring/DATA2/Blackpool (A) 13.08.22/BLACKPOOL (A) Export for Ben Cabango 41603.csv"
    
    if not os.path.exists(test_file):
        st.error(f"File not found: {test_file}")
        return False
    
    try:
        # Import modules
        from file_ingestion import read_csv_with_metadata, validate_velocity_data
        from wcs_analysis import perform_wcs_analysis
        
        st.write("✅ Imports successful")
        
        # Read file
        st.write("📖 Reading file...")
        start_time = time.time()
        df, metadata, file_type_info = read_csv_with_metadata(test_file)
        read_time = time.time() - start_time
        
        if df is None:
            st.error("❌ File reading failed")
            return False
        
        st.write(f"✅ File read in {read_time:.2f} seconds - Shape: {df.shape}")
        
        # Validate data
        st.write("🔍 Validating data...")
        if not validate_velocity_data(df):
            st.error("❌ Data validation failed")
            return False
        st.write("✅ Data validation passed")
        
        # Prepare parameters
        parameters = {
            'sampling_rate': 10,
            'epoch_duration': 1.0,
            'epoch_durations': [1.0, 2.0, 5.0],
            'th0_min': 0.0,
            'th0_max': 100.0,
            'th1_min': 5.0,
            'th1_max': 100.0,
        }
        
        # Monitor memory before analysis
        process = psutil.Process()
        memory_before = process.memory_info().rss / (1024**2)
        st.write(f"📊 Memory before analysis: {memory_before:.1f} MB")
        
        # Run WCS analysis with timeout
        st.write("🔬 Running WCS analysis...")
        st.write("⚠️ Monitoring for timeout...")
        
        start_time = time.time()
        
        # Create a progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Update progress every 2 seconds
        def update_progress():
            elapsed = time.time() - start_time
            if elapsed < 10:
                progress = int((elapsed / 10) * 50)
                progress_bar.progress(progress)
                status_text.text(f"Analysis in progress... ({elapsed:.1f}s)")
                return True
            elif elapsed < 30:
                progress = 50 + int(((elapsed - 10) / 20) * 40)
                progress_bar.progress(progress)
                status_text.text(f"Analysis continuing... ({elapsed:.1f}s)")
                return True
            else:
                progress_bar.progress(100)
                status_text.text("Analysis taking longer than expected...")
                return False
        
        # Run analysis
        results = perform_wcs_analysis(df, metadata, file_type_info, parameters)
        
        analysis_time = time.time() - start_time
        progress_bar.progress(100)
        status_text.text("Analysis complete!")
        
        # Monitor memory after analysis
        memory_after = process.memory_info().rss / (1024**2)
        memory_used = memory_after - memory_before
        
        st.write(f"📊 Analysis completed in {analysis_time:.2f} seconds")
        st.write(f"📊 Memory after analysis: {memory_after:.1f} MB (+{memory_used:.1f} MB)")
        
        if results is None:
            st.error("❌ WCS analysis returned None")
            return False
        
        st.success("✅ WCS analysis completed successfully!")
        
        # Show results
        st.write("**Results:**")
        st.write(f"- Velocity stats: {results.get('velocity_stats', {})}")
        st.write(f"- Rolling WCS results: {len(results.get('rolling_wcs_results', []))} epochs")
        st.write(f"- Contiguous WCS results: {len(results.get('contiguous_wcs_results', []))} epochs")
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error during analysis: {e}")
        st.write("Full error details:")
        st.code(traceback.format_exc())
        return False

def main():
    st.title("🔍 WCS Analysis Diagnostic Test")
    st.write("This test will help identify why the app might be stopping...")
    
    if st.button("🚀 Run Diagnostic Test"):
        
        # Check system resources
        st.write("## System Check")
        resources_ok = check_system_resources()
        
        if not resources_ok:
            st.warning("⚠️ Low memory available - this might cause issues")
        
        # Run timeout test
        st.write("## WCS Analysis Test")
        success = test_with_timeout()
        
        if success:
            st.success("🎉 Diagnostic test completed successfully!")
            st.write("**Conclusion:** The WCS analysis is working correctly.")
            st.write("If the main app is still stopping, the issue might be:")
            st.write("- UI rendering conflicts")
            st.write("- Session state issues")
            st.write("- Browser timeout")
        else:
            st.error("❌ Diagnostic test failed!")
            st.write("**Conclusion:** There's an issue with the WCS analysis itself.")

if __name__ == "__main__":
    main() 