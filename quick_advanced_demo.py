#!/usr/bin/env python3
"""
Quick Advanced Analytics Demo
"""

import sys
import os
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from advanced_analytics import analyze_cohort_performance, create_cohort_report

def main():
    """Quick demo of advanced analytics"""
    
    print("🔬 Advanced Analytics Demo")
    print("=" * 50)
    
    # Get all test files
    test_files = []
    for file_path in Path("data/test_data").glob("*.csv"):
        if file_path.name != ".DS_Store":
            test_files.append(str(file_path))
    
    print(f"📁 Found {len(test_files)} test files")
    
    if len(test_files) < 10:
        print("❌ Need at least 10 files for advanced analytics")
        return
    
    print("✅ Advanced analytics will be available!")
    
    # Create sample results for demo
    print("\n🔧 Creating sample analysis results...")
    
    sample_results = []
    for i, file_path in enumerate(test_files):
        # Create realistic sample data
        result = {
            'metadata': {
                'player_name': f'Player_{i+1:02d}',
                'file_type': 'GPS',
                'total_records': 5000 + i * 1000,
                'duration_minutes': 90 + i * 5
            },
            'results': {
                'wcs_analysis': [
                    {
                        'epoch_duration': 1.0,
                        'thresholds': [
                            {
                                'threshold_name': 'Default Threshold',
                                'distance': 150 + (i * 10) + 20,
                                'time_range': [0, 90],
                                'frequency': 5 + i,
                                'avg_velocity': 3.5 + (i * 0.1),
                                'max_velocity': 8.0 + (i * 0.2)
                            },
                            {
                                'threshold_name': 'Threshold 1',
                                'distance': 120 + (i * 8) + 15,
                                'time_range': [0, 90],
                                'frequency': 3 + i,
                                'avg_velocity': 3.2 + (i * 0.1),
                                'max_velocity': 7.5 + (i * 0.2)
                            }
                        ]
                    },
                    {
                        'epoch_duration': 2.0,
                        'thresholds': [
                            {
                                'threshold_name': 'Default Threshold',
                                'distance': 180 + (i * 12) + 25,
                                'time_range': [0, 90],
                                'frequency': 4 + i,
                                'avg_velocity': 3.8 + (i * 0.1),
                                'max_velocity': 8.5 + (i * 0.2)
                            }
                        ]
                    },
                    {
                        'epoch_duration': 5.0,
                        'thresholds': [
                            {
                                'threshold_name': 'Default Threshold',
                                'distance': 220 + (i * 15) + 30,
                                'time_range': [0, 90],
                                'frequency': 2 + i,
                                'avg_velocity': 4.2 + (i * 0.1),
                                'max_velocity': 9.0 + (i * 0.2)
                            }
                        ]
                    }
                ]
            }
        }
        sample_results.append(result)
    
    print(f"✅ Created {len(sample_results)} sample results")
    
    # Perform advanced analytics
    print("\n🔬 Performing advanced analytics...")
    start_time = time.time()
    
    cohort_analysis = analyze_cohort_performance(sample_results)
    
    analysis_time = time.time() - start_time
    
    if 'error' in cohort_analysis:
        print(f"❌ Analysis failed: {cohort_analysis['error']}")
        return
    
    # Display results
    print(f"✅ Analysis completed in {analysis_time:.2f} seconds")
    
    summary = cohort_analysis['summary']
    
    print(f"\n📊 Cohort Summary:")
    print(f"   • Players analyzed: {summary['total_players']}")
    print(f"   • Total observations: {summary['total_observations']}")
    print(f"   • Average distance: {summary['distance_range']['mean']:.1f} m")
    print(f"   • Distance range: {summary['distance_range']['min']:.1f} - {summary['distance_range']['max']:.1f} m")
    
    print(f"\n🏆 Top Performers:")
    for i, (player, distance) in enumerate(summary['top_performers'].items(), 1):
        print(f"   {i}. {player}: {distance:.1f} m")
    
    print(f"\n💡 Key Insights:")
    for insight in summary['insights']:
        print(f"   • {insight}")
    
    # Show available visualizations
    if 'visualizations' in cohort_analysis:
        print(f"\n📈 Available Visualizations:")
        for viz_name in cohort_analysis['visualizations'].keys():
            print(f"   • {viz_name.replace('_', ' ').title()}")
    
    # Show available statistics
    if 'statistics' in cohort_analysis:
        print(f"\n📊 Available Statistics:")
        for stat_name in cohort_analysis['statistics'].keys():
            print(f"   • {stat_name.replace('_', ' ').title()}")
    
    # Show available rankings
    if 'rankings' in cohort_analysis:
        print(f"\n🏅 Available Rankings:")
        for rank_name in cohort_analysis['rankings'].keys():
            print(f"   • {rank_name.replace('_', ' ').title()}")
    
    print(f"\n🎉 Advanced Analytics Demo Complete!")
    print(f"📈 Processed {len(sample_results)} players with comprehensive cohort analysis")
    print(f"🚀 Ready for production use with real data!")

if __name__ == "__main__":
    main() 