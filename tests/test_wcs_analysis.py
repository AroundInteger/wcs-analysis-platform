"""
Unit tests for WCS Analysis functions
Tests individual functions in isolation with known inputs and expected outputs
"""

import pytest
import numpy as np
import pandas as pd
from src.wcs_analysis import (
    calculate_wcs_period_rolling,
    calculate_wcs_period_contiguous,
    calculate_kinematic_parameters,
    perform_wcs_analysis
)

class TestWCSAnalysis:
    """Test suite for WCS analysis functions"""
    
    def setup_method(self):
        """Set up test data before each test"""
        # Create a simple test signal: 60 seconds at 10Hz = 600 samples
        self.time_data = np.arange(0, 60, 0.1)  # 0 to 60s, 0.1s intervals
        self.velocity_data = np.ones(600) * 5.0  # Constant 5 m/s
        
        # Add a peak in the middle
        peak_start = 300  # 30 seconds in
        peak_end = 400    # 40 seconds in
        self.velocity_data[peak_start:peak_end] = 8.0  # Peak at 8 m/s
        
        # Create DataFrame
        self.df = pd.DataFrame({
            'Time': self.time_data,
            'Velocity': self.velocity_data
        })
    
    def test_calculate_wcs_period_rolling_basic(self):
        """Test rolling WCS with simple constant velocity"""
        # Test with 10-second epoch, no thresholding
        epoch_duration = 10.0  # 10 seconds
        threshold_min = 0.0
        threshold_max = 100.0
        
        result = calculate_wcs_period_rolling(
            self.velocity_data, 
            self.time_data, 
            epoch_duration, 
            threshold_min, 
            threshold_max
        )
        
        # Expected: 10 seconds * 5 m/s = 50 meters
        expected_distance = 50.0
        
        assert result['distance'] == pytest.approx(expected_distance, rel=1e-2)
        assert result['start_time'] >= 0
        assert result['end_time'] <= 60
        assert result['duration'] == pytest.approx(epoch_duration, rel=1e-2)
    
    def test_calculate_wcs_period_rolling_with_threshold(self):
        """Test rolling WCS with velocity thresholding"""
        # Test with 10-second epoch, threshold 6-10 m/s
        epoch_duration = 10.0
        threshold_min = 6.0
        threshold_max = 10.0
        
        result = calculate_wcs_period_rolling(
            self.velocity_data, 
            self.time_data, 
            epoch_duration, 
            threshold_min, 
            threshold_max
        )
        
        # Should find the peak period (30-40s) where velocity is 8 m/s
        # Expected: 10 seconds * 8 m/s = 80 meters
        expected_distance = 80.0
        
        assert result['distance'] == pytest.approx(expected_distance, rel=1e-2)
        assert 25 <= result['start_time'] <= 35  # Should be around the peak
        assert 35 <= result['end_time'] <= 45
    
    def test_calculate_wcs_period_contiguous_basic(self):
        """Test contiguous WCS with simple constant velocity"""
        epoch_duration = 10.0
        threshold_min = 0.0
        threshold_max = 100.0
        
        result = calculate_wcs_period_contiguous(
            self.velocity_data, 
            self.time_data, 
            epoch_duration, 
            threshold_min, 
            threshold_max
        )
        
        # Expected: 10 seconds * 5 m/s = 50 meters
        expected_distance = 50.0
        
        assert result['distance'] == pytest.approx(expected_distance, rel=1e-2)
        assert result['duration'] == pytest.approx(epoch_duration, rel=1e-2)
    
    def test_calculate_wcs_period_contiguous_with_threshold(self):
        """Test contiguous WCS with velocity thresholding"""
        epoch_duration = 10.0
        threshold_min = 6.0
        threshold_max = 10.0
        
        result = calculate_wcs_period_contiguous(
            self.velocity_data, 
            self.time_data, 
            epoch_duration, 
            threshold_min, 
            threshold_max
        )
        
        # Should find the peak period where velocity is 8 m/s
        expected_distance = 80.0
        
        assert result['distance'] == pytest.approx(expected_distance, rel=1e-2)
        assert result['duration'] == pytest.approx(epoch_duration, rel=1e-2)
    
    def test_kinematic_parameters_calculation(self):
        """Test kinematic parameters calculation"""
        # Create velocity data with known acceleration
        time_data = np.arange(0, 10, 0.1)  # 10 seconds, 0.1s intervals
        velocity_data = 2.0 * time_data  # Linear increase: v = 2t, so a = 2 m/s²
        
        result = calculate_kinematic_parameters(velocity_data, time_data)
        
        # Check acceleration (should be constant 2 m/s²)
        assert np.mean(result['acceleration']) == pytest.approx(2.0, rel=1e-1)
        
        # Check distance (integral of velocity: ∫2t dt = t²)
        expected_distance = 100.0  # At t=10s: 10² = 100m
        assert result['distance'][-1] == pytest.approx(expected_distance, rel=1e-1)
        
        # Check power (P = |a| * v)
        expected_power = 2.0 * velocity_data  # |2| * v
        assert np.allclose(result['power'], expected_power, rtol=1e-1)
    
    def test_perform_wcs_analysis_integration(self):
        """Test the full WCS analysis pipeline"""
        epoch_durations = [5.0, 10.0]
        thresholds = [
            {'min': 0.0, 'max': 100.0, 'name': 'Default Threshold'},
            {'min': 6.0, 'max': 10.0, 'name': 'Threshold 1'}
        ]
        
        result = perform_wcs_analysis(
            self.df, 
            epoch_durations, 
            thresholds
        )
        
        # Check structure
        assert 'rolling_wcs' in result
        assert 'contiguous_wcs' in result
        assert 'kinematic_params' in result
        assert 'kinematic_stats' in result
        
        # Check rolling WCS results
        rolling = result['rolling_wcs']
        assert len(rolling) == len(epoch_durations) * len(thresholds)
        
        # Check contiguous WCS results
        contiguous = result['contiguous_wcs']
        assert len(contiguous) == len(epoch_durations) * len(thresholds)
        
        # Check kinematic parameters
        kinematic = result['kinematic_params']
        assert 'Acceleration' in kinematic.columns
        assert 'Distance' in kinematic.columns
        assert 'Power' in kinematic.columns
    
    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        # Test with very short signal
        short_time = np.array([0, 0.1, 0.2])
        short_velocity = np.array([5.0, 5.0, 5.0])
        
        # Should handle gracefully
        result = calculate_wcs_period_rolling(
            short_velocity, 
            short_time, 
            1.0,  # 1 second epoch
            0.0, 
            100.0
        )
        
        assert result['distance'] >= 0
        assert result['duration'] <= 0.3  # Should not exceed signal length
    
    def test_performance_benchmark(self):
        """Test performance with larger dataset"""
        # Create larger dataset: 10 minutes at 10Hz = 6000 samples
        large_time = np.arange(0, 600, 0.1)
        large_velocity = np.random.normal(5.0, 1.0, 6000)  # Random velocity
        
        import time
        start_time = time.time()
        
        result = calculate_wcs_period_rolling(
            large_velocity, 
            large_time, 
            30.0,  # 30 second epoch
            0.0, 
            100.0
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete within reasonable time (< 1 second)
        assert processing_time < 1.0
        assert result['distance'] >= 0

class TestDataValidation:
    """Test data validation and error handling"""
    
    def test_invalid_inputs(self):
        """Test handling of invalid inputs"""
        # Test with mismatched array lengths
        time_data = np.arange(0, 10, 0.1)
        velocity_data = np.ones(50)  # Wrong length
        
        with pytest.raises(ValueError):
            calculate_wcs_period_rolling(
                velocity_data, 
                time_data, 
                5.0, 
                0.0, 
                100.0
            )
    
    def test_invalid_thresholds(self):
        """Test handling of invalid threshold values"""
        time_data = np.arange(0, 10, 0.1)
        velocity_data = np.ones(100)
        
        # Test with min > max
        with pytest.raises(ValueError):
            calculate_wcs_period_rolling(
                velocity_data, 
                time_data, 
                5.0, 
                10.0,  # min
                5.0    # max (less than min)
            )
    
    def test_empty_data(self):
        """Test handling of empty data"""
        empty_time = np.array([])
        empty_velocity = np.array([])
        
        with pytest.raises(ValueError):
            calculate_wcs_period_rolling(
                empty_velocity, 
                empty_time, 
                5.0, 
                0.0, 
                100.0
            )

if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"]) 