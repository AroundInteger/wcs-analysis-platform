# Batch Processing System Guide

## Overview

The WCS Analysis Platform includes a robust batch processing system designed to handle multiple GPS data files efficiently. This system is optimized for the main usage scenario where users need to process multiple files simultaneously while maintaining high performance and providing comprehensive error handling.

## Features

### 🚀 Core Capabilities

- **Multi-File Processing**: Process multiple GPS data files in a single session
- **Smart Output Organization**: Automatic file organization with timestamped sessions
- **Error Handling**: Graceful handling of corrupted, empty, or invalid files
- **Performance Optimization**: Fast processing of large datasets (22K-1.6M records/second)
- **Multiple Export Formats**: Excel, CSV, JSON, and standard CSV exports
- **Combined Analysis**: Aggregate results across multiple files

### 📊 Supported File Types

- **StatSport**: Automatic detection of StatSport GPS data format
- **Catapult**: Support for Catapult GPS data files
- **Generic CSV**: Flexible handling of custom CSV formats
- **Mixed Formats**: Process different file types in the same batch

### 🛡️ Robustness Features

- **Data Validation**: Comprehensive velocity data validation
- **Error Recovery**: Continues processing despite individual file failures
- **Progress Tracking**: Real-time feedback on processing status
- **File Management**: Professional output organization and naming

## Usage

### Basic Batch Processing

1. **Select Input Method**: Choose "Select from Folder" for batch processing
2. **Navigate to Data Folder**: Use the enhanced folder navigation system
3. **Select Multiple Files**: Choose multiple CSV files for processing
4. **Configure Parameters**: Set WCS analysis parameters
5. **Run Analysis**: Execute batch processing
6. **Review Results**: Examine individual and combined results
7. **Export Data**: Save results in multiple formats

### Smart Output System

The batch processing system automatically organizes output files:

```
data/selected_folder/OUTPUT/YYYY-MM-DD_HH-MM-SS/
├── WCS_Analysis_YYYYMMDD_HHMMSS_checkPython.xlsx
├── WCS_Analysis_YYYYMMDD_HHMMSS_checkPython.csv
├── WCS_Analysis_Results_YYYYMMDD_HHMMSS.csv
└── README.txt
```

### Output Organization Rules

- **Folder Selection**: Output placed in `OUTPUT/` subfolder of selected directory
- **File Upload**: Output placed in project root `OUTPUT/` directory
- **Session Isolation**: Each batch session gets a unique timestamped folder
- **File Naming**: Consistent naming convention with timestamps

## Technical Details

### Performance Benchmarks

| File Type | Records | Read Time | Analysis Time | Total Time | Records/Second |
|-----------|---------|-----------|---------------|------------|----------------|
| StatSport | 6,000 | 0.003s | 0.265s | 0.268s | 22,401 |
| Catapult | 6,000 | 0.005s | 0.000s | 0.005s | 1,238,135 |
| Generic | 6,000 | 0.004s | 0.000s | 0.004s | 1,623,816 |
| Large File | 5,000 | ~0.004s | ~0.000s | ~0.004s | ~1,275,185 |

### Error Handling

The system handles various error scenarios gracefully:

- **Empty Files**: Skipped with clear warnings
- **Corrupted Files**: Handled without crashing
- **Missing Velocity Data**: Properly validated and skipped
- **Invalid Formats**: Clear error messages and graceful failures
- **Permission Errors**: User-friendly error messages

### File Type Detection

Automatic detection of GPS data formats:

#### StatSport Format
```
Columns: ['Time', 'Velocity', 'Latitude', 'Longitude']
Velocity Column: Velocity
```

#### Catapult Format
```
Columns: ['Time (s)', 'Velocity (m/s)', 'Latitude (deg)', 'Longitude (deg)']
Velocity Column: Velocity (m/s)
```

#### Generic Format
```
Columns: ['timestamp', 'speed', 'lat', 'lon']
Velocity Column: speed
```

## API Reference

### Core Functions

#### `process_batch_files(file_paths, parameters)`
Process multiple files in batch mode.

**Parameters:**
- `file_paths`: List of file paths to process
- `parameters`: Analysis parameters dictionary

**Returns:**
- List of analysis results for successful files

#### `export_wcs_data_to_csv(results, output_folder)`
Export batch results to CSV format.

**Parameters:**
- `results`: List of analysis results
- `output_folder`: Output directory path

**Returns:**
- Path to exported CSV file

#### `create_combined_visualizations(results)`
Create combined visualizations for multiple files.

**Parameters:**
- `results`: List of analysis results

**Returns:**
- List of plotly figure objects

#### `create_combined_wcs_dataframe(results)`
Create a combined DataFrame from multiple analysis results.

**Parameters:**
- `results`: List of analysis results

**Returns:**
- Pandas DataFrame with combined data

### Smart Output Functions

#### `get_smart_output_path(input_method, data_folder, uploaded_files)`
Generate optimal output path based on input method.

**Parameters:**
- `input_method`: "Select from Folder" or "Upload File"
- `data_folder`: Selected data folder (optional)
- `uploaded_files`: List of uploaded files (optional)

**Returns:**
- Generated output path string

#### `display_output_settings(input_method, data_folder)`
Display output settings UI component.

**Parameters:**
- `input_method`: Input method string
- `data_folder`: Selected data folder (optional)

**Returns:**
- User-specified output path

## Best Practices

### File Organization

1. **Use Descriptive Names**: Name files with player/team information
2. **Consistent Format**: Use consistent file naming conventions
3. **Backup Data**: Keep original files backed up
4. **Organize Folders**: Group related files in dedicated folders

### Performance Optimization

1. **Batch Size**: Process 10-50 files per batch for optimal performance
2. **File Size**: Large files (>10K records) are handled efficiently
3. **Memory Usage**: System automatically manages memory for large datasets
4. **Parallel Processing**: Consider future parallel processing for very large batches

### Error Prevention

1. **Validate Data**: Ensure velocity data is present and valid
2. **Check Formats**: Verify file formats before processing
3. **Test Small Batches**: Test with small batches before large-scale processing
4. **Monitor Output**: Check output files for completeness

## Troubleshooting

### Common Issues

#### "Invalid velocity data" Error
- **Cause**: Missing or invalid velocity column
- **Solution**: Check file format and ensure velocity data is present

#### "Empty file" Warning
- **Cause**: File contains no data records
- **Solution**: Verify file content and format

#### "Corrupted file" Error
- **Cause**: File format is not valid CSV
- **Solution**: Check file encoding and format

#### Performance Issues
- **Cause**: Very large files or many files
- **Solution**: Process in smaller batches or optimize file sizes

### Debug Mode

Enable debug mode for detailed error information:

```python
# Set debug flag in app configuration
DEBUG_MODE = True
```

## Future Enhancements

### Planned Features

1. **Parallel Processing**: Multi-threaded batch processing
2. **Progress Bars**: Real-time progress indicators
3. **Resume Capability**: Resume interrupted batch processing
4. **Advanced Filtering**: Filter files by type, size, or date
5. **Batch Templates**: Save and reuse batch configurations

### Performance Improvements

1. **Memory Optimization**: Better memory management for large datasets
2. **Caching**: Cache processed results for faster re-analysis
3. **Compression**: Support for compressed file formats
4. **Streaming**: Stream processing for very large files

## Examples

### Basic Batch Processing Example

```python
from src.batch_processing import process_batch_files
from src.app import get_smart_output_path

# Define file paths
file_paths = [
    "data/player1_statsport.csv",
    "data/player2_catapult.csv",
    "data/player3_generic.csv"
]

# Set analysis parameters
parameters = {
    'sampling_rate': 10,
    'epoch_duration': 1.0,
    'epoch_durations': [1.0, 2.0, 5.0],
    'th1_min': 5.0,
    'th1_max': 100.0,
}

# Get output path
output_path = get_smart_output_path("Select from Folder", "data")

# Process batch
results = process_batch_files(file_paths, parameters)

# Export results
export_wcs_data_to_csv(results, output_path)
```

### Custom Output Organization

```python
from src.app import get_smart_output_path

# Custom output path
custom_path = "custom_output/team_analysis"
output_path = get_smart_output_path("Select from Folder", custom_path)

# Process with custom output
results = process_batch_files(file_paths, parameters)
export_wcs_data_to_csv(results, output_path)
```

## Support

For issues or questions about the batch processing system:

1. **Check Documentation**: Review this guide and other documentation
2. **Test with Sample Data**: Use provided sample data for testing
3. **Enable Debug Mode**: Use debug mode for detailed error information
4. **Report Issues**: Report bugs with detailed error messages and file examples

---

*Last Updated: July 21, 2025*
*Version: 1.0* 