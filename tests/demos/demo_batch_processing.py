#!/usr/bin/env python3
"""
Comprehensive Batch Processing Demo

This script demonstrates end-to-end batch processing of all test data files,
showing progress, visualizations, and advanced analytics capabilities.
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

def get_all_test_files():
    """Get all available test data files"""
    
    test_files = []
    
    # Test data folder
    test_data_path = Path("data/test_data")
    if test_data_path.exists():
        for file in test_data_path.glob("*.csv"):
            if file.name != ".DS_Store":
                test_files.append(str(file))
    
    # Sample data folder
    sample_data_path = Path("data/sample_data")
    if sample_data_path.exists():
        for file in sample_data_path.glob("*.csv"):
            if file.name != ".DS_Store":
                test_files.append(str(file))
    
    return sorted(test_files)

def print_progress(current, total, message=""):
    """Print progress bar"""
    progress = (current / total) * 100
    bar_length = 40
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    
    print(f"\r🔄 Progress: [{bar}] {progress:.1f}% ({current}/{total}) {message}", end='', flush=True)
    if current == total:
        print()  # New line when complete

def demo_batch_processing():
    """Run comprehensive batch processing demo"""
    
    print("🚀 WCS Analysis Platform - Batch Processing Demo")
    print("=" * 60)
    
    # Step 1: Discover test files
    print("\n📁 Step 1: Discovering test data files...")
    test_files = get_all_test_files()
    
    if not test_files:
        print("❌ No test files found!")
        return
    
    print(f"✅ Found {len(test_files)} test files:")
    for i, file_path in enumerate(test_files, 1):
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        print(f"   {i:2d}. {os.path.basename(file_path)} ({file_size:.1f} MB)")
    
    # Step 2: Set up analysis parameters
    print("\n⚙️  Step 2: Configuring analysis parameters...")
    
    analysis_parameters = {
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
    for key, value in analysis_parameters.items():
        print(f"   • {key}: {value}")
    
    # Step 3: Process files in batch
    print(f"\n🔬 Step 3: Processing {len(test_files)} files in batch mode...")
    print("   This may take a few minutes depending on file sizes...")
    
    start_time = time.time()
    
    try:
        # Process batch files
        all_results = process_batch_files(test_files, analysis_parameters)
        
        processing_time = time.time() - start_time
        
        if not all_results:
            print("❌ No files were successfully processed!")
            return
        
        print(f"\n✅ Batch processing completed in {processing_time:.2f} seconds!")
        print(f"✅ Successfully processed {len(all_results)} files")
        
        # Step 4: Display processing summary
        print("\n📊 Step 4: Processing Summary")
        print("-" * 40)
        
        total_records = 0
        total_duration = 0
        
        for i, result in enumerate(all_results, 1):
            metadata = result.get('metadata', {})
            records = metadata.get('total_records', 0)
            duration = metadata.get('duration_minutes', 0)
            player = metadata.get('player_name', 'Unknown')
            file_type = metadata.get('file_type', 'Unknown')
            
            total_records += records
            total_duration += duration
            
            print(f"   {i:2d}. {player} ({file_type}): {records:,} records, {duration:.1f} min")
        
        print(f"\n📈 Total Statistics:")
        print(f"   • Total Files: {len(all_results)}")
        print(f"   • Total Records: {total_records:,}")
        print(f"   • Total Duration: {total_duration:.1f} minutes")
        print(f"   • Processing Speed: {total_records/processing_time:.0f} records/second")
        
        # Step 5: Create combined visualizations
        print("\n📈 Step 5: Creating combined visualizations...")
        
        if len(all_results) > 1:
            combined_viz = create_combined_visualizations(all_results)
            
            if combined_viz:
                print("✅ Combined visualizations created:")
                for viz_name in combined_viz.keys():
                    print(f"   • {viz_name}")
            else:
                print("⚠️  Could not create combined visualizations")
        else:
            print("ℹ️  Need multiple files for combined visualizations")
        
        # Step 6: Advanced Analytics (if ≥10 files)
        print(f"\n🔬 Step 6: Advanced Analytics Check...")
        
        if len(all_results) >= 10:
            print("🎯 Advanced Analytics Available! (≥10 files detected)")
            
            # Perform cohort analysis
            print("   Performing cohort analysis...")
            cohort_analysis = analyze_cohort_performance(all_results)
            
            if 'error' not in cohort_analysis:
                summary = cohort_analysis['summary']
                print("✅ Cohort analysis completed:")
                print(f"   • Players analyzed: {summary['total_players']}")
                print(f"   • Total observations: {summary['total_observations']}")
                print(f"   • Average distance: {summary['distance_range']['mean']:.1f} m")
                print(f"   • Distance range: {summary['distance_range']['min']:.1f} - {summary['distance_range']['max']:.1f} m")
                
                # Show top performers
                if summary['top_performers']:
                    print("   • Top performers:")
                    for i, (player, distance) in enumerate(summary['top_performers'].items(), 1):
                        print(f"     {i}. {player}: {distance:.1f} m")
                
                # Show insights
                if summary['insights']:
                    print("   • Key insights:")
                    for insight in summary['insights']:
                        print(f"     • {insight}")
            else:
                print(f"❌ Cohort analysis failed: {cohort_analysis['error']}")
        else:
            print(f"ℹ️  Advanced analytics require ≥10 files (current: {len(all_results)})")
            print("   Add more files to enable comprehensive cohort analysis")
        
        # Step 7: Export results
        print("\n📤 Step 7: Exporting results...")
        
        # Create output directory
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = f"OUTPUT/demo_batch_{timestamp}"
        os.makedirs(output_path, exist_ok=True)
        
        # Export in multiple formats
        try:
            # MATLAB format export
            excel_path = export_data_matlab_format(all_results, output_path, "xlsx")
            print(f"✅ MATLAB format Excel exported: {excel_path}")
            
            # Standard CSV export
            csv_path = export_wcs_data_to_csv(all_results, output_path)
            if csv_path:
                print(f"✅ Standard CSV exported: {csv_path}")
            
            # Advanced analytics export (if available)
            if len(all_results) >= 10 and 'error' not in cohort_analysis:
                exported_files = export_cohort_analysis(cohort_analysis, output_path)
                if 'error' not in exported_files:
                    print("✅ Advanced analytics exported:")
                    for file_type, file_path in exported_files.items():
                        print(f"   • {file_type}: {file_path}")
            
            print(f"\n📁 All exports saved to: {output_path}")
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
        
        # Step 8: Final summary
        print("\n🎉 Step 8: Demo Complete!")
        print("=" * 60)
        print("✅ Batch processing demo completed successfully!")
        print(f"📊 Processed {len(all_results)} files with {total_records:,} total records")
        print(f"⏱️  Total processing time: {processing_time:.2f} seconds")
        print(f"📈 Processing speed: {total_records/processing_time:.0f} records/second")
        
        if len(all_results) >= 10:
            print("🔬 Advanced analytics enabled with comprehensive cohort analysis")
        else:
            print("💡 Add more files (≥10) to enable advanced analytics features")
        
        print(f"📁 Results exported to: {output_path}")
        print("\n🚀 Ready for production use!")
        
        return all_results
        
    except Exception as e:
        print(f"\n❌ Batch processing failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main demo function"""
    
    print("🎯 WCS Analysis Platform - End-to-End Batch Processing Demo")
    print("This demo will process all available test data files and show:")
    print("• File discovery and validation")
    print("• Batch processing with progress tracking")
    print("• Combined visualizations")
    print("• Advanced analytics (if ≥10 files)")
    print("• Multiple export formats")
    print("• Performance metrics")
    
    input("\nPress Enter to start the demo...")
    
    results = demo_batch_processing()
    
    if results:
        print("\n🎊 Demo completed successfully!")
        print("You can now:")
        print("• View the exported files in the OUTPUT directory")
        print("• Run the Streamlit app to see interactive visualizations")
        print("• Use the advanced analytics features with your own data")
    else:
        print("\n❌ Demo failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 