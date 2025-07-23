#!/usr/bin/env python3
"""
Quick Unit Conversion Test - Command Line Version

This script quickly tests the unit conversion logic from the command line.
"""

import sys
import os
import pandas as pd

# Add src to path
sys.path.insert(0, 'src')

def quick_unit_test():
    """Quick test of unit conversion logic"""
    print("🔬 Quick Unit Conversion Test")
    print("=" * 50)
    
    # Test with a file that likely has km/hr units
    test_file = "/Users/rowanbrown/Library/CloudStorage/OneDrive-SwanseaUniversity/Research/WIPS/Intensity Monitoring/DATA2/Blackpool (A) 13.08.22/BLACKPOOL (A) Export for Ben Cabango 41603.csv"
    
    if not os.path.exists(test_file):
        print(f"❌ File not found: {test_file}")
        return
    
    try:
        from file_ingestion import read_csv_with_metadata, validate_velocity_data
        
        print("📖 Reading file with unit detection...")
        
        # Read the file
        df, metadata, file_type_info = read_csv_with_metadata(test_file)
        
        if df is None:
            print("❌ File reading failed")
            return
        
        print(f"✅ File read successfully")
        print(f"📊 File type: {file_type_info.get('type', 'Unknown')}")
        print(f"📊 Player: {metadata.get('player_name', 'Unknown')}")
        
        # Check if velocity units were detected
        velocity_units = metadata.get('velocity_units', 'Not detected')
        print(f"📊 Velocity units detected: {velocity_units}")
        
        # Check if conversion was performed
        velocity_converted = metadata.get('velocity_converted', False)
        print(f"📊 Velocity converted: {velocity_converted}")
        
        if velocity_converted:
            print("✅ Unit conversion was performed!")
            print(f"📊 Original units: {metadata.get('original_units', 'Unknown')}")
            print(f"📊 Converted units: {metadata.get('converted_units', 'Unknown')}")
        else:
            print("ℹ️ No unit conversion was needed or units were not detected")
        
        # Show velocity statistics
        if 'Velocity' in df.columns:
            print("\n📊 Velocity Statistics:")
            
            velocity_stats = df['Velocity'].describe()
            print(f"  - Count: {velocity_stats['count']:.0f}")
            print(f"  - Mean: {velocity_stats['mean']:.2f}")
            print(f"  - Std: {velocity_stats['std']:.2f}")
            print(f"  - Min: {velocity_stats['min']:.2f}")
            print(f"  - Max: {velocity_stats['max']:.2f}")
            
            # Check if original km/hr values are stored
            if 'Velocity_kmphr' in df.columns:
                print("\n📊 Original km/hr Values:")
                kmphr_stats = df['Velocity_kmphr'].describe()
                print(f"  - Mean: {kmphr_stats['mean']:.2f} km/hr")
                print(f"  - Max: {kmphr_stats['max']:.2f} km/hr")
                
                # Verify conversion (km/hr * 5/18 should equal m/s)
                conversion_factor = 5/18
                expected_mps = kmphr_stats['max'] * conversion_factor
                actual_mps = velocity_stats['max']
                
                print(f"\n🔍 Conversion Verification:")
                print(f"  - Expected max velocity: {expected_mps:.2f} m/s")
                print(f"  - Actual max velocity: {actual_mps:.2f} m/s")
                
                if abs(expected_mps - actual_mps) < 0.01:
                    print("✅ Conversion verified correctly!")
                else:
                    print(f"❌ Conversion mismatch: {abs(expected_mps - actual_mps):.4f}")
            
            # Validate the data
            print(f"\n🔍 Data Validation:")
            is_valid = validate_velocity_data(df)
            print(f"  - Data validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
            
            # Show sample data
            print(f"\n📋 Sample Data (first 5 rows):")
            sample_data = df[['Velocity'] + (['Velocity_kmphr'] if 'Velocity_kmphr' in df.columns else [])].head(5)
            print(sample_data.to_string())
        
        print("\n🎉 Unit conversion test completed!")
        
    except Exception as e:
        print(f"❌ Error during unit conversion test: {e}")

def test_metadata_parsing():
    """Test metadata parsing for unit detection"""
    print("\n" + "=" * 50)
    print("🔍 Metadata Parsing Test")
    print("=" * 50)
    
    test_file = "/Users/rowanbrown/Library/CloudStorage/OneDrive-SwanseaUniversity/Research/WIPS/Intensity Monitoring/DATA2/Blackpool (A) 13.08.22/BLACKPOOL (A) Export for Ben Cabango 41603.csv"
    
    if not os.path.exists(test_file):
        print(f"❌ File not found: {test_file}")
        return
    
    try:
        # Read the first 10 lines to check metadata
        with open(test_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:10]
        
        print("First 10 lines of file:")
        for i, line in enumerate(lines, 1):
            print(f"Line {i}: {repr(line.strip())}")
        
        # Check for unit indicators
        print("\nUnit Detection:")
        for i, line in enumerate(lines, 1):
            if 'Kilometers' in line or 'km/hr' in line or 'km/h' in line:
                print(f"✅ Line {i}: Found km/hr indicator")
            elif 'Meters' in line or 'm/s' in line:
                print(f"✅ Line {i}: Found m/s indicator")
        
    except Exception as e:
        print(f"❌ Error reading metadata: {e}")

if __name__ == "__main__":
    quick_unit_test()
    test_metadata_parsing() 