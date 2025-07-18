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
    # Check for StatSport format with leading spaces
    if any('Player Id' in line and ' Player Display Name' in line for line in content_lines[:3]):
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
        uploaded_file: Streamlit uploaded file or StringIO object
        
    Returns:
        Tuple of (DataFrame, metadata_dict)
    """
    try:
        # Read the file
        df = pd.read_csv(uploaded_file)
        
        # Debug: Show columns found
        st.write(f"📊 Found columns: {list(df.columns)}")
        
        # Extract metadata
        metadata = {
            'file_type': 'StatSport',
            'player_id': df['Player Id'].iloc[0] if 'Player Id' in df.columns else 'Unknown',
            'player_name': df[' Player Display Name'].iloc[0] if ' Player Display Name' in df.columns else 'Unknown',
            'total_records': len(df),
            'duration_minutes': df[' Elapsed Time (s)'].max() / 60 if ' Elapsed Time (s)' in df.columns else 0,
            'analysis_id': f"SS_{df['Player Id'].iloc[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}" if 'Player Id' in df.columns else f"SS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        # Rename columns to standard format (handle variations in column names)
        column_mapping = {
            ' Time': 'Timestamp',
            ' Elapsed Time (s)': 'Seconds',
            '  Speed m/s': 'Velocity',  # StatSport format with two leading spaces
            ' Speed m/s': 'Velocity',   # StatSport format with one leading space
            'Speed m/s': 'Velocity',    # Alternative format
            'Speed': 'Velocity',        # Generic speed column
            ' Lat': 'Latitude',
            ' Lon': 'Longitude'
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
        uploaded_file: Streamlit uploaded file or StringIO object
        
    Returns:
        Tuple of (DataFrame, metadata_dict)
    """
    try:
        # Read metadata headers first
        if hasattr(uploaded_file, 'read'):
            # File object - read content
            content = uploaded_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
        else:
            # StringIO object - get value
            content = uploaded_file.getvalue()
        
        lines = content.split('\n')
        
        metadata = {
            'file_type': 'Catapult',
            'player_name': 'Unknown',
            'date': 'Unknown',
            'device_id': 'Unknown',
            'period': 'Unknown',
            'total_records': 0
        }
        
        # Extract metadata from # lines (including quoted # lines)
        for line in lines[:10]:  # Check first 10 lines for metadata
            if line.startswith('#') or line.startswith('"#'):
                if 'Athlete:' in line:
                    # Handle both quoted and unquoted formats
                    if '"' in line:
                        # Extract from quoted format: '"# Athlete: ""Ramsey"""'
                        # Remove the leading quote and split by quotes
                        clean_line = line.strip('"')
                        parts = clean_line.split('"')
                        if len(parts) >= 3:
                            # Find the first non-empty part after the colon
                            for part in parts:
                                if part and part != '# Athlete: ' and part != '\n':
                                    metadata['player_name'] = part
                                    break
                    else:
                        # Handle unquoted format: "# Athlete: Name"
                        metadata['player_name'] = line.split('Athlete:')[1].strip()
                elif 'Reference time:' in line:
                    # Handle format: "# Reference time : 2024-09-09"
                    metadata['date'] = line.split('Reference time :')[1].strip()
                elif 'DeviceId:' in line:
                    # Handle format: "# DeviceId : 257583"
                    metadata['device_id'] = line.split('DeviceId :')[1].strip()
                elif 'Period:' in line:
                    # Handle both quoted and unquoted formats
                    if '"' in line:
                        # Extract from quoted format: '"# Period: ""Raw Data 09.09.24 MD vs Montenegro"""'
                        # Remove the leading quote and split by quotes
                        clean_line = line.strip('"')
                        parts = clean_line.split('"')
                        if len(parts) >= 3:
                            # Find the first non-empty part after the colon
                            for part in parts:
                                if part and part != '# Period: ' and part != '\n':
                                    metadata['period'] = part
                                    break
                    else:
                        # Handle unquoted format: "# Period: Name"
                        metadata['period'] = line.split('Period:')[1].strip()
        
        # Find data start (look for Timestamp header)
        data_start = 0
        for i, line in enumerate(lines):
            if 'Timestamp' in line and ',' in line and not line.startswith('#'):
                data_start = i
                break
        
        # If Timestamp header not found, assume data starts after metadata
        if data_start == 0:
            # Find the first non-metadata line
            for i, line in enumerate(lines):
                if not line.startswith('#') and ',' in line:
                    data_start = i
                    break
        
        # Read data portion with proper CSV parsing
        data_content = '\n'.join(lines[data_start:])
        from io import StringIO
        
        # Debug: Show data content preview
        st.write(f"📊 Data content preview (first 3 lines):")
        data_lines = data_content.split('\n')
        for i, line in enumerate(data_lines[:3]):
            st.write(f"  Line {i+1}: {repr(line)}")
        
        # Use pandas with proper error handling
        try:
            df = pd.read_csv(StringIO(data_content), on_bad_lines='skip')
        except Exception as csv_error:
            st.error(f"CSV parsing error: {str(csv_error)}")
            # Try alternative parsing
            try:
                df = pd.read_csv(StringIO(data_content), on_bad_lines='skip', engine='python')
            except Exception as alt_error:
                st.error(f"Alternative parsing also failed: {str(alt_error)}")
                return None, None
        
        metadata['total_records'] = len(df)
        metadata['duration_minutes'] = df['Seconds'].max() / 60 if 'Seconds' in df.columns else 0
        metadata['analysis_id'] = f"CP_{metadata['player_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return df, metadata
        
    except Exception as e:
        st.error(f"Error reading Catapult file: {str(e)}")
        return None, None


def read_catapult_file_from_path(file_path: str) -> Tuple[Optional[pd.DataFrame], Optional[Dict]]:
    """
    Read Catapult format CSV file from file path
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Tuple of (DataFrame, metadata_dict)
    """
    try:
        # Read metadata headers first
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.split('\n')
        
        metadata = {
            'file_type': 'Catapult',
            'player_name': 'Unknown',
            'date': 'Unknown',
            'device_id': 'Unknown',
            'period': 'Unknown',
            'total_records': 0
        }
        
        # Extract metadata from # lines (including quoted # lines)
        for line in lines[:10]:  # Check first 10 lines for metadata
            if line.startswith('#') or line.startswith('"#'):
                if 'Athlete:' in line:
                    # Handle both quoted and unquoted formats
                    if '"' in line:
                        # Extract from quoted format: '"# Athlete: ""Ramsey"""'
                        # Remove the leading quote and split by quotes
                        clean_line = line.strip('"')
                        parts = clean_line.split('"')
                        if len(parts) >= 3:
                            # Find the first non-empty part after the colon
                            for part in parts:
                                if part and part != '# Athlete: ' and part != '\n':
                                    metadata['player_name'] = part
                                    break
                    else:
                        # Handle unquoted format: "# Athlete: Name"
                        metadata['player_name'] = line.split('Athlete:')[1].strip()
                elif 'Reference time:' in line:
                    # Handle format: "# Reference time : 2024-09-09"
                    metadata['date'] = line.split('Reference time :')[1].strip()
                elif 'DeviceId:' in line:
                    # Handle format: "# DeviceId : 257583"
                    metadata['device_id'] = line.split('DeviceId :')[1].strip()
                elif 'Period:' in line:
                    # Handle both quoted and unquoted formats
                    if '"' in line:
                        # Extract from quoted format: '"# Period: ""Raw Data 09.09.24 MD vs Montenegro"""'
                        # Remove the leading quote and split by quotes
                        clean_line = line.strip('"')
                        parts = clean_line.split('"')
                        if len(parts) >= 3:
                            # Find the first non-empty part after the colon
                            for part in parts:
                                if part and part != '# Period: ' and part != '\n':
                                    metadata['period'] = part
                                    break
                    else:
                        # Handle unquoted format: "# Period: Name"
                        metadata['period'] = line.split('Period:')[1].strip()
        
        # Find data start (look for Timestamp header)
        data_start = 0
        for i, line in enumerate(lines):
            if 'Timestamp' in line and ',' in line and not line.startswith('#'):
                data_start = i
                break
        
        # If Timestamp header not found, assume data starts after metadata
        if data_start == 0:
            # Find the first non-metadata line
            for i, line in enumerate(lines):
                if not line.startswith('#') and ',' in line:
                    data_start = i
                    break
        
        # Read data portion with proper CSV parsing
        data_content = '\n'.join(lines[data_start:])
        from io import StringIO
        
        # Use pandas with proper error handling
        try:
            df = pd.read_csv(StringIO(data_content), on_bad_lines='skip')
        except Exception as csv_error:
            st.error(f"CSV parsing error: {str(csv_error)}")
            # Try alternative parsing
            try:
                df = pd.read_csv(StringIO(data_content), on_bad_lines='skip', engine='python')
            except Exception as alt_error:
                st.error(f"Alternative parsing also failed: {str(alt_error)}")
                return None, None
        
        metadata['total_records'] = len(df)
        metadata['duration_minutes'] = df['Seconds'].max() / 60 if 'Seconds' in df.columns else 0
        metadata['analysis_id'] = f"CP_{metadata['player_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return df, metadata
        
    except Exception as e:
        st.error(f"Error reading Catapult file from path: {str(e)}")
        return None, None


def read_csv_with_metadata(uploaded_file) -> Tuple[Optional[pd.DataFrame], Optional[Dict], Optional[Dict]]:
    """
    Universal CSV reader with format detection
    
    Args:
        uploaded_file: Streamlit uploaded file or file path string
        
    Returns:
        Tuple of (DataFrame, metadata_dict, file_type_info)
    """
    try:
        # Handle both file objects and file paths
        if isinstance(uploaded_file, str):
            # File path - read from file
            with open(uploaded_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            # File object - read directly
            content = uploaded_file.read().decode('utf-8')
        
        # Debug: Show first few lines of content
        lines = content.split('\n')
        st.write(f"📄 File content preview (first 5 lines):")
        for i, line in enumerate(lines[:5]):
            st.write(f"  Line {i+1}: {repr(line)}")
        
        # Check if content is empty
        if not content.strip():
            st.error("File appears to be empty")
            return None, None, None
        
        # Detect file format using first 10 lines
        file_type_info = detect_file_format(lines[:10])
        st.write(f"🔍 Detected format: {file_type_info}")
        
        # Read based on detected format
        if file_type_info['type'] == 'statsport':
            if isinstance(uploaded_file, str):
                # File path - read with pandas directly
                df = pd.read_csv(uploaded_file)
                metadata = {
                    'file_type': 'StatSport',
                    'player_id': df['Player Id'].iloc[0] if 'Player Id' in df.columns else 'Unknown',
                    'player_name': df[' Player Display Name'].iloc[0] if ' Player Display Name' in df.columns else 'Unknown',
                    'total_records': len(df),
                    'duration_minutes': df[' Elapsed Time (s)'].max() / 60 if ' Elapsed Time (s)' in df.columns else 0,
                    'analysis_id': f"SS_{df['Player Id'].iloc[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}" if 'Player Id' in df.columns else f"SS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
                
                # Rename columns to standard format
                column_mapping = {
                    ' Time': 'Timestamp',
                    ' Elapsed Time (s)': 'Seconds',
                    '  Speed m/s': 'Velocity',  # StatSport format with two leading spaces
                    ' Speed m/s': 'Velocity',   # StatSport format with one leading space
                    'Speed m/s': 'Velocity',    # Alternative format
                    'Speed': 'Velocity',        # Generic speed column
                    ' Lat': 'Latitude',
                    ' Lon': 'Longitude'
                }
                df = df.rename(columns=column_mapping)
            else:
                # File object - use StringIO to recreate file-like object
                from io import StringIO
                file_like = StringIO(content)
                df, metadata = read_statsport_file(file_like)
        elif file_type_info['type'] in ['catapult', 'catapult_export']:
            if isinstance(uploaded_file, str):
                # File path - read with pandas and handle metadata
                df, metadata = read_catapult_file_from_path(uploaded_file)
            else:
                # File object - use StringIO to recreate file-like object
                from io import StringIO
                file_like = StringIO(content)
                df, metadata = read_catapult_file(file_like)
        else:
            # Generic CSV reader
            if isinstance(uploaded_file, str):
                df = pd.read_csv(uploaded_file)
            else:
                # Use StringIO to recreate file-like object
                from io import StringIO
                file_like = StringIO(content)
                df = pd.read_csv(file_like)
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