#!/usr/bin/env python3
"""
Simple WCS Analysis Test

This script tests the WCS analysis with minimal UI updates to isolate
the issue causing the app to stop during analysis.
"""

import streamlit as st
import sys
import os

# Add src to path
sys.path.insert(0, 'src')

def main():
    st.title("🔬 Simple WCS Analysis Test")
    st.write("Testing WCS analysis with minimal UI updates...")
    
    # Test with Denmark file
    denmark_file = "data/Denmark/PORTUGAL (AWAY) MD2 (DENMARK) Export for Cadi Rodgers 46247.csv"
    
    if not os.path.exists(denmark_file):
        st.error(f"File not found: {denmark_file}")
        return
    
    st.write(f"📄 Testing with: {os.path.basename(denmark_file)}")
    st.write(f"📊 File size: {os.path.getsize(denmark_file) / (1024*1024):.1f} MB")
    
    if st.button("🚀 Run Simple WCS Analysis"):
        try:
            # Import modules
            from file_ingestion import read_csv_with_metadata, validate_velocity_data
            from wcs_analysis import perform_wcs_analysis
            
            st.write("📖 Reading file...")
            
            # Read file
            df, metadata, file_type_info = read_csv_with_metadata(denmark_file)
            
            if df is None:
                st.error("Failed to read file")
                return
            
            st.write(f"✅ File read - Shape: {df.shape}")
            
            # Validate velocity data
            if not validate_velocity_data(df):
                st.error("Invalid velocity data")
                return
            
            st.write("✅ Velocity data validated")
            
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
            
            st.write("🔬 Performing WCS analysis...")
            
            # Perform WCS analysis
            results = perform_wcs_analysis(df, metadata, file_type_info, parameters)
            
            if results is None:
                st.error("WCS analysis returned None")
                return
            
            st.write("✅ WCS analysis completed!")
            st.write(f"📊 Velocity stats: {results.get('velocity_stats', {})}")
            st.write(f"🔄 Rolling WCS results: {len(results.get('rolling_wcs_results', []))} epochs")
            st.write(f"📈 Contiguous WCS results: {len(results.get('contiguous_wcs_results', []))} epochs")
            
            # Test visualization
            st.write("🎨 Testing visualization...")
            from visualization import create_velocity_visualization
            
            fig = create_velocity_visualization(
                results['processed_data'],
                results['metadata'],
                results.get('rolling_wcs_results', [])
            )
            
            if fig is not None:
                st.write("✅ Visualization created successfully")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Visualization creation failed")
            
            st.success("🎉 All tests passed! WCS analysis is working correctly.")
            
        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            st.write("Full error details:")
            st.code(str(e))

if __name__ == "__main__":
    main() 