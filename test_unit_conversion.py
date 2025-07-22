#!/usr/bin/env python3
"""
Test Unit Conversion for Catapult Files

This script tests the unit conversion logic for Catapult files that have velocity in km/hr.
"""

import streamlit as st
import sys
import os
import pandas as pd

# Add src to path
sys.path.insert(0, 'src')

def test_unit_conversion():
    """Test the unit conversion logic"""
    st.title("🔬 Unit Conversion Test")
    st.write("Testing velocity unit conversion from km/hr to m/s...")
    
    # Test with a file that likely has km/hr units
    test_file = "/Users/rowanbrown/Library/CloudStorage/OneDrive-SwanseaUniversity/Research/WIPS/Intensity Monitoring/DATA2/Blackpool (A) 13.08.22/BLACKPOOL (A) Export for Ben Cabango 41603.csv"
    
    if not os.path.exists(test_file):
        st.error(f"File not found: {test_file}")
        return
    
    if st.button("🚀 Test Unit Conversion"):
        
        try:
            from file_ingestion import read_csv_with_metadata, validate_velocity_data
            
            st.write("**Step 1: Reading file with unit detection...**")
            
            # Read the file
            df, metadata, file_type_info = read_csv_with_metadata(test_file)
            
            if df is None:
                st.error("❌ File reading failed")
                return
            
            st.write(f"✅ File read successfully")
            st.write(f"📊 File type: {file_type_info.get('type', 'Unknown')}")
            st.write(f"📊 Player: {metadata.get('player_name', 'Unknown')}")
            
            # Check if velocity units were detected
            velocity_units = metadata.get('velocity_units', 'Not detected')
            st.write(f"📊 Velocity units detected: {velocity_units}")
            
            # Check if conversion was performed
            velocity_converted = metadata.get('velocity_converted', False)
            st.write(f"📊 Velocity converted: {velocity_converted}")
            
            if velocity_converted:
                st.success("✅ Unit conversion was performed!")
                st.write(f"📊 Original units: {metadata.get('original_units', 'Unknown')}")
                st.write(f"📊 Converted units: {metadata.get('converted_units', 'Unknown')}")
            else:
                st.info("ℹ️ No unit conversion was needed or units were not detected")
            
            # Show velocity statistics
            if 'Velocity' in df.columns:
                st.write("**Step 2: Velocity Statistics**")
                
                velocity_stats = df['Velocity'].describe()
                st.write(f"📊 Velocity statistics:")
                st.write(f"  - Count: {velocity_stats['count']:.0f}")
                st.write(f"  - Mean: {velocity_stats['mean']:.2f}")
                st.write(f"  - Std: {velocity_stats['std']:.2f}")
                st.write(f"  - Min: {velocity_stats['min']:.2f}")
                st.write(f"  - Max: {velocity_stats['max']:.2f}")
                
                # Check if original km/hr values are stored
                if 'Velocity_kmphr' in df.columns:
                    st.write("**Step 3: Original km/hr Values**")
                    kmphr_stats = df['Velocity_kmphr'].describe()
                    st.write(f"📊 Original km/hr statistics:")
                    st.write(f"  - Mean: {kmphr_stats['mean']:.2f} km/hr")
                    st.write(f"  - Max: {kmphr_stats['max']:.2f} km/hr")
                    
                    # Verify conversion (km/hr * 5/18 should equal m/s)
                    conversion_factor = 5/18
                    expected_mps = kmphr_stats['max'] * conversion_factor
                    actual_mps = velocity_stats['max']
                    
                    st.write(f"**Step 4: Conversion Verification**")
                    st.write(f"📊 Expected max velocity: {expected_mps:.2f} m/s")
                    st.write(f"📊 Actual max velocity: {actual_mps:.2f} m/s")
                    
                    if abs(expected_mps - actual_mps) < 0.01:
                        st.success("✅ Conversion verified correctly!")
                    else:
                        st.error(f"❌ Conversion mismatch: {abs(expected_mps - actual_mps):.4f}")
                
                # Validate the data
                st.write("**Step 5: Data Validation**")
                is_valid = validate_velocity_data(df)
                st.write(f"📊 Data validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
                
                # Show sample data
                st.write("**Step 6: Sample Data**")
                sample_data = df[['Velocity'] + (['Velocity_kmphr'] if 'Velocity_kmphr' in df.columns else [])].head(10)
                st.dataframe(sample_data, use_container_width=True)
            
            st.success("🎉 Unit conversion test completed!")
            
        except Exception as e:
            st.error(f"❌ Error during unit conversion test: {e}")
            st.write("Full error details:")
            st.code(str(e))

def test_metadata_parsing():
    """Test metadata parsing for unit detection"""
    st.write("---")
    st.write("## 🔍 Metadata Parsing Test")
    
    test_file = "/Users/rowanbrown/Library/CloudStorage/OneDrive-SwanseaUniversity/Research/WIPS/Intensity Monitoring/DATA2/Blackpool (A) 13.08.22/BLACKPOOL (A) Export for Ben Cabango 41603.csv"
    
    if not os.path.exists(test_file):
        st.error(f"File not found: {test_file}")
        return
    
    if st.button("🔍 Test Metadata Parsing"):
        
        try:
            # Read the first 10 lines to check metadata
            with open(test_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:10]
            
            st.write("**First 10 lines of file:**")
            for i, line in enumerate(lines, 1):
                st.write(f"Line {i}: {repr(line.strip())}")
            
            # Check for unit indicators
            st.write("**Unit Detection:**")
            for i, line in enumerate(lines, 1):
                if 'Kilometers' in line or 'km/hr' in line or 'km/h' in line:
                    st.success(f"✅ Line {i}: Found km/hr indicator")
                elif 'Meters' in line or 'm/s' in line:
                    st.success(f"✅ Line {i}: Found m/s indicator")
            
        except Exception as e:
            st.error(f"❌ Error reading metadata: {e}")

def main():
    test_unit_conversion()
    test_metadata_parsing()

if __name__ == "__main__":
    main() 