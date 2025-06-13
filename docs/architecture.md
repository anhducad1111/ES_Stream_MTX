# System Architecture

## Overview

ES IoT Tutorial MTX follows the MVP (Model-View-Presenter) architecture pattern, providing clear separation of concerns and maintainable code structure.

## MVP Architecture

### Model Layer

- **AuthModel**: Handles authentication logic and credential management
- **DataModel**: Processes incoming sensor data and manages data state
- **GraphModel**: Manages graph data, calculations, and data transformations
- **SettingsModel**: Handles application and device configuration
- **TCPModel**: Manages TCP communication with IoT devices
- **VideoModel**: Handles video stream processing and management

### View Layer

- **App**: Main application window and UI coordination
- **ConnectionModal**: Initial connection setup interface
- **GraphView**: Data visualization components and charts
- **SettingView**: Configuration interface for settings
- **VideoView**: Video stream display and controls

### Presenter Layer

- **MainPresenter**: Central coordinator for application logic
- **AuthPresenter**: Authentication flow management
- **ConnectionPresenter**: Connection establishment logic
- **GraphPresenter**: Graph interaction and data binding
- **SettingsPresenter**: Settings management and validation
- **VideoPresenter**: Video stream control and processing

## Communication Flow

```
User Input → View → Presenter → Model → External Services
                ↑                ↓
            UI Updates ← Presenter ← Data/Events
```

## Key Design Principles

1. **Separation of Concerns**: Each layer has distinct responsibilities
2. **Loose Coupling**: Components communicate through well-defined interfaces
3. **Observer Pattern**: Models notify presenters of state changes
4. **Dependency Injection**: Dependencies are injected rather than created
5. **Error Handling**: Comprehensive error handling at each layer

## Data Flow

1. **User Interaction**: User interacts with View components
2. **Event Handling**: View notifies Presenter of user actions
3. **Business Logic**: Presenter processes logic and updates Model
4. **Data Processing**: Model processes data and communicates with external services
5. **State Updates**: Model notifies Presenter of state changes
6. **UI Updates**: Presenter updates View to reflect new state

## External Dependencies

- **TCP Server**: Real-time data communication
- **RTSP Stream**: Video streaming protocol
- **Configuration Files**: JSON-based settings management
- **Logging System**: Structured logging for debugging and monitoring
