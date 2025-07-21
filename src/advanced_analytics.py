"""
Advanced Analytics Module for WCS Analysis Platform

This module provides advanced analytics capabilities for batch processing with >10 files,
including group/cohort analysis, statistical comparisons, and performance insights.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Dict, Any, Optional, Tuple
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

def analyze_cohort_performance(results: List[Dict], metadata_key: str = 'player_name') -> Dict[str, Any]:
    """
    Perform comprehensive cohort analysis across multiple files.
    
    Args:
        results: List of analysis results from batch processing
        metadata_key: Key to use for grouping (default: 'player_name')
    
    Returns:
        Dictionary containing cohort analysis results
    """
    if len(results) < 2:
        return {"error": "Need at least 2 files for cohort analysis"}
    
    # Extract cohort data
    cohort_data = []
    for result in results:
        if 'results' not in result or 'wcs_analysis' not in result['results']:
            continue
            
        metadata = result.get('metadata', {})
        player_name = metadata.get(metadata_key, 'Unknown')
        
        wcs_data = result['results']['wcs_analysis']
        for epoch_data in wcs_data:
            for threshold_data in epoch_data.get('thresholds', []):
                cohort_data.append({
                    'player_name': player_name,
                    'epoch_duration': epoch_data['epoch_duration'],
                    'threshold': threshold_data['threshold_name'],
                    'distance': threshold_data['distance'],
                    'time_range': threshold_data['time_range'],
                    'frequency': threshold_data.get('frequency', 0),
                    'avg_velocity': threshold_data.get('avg_velocity', 0),
                    'max_velocity': threshold_data.get('max_velocity', 0)
                })
    
    if not cohort_data:
        return {"error": "No valid WCS data found for cohort analysis"}
    
    df = pd.DataFrame(cohort_data)
    
    # Perform statistical analysis
    stats_analysis = perform_statistical_analysis(df)
    
    # Generate visualizations
    visualizations = create_cohort_visualizations(df)
    
    # Calculate performance rankings
    rankings = calculate_performance_rankings(df)
    
    # Identify outliers and trends
    outliers = identify_outliers_and_trends(df)
    
    return {
        'cohort_data': df,
        'statistics': stats_analysis,
        'visualizations': visualizations,
        'rankings': rankings,
        'outliers': outliers,
        'summary': generate_cohort_summary(df)
    }

def perform_statistical_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Perform comprehensive statistical analysis on cohort data."""
    
    stats_results = {}
    
    # Overall statistics
    stats_results['overall'] = {
        'total_players': df['player_name'].nunique(),
        'total_observations': len(df),
        'mean_distance': df['distance'].mean(),
        'std_distance': df['distance'].std(),
        'median_distance': df['distance'].median(),
        'min_distance': df['distance'].min(),
        'max_distance': df['distance'].max(),
        'iqr_distance': df['distance'].quantile(0.75) - df['distance'].quantile(0.25)
    }
    
    # By player statistics
    player_stats = df.groupby('player_name').agg({
        'distance': ['mean', 'std', 'min', 'max', 'count'],
        'avg_velocity': ['mean', 'std'],
        'max_velocity': ['mean', 'std']
    }).round(3)
    
    stats_results['by_player'] = player_stats
    
    # By epoch duration statistics
    epoch_stats = df.groupby('epoch_duration').agg({
        'distance': ['mean', 'std', 'min', 'max'],
        'player_name': 'nunique'
    }).round(3)
    
    stats_results['by_epoch'] = epoch_stats
    
    # By threshold statistics
    threshold_stats = df.groupby('threshold').agg({
        'distance': ['mean', 'std', 'min', 'max'],
        'player_name': 'nunique'
    }).round(3)
    
    stats_results['by_threshold'] = threshold_stats
    
    # Correlation analysis
    numeric_cols = ['distance', 'avg_velocity', 'max_velocity', 'frequency']
    correlation_matrix = df[numeric_cols].corr().round(3)
    stats_results['correlations'] = correlation_matrix
    
    return stats_results

def create_cohort_visualizations(df: pd.DataFrame) -> Dict[str, go.Figure]:
    """Create comprehensive visualizations for cohort analysis."""
    
    figures = {}
    
    # 1. Performance Distribution by Player
    fig_dist = px.box(df, x='player_name', y='distance', 
                     title='WCS Distance Distribution by Player',
                     labels={'distance': 'WCS Distance (m)', 'player_name': 'Player'},
                     color='player_name')
    fig_dist.update_layout(height=500, showlegend=False)
    figures['performance_distribution'] = fig_dist
    
    # 2. Performance Heatmap
    pivot_data = df.pivot_table(values='distance', 
                               index='player_name', 
                               columns='epoch_duration', 
                               aggfunc='mean')
    
    fig_heatmap = px.imshow(pivot_data, 
                           title='WCS Performance Heatmap (Distance by Player & Epoch)',
                           labels=dict(x='Epoch Duration (min)', y='Player', color='Distance (m)'),
                           aspect='auto')
    fig_heatmap.update_layout(height=400)
    figures['performance_heatmap'] = fig_heatmap
    
    # 3. Performance Comparison by Threshold
    fig_threshold = px.box(df, x='threshold', y='distance', color='player_name',
                          title='WCS Performance by Threshold',
                          labels={'distance': 'WCS Distance (m)', 'threshold': 'Threshold'})
    fig_threshold.update_layout(height=500)
    figures['threshold_comparison'] = fig_threshold
    
    # 4. Performance Trends by Epoch Duration
    epoch_means = df.groupby('epoch_duration')['distance'].mean().reset_index()
    fig_trend = px.line(epoch_means, x='epoch_duration', y='distance',
                       title='Average WCS Performance by Epoch Duration',
                       labels={'distance': 'Average Distance (m)', 'epoch_duration': 'Epoch Duration (min)'})
    fig_trend.update_layout(height=400)
    figures['epoch_trends'] = fig_trend
    
    # 5. Player Performance Radar Chart
    player_avg = df.groupby('player_name').agg({
        'distance': 'mean',
        'avg_velocity': 'mean',
        'max_velocity': 'mean',
        'frequency': 'mean'
    }).reset_index()
    
    # Normalize values for radar chart
    for col in ['distance', 'avg_velocity', 'max_velocity', 'frequency']:
        player_avg[f'{col}_norm'] = (player_avg[col] - player_avg[col].min()) / (player_avg[col].max() - player_avg[col].min())
    
    fig_radar = go.Figure()
    
    for _, player in player_avg.iterrows():
        fig_radar.add_trace(go.Scatterpolar(
            r=[player['distance_norm'], player['avg_velocity_norm'], 
               player['max_velocity_norm'], player['frequency_norm']],
            theta=['Distance', 'Avg Velocity', 'Max Velocity', 'Frequency'],
            fill='toself',
            name=player['player_name']
        ))
    
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        title='Player Performance Comparison (Normalized)',
        height=500
    )
    figures['player_radar'] = fig_radar
    
    # 6. Performance Scatter Plot
    fig_scatter = px.scatter(df, x='avg_velocity', y='distance', 
                           color='player_name', size='max_velocity',
                           title='WCS Distance vs Average Velocity',
                           labels={'distance': 'WCS Distance (m)', 'avg_velocity': 'Average Velocity (m/s)'})
    fig_scatter.update_layout(height=500)
    figures['performance_scatter'] = fig_scatter
    
    return figures

def calculate_performance_rankings(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Calculate performance rankings across different metrics."""
    
    rankings = {}
    
    # Overall performance ranking
    overall_ranking = df.groupby('player_name')['distance'].mean().sort_values(ascending=False).reset_index()
    overall_ranking['rank'] = range(1, len(overall_ranking) + 1)
    rankings['overall'] = overall_ranking
    
    # Ranking by epoch duration
    epoch_rankings = {}
    for epoch in df['epoch_duration'].unique():
        epoch_data = df[df['epoch_duration'] == epoch]
        epoch_rank = epoch_data.groupby('player_name')['distance'].mean().sort_values(ascending=False).reset_index()
        epoch_rank['rank'] = range(1, len(epoch_rank) + 1)
        epoch_rankings[f'{epoch}_min'] = epoch_rank
    
    rankings['by_epoch'] = epoch_rankings
    
    # Ranking by threshold
    threshold_rankings = {}
    for threshold in df['threshold'].unique():
        threshold_data = df[df['threshold'] == threshold]
        threshold_rank = threshold_data.groupby('player_name')['distance'].mean().sort_values(ascending=False).reset_index()
        threshold_rank['rank'] = range(1, len(threshold_rank) + 1)
        threshold_rankings[threshold] = threshold_rank
    
    rankings['by_threshold'] = threshold_rankings
    
    # Consistency ranking (lowest standard deviation)
    consistency_ranking = df.groupby('player_name')['distance'].std().sort_values().reset_index()
    consistency_ranking['rank'] = range(1, len(consistency_ranking) + 1)
    consistency_ranking.rename(columns={'distance': 'std_distance'}, inplace=True)
    rankings['consistency'] = consistency_ranking
    
    return rankings

def identify_outliers_and_trends(df: pd.DataFrame) -> Dict[str, Any]:
    """Identify outliers and performance trends in the data."""
    
    outliers = {}
    
    # Statistical outliers using IQR method
    Q1 = df['distance'].quantile(0.25)
    Q3 = df['distance'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers['statistical'] = df[(df['distance'] < lower_bound) | (df['distance'] > upper_bound)]
    
    # Performance outliers by player (players with unusually high/low performance)
    player_means = df.groupby('player_name')['distance'].mean()
    player_std = df.groupby('player_name')['distance'].std()
    
    # Players with mean performance > 2 standard deviations from overall mean
    overall_mean = df['distance'].mean()
    overall_std = df['distance'].std()
    
    high_performers = player_means[player_means > overall_mean + 2 * overall_std]
    low_performers = player_means[player_means < overall_mean - 2 * overall_std]
    
    outliers['high_performers'] = high_performers
    outliers['low_performers'] = low_performers
    
    # Trend analysis
    trends = {}
    
    # Performance trend by epoch duration
    epoch_trend = df.groupby('epoch_duration')['distance'].mean()
    if len(epoch_trend) > 1:
        trend_slope = np.polyfit(epoch_trend.index, epoch_trend.values, 1)[0]
        trends['epoch_trend'] = {
            'slope': trend_slope,
            'direction': 'increasing' if trend_slope > 0 else 'decreasing',
            'strength': abs(trend_slope)
        }
    
    # Performance consistency trend
    player_consistency = df.groupby('player_name')['distance'].std()
    trends['consistency'] = {
        'most_consistent': player_consistency.idxmin(),
        'least_consistent': player_consistency.idxmax(),
        'consistency_range': player_consistency.max() - player_consistency.min()
    }
    
    return {
        'outliers': outliers,
        'trends': trends
    }

def generate_cohort_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate a comprehensive summary of cohort performance."""
    
    summary = {}
    
    # Basic statistics
    summary['total_players'] = df['player_name'].nunique()
    summary['total_observations'] = len(df)
    summary['epoch_durations'] = sorted(df['epoch_duration'].unique())
    summary['thresholds'] = sorted(df['threshold'].unique())
    
    # Performance ranges
    summary['distance_range'] = {
        'min': df['distance'].min(),
        'max': df['distance'].max(),
        'mean': df['distance'].mean(),
        'median': df['distance'].median()
    }
    
    # Top performers
    top_performers = df.groupby('player_name')['distance'].mean().nlargest(3)
    summary['top_performers'] = top_performers.to_dict()
    
    # Most consistent performers
    most_consistent = df.groupby('player_name')['distance'].std().nsmallest(3)
    summary['most_consistent'] = most_consistent.to_dict()
    
    # Performance insights
    summary['insights'] = []
    
    # Check for performance gaps
    player_means = df.groupby('player_name')['distance'].mean()
    if player_means.max() - player_means.min() > player_means.mean() * 0.5:
        summary['insights'].append("Significant performance gap detected between players")
    
    # Check for consistency
    player_stds = df.groupby('player_name')['distance'].std()
    if player_stds.max() - player_stds.min() > player_stds.mean() * 0.5:
        summary['insights'].append("Varied consistency levels across players")
    
    # Check for epoch preferences
    epoch_means = df.groupby('epoch_duration')['distance'].mean()
    if epoch_means.max() - epoch_means.min() > epoch_means.mean() * 0.3:
        summary['insights'].append("Performance varies significantly by epoch duration")
    
    return summary

def create_cohort_report(cohort_analysis: Dict[str, Any]) -> str:
    """Generate a comprehensive text report from cohort analysis."""
    
    if 'error' in cohort_analysis:
        return f"Error in cohort analysis: {cohort_analysis['error']}"
    
    summary = cohort_analysis['summary']
    stats = cohort_analysis['statistics']
    rankings = cohort_analysis['rankings']
    outliers = cohort_analysis['outliers']
    
    report = f"""
# Cohort Analysis Report

## Overview
- **Total Players**: {summary['total_players']}
- **Total Observations**: {summary['total_observations']}
- **Epoch Durations**: {', '.join(map(str, summary['epoch_durations']))} minutes
- **Thresholds**: {', '.join(summary['thresholds'])}

## Performance Summary
- **Average Distance**: {summary['distance_range']['mean']:.2f} m
- **Distance Range**: {summary['distance_range']['min']:.2f} - {summary['distance_range']['max']:.2f} m
- **Median Distance**: {summary['distance_range']['median']:.2f} m

## Top Performers
"""
    
    for i, (player, distance) in enumerate(summary['top_performers'].items(), 1):
        report += f"{i}. {player}: {distance:.2f} m\n"
    
    report += "\n## Most Consistent Performers\n"
    for i, (player, std) in enumerate(summary['most_consistent'].items(), 1):
        report += f"{i}. {player}: ±{std:.2f} m\n"
    
    # Handle outliers (nested structure)
    if 'outliers' in outliers:
        outlier_data = outliers['outliers']
        if 'high_performers' in outlier_data and len(outlier_data['high_performers']) > 0:
            report += "\n## High Performers (Outliers)\n"
            for player, distance in outlier_data['high_performers'].items():
                report += f"- {player}: {distance:.2f} m\n"
        
        if 'low_performers' in outlier_data and len(outlier_data['low_performers']) > 0:
            report += "\n## Low Performers (Outliers)\n"
            for player, distance in outlier_data['low_performers'].items():
                report += f"- {player}: {distance:.2f} m\n"
    
    if summary['insights']:
        report += "\n## Key Insights\n"
        for insight in summary['insights']:
            report += f"- {insight}\n"
    
    return report

def export_cohort_analysis(cohort_analysis: Dict[str, Any], output_path: str) -> Dict[str, str]:
    """Export cohort analysis results to multiple formats."""
    
    exported_files = {}
    
    try:
        # Export cohort data to CSV
        if 'cohort_data' in cohort_analysis:
            csv_path = f"{output_path}/cohort_analysis_data.csv"
            cohort_analysis['cohort_data'].to_csv(csv_path, index=False)
            exported_files['cohort_data_csv'] = csv_path
        
        # Export statistics to Excel
        if 'statistics' in cohort_analysis:
            excel_path = f"{output_path}/cohort_statistics.xlsx"
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                # Overall statistics
                pd.DataFrame([cohort_analysis['statistics']['overall']]).to_excel(writer, sheet_name='Overall_Stats', index=False)
                
                # Player statistics
                if 'by_player' in cohort_analysis['statistics']:
                    cohort_analysis['statistics']['by_player'].to_excel(writer, sheet_name='Player_Stats')
                
                # Epoch statistics
                if 'by_epoch' in cohort_analysis['statistics']:
                    cohort_analysis['statistics']['by_epoch'].to_excel(writer, sheet_name='Epoch_Stats')
                
                # Threshold statistics
                if 'by_threshold' in cohort_analysis['statistics']:
                    cohort_analysis['statistics']['by_threshold'].to_excel(writer, sheet_name='Threshold_Stats')
                
                # Correlations
                if 'correlations' in cohort_analysis['statistics']:
                    cohort_analysis['statistics']['correlations'].to_excel(writer, sheet_name='Correlations')
            
            exported_files['statistics_excel'] = excel_path
        
        # Export rankings to CSV
        if 'rankings' in cohort_analysis:
            rankings_path = f"{output_path}/cohort_rankings.csv"
            rankings_data = []
            
            for ranking_type, ranking_data in cohort_analysis['rankings'].items():
                if isinstance(ranking_data, dict):
                    for sub_type, sub_data in ranking_data.items():
                        sub_data['ranking_type'] = f"{ranking_type}_{sub_type}"
                        rankings_data.append(sub_data)
                else:
                    ranking_data['ranking_type'] = ranking_type
                    rankings_data.append(ranking_data)
            
            if rankings_data:
                pd.concat(rankings_data, ignore_index=True).to_csv(rankings_path, index=False)
                exported_files['rankings_csv'] = rankings_path
        
        # Export text report
        report_path = f"{output_path}/cohort_analysis_report.txt"
        report_text = create_cohort_report(cohort_analysis)
        with open(report_path, 'w') as f:
            f.write(report_text)
        exported_files['report_txt'] = report_path
        
    except Exception as e:
        exported_files['error'] = f"Export error: {str(e)}"
    
    return exported_files 