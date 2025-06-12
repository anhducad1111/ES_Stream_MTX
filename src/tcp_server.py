import socket
import threading
import struct
import time
from abc import ABC, abstractmethod

class TCPBase(ABC):
    """Base class with common TCP functionality"""
    def __init__(self, server_ip, port):
        self.server_ip = server_ip
        self.port = port
        self.run = True
        self.thread = None
        self.connected = False
        self.last_data_time = 0
        self.last_reconnect = 0
        self.reconnect_delay = 1.0
        self.data_timeout = 2.0

    def _connect(self):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(1.0)
            client.connect((self.server_ip, self.port))
            print(f"TCP connected to {self.server_ip}:{self.port}")
            self.last_data_time = time.time()
            return client
        except Exception as e:
            print(f"TCP connection failed: {e}")
            return None

    def _calculate_checksum(self, data):
        result = 0
        for b in data:
            result ^= b
        return result

    def start(self):
        self.thread = threading.Thread(target=self._tcp_receiver, daemon=True)
        self.thread.start()

    def stop(self):
        self.run = False
        if self.thread:
            self.thread.join(timeout=2)

    def is_connected(self):
        return self.connected and time.time() - self.last_data_time < self.data_timeout

    def _tcp_receiver(self):
        while self.run:
            try:
                if self.connected and time.time() - self.last_data_time > self.data_timeout:
                    print(f"{self.__class__.__name__} connection stale, reconnecting...")
                    self.connected = False
                    continue

                if not self.connected:
                    current_time = time.time()
                    if current_time - self.last_reconnect >= self.reconnect_delay:
                        print(f"Attempting to connect to {self.__class__.__name__} {self.server_ip}:{self.port}")
                        client = self._connect()
                        if not client:
                            self.last_reconnect = current_time
                            time.sleep(self.reconnect_delay)
                            continue
                        self.connected = True

                while self.run and self.connected:
                    try:
                        # Read packet header
                        header = client.recv(6)
                        if not header or len(header) != 6:
                            raise ConnectionError("Invalid header")

                        if header[0] != 0x00 or header[1] != 0xFF:
                            continue

                        id_ = header[2]
                        typ = header[3]
                        payload_len = (header[4] << 8) | header[5]

                        # Read payload and checksum
                        data = client.recv(payload_len + 1)
                        if len(data) != payload_len + 1:
                            raise ConnectionError("Invalid payload")

                        # Verify checksum
                        packet = header + data[:-1]
                        if self._calculate_checksum(packet) != data[-1]:
                            continue

                        # Handle packet
                        self._handle_packet(id_, typ, data[:-1])
                        self.last_data_time = time.time()

                    except socket.timeout:
                        continue
                    except Exception as e:
                        print(f"{self.__class__.__name__} read error: {e}")
                        self.connected = False
                        break

            except Exception as e:
                print(f"{self.__class__.__name__} connection error: {e}")
                self.connected = False
            finally:
                if 'client' in locals():
                    client.close()
                time.sleep(self.reconnect_delay)

    @abstractmethod
    def _handle_packet(self, id_, typ, payload):
        """Handle specific packet types in subclasses"""
        pass

class NumberDataReceiver(TCPBase):
    """Handles receiving numeric data stream"""
    def __init__(self, server_ip, port=5000):
        super().__init__(server_ip, port)
        self.finger_count = 0
        self.timestamp_ms = 0

    def _handle_packet(self, id_, typ, payload):
        if id_ == 0x01 and typ == 0x00 and len(payload) == 9:
            value = payload[0]
            timestamp = struct.unpack('>Q', payload[1:9])[0]
            self.finger_count = value
            self.timestamp_ms = timestamp

    def get_finger_count(self):
        return self.finger_count

    def get_timestamp_ms(self):
        return self.timestamp_ms

class SettingsReceiver(TCPBase):
    """Handles settings synchronization"""
    def __init__(self, server_ip, port=5001):
        super().__init__(server_ip, port)
        self.settings = None  # Will be populated when settings are received
        self.settings_received = False  # Flag to track successful receipt

    def _tcp_receiver(self):
        while self.run:
            try:
                if self.connected and time.time() - self.last_data_time > self.data_timeout:
                    print("Settings connection stale, reconnecting...")
                    self.connected = False
                    continue

                if not self.connected:
                    current_time = time.time()
                    if current_time - self.last_reconnect >= self.reconnect_delay:
                        print(f"Attempting to connect to Settings TCP {self.server_ip}:{self.port}")
                        client = self._connect()
                        if not client:
                            self.last_reconnect = current_time
                            time.sleep(self.reconnect_delay)
                            continue
                        self.connected = True
                        self.next_request_time = current_time

                while self.run and self.connected and not self.settings_received:
                    try:
                        # Send settings request
                        request = bytes([
                            0x00, 0xFF,  # P, N
                            0x02,        # ID (Settings)
                            0x01,        # Type (Request)
                            0x00, 0x00   # Payload Length
                        ]) + bytes([0])  # Checksum placeholder
                        request = request[:-1] + bytes([self._calculate_checksum(request[:-1])])
                        client.send(request)
                        print("Requesting settings...")

                        # Wait for response
                        header = client.recv(6)
                        if not header or len(header) != 6:
                            raise ConnectionError("Invalid header")

                        if header[0] != 0x00 or header[1] != 0xFF:
                            continue

                        id_ = header[2]
                        typ = header[3]
                        payload_len = (header[4] << 8) | header[5]

                        data = client.recv(payload_len + 1)
                        if len(data) != payload_len + 1:
                            raise ConnectionError("Invalid payload")

                        packet = header + data[:-1]
                        if self._calculate_checksum(packet) != data[-1]:
                            continue

                        # Handle settings response
                        self._handle_packet(id_, typ, data[:-1])
                        if self.settings is not None:
                            self.settings_received = True
                            print("Settings received successfully")
                            break  # Exit loop after successful receipt

                    except socket.timeout:
                        continue
                    except Exception as e:
                        print(f"Settings read error: {e}")
                        self.connected = False
                        break

                # Break main loop if settings received
                if self.settings_received:
                    break

            except Exception as e:
                print(f"Settings connection error: {e}")
                self.connected = False
            finally:
                if 'client' in locals():
                    client.close()
                time.sleep(self.reconnect_delay)

    def _handle_packet(self, id_, typ, payload):
        """Handle settings response packet"""
        if id_ == 0x02 and typ == 0x00 and len(payload) == 9:
            try:
                # Get raw values from payload
                gain = payload[0]  # Direct value
                exposure = float(payload[1]) / 10.0  # Multiply by 10 on server
                awb_red = float(payload[2]) / 10.0   # Multiply by 10 on server
                awb_green = float(payload[3]) / 10.0
                awb_blue = float(payload[4]) / 10.0
                
                self.settings = {
                    'gain': gain,
                    'exposure': exposure,
                    'awb_red': awb_red,
                    'awb_green': awb_green,
                    'awb_blue': awb_blue
                }
                print("Settings received:", self.settings)
                self.settings_received = True  # Mark successful receipt
            except Exception as e:
                print(f"Error unpacking settings: {e}")
                self.settings_received = False  # Keep trying on error

    def get_settings(self):
        return self.settings