"""
Test file for file ingestion module
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from io import StringIO

# Import the module to test
import sys
sys.path.append('src')
from file_ingestion import (
    detect_file_format,
    read_statsport_file,
    read_catapult_file,
    read_csv_with_metadata,
    validate_velocity_data
)


class TestFileIngestion:
    """Test cases for file ingestion functionality"""
    
    def test_detect_statsport_format(self):
        """Test StatSport format detection"""
        content_lines = [
            "Player Id,Player Display Name,Time,  Speed m/s",
            "12345,John Doe,00:00:01,2.5",
            "12345,John Doe,00:00:02,3.1"
        ]
        
        result = detect_file_format(content_lines)
        assert result['type'] == 'statsport'
        assert result['confidence'] > 0.8
    
    def test_detect_catapult_format(self):
        """Test Catapult format detection"""
        content_lines = [
            "# OpenField Export",
            "# Athlete: John Doe",
            "# DeviceId: 12345",
            "# Period: Match 1",
            "Timestamp,Velocity,Latitude,Longitude",
            "00:00:01,2.5,51.5074,-0.1278",
            "00:00:02,3.1,51.5075,-0.1279"
        ]
        
        result = detect_file_format(content_lines)
        assert result['type'] in ['catapult', 'catapult_export']
        assert result['confidence'] > 0.8
    
    def test_detect_generic_format(self):
        """Test generic GPS format detection"""
        content_lines = [
            "Timestamp,Velocity,Latitude,Longitude",
            "00:00:01,2.5,51.5074,-0.1278",
            "00:00:02,3.1,51.5075,-0.1279"
        ]
        
        result = detect_file_format(content_lines)
        assert result['type'] == 'generic_gps'
        assert result['confidence'] > 0.6
    
    def test_validate_velocity_data_valid(self):
        """Test velocity data validation with valid data"""
        df = pd.DataFrame({
            'Velocity': [1.0, 2.0, 3.0, 4.0, 5.0],
            'Seconds': [0, 1, 2, 3, 4]
        })
        
        assert validate_velocity_data(df) == True
    
    def test_validate_velocity_data_missing_column(self):
        """Test velocity data validation with missing velocity column"""
        df = pd.DataFrame({
            'Speed': [1.0, 2.0, 3.0, 4.0, 5.0],
            'Seconds': [0, 1, 2, 3, 4]
        })
        
        assert validate_velocity_data(df) == False
    
    def test_validate_velocity_data_non_numeric(self):
        """Test velocity data validation with non-numeric data"""
        df = pd.DataFrame({
            'Velocity': ['a', 'b', 'c', 'd', 'e'],
            'Seconds': [0, 1, 2, 3, 4]
        })
        
        assert validate_velocity_data(df) == False
    
    def test_validate_velocity_data_out_of_range(self):
        """Test velocity data validation with out-of-range values"""
        df = pd.DataFrame({
            'Velocity': [25.0, 30.0, 35.0],  # Unrealistic for human movement
            'Seconds': [0, 1, 2]
        })
        
        # Should still return True but with warning
        assert validate_velocity_data(df) == True


class TestFileReading:
    """Test cases for file reading functionality"""
    
    def create_temp_csv(self, content):
        """Helper method to create temporary CSV file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    def test_read_statsport_file(self):
        """Test reading StatSport format file"""
        content = """Player Id,Player Display Name,Time,  Speed m/s,Elapsed Time (s)
12345,John Doe,00:00:01,2.5,1
12345,John Doe,00:00:02,3.1,2
12345,John Doe,00:00:03,1.8,3"""
        
        temp_file = self.create_temp_csv(content)
        
        try:
            # Create a mock uploaded file
            class MockUploadedFile:
                def __init__(self, file_path):
                    self.file_path = file_path
                    self.name = os.path.basename(file_path)
                
                def read(self):
                    with open(self.file_path, 'r') as f:
                        return f.read().encode('utf-8')
                
                def seek(self, pos):
                    pass
            
            mock_file = MockUploadedFile(temp_file)
            df, metadata = read_statsport_file(mock_file)
            
            assert df is not None
            assert metadata is not None
            assert 'Velocity' in df.columns
            assert metadata['file_type'] == 'StatSport'
            assert metadata['player_name'] == 'John Doe'
            
        finally:
            os.unlink(temp_file)
    
    def test_read_catapult_file(self):
        """Test reading Catapult format file"""
        content = """# OpenField Export
# Athlete: John Doe
# DeviceId: 12345
# Period: Match 1
# Reference time: 2023-01-01 12:00:00
# 
# 
Timestamp,Velocity,Latitude,Longitude,Seconds
00:00:01,2.5,51.5074,-0.1278,1
00:00:02,3.1,51.5075,-0.1279,2
00:00:03,1.8,51.5076,-0.1280,3"""
        
        temp_file = self.create_temp_csv(content)
        
        try:
            # Create a mock uploaded file
            class MockUploadedFile:
                def __init__(self, file_path):
                    self.file_path = file_path
                    self.name = os.path.basename(file_path)
                
                def read(self):
                    with open(self.file_path, 'r') as f:
                        return f.read().encode('utf-8')
                
                def seek(self, pos):
                    pass
            
            mock_file = MockUploadedFile(temp_file)
            df, metadata = read_catapult_file(mock_file)
            
            assert df is not None
            assert metadata is not None
            assert 'Velocity' in df.columns
            assert metadata['file_type'] == 'Catapult'
            assert metadata['player_name'] == 'John Doe'
            
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 