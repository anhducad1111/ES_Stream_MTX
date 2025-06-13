# ES IoT Tutorial MTX

## Description

ES IoT Tutorial MTX is a desktop application for real-time IoT data visualization and camera control. Built with Python using the MVP (Model-View-Presenter) architecture pattern, this application provides a modern GUI interface using CustomTkinter for connecting to IoT devices, viewing live camera streams, and monitoring sensor data.

## Features

- **Real-time Data Visualization**: Interactive graphs and charts for sensor data
- **Live Camera Streaming**: RTSP camera stream integration with controls
- **Device Authentication**: Secure connection to IoT devices
- **Settings Management**: Configurable camera and connection settings
- **Modern UI**: CustomTkinter-based interface with dark/light theme support

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd tutorial_mtx
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Usage

### Starting the Application

Run the main application:
```bash
python main.py
```

The application will start with a connection modal where you can:
1. Enter the server IP address
2. Authenticate with the IoT device
3. Connect to start using the application

### Main Features

- **Connection Modal**: Initial setup for device connection
- **Main Dashboard**: Overview of connected devices and data
- **Graph View**: Real-time data visualization
- **Video View**: Live camera stream display
- **Settings**: Configure camera parameters and connection settings

## Project Structure

```
tutorial_mtx/
├── src/                    # Source code package
│   ├── __init__.py        # Root package init
│   ├── model/             # Data models (MVP)
│   │   ├── __init__.py
│   │   ├── auth_model.py      # Authentication logic
│   │   ├── data_model.py      # Data processing
│   │   ├── graph_model.py     # Graph data management
│   │   ├── settings_model.py  # Settings management
│   │   ├── tcp_model.py       # TCP communication
│   │   └── video_model.py     # Video stream handling
│   ├── view/              # UI components (MVP)
│   │   ├── __init__.py
│   │   ├── connection_modal.py # Connection dialog
│   │   ├── graph_view.py      # Data visualization UI
│   │   ├── main_view.py       # Main application window
│   │   ├── setting_view.py    # Settings interface
│   │   └── video_view.py      # Video display UI
│   └── presenter/         # Business logic (MVP)
│       ├── __init__.py
│       ├── auth_presenter.py      # Authentication logic
│       ├── connection_presenter.py # Connection handling
│       ├── graph_presenter.py     # Graph interactions
│       ├── main_presenter.py      # Main app coordination
│       ├── settings_presenter.py  # Settings management
│       └── video_presenter.py     # Video stream control
├── docs/                  # Documentation
├── assets/                # Static assets
├── server/                # TCP server component
├── requirements.txt       # Dependencies
├── README.md             # Project documentation
├── .gitignore            # Git ignore rules
└── main.py               # Application entry point
```

## Architecture

This application follows the **MVP (Model-View-Presenter)** architecture pattern:

- **Model**: Handles data, business logic, and communication with external services
- **View**: Manages the user interface components and user interactions
- **Presenter**: Mediates between Model and View, handling application logic

### Key Components

- **AppManager**: Orchestrates application startup and component initialization
- **TCP Communication**: Handles real-time data exchange with IoT devices
- **Authentication**: Secure device connection and session management
- **Data Visualization**: Real-time graphs and charts using matplotlib
- **Video Streaming**: RTSP stream integration for camera feeds

## Configuration

The application supports configuration through:

- Environment variables for sensitive data
- JSON configuration files for settings
- Runtime settings through the UI

## Development

### Code Standards

This project follows Python development standards including:

- PEP 8 code style
- Type hints for better code documentation
- Comprehensive docstrings
- MVP architecture separation
- Proper error handling and logging

### Dependencies

Key dependencies include:

- `customtkinter`: Modern UI framework
- `matplotlib`: Data visualization
- `opencv-python`: Video processing
- `requests`: HTTP communication
- `threading`: Concurrent operations

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes following the coding standards
4. Add tests for new functionality
5. Commit your changes (`git commit -am 'Add new feature'`)
6. Push to the branch (`git push origin feature/new-feature`)
7. Create a Pull Request

### Coding Guidelines

- Follow MVP architecture principles
- Write comprehensive docstrings
- Include type hints
- Handle exceptions gracefully
- Write unit tests for new features

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Create an issue in the GitHub repository
- Check the documentation in the `docs/` directory
- Review the troubleshooting section below

## Troubleshooting

### Common Issues

1. **Connection Failed**: Check server IP and network connectivity
2. **Video Stream Not Loading**: Verify RTSP server is running
3. **Authentication Error**: Confirm credentials and server availability
4. **UI Not Responsive**: Check for background thread issues

### Debug Commands

```bash
# Check dependencies
pip list

# Test network connectivity
ping <server-ip>

# Run with debug logging
python main.py --debug
```

## Version History

- **v1.0.0**: Initial release with MVP architecture
- Camera streaming integration
- Real-time data visualization
- Device authentication system
