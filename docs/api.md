# API Documentation

## TCP Communication Protocol

The application uses a custom binary packet protocol for communication with IoT devices. All packets follow a specific header format with checksum validation.

### Packet Structure

Each packet consists of:

```
[P][N][ID][Type][Length MSB][Length LSB][Payload...][Checksum]
```

#### Header Format (6 bytes)

- **Byte 0**: P = 0x00 (Packet marker)
- **Byte 1**: N = 0xFF (Packet marker)
- **Byte 2**: ID (Packet identifier)
- **Byte 3**: Type (Packet type)
- **Byte 4**: Length MSB (Payload length high byte)
- **Byte 5**: Length LSB (Payload length low byte)

#### Payload

- Variable length data (0-65535 bytes)

#### Checksum (1 byte)

- XOR checksum of entire packet (header + payload)

### Communication Ports

#### Data Stream Port: 5000

- **Purpose**: Real-time finger count data transmission
- **Packet ID**: 0x01
- **Data Type**: Numeric sensor values with timestamps

#### Settings Port: 5001

- **Purpose**: Camera settings configuration
- **Packet ID**: 0x02
- **Data Type**: Camera parameters (shutter, gain, white balance, etc.)

#### Authentication Port: 5002

- **Purpose**: Device authentication
- **Packet ID**: 0x00
- **Data Type**: Password authentication

### Packet Types and Formats

## Data Stream Packets (Port 5000)

### Finger Count Data (ID: 0x01, Type: 0x00)

**Direction**: Server → Client  
**Payload**: 9 bytes

```
[Finger Count][Timestamp (8 bytes)]
```

- **Finger Count** (1 byte): Number of detected fingers (0-255)
- **Timestamp** (8 bytes): Big-endian uint64 timestamp in milliseconds

**Example Packet**:

```
00 FF 01 00 00 09 [05] [00 00 01 8B 23 45 67 89] [CS]
```

- Finger count: 5
- Timestamp: 0x00000018B23456789

## Settings Packets (Port 5001)

### Settings Request (ID: 0x02, Type: 0x01)

**Direction**: Client → Server  
**Payload**: 0 bytes (request) or 6 bytes (command)

#### Settings Request

```
00 FF 02 01 00 00 [CS]
```

#### Settings Command  

**Payload**: 6 bytes

```
[Shutter][Gain][AWB Red][AWB Blue][Contrast][Brightness]
```

- **Shutter** (1 byte): Shutter speed / 100 (microseconds)
- **Gain** (1 byte): Direct gain value (0-255)
- **AWB Red** (1 byte): Auto white balance red * 10 (decimal precision)
- **AWB Blue** (1 byte): Auto white balance blue * 10
- **Contrast** (1 byte): Contrast * 10 (-10.0 to +10.0 range)
- **Brightness** (1 byte): Brightness mapped from -1.0,+1.0 to 0,255

### Settings Response (ID: 0x02, Type: 0x00)

**Direction**: Server → Client  
**Payload**: 9 bytes

```
[Shutter][Gain][AWB Red][AWB Blue][Contrast][Brightness][Reserved][Reserved][Reserved]
```

**Decoding**:

- Shutter (microseconds) = payload[0] * 100
- Gain = payload[1]
- AWB Red = payload[2] / 10.0
- AWB Blue = payload[3] / 10.0
- Contrast = payload[4] / 10.0
- Brightness = (payload[5] / 127.5) - 1.0

## Authentication Packets (Port 5002)

### Authentication Request (ID: 0x00, Type: 0x01)

**Direction**: Client → Server  
**Payload**: Variable length ASCII password

```
00 FF 00 01 [Len MSB][Len LSB] [Password ASCII bytes...] [CS]
```

### Authentication Success (ID: 0x00, Type: 0x00)

**Direction**: Server → Client  
**Payload**: 5 bytes ASCII "ready"

```
00 FF 00 00 00 05 [72 65 61 64 79] [CS]
```

- Payload: "ready" (ASCII)

### Authentication Failure (ID: 0x00, Type: 0x02)

**Direction**: Server → Client  
**Payload**: Variable length error message

```
00 FF 00 02 [Len MSB][Len LSB] [Error message...] [CS]
```

## Checksum Calculation

The checksum is calculated as XOR of all packet bytes (header + payload):

```python
def calculate_checksum(packet_data):
    return reduce(lambda x, y: x ^ y, packet_data)
```

## Connection Management

### Connection States

- **Disconnected**: No active connection
- **Connected**: TCP socket established
- **Authenticated**: Password verification completed (Auth port only)

### Timeouts and Reconnection

- **Data Timeout**: 2.0 seconds (connection considered stale)
- **Reconnect Delay**: 1.0 second between connection attempts
- **Socket Timeout**: 1.0 second for individual operations

### Connection Flow

1. Establish TCP socket connection
2. Send authentication request (Auth port only)
3. Wait for authentication response
4. Begin data/settings communication
5. Monitor connection health via data timeout

## Error Handling

### Connection Errors

- **Connection Refused**: Server not running or port blocked
- **Timeout**: No response within timeout period  
- **Invalid Header**: Packet markers don't match (0x00, 0xFF)
- **Checksum Mismatch**: Packet corruption detected
- **Payload Length Mismatch**: Incomplete packet received

### Recovery Mechanisms

- Automatic reconnection with exponential backoff
- Packet validation and discard on corruption
- Connection health monitoring via data timestamps
- Graceful degradation when services unavailable

## Implementation Examples

### Creating a Data Packet

```python
def create_packet(id_, typ, payload=b''):
    header = bytes([
        0x00, 0xFF,              # Packet markers
        id_,                     # Packet ID
        typ,                     # Packet type
        len(payload) >> 8,       # Length MSB
        len(payload) & 0xFF      # Length LSB
    ])
    packet = header + payload
    checksum = reduce(lambda x, y: x ^ y, packet)
    return packet + bytes([checksum])
```

### Reading a Packet

```python
def read_packet(socket):
    # Read 6-byte header
    header = socket.recv(6)
    if header[0] != 0x00 or header[1] != 0xFF:
        raise ValueError("Invalid packet markers")
    
    id_ = header[2]
    typ = header[3]
    payload_len = (header[4] << 8) | header[5]
    
    # Read payload + checksum
    data = socket.recv(payload_len + 1)
    payload = data[:-1]
    received_checksum = data[-1]
    
    # Verify checksum
    packet = header + payload
    calculated_checksum = reduce(lambda x, y: x ^ y, packet)
    if calculated_checksum != received_checksum:
        raise ValueError("Checksum mismatch")
    
    return id_, typ, payload
```

### Settings Update Example

```python
# Update camera settings
settings = {
    'shutter': 10000,    # 10ms = 10000 microseconds
    'gain': 64,          # Gain value
    'awb_red': 1.5,      # White balance red
    'awb_blue': 1.2,     # White balance blue  
    'contrast': 1.0,     # Contrast
    'brightness': 0.0    # Brightness
}

# Pack into payload
payload = bytes([
    (settings['shutter'] // 100) & 0xFF,     # 100
    int(settings['gain']),                   # 64
    int(settings['awb_red'] * 10),          # 15
    int(settings['awb_blue'] * 10),         # 12
    int(settings['contrast'] * 10),         # 10
    int((settings['brightness'] + 1.0) * 127.5)  # 127
])

# Create and send packet
packet = create_packet(0x02, 0x01, payload)
socket.send(packet)
