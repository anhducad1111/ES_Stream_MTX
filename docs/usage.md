# User Guide

## Getting Started

### Application Startup

1. Run the application: `python main.py`
2. A connection modal will appear first
3. Enter your IoT device IP address
4. Click "Connect" to establish connection

### Initial Connection Setup

1. **Server IP**: Enter the IP address of your IoT device (e.g., 192.168.1.100)
2. **Authentication**: Enter the device password when prompted
3. **Connection Status**: Wait for successful connection confirmation
4. **Main Interface**: The main application window opens automatically after connection

## Main Application Interface

The main window contains three sections:

### 1. Live Video Stream (Top Left)

- **Purpose**: Displays real-time RTSP video feed from the device camera
- **Features**:
  - Live video display
  - Automatic video stream connection
  - Real-time video rendering

### 2. Data Visualization (Bottom Left)

- **Purpose**: Shows real-time finger count data in graph format
- **Features**:
  - Real-time data plotting
  - Automatic graph updates
  - Time-series visualization
  - Data smoothing display

### 3. Camera Controls (Right Panel)

- **Purpose**: Adjust camera settings in real-time
- **Available Controls**:
  - **Shutter**: Exposure time (100-10000 microseconds)
  - **Gain**: ISO sensor gain (1-16x)
  - **AWB Red**: Auto white balance red channel (0.1-5.0)
  - **AWB Blue**: Auto white balance blue channel (0.1-5.0)
  - **Contrast**: Image contrast (0.0-2.0)
  - **Brightness**: Image brightness (-1.0 to +1.0)

## Using Camera Controls

### Adjusting Settings

1. Use the sliders in the right panel to adjust camera parameters
2. Changes are applied automatically when you move the sliders
3. Settings are sent to the device in real-time
4. Effects are visible immediately in the video stream

### Setting Parameters Guide

#### Shutter Speed

- **Lower values** (100-1000μs): Faster shutter, less motion blur, needs more light
- **Higher values** (5000-10000μs): Slower shutter, more light captured, may blur with movement

#### Gain (ISO)

- **Lower values** (1-4x): Less noise, needs adequate lighting
- **Higher values** (8-16x): Brighter image, more noise

#### White Balance

- **Red/Blue channels**: Adjust for different lighting conditions
- **Indoor lighting**: Typically increase red, decrease blue
- **Outdoor/daylight**: Typically decrease red, increase blue

#### Contrast & Brightness

- **Contrast**: Affects the difference between light and dark areas
- **Brightness**: Overall image luminance adjustment

## Data Monitoring

### Finger Count Display

- Real-time finger count detection data is displayed in the graph
- Data updates automatically as received from the device
- Graph shows both raw data and smoothed trend line
- Time window adjusts automatically to show recent data

### Graph Features

- **X-axis**: Time progression
- **Y-axis**: Finger count values (0-10 typically)
- **Blue line**: Raw data points
- **Red line**: Smoothed data trend

## Connection Management

### Connection Status

- Connection status is displayed in the application
- Automatic reconnection if connection is lost
- Error messages displayed for connection issues

### Reconnecting

If connection is lost:

1. The application will attempt automatic reconnection
2. Check device power and network connectivity
3. Restart the application if needed
4. Verify IP address is correct

## Common Tasks

### Optimizing Video Quality

1. Adjust **Shutter** based on lighting conditions
2. Increase **Gain** in low light (accept some noise)
3. Fine-tune **White Balance** for color accuracy
4. Adjust **Contrast** for better definition

### Improving Finger Detection

1. Ensure adequate lighting
2. Use contrasting background
3. Keep hand at consistent distance from camera
4. Minimize camera movement

### Troubleshooting

#### Video Stream Issues

- **Black screen**: Check RTSP connection, verify camera is working
- **Choppy video**: Check network connection, reduce video quality settings
- **Wrong colors**: Adjust white balance settings

#### Data Display Issues

- **No graph updates**: Check TCP data connection (port 5000)
- **Frozen data**: Verify device is sending data, check connection status

#### Connection Problems

- **Cannot connect**: Verify IP address, check network connectivity
- **Authentication failed**: Verify password, check device status
- **Frequent disconnections**: Check network stability, device power

## Best Practices

### Optimal Setup

1. **Lighting**: Provide consistent, adequate lighting for the camera
2. **Network**: Use stable network connection (wired preferred)
3. **Position**: Keep camera stable and at appropriate distance
4. **Background**: Use contrasting background for better finger detection

### Performance Tips

1. **Start with default settings** and adjust gradually
2. **Test different lighting conditions** to find optimal settings
3. **Monitor connection status** regularly
4. **Keep device firmware updated** for best compatibility

## Keyboard Shortcuts

- **Ctrl+Q**: Quit application
- **ESC**: Close application (when focused)

## Application Limits

### Current Features

This application provides:

- Real-time video streaming via RTSP
- Live finger count data visualization
- Camera parameter adjustment
- Connection management

### Not Included

- Video recording or screenshot capabilities
- Data export functionality
- Multiple device connections
- Advanced graph analysis tools
- Settings persistence between sessions

## Support

### Getting Help

1. Check connection status in the application
2. Verify network connectivity to device
3. Review device documentation for parameter ranges
4. Check application logs for error messages

### Common Error Messages

- **"Connection failed"**: Device not reachable or wrong IP
- **"Authentication failed"**: Incorrect password
- **"Video stream unavailable"**: RTSP service not running
- **"No data received"**: TCP data service not working

For additional support, refer to the technical documentation in the `docs/` directory.
