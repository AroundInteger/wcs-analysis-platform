# 🔥 WCS Analysis Platform

A professional Streamlit application for Worst Case Scenario (WCS) analysis of GPS data with MATLAB-equivalent algorithms and support for multiple file formats.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](tests/)

## 🎯 Overview

The WCS Analysis Platform is designed for sports performance analysts, coaches, and researchers who need to identify maximum intensity periods in GPS data. It provides MATLAB-equivalent worst case scenario analysis with an intuitive web interface.

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
- CSV files with velocity data in `  Speed m/s` column
- Player identification via `Player Id` and `Player Display Name`
- Automatic metadata extraction

### **Catapult Files**
- GPS data with 8 lines of metadata headers
- Velocity data in `Velocity` column
- Athlete information from metadata

### **Generic GPS Files**
- Standard CSV format with velocity column
- Flexible column mapping
- Basic metadata support

## 🎯 Features

### **Core Functionality**
- ✅ **Multi-format File Ingestion**: Automatic format detection and processing
- ✅ **Velocity Data Extraction**: Clean velocity data with validation
- 🔄 **WCS Analysis**: MATLAB-equivalent worst case scenario algorithms
- 📊 **Interactive Visualizations**: Real-time charts and performance metrics
- 📤 **Export Capabilities**: JSON, CSV, and report generation
- 🔄 **Batch Processing**: Multiple file analysis

### **Technical Features**
- **10Hz Processing**: Standard GPS sampling rate support
- **Error Handling**: Graceful failure with detailed error messages
- **Performance Optimization**: Efficient memory and CPU usage
- **Modular Architecture**: Clean, maintainable code structure

## 🏗️ Architecture

```
File Upload → Format Detection → Data Processing → WCS Analysis → Visualization → Export
     ↓              ↓                ↓              ↓              ↓           ↓
StatSport    Column Mapping    Velocity Calc   Epoch Analysis   Charts    Reports
Catapult     Metadata Parse    Distance Calc   Threshold Calc   Graphs    Data Files
Generic      Validation        Acceleration    Peak Detection   Metrics   Images
```

## 📊 Usage Examples

### **Single File Analysis**
1. Launch the app: `python run_app.py`
2. Select "Upload File" method
3. Upload your GPS CSV file
4. Configure WCS parameters
5. View results and export data

### **Batch Analysis**
1. Select "Select from Folder" method
2. Enter folder path containing CSV files
3. Select multiple files for analysis
4. Enable "Batch Processing Mode"
5. View comparative results

### **Custom Analysis**
1. Configure custom epoch durations (30s, 60s, 90s, etc.)
2. Set custom velocity thresholds (TH_0, TH_1)
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
    th0_min: 0.0
    th0_max: 100.0
    th1_min: 5.0
    th1_max: 100.0
```

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