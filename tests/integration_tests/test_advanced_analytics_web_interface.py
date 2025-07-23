#!/usr/bin/env python3
"""
Test Advanced Analytics Web Interface
This script provides a step-by-step guide to test the advanced analytics
functionality using the web interface with the created test data.
"""

import webbrowser
import time
import os
from pathlib import Path

def test_advanced_analytics_workflow():
    """Guide through testing advanced analytics in the web interface"""
    
    print("🧪 Testing Advanced Analytics in Web Interface")
    print("=" * 60)
    
    # Check if test data exists
    test_dir = Path("test_data_advanced_analytics")
    if not test_dir.exists():
        print("❌ Test data directory not found!")
        print("Please run 'python create_test_data_for_advanced_analytics.py' first")
        return False
    
    # Check if files exist
    csv_files = list(test_dir.glob("*.csv"))
    if not csv_files:
        print("❌ No CSV files found in test data directory!")
        return False
    
    print(f"✅ Found {len(csv_files)} test files")
    for file in csv_files:
        print(f"  📄 {file.name}")
    
    # Check if Streamlit app is running
    print("\n🌐 Checking if WCS Analysis Platform is running...")
    try:
        import requests
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ WCS Analysis Platform is running")
        else:
            print("⚠️  Platform may not be fully loaded")
    except:
        print("❌ WCS Analysis Platform is not running!")
        print("Please start it with: ./start_app.sh")
        return False
    
    print("\n" + "="*60)
    print("📋 STEP-BY-STEP TESTING GUIDE")
    print("="*60)
    
    print("\n1️⃣  OPEN THE WEB INTERFACE")
    print("   🌐 URL: http://localhost:8501")
    print("   📱 The app should open in your browser")
    
    # Try to open the browser
    try:
        webbrowser.open("http://localhost:8501")
        print("   ✅ Browser opened automatically")
    except:
        print("   ⚠️  Please manually open: http://localhost:8501")
    
    print("\n2️⃣  UPLOAD TEST FILES")
    print("   📁 Navigate to the 'File Selection' section")
    print("   📤 Click 'Browse files' and select ALL files from:")
    print(f"      {test_dir.absolute()}")
    print("   📋 Files to upload:")
    for file in csv_files:
        print(f"      - {file.name}")
    
    print("\n3️⃣  PROCESS FILES IN BATCH MODE")
    print("   ⚙️  In the 'Analysis Parameters' section:")
    print("      - Method: Rolling")
    print("      - Default Threshold Min: 5.5")
    print("      - Default Threshold Max: 7.0")
    print("      - Epoch Duration: 300 seconds")
    print("   🚀 Click 'Run Analysis'")
    print("   ⏳ Wait for processing to complete")
    
    print("\n4️⃣  TEST ADVANCED ANALYTICS")
    print("   📊 Navigate to the 'Advanced Analytics' tab")
    print("   🔍 Verify the following sections are populated:")
    print("      ✅ Cohort Performance Summary")
    print("      ✅ Performance Distribution")
    print("      ✅ Player Performance Ranking")
    print("      ✅ Statistical Analysis")
    print("      ✅ Performance Insights")
    
    print("\n5️⃣  TEST EXPORT FUNCTIONALITY")
    print("   📄 Test CSV Export:")
    print("      - Click 'Export Cohort Data (CSV)'")
    print("      - Verify file downloads correctly")
    print("   📋 Test Report Generation:")
    print("      - Click 'Generate Cohort Report'")
    print("      - Verify report content is comprehensive")
    
    print("\n6️⃣  VERIFY DATA ACCURACY")
    print("   📊 Check that:")
    print("      - 5 players are shown in the cohort")
    print("      - Performance metrics are realistic")
    print("      - Visualizations display correctly")
    print("      - No error messages appear")
    
    print("\n" + "="*60)
    print("🔍 EXPECTED RESULTS")
    print("="*60)
    
    print("\n📊 Cohort Summary should show:")
    print("   - Total Players: 5")
    print("   - Total Sessions: 5")
    print("   - Total WCS Events: ~30,000+ (combined)")
    print("   - Advanced Analytics: Available with 3+ files (threshold updated!)")
    
    print("\n📈 Performance Metrics should show:")
    print("   - Mean Distance: 15-25 meters per WCS event")
    print("   - Mean Velocity: 6.0-7.0 m/s")
    print("   - Performance variations between players")
    
    print("\n🎯 Player Rankings should show:")
    print("   - Player_B (Midfielder) likely highest performer")
    print("   - Player_A and Player_D (Forwards) in middle range")
    print("   - Player_C and Player_E in lower range")
    
    print("\n📊 Visualizations should include:")
    print("   - Distance distribution histogram")
    print("   - Performance heatmap")
    print("   - Player comparison charts")
    print("   - Statistical correlation plots")
    
    print("\n" + "="*60)
    print("❌ TROUBLESHOOTING")
    print("="*60)
    
    print("\nIf Advanced Analytics tab is blank:")
    print("   🔄 Refresh the page and try again")
    print("   📊 Ensure at least 3 files are processed (threshold updated!)")
    print("   ⚙️  Check that WCS analysis completed successfully")
    
    print("\nIf files fail to upload:")
    print("   📁 Verify file paths are correct")
    print("   🔍 Check file format (should be CSV)")
    print("   📊 Ensure files have 'Velocity' column")
    
    print("\nIf processing fails:")
    print("   ⚙️  Check analysis parameters")
    print("   🔄 Try with fewer files first")
    print("   📊 Verify data quality in files")
    
    print("\n" + "="*60)
    print("✅ SUCCESS CRITERIA")
    print("="*60)
    
    print("\nThe test is successful if:")
    print("   ✅ All 5 files upload and process correctly")
    print("   ✅ Advanced Analytics tab shows comprehensive data")
    print("   ✅ All visualizations render properly")
    print("   ✅ Export functions work correctly")
    print("   ✅ No error messages appear")
    print("   ✅ Performance metrics are realistic")
    
    print("\n🎉 Ready to test! Follow the steps above.")
    print("📞 If you encounter issues, check the troubleshooting section.")
    
    return True

def check_test_data_quality():
    """Check the quality of the test data files"""
    
    print("\n🔍 CHECKING TEST DATA QUALITY")
    print("=" * 40)
    
    test_dir = Path("test_data_advanced_analytics")
    csv_files = list(test_dir.glob("*.csv"))
    
    for file in csv_files:
        print(f"\n📄 Checking {file.name}...")
        
        try:
            import pandas as pd
            df = pd.read_csv(file)
            
            print(f"   📊 Shape: {df.shape}")
            print(f"   📋 Columns: {list(df.columns)}")
            
            if 'Velocity' in df.columns:
                print(f"   🏃 Velocity range: {df['Velocity'].min():.2f} - {df['Velocity'].max():.2f} m/s")
                print(f"   ⚡ WCS events (>5.5 m/s): {(df['Velocity'] > 5.5).sum()}")
                print(f"   📈 Mean velocity: {df['Velocity'].mean():.2f} m/s")
            else:
                print("   ❌ Missing 'Velocity' column!")
            
            if 'Timestamp' in df.columns:
                print(f"   ⏰ Duration: {df['Timestamp'].max() - df['Timestamp'].min():.1f} seconds")
            
            print("   ✅ File looks good")
            
        except Exception as e:
            print(f"   ❌ Error reading file: {str(e)}")

if __name__ == "__main__":
    print("🚀 Advanced Analytics Web Interface Test")
    print("=" * 60)
    
    # Check test data quality first
    check_test_data_quality()
    
    # Provide testing guide
    test_advanced_analytics_workflow()
    
    print("\n🏁 Test guide completed!")
    print("📋 Follow the steps above to test the advanced analytics functionality.") 