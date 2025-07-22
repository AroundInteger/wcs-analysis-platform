#!/usr/bin/env python3
"""
Minimal WCS Test - Step by Step

This script tests each component individually to identify exactly where the issue occurs.
"""

import streamlit as st
import sys
import os
import time

# Add src to path
sys.path.insert(0, 'src')

def main():
    st.title("🔬 Minimal WCS Test")
    st.write("Testing each step individually...")
    
    # Test file
    test_file = "/Users/rowanbrown/Library/CloudStorage/OneDrive-SwanseaUniversity/Research/WIPS/Intensity Monitoring/DATA2/Blackpool (A) 13.08.22/BLACKPOOL (A) Export for Ben Cabango 41603.csv"
    
    if not os.path.exists(test_file):
        st.error(f"File not found: {test_file}")
        return
    
    st.write(f"📄 Testing with: {os.path.basename(test_file)}")
    
    if st.button("🚀 Start Step-by-Step Test"):
        
        # Step 1: Import test
        st.write("**Step 1: Testing imports...**")
        try:
            from file_ingestion import read_csv_with_metadata, validate_velocity_data
            from wcs_analysis import perform_wcs_analysis
            st.success("✅ Imports successful")
        except Exception as e:
            st.error(f"❌ Import failed: {e}")
            return
        
        # Step 2: File reading test
        st.write("**Step 2: Reading file...**")
        try:
            df, metadata, file_type_info = read_csv_with_metadata(test_file)
            if df is None:
                st.error("❌ File reading failed")
                return
            st.success(f"✅ File read - Shape: {df.shape}")
        except Exception as e:
            st.error(f"❌ File reading failed: {e}")
            return
        
        # Step 3: Validation test
        st.write("**Step 3: Validating data...**")
        try:
            if not validate_velocity_data(df):
                st.error("❌ Data validation failed")
                return
            st.success("✅ Data validation passed")
        except Exception as e:
            st.error(f"❌ Data validation failed: {e}")
            return
        
        # Step 4: Parameters setup
        st.write("**Step 4: Setting up parameters...**")
        try:
            parameters = {
                'sampling_rate': 10,
                'epoch_duration': 1.0,
                'epoch_durations': [1.0, 2.0, 5.0],
                'th0_min': 0.0,
                'th0_max': 100.0,
                'th1_min': 5.0,
                'th1_max': 100.0,
            }
            st.success("✅ Parameters set up")
        except Exception as e:
            st.error(f"❌ Parameter setup failed: {e}")
            return
        
        # Step 5: WCS Analysis (the critical step)
        st.write("**Step 5: Running WCS Analysis...**")
        st.write("⚠️ This is where the app might stop...")
        
        try:
            # Add a progress indicator
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Starting WCS analysis...")
            progress_bar.progress(25)
            time.sleep(0.5)
            
            status_text.text("Processing data...")
            progress_bar.progress(50)
            time.sleep(0.5)
            
            status_text.text("Calculating WCS periods...")
            progress_bar.progress(75)
            time.sleep(0.5)
            
            # This is the critical call
            results = perform_wcs_analysis(df, metadata, file_type_info, parameters)
            
            progress_bar.progress(100)
            status_text.text("Analysis complete!")
            
            if results is None:
                st.error("❌ WCS analysis returned None")
                return
            
            st.success("✅ WCS analysis completed successfully!")
            
            # Show results
            st.write("**Results:**")
            st.write(f"- Velocity stats: {results.get('velocity_stats', {})}")
            st.write(f"- Rolling WCS results: {len(results.get('rolling_wcs_results', []))} epochs")
            st.write(f"- Contiguous WCS results: {len(results.get('contiguous_wcs_results', []))} epochs")
            
            # Show sample results
            if results.get('rolling_wcs_results'):
                st.write("**Sample Rolling WCS Results:**")
                for i, result in enumerate(results['rolling_wcs_results']):
                    epoch_duration = result[8]
                    th0_distance = result[0]
                    th1_distance = result[4]
                    st.write(f"  Epoch {i+1} ({epoch_duration}min): TH0={th0_distance:.1f}m, TH1={th1_distance:.1f}m")
            
            st.success("🎉 All tests passed! The WCS analysis is working correctly.")
            
        except Exception as e:
            st.error(f"❌ WCS analysis failed: {e}")
            st.write("Full error details:")
            st.code(str(e))
            return

if __name__ == "__main__":
    main() 