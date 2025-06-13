# TCP Server Application

## Description

A Python TCP server application that provides real-time camera streaming and control functionality. The server implements a multi-threaded architecture with three specialized services: data streaming, camera settings management, and client authentication.

## Features

- **Real-time Data Streaming**: Sends continuous numeric data packets at 24 Hz frequency
- **Camera Control**: Manages libcamera and ffmpeg processes for RTSP streaming
- **Settings Management**: Handles camera parameter updates (shutter, gain, white balance, etc.)
- **Authentication**: Secure client authentication with password validation
- **Logging**: Comprehensive logging with configurable levels
- **Configuration Management**: Environment variable support and JSON configuration

## Installation

### Prerequisites

- Python 3.8 or higher
- libcamera (for Raspberry Pi camera support)
- ffmpeg (for video streaming)
- RTSP server (e.g., MediaMTX)

### Setup

1. Navigate to the server directory:
```bash
cd server
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

3. Ensure camera and streaming dependencies are installed:
```bash
# On Raspberry Pi OS
sudo apt update
sudo apt install libcamera-apps ffmpeg
```

## Usage

### Basic Usage

Run the server with default configuration:
```bash
python main.py
```

### Configuration

The server uses a hierarchical configuration system supporting:

1. **Default configuration** (in `config.py`)
2. **Environment variable overrides**
3. **JSON configuration files**

#### Environment Variables

```bash
export SERVER_HOST=0.0.0.0
export DATA_PORT=5000
export SETTINGS_PORT=5001
export AUTH_PORT=5002
export AUTH_PASSWORD=your_password
export LOG_LEVEL=INFO
```

#### Camera Settings

Camera settings are stored in `config/camera_settings.json`:
```json
{
  "shutter": 10000,
  "gain": 1,
  "awb_red": 1.0,
  "awb_blue": 1.0,
  "contrast": 1.0,
  "brightness": 0.0
}
```

### Server Endpoints

- **Port 5000**: Data streaming server
- **Port 5001**: Camera settings management
- **Port 5002**: Client authentication
- **RTSP Stream**: `rtsp://<SERVER_IP>:8554/ES_MTX`

## Project Structure

```
server/
├── src/                    # Source code package
│   ├── __init__.py        # Root package init
│   ├── model/             # Data models
│   │   ├── __init__.py
│   │   ├── camera_model.py
│   │   └── tcp_server_model.py
│   └── presenter/         # Business logic
│       ├── __init__.py
│       └── server_presenter.py
├── config/                # Configuration files
│   └── camera_settings.json
├── config.py              # Configuration management
├── main.py               # Application entry point
├── README.md             # This file
└── requirements.txt      # Python dependencies
```

## Architecture

The application follows the **MVP (Model-View-Presenter)** architectural pattern:

### Models
- **CameraModel**: Manages camera configuration and streaming processes
- **TCPServerModel**: Base class for TCP server functionality
- **DataServerModel**: Handles numeric data streaming
- **SettingsServerModel**: Manages camera settings requests
- **AuthServerModel**: Handles client authentication

### Presenters
- **ServerPresenter**: Coordinates all server operations and models

### Key Design Principles
- **Separation of Concerns**: Each component has a single responsibility
- **Singleton Pattern**: Camera model ensures single instance
- **Observer Pattern**: Models notify of state changes
- **Error Handling**: Specific exception types with proper logging

## Protocol Specification

### Packet Format
All communication uses a standardized packet format:
```
[0x00][0xFF][ID][TYPE][LEN_HIGH][LEN_LOW][PAYLOAD][CHECKSUM]
```

### Message Types
- **ID 0x00**: Authentication
- **ID 0x01**: Data streaming
- **ID 0x02**: Settings management

### Authentication Flow
1. Client sends password packet to port 5002
2. Server validates password and checksum
3. Server responds with "ready" (success) or error code

### Data Streaming
1. Connect to port 5000
2. Receive continuous data packets at 24 Hz
3. Each packet contains random value + timestamp

### Settings Management
1. Connect to port 5001
2. Send empty packet to request current settings
3. Send 6-byte packet to update settings

## Logging

The application uses Python's standard logging module with:

- **File logging**: `server.log`
- **Console logging**: Real-time output
- **Log levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Structured format**: Timestamp, logger name, level, message

## Error Handling

Custom exception hierarchy:
- **CameraConfigurationError**: Camera setup issues
- **CameraProcessError**: Camera process failures
- **TCPServerError**: Server initialization problems
- **ProtocolError**: Communication protocol violations
- **ServerPresenterError**: Presenter coordination issues

## Development

### Code Standards
- Follow PEP 8 style guidelines
- Use type hints for all function parameters and returns
- Include docstrings for all classes and public methods
- Implement proper error handling with specific exceptions
- Maintain single responsibility principle

### Testing
```bash
# Run basic functionality test
python -c "from src.presenter.server_presenter import ServerPresenter; print('Import successful')"
```

## Contributing

1. Follow the established code formatting standards
2. Add comprehensive docstrings to new functions
3. Include proper error handling
4. Update README.md for new features
5. Test thoroughly before submitting changes

## License

This project is part of the ES_IoT tutorial system.