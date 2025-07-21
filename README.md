# 🔥 WCS Analysis Platform

A professional **Worst Case Scenario (WCS) Analysis Platform** for GPS data processing, designed for sports performance analysis. This Streamlit application provides comprehensive analysis of GPS velocity data with support for multiple file formats and advanced visualization capabilities.

## ✨ Key Features

### 📊 **Dual WCS Analysis**
- **Rolling Window Analysis**: Sliding window approach for continuous performance assessment with **corrected thresholding implementation**
- **Contiguous Period Analysis**: Best continuous period identification within specified durations
- **Scaled Curve Visualization**: Both WCS methods displayed as scaled curves on velocity plots with **improved visibility and positioning**
- **Comprehensive Comparison**: Side-by-side analysis of both methods for complete performance insight

### 🎯 **Advanced Analysis Capabilities**
- **Multi-Epoch Analysis**: Support for multiple epoch durations (0.5, 1.0, 1.5, 2.0, 3.0, 5.0 minutes)
- **Dual Threshold System**: 
  - **Default Threshold**: 0.0-100.0 m/s (all velocities)
  - **Threshold 1**: Customizable range (default: 5.0-100.0 m/s)
- **Enhanced Kinematic Parameters**: Acceleration, distance, power (based on abs(acceleration)), and jerk calculations
- **Deceleration Analysis**: Separate deceleration metrics and event counting
- **Performance Intensity Mapping**: Visual representation of performance levels

### 📁 **Multi-Format Support**
- **StatSport**: Native support with automatic metadata extraction
- **Catapult**: Robust parsing with metadata handling
- **Generic GPS**: Flexible format with customizable column mapping
- **Batch Processing**: Multiple file upload and folder selection with smart output organization
- **Advanced Analytics**: Comprehensive cohort analysis for large datasets (>10 files) with statistical comparisons
- **MATLAB-Compatible Export**: Automatic export in exact MATLAB format with multiple sheets

### 📈 **Enhanced Visualizations**
- **Dual WCS Velocity Plot**: Shows both rolling and contiguous WCS periods as scaled curves with **improved layering and visibility**
- **Enhanced WCS Analysis**: Multi-panel visualization with timeline and intensity mapping
- **Streamlined Kinematic Analysis**: Multi-panel charts for velocity, acceleration, distance, and power (removed redundant deceleration plot)
- **Performance Metrics Dashboard**: Comprehensive statistics with **improved event-based metrics**
- **Consistent Terminology**: Professional naming throughout (Default Threshold, Threshold 1)

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd wcs-test
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   # Option 1: Use the shell script (recommended)
   ./start_app.sh
   
   # Option 2: Use the Python launcher
   python launch_app.py
   
   # Option 3: Direct streamlit command
   PYTHONPATH=src streamlit run src/app.py --server.port 8501
   ```

4. **Access the app**: Open your browser to `http://localhost:8501`

### Basic Usage

1. **Upload Data**: Drag and drop CSV files or select from a folder
2. **Configure Parameters**: Set epoch durations and threshold values
3. **Run Analysis**: The app automatically calculates both rolling and contiguous WCS measures
4. **View Results**: Explore dual WCS visualizations and comprehensive statistics

## 📊 Dual WCS Analysis Explained

### Rolling Window Analysis
- **Method**: Sliding window approach that maximizes accumulated work (area under the curve)
- **Principle**: Finds the window that maximizes ∫ velocity(t) dt over the specified time period
- **Thresholding**: **Correctly applies velocity thresholds** - only data points within the threshold range contribute to the WCS metric
- **Advantage**: Identifies periods of maximum accumulated work, not just peak velocity
- **Use Case**: Identifying sustained high-intensity periods and metabolic demand assessment
- **Key Insight**: WCS epoch ≠ maximum velocity peak (broader peaks often win due to sustained activity)

### Contiguous Period Analysis
- **Method**: Finds the best continuous period of the specified duration
- **Advantage**: Identifies sustained performance over exact time periods
- **Use Case**: Assessing consistent performance over specific time intervals

### Scaled Curve Visualization
- **Display**: Both WCS methods shown as horizontal lines on the velocity plot
- **Scaling**: Distance values scaled to fit within the **fixed 0-10 m/s velocity range** for consistent visibility
- **Color Coding**: 
  - **Rolling**: Solid lines with circle markers
  - **Contiguous**: Dotted lines with diamond markers
- **Hover Information**: Detailed distance, time range, and method information

## 🎯 Analysis Parameters

### Epoch Durations
- **Primary Duration**: Main analysis period (automatically included in all analyses)
- **Additional Durations**: Multiple epochs for comprehensive assessment
- **Automatic Deduplication**: Duplicate durations are automatically removed

### Threshold Configuration
- **Default Threshold**: Fixed at 0.0-100.0 m/s (analyzes all velocity data)
- **Threshold 1**: Customizable range for high-intensity performance analysis
- **Performance Levels**: Automatic classification based on average velocities
- **Rolling WCS Behavior**: **Correctly applies thresholding** to only include velocity data points within the threshold range
- **Contiguous WCS Behavior**: Applies thresholding to find best continuous period within range

## 📈 Visualization Features

### Dual WCS Velocity Analysis
- **Main Velocity Plot**: Clean velocity time series with **reduced opacity fill** for better curve visibility
- **Rolling WCS Curves**: Solid lines showing rolling window results with **increased line width and marker size**
- **Contiguous WCS Curves**: Dotted lines showing contiguous period results
- **Fixed Y-Axis**: **Consistent 0-10 m/s range** with scaled WCS curves positioned appropriately
- **Interactive Legend**: Toggle visibility of different analysis methods
- **Hover Details**: Comprehensive information on hover

### Enhanced WCS Analysis
- **Multi-Panel Layout**: Velocity, timeline, and intensity visualization
- **Period Highlighting**: Clean background highlights for WCS periods
- **Performance Timeline**: Visual representation of period distribution
- **Intensity Mapping**: Normalized performance intensity over time

### Kinematic Analysis
- **Multi-Panel Charts**: Velocity, acceleration, distance, and power
- **Streamlined Design**: **Removed redundant deceleration plot** (acceleration covers both positive and negative)
- **Interactive Elements**: Zoom, pan, and hover functionality
- **Export Capabilities**: High-quality chart export

## 📁 File Format Support

### StatSport Format
- **Automatic Detection**: Recognizes StatSport files by header structure
- **Metadata Extraction**: Player name, date, and session information
- **Column Mapping**: Automatic velocity and time column identification

### Catapult Format
- **Metadata Handling**: Skips metadata lines during parsing
- **Robust Parsing**: Handles quoted headers and special characters
- **Column Detection**: Automatic identification of velocity columns

### Generic GPS Format
- **Flexible Mapping**: Customizable column name mapping
- **Format Detection**: Automatic format identification
- **Error Handling**: Graceful handling of parsing errors

## 🔄 Batch Processing

### Multiple File Upload
- **Drag & Drop**: Support for multiple file upload
- **Progress Tracking**: Real-time progress indicators
- **Error Handling**: Individual file error reporting
- **Combined Analysis**: Aggregate statistics across files

### Folder Selection
- **Directory Browsing**: Select files from local directories
- **Select All Option**: Bulk selection of CSV files
- **File Filtering**: Automatic CSV file detection
- **Path Validation**: Error handling for invalid paths

### Export Capabilities
- **CSV Export**: Comprehensive results export
- **Combined Data**: All files in single export file
- **Detailed Information**: Complete analysis results
- **Timestamped Files**: Automatic file naming with timestamps

## 🛠️ Technical Details

### Data Processing
- **10Hz Standardization**: All data processed to 10Hz sampling rate
- **Quality Control**: Automatic data validation and cleaning
- **Missing Data Handling**: Graceful handling of incomplete data
- **Performance Optimization**: Efficient processing for large datasets

### Analysis Algorithms
- **Central Difference**: Accurate acceleration calculation
- **Trapezoidal Integration**: Precise distance calculation
- **Rolling Window**: **Corrected implementation with proper thresholding**
- **Contiguous Search**: Optimized period identification
- **Power Calculation**: **Based on absolute acceleration** for physically meaningful values

### Visualization Engine
- **Plotly Integration**: Interactive, publication-quality charts
- **Responsive Design**: Adapts to different screen sizes
- **Export Options**: PNG, SVG, and HTML export
- **Performance Optimization**: Efficient rendering for large datasets

## 📊 Performance Metrics

### Velocity Statistics
- **Peak Velocity**: Maximum velocity achieved
- **Mean Velocity**: Average velocity over session
- **Velocity Variability**: Standard deviation and range
- **Duration Analysis**: Total session duration and active time

### WCS Metrics
- **Distance Covered**: Total distance in WCS periods
- **Time in Threshold**: Duration within specified velocity ranges
- **Performance Intensity**: Average velocity during WCS periods
- **Method Comparison**: Rolling vs. contiguous analysis results

### Enhanced Kinematic Parameters
- **Acceleration Profile**: **Event-based metrics** - mean acceleration over acceleration events only
- **Deceleration Analysis**: **Separate deceleration metrics** with event counting
- **Distance Analysis**: Total distance and distance rate
- **Power Output**: **Instantaneous power based on absolute acceleration**
- **Movement Quality**: Jerk analysis for movement smoothness

## 🔧 Configuration

### App Configuration
- **Port Settings**: Configurable server port (default: 8501)
- **Layout Options**: Wide layout for better visualization
- **Theme Customization**: Professional dark/light theme support
- **Performance Settings**: Optimized for large datasets

### Analysis Settings
- **Sampling Rate**: Fixed at 10Hz for consistency
- **Epoch Durations**: Configurable analysis periods
- **Threshold Values**: Customizable velocity thresholds
- **Visualization Options**: Toggle different chart types

## 🚨 Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all dependencies are installed
2. **File Upload Issues**: Check file format and size limits
3. **Analysis Errors**: Verify data quality and column names
4. **Visualization Issues**: Check browser compatibility

### Performance Tips
- **Large Files**: Use batch processing for multiple large files
- **Memory Usage**: Close unused browser tabs during analysis
- **Processing Speed**: Reduce epoch durations for faster analysis
- **Export Optimization**: Use CSV export for large datasets

## 📤 MATLAB-Compatible Export

### 🎯 **Seamless Integration with Existing Workflows**
The WCS Analysis Platform now exports data in the **exact format** used by your MATLAB workflow, ensuring complete compatibility with existing analysis pipelines.

### 📊 **Export Formats**

#### **Excel (MATLAB Format) - Recommended**
- **Multiple Sheets**: WCS Report, Summary Maximum Values, and Binned Data sheets
- **Exact Column Names**: Matches MATLAB output format precisely
- **Timestamp Integration**: Proper datetime handling for analysis
- **Threshold Classification**: TH_0, TH_1 format matching your existing workflow

#### **CSV (MATLAB Format)**
- **WCS Report Data**: Primary analysis results in CSV format
- **Compatible Headers**: Column names match MATLAB output
- **Easy Integration**: Direct import into existing MATLAB scripts

#### **JSON (MATLAB Format)**
- **Structured Data**: Hierarchical organization of all results
- **Metadata Included**: Export timestamp, file counts, and analysis parameters
- **API Integration**: Perfect for automated workflows

### 🔄 **Automatic Export for Batch Mode**
- **Default Behavior**: When batch processing is enabled, MATLAB format Excel export happens automatically
- **File Naming**: Follows MATLAB convention with `_checkPython.xlsx` suffix
- **Output Location**: Saved to `OUTPUT/` folder for easy access
- **Multiple Sheets**: Excel file contains all analysis components

### 📋 **Sheet Structure (Excel Export)**

#### **1. WCS Report Sheet**
- **Individual WCS Periods**: Each row represents a WCS analysis period
- **Columns**: Distance_TH_0, Time_TH_0, Frequency_TH_0, Threshold, PLAYER_METADATA, TimeStamp, Index
- **Threshold Classification**: TH_0 (Default), TH_1 (Threshold 1)
- **Timestamp Integration**: Proper datetime conversion from GPS data

#### **2. Summary Maximum Values Sheet**
- **Maximum Values**: Highest WCS distance for each epoch duration per player
- **Columns**: PLAYER_METADATA, Epoch, Distance_TH_0, Distance_TH_1
- **Player Comparison**: Easy comparison across multiple athletes

#### **3. X.X minute Bin Sheets**
- **Binned Data**: Individual WCS periods grouped by epoch duration
- **Sheet Names**: "5.0 minute Bin", "10.0 minute Bin", etc.
- **Detailed Analysis**: Complete breakdown of all WCS periods

### 🎯 **Benefits**
- **Zero Learning Curve**: Use existing MATLAB analysis scripts without modification
- **Consistent Results**: Same format, same interpretation, same workflow
- **Time Savings**: No need to reformat or restructure data
- **Professional Output**: Publication-ready Excel files with proper formatting

## 📝 Changelog

### Latest Updates (Today's Achievements! 🎉)
- **✅ MATLAB-Compatible Export**: Complete export system matching your existing MATLAB workflow format
- **✅ Automatic Batch Export**: Default MATLAB format Excel export for batch processing
- **✅ Multiple Export Formats**: Excel, CSV, and JSON in MATLAB format
- **✅ Corrected Rolling WCS Implementation**: Fixed thresholding behavior to properly apply velocity thresholds
- **✅ Enhanced Visualization Layering**: Improved curve visibility with reduced velocity line opacity and increased WCS curve prominence
- **✅ Consistent Professional Terminology**: Updated all "TH_1" references to "Threshold 1" throughout the application
- **✅ Fixed Y-Axis Scaling**: Implemented consistent 0-10 m/s range with properly scaled WCS curves
- **✅ Streamlined Kinematic Analysis**: Removed redundant deceleration plot for cleaner visualization
- **✅ Improved Power Calculation**: Updated to use absolute acceleration for physically meaningful values
- **✅ Enhanced Event-Based Metrics**: Mean acceleration and deceleration now calculated over events only
- **✅ Comprehensive Documentation**: Updated README and created detailed rolling WCS theory documentation

### Previous Features
- **Dual WCS Analysis**: Added both rolling and contiguous WCS methods
- **Scaled Curve Visualization**: WCS periods displayed as curves on velocity plots
- **Enhanced UI**: Improved layout and user experience
- **Batch Processing**: Enhanced multiple file handling
- **Export Features**: Comprehensive data export capabilities
- **Multi-format Support**: StatSport, Catapult, and Generic GPS
- **Kinematic Analysis**: Acceleration, distance, and power calculations
- **Enhanced Visualizations**: Multi-panel charts and performance mapping

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for details on:
- Code style and standards
- Testing requirements
- Documentation updates
- Feature requests and bug reports

## 📚 Documentation

### 📖 **Comprehensive Guides**
- **[Getting Started Guide](docs/GETTING_STARTED.md)**: Detailed setup and usage instructions
- **[Batch Processing Guide](docs/BATCH_PROCESSING_GUIDE.md)**: Complete guide to batch processing system
- **[Advanced Analytics Guide](docs/ADVANCED_ANALYTICS_GUIDE.md)**: Comprehensive cohort analysis for large datasets (>10 files)
- **[Rolling WCS Theory](ROLLING_WCS_THEORY.md)**: Technical explanation of rolling WCS analysis
- **[Automated Testing](docs/AUTOMATED_TESTING.md)**: Testing procedures and validation

### 🎯 **Key Documentation Features**
- **Step-by-step Instructions**: Clear guidance for all features
- **Technical Details**: In-depth explanations of algorithms and methods
- **Performance Benchmarks**: Real-world performance metrics
- **Troubleshooting**: Common issues and solutions
- **API Reference**: Complete function documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. 