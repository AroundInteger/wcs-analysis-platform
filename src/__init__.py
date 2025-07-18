"""
WCS Analysis Platform - Source Package
"""

__version__ = "1.0.0"
__author__ = "WCS Analysis Team"
__email__ = "support@wcs-analysis.com"

from .file_ingestion import read_csv_with_metadata
from .wcs_analysis import perform_wcs_analysis
from .visualization import create_velocity_visualization

__all__ = [
    'read_csv_with_metadata',
    'perform_wcs_analysis', 
    'create_velocity_visualization'
] 