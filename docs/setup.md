# Setup and Installation Guide

## Prerequisites

### System Requirements

- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Network**: TCP/IP connection to IoT device

### Python Dependencies

The application requires several Python packages listed in `requirements.txt`:

```
customtkinter>=5.2.0
matplotlib>=3.7.0
opencv-python>=4.8.0
numpy>=1.24.0
Pillow>=10.0.0
```

## Installation Steps

### 1. Clone Repository

```bash
git clone <repository-url>
cd tutorial_mtx
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
python -c "import customtkinter, matplotlib, cv2; print('All dependencies installed successfully')"
```

## Configuration

### 1. Network Configuration

Ensure your IoT device is accessible on the network:

```bash
# Test connectivity
ping <device-ip-address>

# Test port availability
telnet <device-ip-address> 5000
telnet <device-ip-address> 5001
telnet <device-ip-address> 5002
```

### 2. Application Settings

Edit `config/settings.json` to customize application behavior:

```json
{
  "connection": {
    "default_port": 8554,
    "timeout": 30,
    "retry_attempts": 3
  },
  "video": {
    "resolution": {
      "width": 640,
      "height": 480
    },
    "framerate": 30
  }
}
```

### 3. Logging Configuration

Logs are stored in the `logs/` directory. Configure logging levels in `config/settings.json`:

```json
{
  "logging": {
    "level": "INFO",
    "file": "logs/app.log"
  }
}
```

## Running the Application

### Standard Startup

```bash
python main.py
```

### Debug Mode

```bash
# Enable verbose logging
python main.py --debug
```

### Command Line Options

```bash
# Show help
python main.py --help

# Specify config file
python main.py --config custom_config.json

# Set log level
python main.py --log-level DEBUG
```

## First Time Setup

### 1. Connection Setup

1. Start the application
2. Enter your IoT device IP address in the connection modal
3. Click "Connect" to establish connection

### 2. Authentication

1. Enter the device password when prompted
2. Wait for authentication confirmation
3. Connection status will be displayed

### 3. Verify Functionality

1. Check that data is displayed in the graph view
2. Verify video stream is working (if camera connected)
3. Test settings modifications

## Troubleshooting

### Common Issues

#### Connection Failed

**Symptoms**: Cannot connect to device
**Solutions**:

1. Verify device IP address
2. Check network connectivity
3. Ensure device is powered on
4. Verify firewall settings

```bash
# Test network connectivity
ping <device-ip>
nmap -p 5000-5002 <device-ip>
```

#### Authentication Failed

**Symptoms**: Login rejected
**Solutions**:

1. Verify password is correct
2. Check device authentication service
3. Review device logs for auth errors

#### Video Stream Not Working

**Symptoms**: Black video window or connection timeout
**Solutions**:

1. Check RTSP service on device
2. Verify port 8554 is open
3. Test with VLC media player:

   ```
   rtsp://<device-ip>:8554/ES_MTX
   ```

#### No Data Display

**Symptoms**: Empty graphs, no sensor data
**Solutions**:

1. Check data service connection (port 5000)
2. Verify device is sending data
3. Check logs for data parsing errors

### Debug Commands

#### Network Diagnostics

```bash
# Check port connectivity
nc -zv <device-ip> 5000
nc -zv <device-ip> 5001
nc -zv <device-ip> 5002

# Monitor network traffic
wireshark -i <interface> -f "host <device-ip>"
```

#### Application Diagnostics

```bash
# Run with debug logging
python main.py --log-level DEBUG

# Check log files
tail -f logs/app.log

# Verify dependencies
pip list | grep -E "(customtkinter|matplotlib|opencv)"
```

#### System Diagnostics

```bash
# Check Python version
python --version

# Check available memory
# Windows:
systeminfo | findstr "Total Physical Memory"
# Linux/macOS:
free -h
```

### Log Analysis

#### Log Locations

- **Application logs**: `logs/app.log`
- **Error logs**: Console output
- **Debug logs**: `logs/debug.log` (when debug enabled)

#### Common Log Messages

```
INFO - Connection established to 192.168.1.100
ERROR - Authentication failed: Invalid password
WARNING - Data timeout, attempting reconnection
DEBUG - Received packet: ID=0x01, Type=0x00, Length=9
```

## Performance Optimization

### Network Optimization

```json
{
  "connection": {
    "timeout": 10,
    "retry_attempts": 2
  }
}
```

### Video Optimization

```json
{
  "video": {
    "resolution": {
      "width": 320,
      "height": 240
    },
    "framerate": 15
  }
}
```

### Memory Optimization

```json
{
  "graph": {
    "max_data_points": 500,
    "update_interval": 200
  }
}
```

## Development Setup

### Additional Dependencies

```bash
# Development tools
pip install black flake8 pytest coverage mypy

# Pre-commit hooks
pip install pre-commit
pre-commit install
```

### Code Quality

```bash
# Format code
black src/ main.py

# Lint code
flake8 src/ main.py

# Type checking
mypy src/ main.py

# Run tests
pytest tests/
```

### IDE Configuration

#### Visual Studio Code

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true
}
```

#### PyCharm

1. Set interpreter to virtual environment
2. Enable code formatting with Black
3. Configure flake8 as external tool
4. Enable type checking with mypy

## Deployment

### Packaging for Distribution

```bash
# Create standalone executable
pip install pyinstaller
pyinstaller --onefile --windowed main.py

# Create installer (Windows)
pip install nsis
makensis installer.nsi
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## Support

### Getting Help

1. Check this documentation
2. Review log files for error messages
3. Test individual components
4. Create GitHub issue with logs and system info

### System Information Collection

```bash
# Collect system info for support
python -c "
import sys, platform
print(f'Python: {sys.version}')
print(f'Platform: {platform.platform()}')
print(f'Architecture: {platform.architecture()}')
"
