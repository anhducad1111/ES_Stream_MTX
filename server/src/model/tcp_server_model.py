"""
TCP Server Model Module
Handles TCP server operations and client communication protocols.
"""

# Standard library imports
import json
import logging
import random
import socket
import struct
import threading
import time
from typing import Optional, Dict, Any

# Third-party imports

# Local application imports
from .camera_model import CameraModel


# Configure logging
logger = logging.getLogger(__name__)


class TCPServerError(Exception):
    """Raised when TCP server operations fail."""
    pass


class ProtocolError(Exception):
    """Raised when communication protocol errors occur."""
    pass


class TCPServerModel:
    """
    Base class for TCP servers following the communication protocol.
    
    Provides common functionality for packet handling and client management.
    """

    def __init__(self, host: str = '0.0.0.0', port: int = 5000):
        """
        Initialize TCP server.
        
        Args:
            host: Server host address
            port: Server port number
            
        Raises:
            TCPServerError: If server cannot be initialized
        """
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((host, port))
            self.server.listen(1)
            self.running = True
            self.host = host
            self.port = port
            logger.info(f"TCP Server initialized on {host}:{port}")
        except OSError as e:
            logger.error(f"Failed to initialize TCP server: {e}")
            raise TCPServerError(f"Server initialization failed: {e}")

    def calculate_checksum(self, data: bytes) -> int:
        """
        Calculate XOR checksum for data packet.
        
        Args:
            data: Packet data bytes
            
        Returns:
            int: Calculated checksum value
        """
        result = 0
        for b in data:
            result ^= b
        return result

    def run(self) -> None:
        """
        Start server and handle incoming connections.
        
        Creates daemon threads for each client connection.
        """
        logger.info(f"Starting TCP server on {self.host}:{self.port}")
        while self.running:
            try:
                client_socket, addr = self.server.accept()
                logger.info(f"Client connected from {addr}")
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket,), 
                    daemon=True
                )
                client_thread.start()
            except OSError:
                if self.running:
                    logger.error("Server socket error occurred")
                break
            except Exception as e:
                logger.error(f"Unexpected error in server loop: {e}")
                break
        self.cleanup()

    def handle_client(self, client_socket: socket.socket) -> None:
        """
        Handle individual client connection.
        
        Args:
            client_socket: Connected client socket
            
        Note:
            This method should be overridden by subclasses
        """
        raise NotImplementedError("Subclasses must implement handle_client method")

    def cleanup(self) -> None:
        """Clean up server resources."""
        self.running = False
        try:
            self.server.close()
            logger.info("TCP server closed successfully")
        except Exception as e:
            logger.error(f"Error during server cleanup: {e}")


class DataServerModel(TCPServerModel):
    """
    Handles numeric data streaming to clients.
    
    Sends continuous data packets with random values and timestamps
    at 24 Hz frequency.
    """

    def __init__(self, host: str = '0.0.0.0', port: int = 5000):
        """
        Initialize data server.
        
        Args:
            host: Server host address  
            port: Server port number
        """
        super().__init__(host, port)
        self.camera_mgr = CameraModel()

    def start_camera_streaming(self) -> None:
        """Start camera streaming when server starts."""
        try:
            self.camera_mgr.start_camera()
            logger.info("Camera streaming started for data server")
            logger.info("Streaming available at rtsp://<IP_RPI>:8554/ES_MTX")
        except Exception as e:
            logger.error(f"Failed to start camera streaming: {e}")

    def handle_client(self, client_socket: socket.socket) -> None:
        """
        Handle data streaming client connection.
        
        Args:
            client_socket: Connected client socket
        """
        try:
            while self.running:
                # Generate data packet
                random_value = random.randint(0, 10)
                timestamp_ms = int(time.time() * 1000)
                
                # Create data packet structure
                timestamp_bytes = struct.pack('>Q', timestamp_ms)
                payload = bytes([random_value]) + timestamp_bytes
                
                packet = bytes([
                    0x00,           # P
                    0xFF,           # N
                    0x01,           # ID (Data)
                    0x00,           # Type (Response)
                    0x00, 0x09      # Payload Length (9 bytes)
                ]) + payload + bytes([0])
                
                # Calculate and append checksum
                packet = packet[:-1] + bytes([self.calculate_checksum(packet[:-1])])
                client_socket.send(packet)
                time.sleep(1 / 24)  # 24 Hz frequency

        except (socket.error, ConnectionResetError) as e:
            logger.info(f"Data client disconnected: {e}")
        except Exception as e:
            logger.error(f"Error handling data client: {e}")
        finally:
            client_socket.close()

    def cleanup(self) -> None:
        """Clean up data server resources including camera."""
        super().cleanup()
        try:
            self.camera_mgr.stop_camera()
            logger.info("Camera streaming stopped")
        except Exception as e:
            logger.error(f"Error stopping camera: {e}")


class SettingsServerModel(TCPServerModel):
    """
    Handles camera settings requests and updates.
    
    Processes settings queries and configuration updates from clients.
    """

    def __init__(self, host: str = '0.0.0.0', port: int = 5001):
        """
        Initialize settings server.
        
        Args:
            host: Server host address
            port: Server port number
        """
        super().__init__(host, port)
        self.camera_mgr = CameraModel()

    def handle_client(self, client_socket: socket.socket) -> None:
        """
        Handle settings client connection.
        
        Args:
            client_socket: Connected client socket
        """
        client_socket.settimeout(1.0)
        logger.info("Settings client connected")

        try:
            while self.running:
                try:
                    # Read request header
                    header = client_socket.recv(6)
                    if not header or len(header) != 6:
                        continue

                    if header[0] != 0x00 or header[1] != 0xFF:
                        continue

                    id_ = header[2]
                    typ = header[3]
                    payload_len = (header[4] << 8) | header[5]

                    # Get payload if present
                    payload = None
                    if payload_len > 0:
                        payload = client_socket.recv(payload_len)
                        if len(payload) != payload_len:
                            continue

                    # Handle settings requests
                    if id_ == 0x02 and typ == 0x01:
                        self._handle_settings_request(client_socket, payload_len, payload)

                except socket.timeout:
                    pass  # Normal timeout, continue loop
                except Exception as e:
                    logger.error(f"Error handling settings client: {e}")
                    break

        except (socket.error, ConnectionResetError) as e:
            logger.info(f"Settings client disconnected: {e}")
        finally:
            client_socket.close()

    def _handle_settings_request(self, client_socket: socket.socket, 
                               payload_len: int, payload: Optional[bytes]) -> None:
        """
        Process settings request or update.
        
        Args:
            client_socket: Client socket connection
            payload_len: Length of payload data
            payload: Payload data bytes
        """
        try:
            if payload_len == 0:  # Request current settings
                self._send_current_settings(client_socket)
            elif payload_len == 6:  # Update settings command
                self._update_camera_settings(payload)
        except Exception as e:
            logger.error(f"Error handling settings request: {e}")

    def _send_current_settings(self, client_socket: socket.socket) -> None:
        """
        Send current camera settings to client.
        
        Args:
            client_socket: Client socket connection
        """
        settings = self.camera_mgr.get_settings()
        settings_data = bytes([
            (settings['shutter'] // 100) & 0xFF,
            int(settings['gain']),
            int(settings['awb_red'] * 10),
            int(settings['awb_blue'] * 10),
            int(settings['contrast'] * 10),
            int((settings['brightness'] + 1.0) * 127.5),
            0, 0, 0  # padding
        ])

        packet = bytes([
            0x00,           # P
            0xFF,           # N
            0x02,           # ID (Settings)
            0x00,           # Type (Response)
            0x00, 0x09      # Payload Length
        ]) + settings_data + bytes([0])

        packet = packet[:-1] + bytes([self.calculate_checksum(packet[:-1])])
        client_socket.send(packet)
        logger.info("Sent current camera settings to client")

    def _update_camera_settings(self, payload: bytes) -> None:
        """
        Update camera settings from payload data.
        
        Args:
            payload: Settings data bytes
        """
        new_settings = {
            'shutter': payload[0] * 100,
            'gain': payload[1],
            'awb_red': payload[2] / 10.0,
            'awb_blue': payload[3] / 10.0,
            'contrast': payload[4] / 10.0,
            'brightness': (payload[5] / 127.5) - 1.0
        }
        self.camera_mgr.update_settings(new_settings)
        logger.info("Camera settings updated successfully")


class AuthServerModel(TCPServerModel):
    """
    Handles client authentication requests.
    
    Validates passwords and sends appropriate responses.
    """

    def __init__(self, host: str = '0.0.0.0', port: int = 5002):
        """
        Initialize authentication server.
        
        Args:
            host: Server host address
            port: Server port number
        """
        super().__init__(host, port)
        self.valid_password = "1111"

    def handle_client(self, client_socket: socket.socket) -> None:
        """
        Handle authentication client connection.
        
        Args:
            client_socket: Connected client socket
        """
        client_socket.settimeout(5.0)
        logger.info("Authentication client connected")
        
        try:
            # Read authentication request
            header = client_socket.recv(6)
            if not header or len(header) != 6:
                logger.warning("Invalid authentication header received")
                return
            
            if header[0] != 0x00 or header[1] != 0xFF:
                logger.warning("Invalid authentication packet format")
                return
            
            id_ = header[2]
            typ = header[3]
            payload_len = (header[4] << 8) | header[5]
            
            # Process authentication request
            if id_ == 0x00 and typ == 0x01:
                self._process_auth_request(client_socket, header, payload_len)
            else:
                logger.warning(f"Invalid auth request: ID={id_:02x}, Type={typ:02x}")
                
        except socket.timeout:
            logger.warning("Authentication client timeout")
        except Exception as e:
            logger.error(f"Authentication client error: {e}")
        finally:
            client_socket.close()

    def _process_auth_request(self, client_socket: socket.socket, 
                            header: bytes, payload_len: int) -> None:
        """
        Process authentication request with password validation.
        
        Args:
            client_socket: Client socket connection
            header: Request header bytes
            payload_len: Length of password payload
        """
        try:
            if payload_len > 0:
                # Get password payload and checksum
                password_payload = client_socket.recv(payload_len)
                if len(password_payload) != payload_len:
                    logger.warning("Invalid password payload length")
                    return
                
                checksum_byte = client_socket.recv(1)
                if len(checksum_byte) != 1:
                    logger.warning("Missing authentication checksum")
                    return
                
                # Verify checksum
                packet = header + password_payload
                expected_checksum = self.calculate_checksum(packet)
                
                if checksum_byte[0] != expected_checksum:
                    logger.warning("Invalid authentication checksum")
                    return
                
                # Validate password
                received_password = password_payload.decode('ascii', errors='ignore')
                logger.debug(f"Authentication attempt with password length: {len(received_password)}")
                
                if received_password == self.valid_password:
                    self._send_success_response(client_socket)
                else:
                    self._send_error_response(client_socket)
            else:
                logger.warning("No password provided in authentication request")
                
        except Exception as e:
            logger.error(f"Error processing authentication request: {e}")

    def _send_success_response(self, client_socket: socket.socket) -> None:
        """
        Send successful authentication response.
        
        Args:
            client_socket: Client socket connection
        """
        success_payload = b'ready'
        response_packet = bytes([
            0x00,           # P
            0xFF,           # N
            0x00,           # ID (Auth)
            0x00,           # Type (Response)
            0x00, len(success_payload)  # Payload Length
        ]) + success_payload
        
        response_packet += bytes([self.calculate_checksum(response_packet)])
        client_socket.send(response_packet)
        logger.info("Authentication successful - sent 'ready' response")

    def _send_error_response(self, client_socket: socket.socket) -> None:
        """
        Send authentication error response.
        
        Args:
            client_socket: Client socket connection
        """
        error_packet = bytes([
            0x00,           # P
            0xFF,           # N
            0x00,           # ID (Auth)
            0x02,           # Type (Error)
            0x00, 0x00      # No payload
        ])
        
        error_packet += bytes([self.calculate_checksum(error_packet)])
        client_socket.send(error_packet)
        logger.info("Authentication failed - wrong password")

    def set_password(self, new_password: str) -> None:
        """
        Update the valid authentication password.
        
        Args:
            new_password: New password string
        """
        self.valid_password = new_password
        logger.info("Authentication password updated")