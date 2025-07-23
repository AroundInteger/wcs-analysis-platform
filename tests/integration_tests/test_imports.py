#!/usr/bin/env python3
"""
Test Imports
This script tests that all required imports are working correctly.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all required imports"""
    
    print("🧪 Testing Imports")
    print("=" * 30)
    
    try:
        print("📦 Testing basic imports...")
        import pandas as pd
        import numpy as np
        import streamlit as st
        print("✅ Basic imports successful")
        
        print("\n📊 Testing visualization imports...")
        import plotly.graph_objects as go
        import plotly.express as px
        print("✅ Visualization imports successful")
        
        print("\n🔬 Testing WCS analysis imports...")
        from wcs_analysis import perform_wcs_analysis
        print("✅ WCS analysis imports successful")
        
        print("\n📁 Testing file ingestion imports...")
        from file_ingestion import read_csv_with_metadata, validate_velocity_data
        print("✅ File ingestion imports successful")
        
        print("\n📈 Testing advanced analytics imports...")
        from advanced_analytics import analyze_cohort_performance, create_cohort_report
        print("✅ Advanced analytics imports successful")
        
        print("\n🔄 Testing batch processing imports...")
        from batch_processing import process_batch_files, create_combined_visualizations
        print("✅ Batch processing imports successful")
        
        print("\n📊 Testing visualization module imports...")
        from visualization import create_enhanced_wcs_visualization
        print("✅ Visualization module imports successful")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n✅ All imports working correctly!")
        print("🌐 The web interface should now work properly.")
    else:
        print("\n❌ Some imports failed. Check the environment setup.") 