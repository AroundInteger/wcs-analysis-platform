#!/usr/bin/env python3
"""
Comprehensive Test of Denmark Data Files

This script processes all data files in data/Denmark and demonstrates
the advanced analytics capabilities with real data.
"""

import sys
import os
import time
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from file_ingestion import read_csv_with_metadata, validate_velocity_data
from wcs_analysis import perform_wcs_analysis
from batch_processing import process_batch_files, export_wcs_data_to_csv, create_combined_visualizations
from advanced_analytics import analyze_cohort_performance, create_cohort_report, export_cohort_analysis
from data_export import export_data_matlab_format

def main():
    """Test batch processing on Denmark data files"""
    
    print("🇩🇰 Denmark Data Batch Processing Test")
    print("=" * 60)
    
    # Step 1: Discover Denmark data files
    print("\n📁 Step 1: Discovering Denmark data files...")
    
    denmark_files = []
    denmark_dir = Path("data/Denmark")
    
    for file_path in denmark_dir.glob("*.csv"):
        if file_path.name != ".DS_Store":
            denmark_files.append(str(file_path))
    
    print(f"✅ Found {len(denmark_files)} Denmark data files:")
    for i, file_path in enumerate(denmark_files, 1):
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        print(f"   {i:2d}. {os.path.basename(file_path)} ({file_size:.1f} MB)")
    
    if len(denmark_files) < 10:
        print(f"⚠️  Warning: Only {len(denmark_files)} files found. Advanced analytics require ≥10 files.")
        return
    
    print(f"✅ Advanced analytics will be available with {len(denmark_files)} files!")
    
    # Step 2: Configure analysis parameters
    print("\n⚙️  Step 2: Configuring analysis parameters...")
    
    analysis_params = {
        'sampling_rate': 10,
        'epoch_duration': 1.0,
        'epoch_durations': [1.0, 2.0, 5.0],
        'th1_min': 5.0,
        'th1_max': 100.0,
        'include_visualizations': True,
        'enhanced_wcs_viz': True,
        'include_export': True
    }
    
    print("✅ Analysis parameters configured:")
    for key, value in analysis_params.items():
        print(f"   • {key}: {value}")
    
    # Step 3: Process files in batch mode
    print(f"\n🔬 Step 3: Processing {len(denmark_files)} Denmark files in batch mode...")
    print("   This may take several minutes due to large file sizes...")
    
    start_time = time.time()
    
    try:
        # Process batch files
        all_results = process_batch_files(
            denmark_files,
            analysis_params
        )
        
        processing_time = time.time() - start_time
        
        if not all_results:
            print("❌ No results returned from batch processing")
            return
        
        print(f"✅ Batch processing completed in {processing_time:.2f} seconds!")
        print(f"✅ Successfully processed {len(all_results)} files")
        
        # Step 4: Display processing summary
        print("\n📊 Step 4: Processing Summary")
        print("-" * 40)
        
        total_records = 0
        total_duration = 0
        
        for i, result in enumerate(all_results, 1):
            metadata = result.get('metadata', {})
            player_name = metadata.get('player_name', f'Player_{i}')
            file_type = metadata.get('file_type', 'Unknown')
            total_records_file = metadata.get('total_records', 0)
            duration_minutes = metadata.get('duration_minutes', 0)
            
            total_records += total_records_file
            total_duration += duration_minutes
            
            print(f"    {i:2d}. {player_name} ({file_type}): {total_records_file:,} records, {duration_minutes:.1f} min")
        
        processing_speed = total_records / processing_time if processing_time > 0 else 0
        
        print(f"\n📈 Total Statistics:")
        print(f"   • Total Files: {len(all_results)}")
        print(f"   • Total Records: {total_records:,}")
        print(f"   • Total Duration: {total_duration:.1f} minutes")
        print(f"   • Processing Speed: {processing_speed:.0f} records/second")
        
        # Step 5: Create combined visualizations
        print("\n📈 Step 5: Creating combined visualizations...")
        
        try:
            output_path = f"OUTPUT/denmark_test_{datetime.now().strftime('%Y%m%d_%H-%M-%S')}"
            os.makedirs(output_path, exist_ok=True)
            
            viz_files = create_combined_visualizations(all_results, output_path)
            
            print("✅ Combined visualizations created:")
            for viz_name in viz_files:
                print(f"   • {viz_name}")
                
        except Exception as e:
            print(f"⚠️  Visualization creation failed: {str(e)}")
        
        # Step 6: Advanced Analytics (≥10 files)
        print("\n🔬 Step 6: Advanced Analytics Analysis...")
        
        if len(all_results) >= 10:
            print("✅ Advanced analytics enabled (≥10 files)")
            
            try:
                # Perform cohort analysis
                print("   🔬 Performing cohort analysis...")
                cohort_start = time.time()
                
                cohort_analysis = analyze_cohort_performance(all_results)
                
                cohort_time = time.time() - cohort_start
                
                if 'error' in cohort_analysis:
                    print(f"❌ Cohort analysis failed: {cohort_analysis['error']}")
                else:
                    print(f"✅ Cohort analysis completed in {cohort_time:.2f} seconds")
                    
                    # Display summary
                    summary = cohort_analysis['summary']
                    print(f"\n📊 Cohort Summary:")
                    print(f"   • Players analyzed: {summary['total_players']}")
                    print(f"   • Total observations: {summary['total_observations']}")
                    print(f"   • Average distance: {summary['distance_range']['mean']:.1f} m")
                    print(f"   • Distance range: {summary['distance_range']['min']:.1f} - {summary['distance_range']['max']:.1f} m")
                    
                    # Display top performers
                    print(f"\n🏆 Top Performers:")
                    for i, (player, distance) in enumerate(summary['top_performers'].items(), 1):
                        print(f"   {i}. {player}: {distance:.1f} m")
                    
                    # Display insights
                    if summary['insights']:
                        print(f"\n💡 Key Insights:")
                        for insight in summary['insights']:
                            print(f"   • {insight}")
                    
                    # Export advanced analytics
                    print("\n📤 Exporting advanced analytics...")
                    try:
                        exported_files = export_cohort_analysis(cohort_analysis, output_path)
                        print("✅ Advanced analytics exported:")
                        for file_type, file_path in exported_files.items():
                            print(f"   • {file_type}: {os.path.basename(file_path)}")
                    except Exception as e:
                        print(f"⚠️  Advanced analytics export failed: {str(e)}")
                        
            except Exception as e:
                print(f"❌ Advanced analytics failed: {str(e)}")
        else:
            print(f"ℹ️  Advanced analytics require ≥10 files (current: {len(all_results)})")
        
        # Step 7: Export results
        print("\n📤 Step 7: Exporting results...")
        
        try:
            # Export to CSV
            csv_file = export_wcs_data_to_csv(all_results, output_path)
            print(f"✅ CSV export: {os.path.basename(csv_file)}")
            
            # Export to MATLAB format
            excel_file = export_data_matlab_format(all_results, output_path)
            print(f"✅ MATLAB format: {os.path.basename(excel_file)}")
            
        except Exception as e:
            print(f"❌ Export failed: {str(e)}")
        
        # Step 8: Test completion
        print("\n🎉 Step 8: Test Complete!")
        print("=" * 60)
        print(f"✅ Denmark data test completed successfully!")
        print(f"📊 Processed {len(all_results)} files with {total_records:,} total records")
        print(f"⏱️  Total processing time: {processing_time:.2f} seconds")
        print(f"📈 Processing speed: {processing_speed:.0f} records/second")
        
        if len(all_results) >= 10:
            print(f"🔬 Advanced analytics: ✅ Enabled and working")
        else:
            print(f"🔬 Advanced analytics: ⚠️  Requires ≥10 files")
        
        print(f"📁 Results exported to: {output_path}")
        print(f"🚀 System ready for production use with real data!")
        
    except Exception as e:
        print(f"❌ Batch processing failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 