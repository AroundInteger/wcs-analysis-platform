"""
Data Export Module for WCS Analysis Platform
Replicates MATLAB output format for compatibility with existing workflows
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
from pathlib import Path


def create_matlab_format_export(
    all_results: List[Dict[str, Any]], 
    output_path: str,
    filename_prefix: str = "WCS_Analysis"
) -> str:
    """
    Create Excel export in MATLAB format with multiple sheets
    
    Args:
        all_results: List of analysis results for each file
        output_path: Directory to save the file
        filename_prefix: Prefix for the output filename
    
    Returns:
        Path to the created Excel file
    """
    
    # Create output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}_checkPython.xlsx"
    full_path = os.path.join(output_path, filename)
    
    # Create Excel writer
    with pd.ExcelWriter(full_path, engine='openpyxl') as writer:
        
        sheets_created = 0
        
        # 1. Create WCS Report Sheet
        wcs_report_df = create_wcs_report_sheet(all_results)
        if not wcs_report_df.empty:
            wcs_report_df.to_excel(writer, sheet_name="WCS Report", index=False)
            sheets_created += 1
        
        # 2. Create Summary Maximum Values Sheet
        summary_df = create_summary_max_values_sheet(all_results)
        if not summary_df.empty:
            summary_df.to_excel(writer, sheet_name="Summary Maximum Values", index=False)
            sheets_created += 1
        
        # 3. Create Binned Data Sheets for each epoch
        binned_sheets_created = create_binned_data_sheets(all_results, writer)
        sheets_created += binned_sheets_created
        
        # 4. If no sheets were created, create a default sheet to prevent Excel error
        if sheets_created == 0:
            # Create a simple info sheet
            info_df = pd.DataFrame({
                'Info': ['No WCS data available', 'Analysis may have failed', 'Check input files'],
                'Value': ['', '', '']
            })
            info_df.to_excel(writer, sheet_name="Info", index=False)
            sheets_created += 1
    
    return full_path


def create_wcs_report_sheet(all_results: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Create WCS Report sheet with individual WCS periods and timestamps
    """
    wcs_data = []
    
    for result in all_results:
        if not result.get('analysis_successful', False):
            continue
            
        metadata = result.get('metadata', {})
        player_name = metadata.get('player_name', 'Unknown')
        start_time = metadata.get('start_time')
        
        # Get WCS results
        wcs_results = result.get('wcs_results', {})
        rolling_wcs = wcs_results.get('rolling_wcs', [])
        contiguous_wcs = wcs_results.get('contiguous_wcs', [])
        
        # Process rolling WCS results
        for wcs_period in rolling_wcs:
            epoch_duration = wcs_period.get('epoch_duration', 0)
            threshold_name = wcs_period.get('threshold_name', 'Default Threshold')
            distance = wcs_period.get('distance', 0)
            start_time_wcs = wcs_period.get('start_time', 0)
            end_time_wcs = wcs_period.get('end_time', 0)
            duration = wcs_period.get('duration', 0)
            
            # Calculate frequency (epochs per minute)
            frequency = 60.0 / epoch_duration if epoch_duration > 0 else 0
            
            # Create timestamp
            if start_time:
                try:
                    # Parse start time and add WCS start time
                    if isinstance(start_time, str):
                        ref_start = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                    else:
                        ref_start = start_time
                    
                    wcs_start_datetime = ref_start + timedelta(seconds=start_time_wcs)
                    wcs_end_datetime = ref_start + timedelta(seconds=end_time_wcs)
                except:
                    wcs_start_datetime = None
                    wcs_end_datetime = None
            else:
                wcs_start_datetime = None
                wcs_end_datetime = None
            
            # Determine threshold number
            if 'Default' in threshold_name:
                threshold_num = 0
                threshold_range = "0 < Velocity < 100"
            elif 'Threshold 1' in threshold_name:
                threshold_num = 1
                threshold_range = "6 < Velocity < 10"
            else:
                threshold_num = 0
                threshold_range = "0 < Velocity < 100"
            
            wcs_data.append({
                'Distance_TH_0' if threshold_num == 0 else f'Distance_TH_{threshold_num}': distance,
                'Time_TH_0' if threshold_num == 0 else f'Time_TH_{threshold_num}': duration,
                'Frequency_TH_0' if threshold_num == 0 else f'Frequency_TH_{threshold_num}': frequency,
                'Threshold': f'TH_{threshold_num}: {threshold_range}',
                'PLAYER_METADATA': player_name,
                'TimeStamp': wcs_start_datetime,
                'Index': int(start_time_wcs * 10)  # Assuming 10Hz data
            })
        
        # Process contiguous WCS results (similar structure)
        for wcs_period in contiguous_wcs:
            epoch_duration = wcs_period.get('epoch_duration', 0)
            threshold_name = wcs_period.get('threshold_name', 'Default Threshold')
            distance = wcs_period.get('distance', 0)
            start_time_wcs = wcs_period.get('start_time', 0)
            end_time_wcs = wcs_period.get('end_time', 0)
            duration = wcs_period.get('duration', 0)
            
            frequency = 60.0 / epoch_duration if epoch_duration > 0 else 0
            
            if start_time:
                try:
                    if isinstance(start_time, str):
                        ref_start = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                    else:
                        ref_start = start_time
                    
                    wcs_start_datetime = ref_start + timedelta(seconds=start_time_wcs)
                except:
                    wcs_start_datetime = None
            else:
                wcs_start_datetime = None
            
            if 'Default' in threshold_name:
                threshold_num = 0
                threshold_range = "0 < Velocity < 100"
            elif 'Threshold 1' in threshold_name:
                threshold_num = 1
                threshold_range = "6 < Velocity < 10"
            else:
                threshold_num = 0
                threshold_range = "0 < Velocity < 100"
            
            wcs_data.append({
                'Distance_TH_0' if threshold_num == 0 else f'Distance_TH_{threshold_num}': distance,
                'Time_TH_0' if threshold_num == 0 else f'Time_TH_{threshold_num}': duration,
                'Frequency_TH_0' if threshold_num == 0 else f'Frequency_TH_{threshold_num}': frequency,
                'Threshold': f'TH_{threshold_num}: {threshold_range}',
                'PLAYER_METADATA': player_name,
                'TimeStamp': wcs_start_datetime,
                'Index': int(start_time_wcs * 10)
            })
    
    if wcs_data:
        df = pd.DataFrame(wcs_data)
        # Reorder columns to match MATLAB format
        column_order = ['TimeStamp', 'PLAYER_METADATA', 'Threshold']
        for col in df.columns:
            if col not in column_order:
                column_order.append(col)
        
        return df[column_order]
    else:
        return pd.DataFrame()


def create_summary_max_values_sheet(all_results: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Create Summary Maximum Values sheet with max values for each epoch
    """
    summary_data = []
    
    for result in all_results:
        if not result.get('analysis_successful', False):
            continue
            
        metadata = result.get('metadata', {})
        player_name = metadata.get('player_name', 'Unknown')
        
        wcs_results = result.get('wcs_results', {})
        rolling_wcs = wcs_results.get('rolling_wcs', [])
        
        # Group by epoch duration
        epoch_data = {}
        for wcs_period in rolling_wcs:
            epoch_duration = wcs_period.get('epoch_duration', 0)
            threshold_name = wcs_period.get('threshold_name', 'Default Threshold')
            distance = wcs_period.get('distance', 0)
            
            if epoch_duration not in epoch_data:
                epoch_data[epoch_duration] = {}
            
            if 'Default' in threshold_name:
                threshold_num = 0
            elif 'Threshold 1' in threshold_name:
                threshold_num = 1
            else:
                threshold_num = 0
            
            key = f'Distance_TH_{threshold_num}'
            if key not in epoch_data[epoch_duration]:
                epoch_data[epoch_duration][key] = []
            epoch_data[epoch_duration][key].append(distance)
        
        # Create summary rows
        for epoch_duration, thresholds in epoch_data.items():
            row_data = {
                'PLAYER_METADATA': player_name,
                'Epoch': epoch_duration
            }
            
            for threshold_key, distances in thresholds.items():
                row_data[threshold_key] = max(distances) if distances else 0
            
            summary_data.append(row_data)
    
    if summary_data:
        df = pd.DataFrame(summary_data)
        # Reorder columns
        column_order = ['PLAYER_METADATA', 'Epoch']
        for col in df.columns:
            if col not in column_order:
                column_order.append(col)
        
        return df[column_order]
    else:
        return pd.DataFrame()


def create_binned_data_sheets(all_results: List[Dict[str, Any]], writer: pd.ExcelWriter):
    """
    Create binned data sheets for each epoch duration
    """
    # Group data by epoch duration
    epoch_groups = {}
    
    for result in all_results:
        if not result.get('analysis_successful', False):
            continue
            
        metadata = result.get('metadata', {})
        player_name = metadata.get('player_name', 'Unknown')
        
        wcs_results = result.get('wcs_results', {})
        rolling_wcs = wcs_results.get('rolling_wcs', [])
        
        for wcs_period in rolling_wcs:
            epoch_duration = wcs_period.get('epoch_duration', 0)
            threshold_name = wcs_period.get('threshold_name', 'Default Threshold')
            distance = wcs_period.get('distance', 0)
            start_time_wcs = wcs_period.get('start_time', 0)
            
            if epoch_duration not in epoch_groups:
                epoch_groups[epoch_duration] = []
            
            if 'Default' in threshold_name:
                threshold_num = 0
            elif 'Threshold 1' in threshold_name:
                threshold_num = 1
            else:
                threshold_num = 0
            
            epoch_groups[epoch_duration].append({
                'PLAYER_METADATA': player_name,
                'Epoch': int(start_time_wcs / epoch_duration) + 1,
                f'Distance_TH_{threshold_num}': distance,
                f'Time_TH_{threshold_num}': epoch_duration,
                f'Frequency_TH_{threshold_num}': 60.0 / epoch_duration if epoch_duration > 0 else 0
            })
    
    # Create sheets for each epoch duration
    sheets_created = 0
    for epoch_duration, data in epoch_groups.items():
        if data:
            df = pd.DataFrame(data)
            
            # Reorder columns
            column_order = ['PLAYER_METADATA', 'Epoch']
            for col in df.columns:
                if col not in column_order:
                    column_order.append(col)
            
            df = df[column_order]
            
            # Create sheet name
            sheet_name = f"{epoch_duration:.1f} minute Bin"
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            sheets_created += 1
    
    return sheets_created


def export_to_csv_matlab_format(
    all_results: List[Dict[str, Any]], 
    output_path: str,
    filename_prefix: str = "WCS_Analysis"
) -> str:
    """
    Export to CSV in MATLAB-compatible format
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}_checkPython.csv"
    full_path = os.path.join(output_path, filename)
    
    # Create WCS report data
    wcs_report_df = create_wcs_report_sheet(all_results)
    
    if not wcs_report_df.empty:
        wcs_report_df.to_csv(full_path, index=False)
    
    return full_path


def export_to_json_matlab_format(
    all_results: List[Dict[str, Any]], 
    output_path: str,
    filename_prefix: str = "WCS_Analysis"
) -> str:
    """
    Export to JSON in MATLAB-compatible format
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}_checkPython.json"
    full_path = os.path.join(output_path, filename)
    
    # Create structured data
    export_data = {
        "WCS_Report": create_wcs_report_sheet(all_results).to_dict('records'),
        "Summary_Max_Values": create_summary_max_values_sheet(all_results).to_dict('records'),
        "Metadata": {
            "export_timestamp": timestamp,
            "total_files": len(all_results),
            "successful_analyses": sum(1 for r in all_results if r.get('analysis_successful', False))
        }
    }
    
    # Handle datetime serialization
    def datetime_handler(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    import json
    with open(full_path, 'w') as f:
        json.dump(export_data, f, default=datetime_handler, indent=2)
    
    return full_path


def get_export_formats() -> Dict[str, str]:
    """
    Get available export formats
    """
    return {
        "Excel (MATLAB Format)": "xlsx",
        "CSV (MATLAB Format)": "csv", 
        "JSON (MATLAB Format)": "json"
    }


def export_data_matlab_format(
    all_results: List[Dict[str, Any]], 
    output_path: str,
    format_type: str = "xlsx",
    filename_prefix: str = "WCS_Analysis"
) -> str:
    """
    Main export function that handles all formats
    
    Args:
        all_results: List of analysis results
        output_path: Output directory
        format_type: Export format ("xlsx", "csv", "json")
        filename_prefix: Filename prefix
    
    Returns:
        Path to exported file
    """
    
    # Ensure output directory exists
    os.makedirs(output_path, exist_ok=True)
    
    if format_type.lower() == "xlsx":
        return create_matlab_format_export(all_results, output_path, filename_prefix)
    elif format_type.lower() == "csv":
        return export_to_csv_matlab_format(all_results, output_path, filename_prefix)
    elif format_type.lower() == "json":
        return export_to_json_matlab_format(all_results, output_path, filename_prefix)
    else:
        raise ValueError(f"Unsupported format: {format_type}") 