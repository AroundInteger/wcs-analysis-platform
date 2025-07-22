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
import re
import os


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
                # Check for units in metadata (row 5 typically contains units info)
                elif 'Speed Units' in line and 'Kilometers' in line:
                    metadata['velocity_units'] = 'km/hr'
                elif 'Speed Units' in line and 'Meters' in line:
                    metadata['velocity_units'] = 'm/s'
        
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
        
        # Debug: Show data content preview (only if needed)
        # st.write(f"📊 Data content preview (first 3 lines):")
        # data_lines = data_content.split('\n')
        # for i, line in enumerate(data_lines[:3]):
        #     st.write(f"  Line {i+1}: {repr(line)}")
        
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
        
        # Convert velocity units if needed (km/hr to m/s)
        if 'Velocity' in df.columns and metadata.get('velocity_units') == 'km/hr':
            # Convert km/hr to m/s: multiply by 5/18 (same as MATLAB)
            df['Velocity_kmphr'] = df['Velocity']  # Store original values
            df['Velocity'] = df['Velocity'] * 5/18  # Convert to m/s
            metadata['velocity_converted'] = True
            metadata['original_units'] = 'km/hr'
            metadata['converted_units'] = 'm/s'
            st.info(f"🔄 Converted velocity from km/hr to m/s (multiplied by 5/18)")
        
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
                # Check for units in metadata (row 5 typically contains units info)
                elif 'Speed Units' in line and 'Kilometers' in line:
                    metadata['velocity_units'] = 'km/hr'
                elif 'Speed Units' in line and 'Meters' in line:
                    metadata['velocity_units'] = 'm/s'
        
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
        
        # Convert velocity units if needed (km/hr to m/s)
        if 'Velocity' in df.columns and metadata.get('velocity_units') == 'km/hr':
            # Convert km/hr to m/s: multiply by 5/18 (same as MATLAB)
            df['Velocity_kmphr'] = df['Velocity']  # Store original values
            df['Velocity'] = df['Velocity'] * 5/18  # Convert to m/s
            metadata['velocity_converted'] = True
            metadata['original_units'] = 'km/hr'
            metadata['converted_units'] = 'm/s'
            st.info(f"🔄 Converted velocity from km/hr to m/s (multiplied by 5/18)")
        
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
        
        # Check if content is empty
        if not content.strip():
            st.error("File appears to be empty")
            return None, None, None
        
        # Detect file format using first 10 lines
        lines = content.split('\n')
        file_type_info = detect_file_format(lines[:10])
        
        # Extract filename for player info parsing
        if isinstance(uploaded_file, str):
            filename = os.path.basename(uploaded_file)
        else:
            filename = uploaded_file.name if hasattr(uploaded_file, 'name') else 'unknown.csv'
        
        # Extract player information from filename
        filename_info = extract_player_info_from_filename(filename)
        
        # Show filename parsing results
        if filename_info['filename_pattern'] != 'unknown' and filename_info['filename_pattern'] != 'error':
            st.success(f"✅ Parsed filename: {filename_info['player_name']} ({filename_info['position']}) - {filename_info['competition']} {filename_info['matchday']}")
        elif filename_info['filename_pattern'] == 'error':
            st.warning(f"⚠️ Could not parse filename: {filename}")
        else:
            st.info(f"📄 Using filename as player name: {filename_info['player_name']}")
        
        # Read based on detected format
        if file_type_info['type'] == 'statsport':
            if isinstance(uploaded_file, str):
                # File path - read with pandas directly
                df = pd.read_csv(uploaded_file)
                
                # Get player name from file data or fallback to filename
                file_player_name = df[' Player Display Name'].iloc[0] if ' Player Display Name' in df.columns else None
                # Use filename-derived player name if it's more specific (not just initials)
                if filename_info['filename_pattern'] != 'unknown' and filename_info['player_name'] != 'unknown.csv':
                    player_name = filename_info['player_name']
                else:
                    player_name = file_player_name if file_player_name and file_player_name != 'Unknown' else 'Unknown'
                
                metadata = {
                    'file_type': 'StatSport',
                    'player_id': df['Player Id'].iloc[0] if 'Player Id' in df.columns else 'Unknown',
                    'player_name': player_name,
                    'total_records': len(df),
                    'duration_minutes': df[' Elapsed Time (s)'].max() / 60 if ' Elapsed Time (s)' in df.columns else 0,
                    'analysis_id': f"SS_{df['Player Id'].iloc[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}" if 'Player Id' in df.columns else f"SS_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    # Add filename-derived information
                    'position': filename_info['position'],
                    'initials': filename_info['initials'],
                    'competition': filename_info['competition'],
                    'matchday': filename_info['matchday'],
                    'filename_pattern': filename_info['filename_pattern']
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
                
                # Update metadata with filename information
                if metadata:
                    metadata.update({
                        'position': filename_info['position'],
                        'initials': filename_info['initials'],
                        'competition': filename_info['competition'],
                        'matchday': filename_info['matchday'],
                        'filename_pattern': filename_info['filename_pattern']
                    })
        elif file_type_info['type'] in ['catapult', 'catapult_export']:
            if isinstance(uploaded_file, str):
                # File path - read with pandas and handle metadata
                df, metadata = read_catapult_file_from_path(uploaded_file)
                
                # Update metadata with filename information
                if metadata:
                    # Use filename-derived player name if available and more specific than 'Unknown'
                    if filename_info['player_name'] != 'unknown.csv' and filename_info['player_name'] != 'Unknown':
                        metadata['player_name'] = filename_info['player_name']
                    
                    metadata.update({
                        'position': filename_info['position'],
                        'initials': filename_info['initials'],
                        'competition': filename_info['competition'],
                        'matchday': filename_info['matchday'],
                        'filename_pattern': filename_info['filename_pattern']
                    })
            else:
                # File object - use StringIO to recreate file-like object
                from io import StringIO
                file_like = StringIO(content)
                df, metadata = read_catapult_file(file_like)
                
                # Update metadata with filename information
                if metadata:
                    # Use filename-derived player name if available and more specific than 'Unknown'
                    if filename_info['player_name'] != 'unknown.csv' and filename_info['player_name'] != 'Unknown':
                        metadata['player_name'] = filename_info['player_name']
                    
                    metadata.update({
                        'position': filename_info['position'],
                        'initials': filename_info['initials'],
                        'competition': filename_info['competition'],
                        'matchday': filename_info['matchday'],
                        'filename_pattern': filename_info['filename_pattern']
                    })
        else:
            # Generic CSV reader
            if isinstance(uploaded_file, str):
                df = pd.read_csv(uploaded_file)
            else:
                # Use StringIO to recreate file-like object
                from io import StringIO
                file_like = StringIO(content)
                df = pd.read_csv(file_like)
            
            # Use filename-derived player name for generic files
            player_name = filename_info['player_name'] if filename_info['player_name'] != 'unknown.csv' else 'Unknown'
            
            metadata = {
                'file_type': 'Generic GPS',
                'player_name': player_name,
                'total_records': len(df),
                'analysis_id': f"GPS_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                # Add filename-derived information
                'position': filename_info['position'],
                'initials': filename_info['initials'],
                'competition': filename_info['competition'],
                'matchday': filename_info['matchday'],
                'filename_pattern': filename_info['filename_pattern']
            }
        
        # Show actual data content preview after processing
        if df is not None and not df.empty:
            st.write(f"📊 Processed data preview:")
            
            # Display basic info
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Columns:** {len(df.columns)}")
                st.write(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
            with col2:
                st.write(f"**File Type:** {file_type_info.get('format', 'Unknown')}")
                st.write(f"**Player:** {metadata.get('player_name', 'Unknown')}")
            
            # Display first 3 rows in a table
            st.write("**First 3 rows:**")
            preview_df = df.head(3).copy()
            
            # Format the data for better display
            for col in preview_df.columns:
                if preview_df[col].dtype in ['float64', 'float32']:
                    preview_df[col] = preview_df[col].round(2)
                elif preview_df[col].dtype in ['int64', 'int32']:
                    preview_df[col] = preview_df[col].astype(str)
            
            st.dataframe(preview_df, use_container_width=True)
        
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
        max_velocity = velocity_range['max']
        min_velocity = velocity_range['min']
        
        # Check if values are in km/hr range (0-72 km/hr) or m/s range (0-20 m/s)
        if max_velocity > 72:
            st.warning(f"Velocity data contains very high values (max: {max_velocity:.2f}). This might indicate units are in km/hr and need conversion.")
        elif max_velocity > 20 and max_velocity <= 72:
            st.info(f"Velocity data appears to be in km/hr range (max: {max_velocity:.2f}). Consider checking metadata for unit information.")
        elif max_velocity > 20:
            st.warning(f"Velocity data contains values outside expected range (0-20 m/s, max: {max_velocity:.2f})")
        
        if min_velocity < 0:
            st.warning(f"Velocity data contains negative values (min: {min_velocity:.2f})")
        
        # Check for missing data
        missing_count = df['Velocity'].isna().sum()
        if missing_count > 0:
            st.warning(f"Found {missing_count} missing velocity values")
        
        return True
        
    except Exception as e:
        st.error(f"Error validating velocity data: {str(e)}")
        return False 


def extract_player_info_from_filename(filename: str) -> Dict[str, str]:
    """
    Extract player information from filename following various patterns:
    
    Standard patterns:
    - position_initials_competition(matchday) -> BR_EC_18s(MD2).csv
    - initials_competition(matchday) -> JR_URC(MD4).csv
    - position_initials_competition -> FR_JR_URC.csv
    
    Catapult patterns:
    - Name_Date_Raw Data Date MD vs Opponent.csv -> Aaron Ramsey_2024-09-09_Raw Data 09.09.24 MD vs Montenegro.csv
    - Export for Name ID.csv -> 3A-NT-GP-LSG-10x10-70x60 Export for Michael Obafemi 22346.csv
    
    Args:
        filename: Filename to parse
        
    Returns:
        Dictionary with extracted player information
    """
    try:
        # Remove file extension
        name_without_ext = os.path.splitext(filename)[0]
        
        # Pattern 1: position_initials_competition(matchday) - e.g., BR_EC_18s(MD2).csv
        pattern1 = r'^([A-Z]+)_([A-Z]+)_([A-Za-z0-9]+)\(([A-Z0-9]+)\)$'
        match1 = re.match(pattern1, name_without_ext)
        
        if match1:
            position, initials, competition, matchday = match1.groups()
            return {
                'position': position,
                'initials': initials,
                'competition': competition,
                'matchday': matchday,
                'player_name': initials,  # Use initials as player name
                'filename_pattern': 'position_initials_competition(matchday)'
            }
        
        # Pattern 2: initials_competition(matchday) - e.g., JR_URC(MD4).csv
        pattern2 = r'^([A-Z]+)_([A-Za-z0-9]+)\(([A-Z0-9]+)\)$'
        match2 = re.match(pattern2, name_without_ext)
        
        if match2:
            initials, competition, matchday = match2.groups()
            return {
                'position': 'Unknown',
                'initials': initials,
                'competition': competition,
                'matchday': matchday,
                'player_name': initials,
                'filename_pattern': 'initials_competition(matchday)'
            }
        
        # Pattern 3: position_initials_competition - e.g., FR_JR_URC.csv
        pattern3 = r'^([A-Z]+)_([A-Z]+)_([A-Za-z0-9]+)$'
        match3 = re.match(pattern3, name_without_ext)
        
        if match3:
            position, initials, competition = match3.groups()
            return {
                'position': position,
                'initials': initials,
                'competition': competition,
                'matchday': 'Unknown',
                'player_name': initials,
                'filename_pattern': 'position_initials_competition'
            }
        
        # Pattern 4: Catapult format - Name_Date_Raw Data Date MD vs Opponent
        # e.g., Aaron Ramsey_2024-09-09_Raw Data 09.09.24 MD vs Montenegro.csv
        pattern4 = r'^([A-Za-z\s]+)_(\d{4}-\d{2}-\d{2})_Raw Data \d{2}\.\d{2}\.\d{2} MD vs ([A-Za-z\s]+)$'
        match4 = re.match(pattern4, name_without_ext)
        
        if match4:
            player_name, date, opponent = match4.groups()
            return {
                'position': 'Unknown',
                'initials': player_name.split()[0] if player_name else 'Unknown',
                'competition': opponent.strip(),
                'matchday': 'MD',
                'player_name': player_name.strip(),
                'filename_pattern': 'catapult_name_date_opponent'
            }
        
        # Pattern 5: Catapult export format with competition - COMPETITION Export for Name ID
        # e.g., HUNGARY (AWAY) MD1 Export for Alfie Cunningham 27993.csv
        pattern5 = r'^([A-Z\s\(\)0-9]+)\s+Export for ([A-Za-z\s]+) \d+$'
        match5 = re.match(pattern5, name_without_ext)
        
        if match5:
            competition, player_name = match5.groups()
            # Extract matchday from competition if present
            matchday = 'Unknown'
            if 'MD' in competition:
                md_match = re.search(r'MD(\d+)', competition)
                if md_match:
                    matchday = f"MD{md_match.group(1)}"
            
            return {
                'position': 'Unknown',
                'initials': player_name.split()[0] if player_name else 'Unknown',
                'competition': competition.strip(),
                'matchday': matchday,
                'player_name': player_name.strip(),
                'filename_pattern': 'catapult_export_competition_name'
            }
        
        # Pattern 6: Catapult export format - Export for Name ID (generic)
        # e.g., 3A-NT-GP-LSG-10x10-70x60 Export for Michael Obafemi 22346.csv
        pattern6 = r'^.*Export for ([A-Za-z\s]+) \d+$'
        match6 = re.match(pattern6, name_without_ext)
        
        if match6:
            player_name = match6.group(1)
            return {
                'position': 'Unknown',
                'initials': player_name.split()[0] if player_name else 'Unknown',
                'competition': 'Unknown',
                'matchday': 'Unknown',
                'player_name': player_name.strip(),
                'filename_pattern': 'catapult_export_name'
            }
        
        # If no pattern matches, return basic info
        return {
            'position': 'Unknown',
            'initials': 'Unknown',
            'competition': 'Unknown',
            'matchday': 'Unknown',
            'player_name': name_without_ext,
            'filename_pattern': 'unknown'
        }
        
    except Exception as e:
        st.warning(f"Could not parse filename '{filename}': {str(e)}")
        return {
            'position': 'Unknown',
            'initials': 'Unknown',
            'competition': 'Unknown',
            'matchday': 'Unknown',
            'player_name': filename,
            'filename_pattern': 'error'
        } 