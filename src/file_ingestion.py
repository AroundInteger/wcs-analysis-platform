"""
File Ingestion Module for WCS Analysis Platform

Handles multi-format GPS data file ingestion with automatic format detection
and validation.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Tuple, Optional, Any
import streamlit as st


def detect_file_format(content_lines: list) -> Dict[str, Any]:
    """
    Automatically detect file format based on content analysis
    
    Args:
        content_lines: First few lines of the file
        
    Returns:
        Dictionary with format type and confidence score
    """
    # Check for StatSport format
    if any('Player Id' in line and 'Player Display Name' in line for line in content_lines[:3]):
        return {'type': 'statsport', 'confidence': 0.95}
    
    # Check for Catapult format (metadata headers)
    if any(line.startswith('#') for line in content_lines[:10]):
        if any('OpenField Export' in line for line in content_lines):
            if any('Athlete:' in line for line in content_lines):
                return {'type': 'catapult', 'confidence': 0.90}
            else:
                return {'type': 'catapult_export', 'confidence': 0.85}
    
    # Check for generic GPS format
    if any('Timestamp' in line and 'Velocity' in line for line in content_lines[:3]):
        return {'type': 'generic_gps', 'confidence': 0.80}
    
    return {'type': 'unknown', 'confidence': 0.0}


def read_statsport_file(uploaded_file) -> Tuple[Optional[pd.DataFrame], Optional[Dict]]:
    """
    Read StatSport format CSV file
    
    Args:
        uploaded_file: Streamlit uploaded file
        
    Returns:
        Tuple of (DataFrame, metadata_dict)
    """
    try:
        # Read the file
        df = pd.read_csv(uploaded_file)
        
        # Extract metadata
        metadata = {
            'file_type': 'StatSport',
            'player_id': df['Player Id'].iloc[0] if 'Player Id' in df.columns else 'Unknown',
            'player_name': df['Player Display Name'].iloc[0] if 'Player Display Name' in df.columns else 'Unknown',
            'total_records': len(df),
            'duration_minutes': df['Elapsed Time (s)'].max() / 60 if 'Elapsed Time (s)' in df.columns else 0,
            'analysis_id': f"SS_{df['Player Id'].iloc[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}" if 'Player Id' in df.columns else f"SS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        # Rename columns to standard format (handle variations in column names)
        column_mapping = {
            'Time': 'Timestamp',
            'Elapsed Time (s)': 'Seconds',
            '  Speed m/s': 'Velocity',  # StatSport format with two leading spaces
            ' Speed m/s': 'Velocity',   # StatSport format with one leading space
            'Speed m/s': 'Velocity',    # Alternative format
            'Speed': 'Velocity',        # Generic speed column
            'Lat': 'Latitude',
            'Lon': 'Longitude'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Ensure required columns exist
        if 'Velocity' not in df.columns:
            st.error("Velocity/Speed column not found in StatSport file")
            st.error(f"Available columns: {list(df.columns)}")
            return None, None
            
        return df, metadata
        
    except Exception as e:
        st.error(f"Error reading StatSport file: {str(e)}")
        return None, None


def read_catapult_file(uploaded_file) -> Tuple[Optional[pd.DataFrame], Optional[Dict]]:
    """
    Read Catapult format CSV file
    
    Args:
        uploaded_file: Streamlit uploaded file
        
    Returns:
        Tuple of (DataFrame, metadata_dict)
    """
    try:
        # Read metadata headers first
        content = uploaded_file.read().decode('utf-8')
        lines = content.split('\n')
        
        metadata = {
            'file_type': 'Catapult',
            'player_name': 'Unknown',
            'date': 'Unknown',
            'device_id': 'Unknown',
            'period': 'Unknown',
            'total_records': 0
        }
        
        # Extract metadata from # lines
        for line in lines[:8]:  # First 8 lines of metadata
            if line.startswith('#'):
                if 'Athlete:' in line:
                    metadata['player_name'] = line.split('"')[1] if '"' in line else line.split(':')[1].strip()
                elif 'Reference time:' in line:
                    metadata['date'] = line.split(':')[1].strip()
                elif 'DeviceId:' in line:
                    metadata['device_id'] = line.split(':')[1].strip()
                elif 'Period:' in line:
                    metadata['period'] = line.split('"')[1] if '"' in line else line.split(':')[1].strip()
        
        # Find data start (look for Timestamp header, typically after 8 lines of metadata)
        data_start = 0
        for i, line in enumerate(lines):
            if 'Timestamp' in line and ',' in line:
                data_start = i
                break
        
        # If Timestamp header not found, assume data starts after 8 lines of metadata
        if data_start == 0:
            data_start = 8
        
        # Read data portion with more flexible CSV parsing
        data_content = '\n'.join(lines[data_start:])
        from io import StringIO
        
        # Try different CSV parsing approaches
        try:
            # First try: standard parsing
            df = pd.read_csv(StringIO(data_content), quotechar='"', escapechar='\\')
        except:
            try:
                # Second try: with different quote handling
                df = pd.read_csv(StringIO(data_content), quotechar='"', escapechar='\\', quoting=3)
            except:
                # Third try: with error handling
                df = pd.read_csv(StringIO(data_content), quotechar='"', escapechar='\\', on_bad_lines='skip')
        
        metadata['total_records'] = len(df)
        metadata['duration_minutes'] = df['Seconds'].max() / 60 if 'Seconds' in df.columns else 0
        metadata['analysis_id'] = f"CP_{metadata['player_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return df, metadata
        
    except Exception as e:
        st.error(f"Error reading Catapult file: {str(e)}")
        return None, None


def read_csv_with_metadata(uploaded_file) -> Tuple[Optional[pd.DataFrame], Optional[Dict], Optional[Dict]]:
    """
    Universal CSV reader with format detection
    
    Args:
        uploaded_file: Streamlit uploaded file
        
    Returns:
        Tuple of (DataFrame, metadata_dict, file_type_info)
    """
    try:
        # Read first few lines for format detection
        content = uploaded_file.read().decode('utf-8')
        lines = content.split('\n')[:10]
        
        # Detect file format
        file_type_info = detect_file_format(lines)
        
        # Reset file pointer
        uploaded_file.seek(0)
        
        # Read based on detected format
        if file_type_info['type'] == 'statsport':
            df, metadata = read_statsport_file(uploaded_file)
        elif file_type_info['type'] in ['catapult', 'catapult_export']:
            df, metadata = read_catapult_file(uploaded_file)
        else:
            # Generic CSV reader
            df = pd.read_csv(uploaded_file)
            metadata = {
                'file_type': 'Generic GPS',
                'player_name': 'Unknown',
                'total_records': len(df),
                'analysis_id': f"GPS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        
        return df, metadata, file_type_info
        
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None, None, None


def validate_velocity_data(df: pd.DataFrame) -> bool:
    """
    Validate velocity data quality
    
    Args:
        df: DataFrame with velocity data
        
    Returns:
        True if data is valid, False otherwise
    """
    try:
        if 'Velocity' not in df.columns:
            return False
        
        # Check for numerical data
        if not pd.api.types.is_numeric_dtype(df['Velocity']):
            return False
        
        # Check for reasonable velocity range (0-20 m/s for human movement)
        velocity_range = df['Velocity'].describe()
        if velocity_range['max'] > 20 or velocity_range['min'] < 0:
            st.warning("Velocity data contains values outside expected range (0-20 m/s)")
        
        # Check for missing data
        missing_count = df['Velocity'].isna().sum()
        if missing_count > 0:
            st.warning(f"Found {missing_count} missing velocity values")
        
        return True
        
    except Exception as e:
        st.error(f"Error validating velocity data: {str(e)}")
        return False 