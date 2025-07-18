# 🔥 WCS Analysis Platform

A professional Streamlit application for Worst Case Scenario (WCS) analysis of GPS data with MATLAB-equivalent algorithms and support for multiple file formats.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](tests/)

## 🎯 Overview

The WCS Analysis Platform is designed for sports performance analysts, coaches, and researchers who need to identify maximum intensity periods in GPS data. It provides MATLAB-equivalent worst case scenario analysis with an intuitive web interface.

**✅ Current Status**: Fully functional with comprehensive kinematic analysis, enhanced visualizations, robust file processing, and production-ready features. All major bugs have been resolved and the application is ready for professional use.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/wcs-analysis-platform.git
cd wcs-analysis-platform

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python run_app.py
```

The app will open in your browser at: **http://localhost:8501**

## 📁 Supported File Formats

### **StatSport Files**
- CSV files with velocity data in `  Speed m/s` column (supports leading spaces)
- Player identification via `Player Id` and `Player Display Name`
- Automatic metadata extraction
- **Tested with**: BR_EC_18s(MD1).csv, BR_EC_18s(MD2).csv

### **Catapult Files**
- GPS data with metadata headers (including quoted formats)
- Velocity data in `Velocity` column
- Athlete information from metadata (`"# Athlete: ""Name"""`)
- **Tested with**: Aaron Ramsey_2024-09-09_Raw Data 09.09.24 MD vs Montenegro.csv, 3A-NT-GP-LSG-10x10-70x60 Export for Michael Obafemi 22346.csv

### **Generic GPS Files**
- Standard CSV format with velocity column
- Flexible column mapping
- Basic metadata support

## 🎯 Features

### **Core Functionality**
- ✅ **Multi-format File Ingestion**: Automatic format detection and processing
- ✅ **Velocity Data Extraction**: Clean velocity data with validation
- 🔄 **WCS Analysis**: MATLAB-equivalent worst case scenario algorithms
- 🏃 **Advanced Kinematic Analysis**: Differentiation and integration for comprehensive movement analysis
- 📊 **Interactive Visualizations**: Real-time charts with intelligent annotation positioning
- 📋 **Summary Statistics Tables**: Clean, organized data presentation
- 📤 **Export Capabilities**: JSON, CSV, and report generation
- 🔄 **Batch Processing**: Multiple file analysis with folder support
- ✅ **Multiple File Upload**: Drag and drop support for multiple files simultaneously
- ✅ **Select All Files**: One-click selection of all CSV files in a folder for batch processing
- ⚡ **Smart Epoch Deduplication**: Automatic removal of duplicate epoch durations to avoid redundant analysis
- 🔍 **Debug Information**: Detailed file processing diagnostics and error reporting
- 📊 **Combined Visualizations**: Multi-file analysis with comprehensive comparison charts
- 💾 **CSV Export**: Automatic export of all WCS data to OUTPUT folder with timestamped files

### **Technical Features**
- **10Hz Processing**: Standard GPS sampling rate support
- **Advanced Signal Processing**: Central difference differentiation and trapezoidal integration
- **Comprehensive Kinematic Calculations**: Real-time acceleration, distance, power, and jerk analysis
- **Intelligent Visualizations**: Smart annotation positioning to prevent overlaps
- **Robust Error Handling**: Graceful failure with detailed error messages and debugging info
- **Performance Optimization**: Efficient memory and CPU usage
- **Modular Architecture**: Clean, maintainable code structure
- **Robust CSV Parsing**: Handles various CSV formats with metadata headers
- **Enhanced UI**: Compact, professional interface with reduced font sizes and better organization

## 🏗️ Architecture

```
File Upload → Format Detection → Data Processing → WCS Analysis → Visualization → Export
     ↓              ↓                ↓              ↓              ↓           ↓
StatSport    Column Mapping    Velocity Calc   Epoch Analysis   Charts    Reports
Catapult     Metadata Parse    Distance Calc   Threshold Calc   Graphs    Data Files
Generic      Validation        Acceleration    Peak Detection   Metrics   Images
```

## 🔧 Recent Improvements & Bug Fixes

### **v1.5.0 - Batch Processing & Export Features**
- ✅ **CSV Export to OUTPUT Folder**: Automatic export of all WCS analysis results to timestamped CSV files
- ✅ **Combined Visualizations**: Multi-file analysis with comprehensive comparison charts including:
  - WCS Distance Distribution by Epoch (Box Plot)
  - Mean WCS Distance vs Epoch Duration (Line Plot)
  - Average WCS Distance by Player (Bar Chart)
  - WCS Distance Heatmap by Player and Epoch
  - Individual Player Analysis Grid
- ✅ **Batch Processing Module**: New dedicated module for handling multiple files efficiently
- ✅ **Download Combined Data**: Direct download of combined WCS data as CSV files
- ✅ **Enhanced Export Options**: Multiple export formats with user-friendly interface

### **v1.4.0 - Enhanced UI & Visualization Improvements**
- ✅ **Summary Statistics Tables**: Replaced individual metric displays with clean, organized tables
- ✅ **Reduced Font Sizes**: More compact interface with better space utilization
- ✅ **Fixed Annotation Errors**: Resolved "Invalid annotation position" errors in visualizations
- ✅ **Enhanced Debug Information**: Added detailed file content preview and processing diagnostics
- ✅ **Improved Error Handling**: Better file parsing error messages and recovery
- ✅ **Professional Layout**: Cleaner, more organized data presentation
- ✅ **Compact WCS Results**: Tabular format for easier comparison across epoch durations

### **v1.3.0 - Kinematic Analysis & Advanced Signal Processing**
- ✅ **Kinematic Parameters**: Added differentiation and integration of velocity signal to calculate acceleration and distance
- ✅ **Advanced Signal Processing**: Implemented central difference differentiation and trapezoidal integration
- ✅ **Comprehensive Metrics**: Added power, jerk, and smoothed signal calculations
- ✅ **Enhanced Visualizations**: New kinematic analysis charts with multiple subplots
- ✅ **Real-time Statistics**: Live calculation of acceleration, distance, and power statistics
- ✅ **Improved Annotation System**: Intelligent positioning to prevent text overlap in visualizations
- ✅ **Better Layout**: Enhanced spacing, margins, and legend positioning for cleaner charts

### **v1.2.0 - Select All Files & Enhanced Batch Processing**
- ✅ **Select All Files Feature**: Added checkbox to select all CSV files in a folder at once
- ✅ **Dual Input Support**: Enhanced file ingestion to handle both uploaded files and folder-selected files
- ✅ **Fixed File Path Processing**: Resolved "'str' object has no attribute 'decode'" error for folder-selected files
- ✅ **Improved Catapult Processing**: Added dedicated function for processing Catapult files from file paths
- ✅ **Enhanced User Experience**: Better feedback and confirmation messages for batch file selection

### **v1.1.0 - File Processing Enhancements**
- ✅ **Fixed Import Issues**: Resolved relative import errors for Streamlit deployment
- ✅ **Enhanced CSV Parsing**: Improved handling of StatSport files with leading spaces in column names
- ✅ **Catapult Metadata Extraction**: Fixed metadata parsing for quoted headers (`"# Athlete: ""Name"""`)
- ✅ **Multiple File Upload**: Added support for drag-and-drop of multiple files simultaneously
- ✅ **WCS Analysis Optimization**: Eliminated file re-reading issues during analysis phase
- ✅ **Robust Error Handling**: Better error messages and graceful failure recovery

### **Supported File Format Improvements**
- **StatSport**: Now handles `'  Speed m/s'` (two spaces), `' Player Display Name'` (one space)
- **Catapult**: Improved metadata extraction from quoted headers and various CSV formats
- **Generic GPS**: Enhanced column mapping and validation

### **Performance Optimizations**
- **Efficient File Processing**: Single-pass file reading with optimized data flow
- **Memory Management**: Reduced memory usage for large GPS datasets
- **Batch Processing**: Streamlined multiple file analysis workflow

## 🚀 Quick Start Guide

### **Enhanced File Processing with Debug Information**
The app now includes comprehensive debugging information to help troubleshoot file processing issues:

1. **Upload files** using drag-and-drop or folder selection
2. **View debug information** showing file content preview and format detection
3. **Monitor processing progress** with detailed feedback
4. **Identify issues** with clear error messages and diagnostics

### **Summary Statistics Tables**
The app now presents all statistics in clean, organized tables:

1. **Velocity Statistics**: Max, mean, min velocity and standard deviation
2. **Kinematic Parameters**: Acceleration, distance, and power metrics
3. **WCS Analysis Results**: Default Threshold and Threshold 1 distances and durations
4. **Compact Presentation**: All data organized by category for easy comparison

### **Select All Files Feature**
The app includes a powerful "Select All Files" feature for batch processing:

1. **Select "Select from Folder"** in the sidebar
2. **Enter folder path** (e.g., `data/test_data`)
3. **Check "Select All Files"** to automatically select all CSV files
4. **Configure analysis parameters** and run batch processing
5. **View results** for all files simultaneously

This feature is perfect for processing multiple GPS sessions, comparing different athletes, or analyzing entire datasets at once.

### **Kinematic Analysis Feature**
The app includes advanced kinematic analysis capabilities:

1. **Automatic Calculation**: Velocity signals are automatically differentiated and integrated
2. **Comprehensive Metrics**: Get acceleration, distance, power, and jerk analysis
3. **Enhanced Visualizations**: Multi-panel charts showing all kinematic parameters
4. **Real-time Statistics**: Live calculation of kinematic statistics during analysis

This provides deeper insights into movement patterns, performance characteristics, and athletic performance metrics.

## 📊 Usage Examples

### **Single File Analysis**
1. Launch the app: `python run_app.py`
2. Select "Upload File" method
3. Upload your GPS CSV file
4. Configure WCS parameters
5. View results and export data

### **Multiple File Analysis**
1. Select "Upload File" method
2. **Drag and drop multiple files** simultaneously into the uploader, or use Ctrl+Click (Cmd+Click on Mac) to select multiple files
3. Configure WCS parameters
4. Enable "Batch Processing Mode" for comparative analysis
5. View results for all files and export data

### **Folder-based Batch Analysis**
1. Select "Select from Folder" method
2. Enter folder path containing CSV files (e.g., `data/test_data`)
3. Check "Select All Files" to process all CSV files in the folder
4. Configure WCS parameters and enable export options
5. View combined visualizations and export data to OUTPUT folder

### **Batch Processing with Export**
1. Upload multiple files or select from folder
2. Enable "Include Export Options" in the sidebar
3. Click "📊 Export WCS Data to CSV" to save all results to OUTPUT folder
4. Use "📋 Download Combined Data" for immediate CSV download
5. View comprehensive combined visualizations for multi-file analysis

### **Combined Visualizations**
When processing multiple files, the app automatically generates:
- **WCS Distance Distribution**: Box plots showing distance ranges by epoch duration
- **Mean Distance Trends**: Line plots showing how average distances change with epoch duration
- **Player Comparisons**: Bar charts comparing average performance across players
- **Performance Heatmaps**: Color-coded tables showing individual player performance by epoch
- **Individual Analysis Grid**: Detailed velocity profiles and epoch comparisons for each player
3. **Use "Select All Files" checkbox** to select all CSV files at once, or manually select specific files
4. Configure WCS parameters (epoch duration, thresholds)
5. Enable "Batch Processing Mode" for comparative analysis
6. View results for all files and export data

### **Custom Analysis**
1. Configure custom epoch durations (30s, 60s, 90s, etc.)
   - **Primary Epoch Duration**: Main analysis window
   - **Additional Epoch Durations**: Extra durations for comprehensive analysis
   - **Smart Deduplication**: Duplicate durations are automatically removed to avoid redundant analysis
2. Set custom velocity thresholds (Default Threshold: 0-100 m/s, Threshold 1: customizable)
3. Enable advanced visualizations
4. Export comprehensive reports

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test module
python -m pytest tests/test_file_ingestion.py

# Run with coverage
python -m pytest --cov=src tests/
```

## 📚 Documentation

- **[API Documentation](docs/API.md)**: Detailed API reference
- **[Deployment Guide](docs/DEPLOYMENT.md)**: Production deployment instructions
- **[Contributing Guidelines](docs/CONTRIBUTING.md)**: How to contribute
- **[Changelog](docs/CHANGELOG.md)**: Version history and updates

## 🔧 Configuration

The application can be configured via `config/app_config.yaml`:

```yaml
# Application settings
app:
  title: "WCS Analysis Platform"
  port: 8501
  debug: false

# Processing settings
processing:
  sampling_rate: 10  # Hz
  max_file_size: 100  # MB
  supported_formats: ["csv"]

# Analysis settings
analysis:
  default_epoch_duration: 1.0  # minutes
  default_thresholds:
    # Default threshold is always 0.0 - 100.0 m/s (all velocities)
th1_min: 5.0
th1_max: 100.0
```

## 🔧 Troubleshooting

### **File Processing Issues**
If you're having trouble processing files:

1. **Check Debug Information**: The app now shows detailed file content preview and format detection
2. **File Format**: Ensure files are in supported CSV format (StatSport, Catapult, or Generic GPS)
3. **Column Names**: Check that velocity data is in the expected column (Speed m/s, Velocity, etc.)
4. **File Encoding**: Ensure files are UTF-8 encoded
5. **File Size**: Large files may take longer to process - check progress indicators

### **Multiple File Upload Issues**
If you're having trouble uploading multiple files:

1. **Drag and Drop**: Try dragging multiple files directly into the upload area
2. **Keyboard Selection**: Use Ctrl+Click (Windows/Linux) or Cmd+Click (Mac) to select multiple files
3. **Browser Compatibility**: Ensure you're using a modern browser (Chrome, Firefox, Safari, Edge)
4. **File Size**: Large files may take longer to upload - check the progress indicators
5. **File Format**: Ensure all files are in CSV format

### **Visualization Issues**
If visualizations aren't displaying properly:

1. **Annotation Errors**: Fixed in v1.4.0 - should no longer occur
2. **Browser Compatibility**: Ensure you're using a modern browser with JavaScript enabled
3. **Data Quality**: Check that velocity data contains valid numerical values
4. **File Size**: Very large files may take longer to render visualizations

### **Performance Tips**
- For large datasets, consider using the "Select from Folder" option
- Enable "Batch Processing Mode" for comparative analysis of multiple files
- Use the "Select All Files" feature for folder-based processing
- Monitor debug information to identify processing bottlenecks

## 🚀 Deployment

### **Local Development**
```bash
python run_app.py
```

### **Production Deployment**
```bash
# Using Docker
docker build -t wcs-analysis-platform .
docker run -p 8501:8501 wcs-analysis-platform

# Using Streamlit Cloud
# Deploy directly from GitHub repository
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](docs/CONTRIBUTING.md) for details.

### **Development Setup**
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/wcs-analysis-platform.git
cd wcs-analysis-platform

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Make your changes and submit a pull request
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **MATLAB WCS Algorithms**: Based on MATLAB-equivalent worst case scenario analysis
- **Streamlit**: Web application framework
- **Pandas**: Data processing and analysis
- **Plotly**: Interactive visualizations

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/wcs-analysis-platform/issues)
- **Documentation**: [docs/](docs/)
- **Email**: your.email@example.com

---

**Made with ❤️ for sports performance analysis** 