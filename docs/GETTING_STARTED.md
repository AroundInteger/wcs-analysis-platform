# 🚀 Getting Started with WCS Analysis Platform

Welcome to the WCS Analysis Platform! This guide will help you get up and running quickly.

## 📋 Prerequisites

- **Python 3.8 or higher**
- **pip package manager**
- **Git** (for cloning the repository)

## 🛠️ Installation

### Option 1: Quick Start (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/wcs-analysis-platform.git
   cd wcs-analysis-platform
   ```

2. **Run the quick start script:**
   ```bash
   python quick_start.py
   ```

   This script will:
   - Check your Python version
   - Install required dependencies
   - Create sample data
   - Run basic tests
   - Launch the application

### Option 2: Manual Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/wcs-analysis-platform.git
   cd wcs-analysis-platform
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the application:**
   ```bash
   python run_app.py
   ```

## 🎯 First Steps

### 1. Access the Application

Once launched, the app will be available at: **http://localhost:8501**

### 2. Upload Your First File

1. **Choose input method** in the sidebar:
   - **Upload File**: For single file analysis
   - **Select from Folder**: For batch processing

2. **Upload a GPS CSV file** or use the sample data:
   - `data/sample_data/sample_statsport.csv` (StatSport format)
   - `data/sample_data/sample_catapult.csv` (Catapult format)

### 3. Configure Analysis Parameters

In the sidebar, configure:
- **Epoch Duration**: Analysis window size (default: 1.0 minute)
- **Threshold Parameters**: Velocity ranges for analysis
- **Additional Epoch Durations**: For comprehensive analysis

### 4. View Results

The application will display:
- **File Information**: Metadata and format detection
- **Velocity Statistics**: Processed data metrics
- **WCS Results**: Worst Case Scenario analysis
- **Visualizations**: Interactive charts and graphs

## 📁 Supported File Formats

### StatSport Files
- CSV format with velocity data in `  Speed m/s` column
- Player identification via `Player Id` and `Player Display Name`
- Automatic metadata extraction

**Example:**
```csv
Player Id,Player Display Name,Time,  Speed m/s,Elapsed Time (s)
12345,John Doe,00:00:01,2.5,1
12345,John Doe,00:00:02,3.1,2
```

### Catapult Files
- GPS data with 8 lines of metadata headers
- Velocity data in `Velocity` column
- Athlete information from metadata

**Example:**
```csv
# OpenField Export
# Athlete: John Doe
# DeviceId: 12345
# Period: Match 1
# Reference time: 2023-01-01 12:00:00
# 
# 
Timestamp,Velocity,Latitude,Longitude,Seconds
00:00:01,2.5,51.5074,-0.1278,1
00:00:02,3.1,51.5075,-0.1279,2
```

### Generic GPS Files
- Standard CSV format with velocity column
- Flexible column mapping
- Basic metadata support

## 🔧 Configuration

### Application Settings

Edit `config/app_config.yaml` to customize:
- **Processing parameters**: Sampling rate, file size limits
- **Analysis settings**: Default thresholds, epoch durations
- **Visualization options**: Colors, chart settings
- **Export settings**: File formats, report options

### Environment Variables

Set these environment variables for customization:
```bash
export WCS_DEBUG=true          # Enable debug mode
export WCS_PORT=8502          # Custom port
export WCS_DATA_DIR=/path/to/data  # Custom data directory
```

## 🧪 Testing

### Run Basic Tests
```bash
python quick_start.py
# Choose option 3: Run full test suite
```

### Run Specific Tests
```bash
# Test file ingestion
python -m pytest tests/test_file_ingestion.py -v

# Test WCS analysis
python -m pytest tests/test_wcs_analysis.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Manual Testing

1. **Test with sample data:**
   - Upload `data/sample_data/sample_statsport.csv`
   - Verify format detection and processing
   - Check WCS results

2. **Test with your own data:**
   - Upload your GPS CSV files
   - Verify velocity data extraction
   - Compare results with expected values

## 🚀 Deployment

### Local Development
```bash
python run_app.py
```

### Production Deployment

#### Using Docker
```bash
# Build Docker image
docker build -t wcs-analysis-platform .

# Run container
docker run -p 8501:8501 wcs-analysis-platform
```

#### Using Streamlit Cloud
1. Push your code to GitHub
2. Connect to Streamlit Cloud
3. Deploy automatically

## 📊 Understanding WCS Analysis

### What is WCS?
**Worst Case Scenario (WCS)** analysis identifies the time windows with the highest cumulative distance within specified velocity thresholds.

### Key Metrics
- **TH_0 Distance**: Maximum distance in velocity range (0 < V < 100 m/s)
- **TH_1 Distance**: Maximum distance in velocity range (5 < V < 100 m/s)
- **WCS Period**: Time window with maximum performance
- **Velocity Statistics**: Mean, peak, and distribution metrics

### Algorithm
1. **Data Processing**: Standardize to 10Hz sampling rate
2. **Threshold Application**: Filter velocity data by ranges
3. **Sliding Window**: Calculate cumulative distance for each epoch
4. **Peak Detection**: Identify maximum performance periods
5. **Results**: Return distance, time, and position metrics

## 🆘 Troubleshooting

### Common Issues

#### "Velocity column not found"
- **Solution**: Check column names in your CSV file
- **Supported variations**: `  Speed m/s`, ` Speed m/s`, `Speed m/s`, `Speed`, `Velocity`

#### "File format not detected"
- **Solution**: Ensure file has proper headers
- **StatSport**: Include `Player Id` and `Player Display Name`
- **Catapult**: Include metadata headers starting with `#`

#### "Analysis failed"
- **Solution**: Check data quality and format
- **Verify**: Velocity data is numeric and within reasonable range (0-20 m/s)

#### "Port already in use"
- **Solution**: Use different port or stop other applications
- **Command**: `python run_app.py --server.port 8502`

### Getting Help

1. **Check the logs**: Look for error messages in the terminal
2. **Verify data format**: Ensure your CSV file matches supported formats
3. **Test with sample data**: Use provided sample files to verify functionality
4. **Check dependencies**: Ensure all required packages are installed

## 📚 Next Steps

### Learn More
- **[API Documentation](API.md)**: Detailed function reference
- **[Deployment Guide](DEPLOYMENT.md)**: Production setup instructions
- **[Contributing Guidelines](CONTRIBUTING.md)**: How to contribute

### Advanced Usage
- **Batch Processing**: Analyze multiple files simultaneously
- **Custom Thresholds**: Configure velocity ranges for your sport
- **Export Options**: Generate reports and data exports
- **Integration**: Use the platform as part of larger workflows

### Support
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Comprehensive guides and examples
- **Community**: Connect with other users and developers

---

**Happy analyzing! 🎯** 