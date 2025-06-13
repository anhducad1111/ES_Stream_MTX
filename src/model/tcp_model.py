import socket
import threading
import struct
import time
from abc import ABC, abstractmethod
from functools import reduce

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
        return reduce(lambda x, y: x ^ y, data)

    def _create_packet(self, id_, typ, payload=b''):
        """Create a packet with header and checksum"""
        header = bytes([
            0x00, 0xFF,  # P, N
            id_,         # ID
            typ,         # Type
            len(payload) >> 8,  # Length MSB
            len(payload) & 0xFF # Length LSB
        ])
        packet = header + payload
        return packet + bytes([self._calculate_checksum(packet)])

    def _read_packet(self, client):
        """Read and validate a complete packet"""
        # Read packet header
        header = client.recv(6)
        if not header or len(header) != 6:
            raise ConnectionError("Invalid header")

        if header[0] != 0x00 or header[1] != 0xFF:
            return None, None, None

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
            return None, None, None

        return id_, typ, data[:-1]

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
            client = None
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
                        self._on_connect(client)

                while self.run and self.connected:
                    try:
                        id_, typ, payload = self._read_packet(client)
                        if id_ is not None:
                            self._handle_packet(id_, typ, payload)
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
                if client:
                    client.close()
                time.sleep(self.reconnect_delay)

    def _on_connect(self, client):
        """Called when connection is established"""
        pass

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
        self.client = None

    def send_command(self, settings):
        """Send settings update command"""
        if not self.connected or not self.client:
            print("Not connected - cannot send settings")
            return False

        try:
            # Pack settings into 5-byte payload
            payload = bytes([
                int(settings['gain']),                  # Direct value
                int(float(settings['exposure']) * 10),  # *10 for decimal
                int(float(settings['awb_red']) * 10),
                int(float(settings['awb_green']) * 10),
                int(float(settings['awb_blue']) * 10)
            ])

            packet = self._create_packet(0x02, 0x01, payload)
            self.client.send(packet)
            print("Sent settings command:", settings)
            return True

        except Exception as e:
            print(f"Error sending settings command: {e}")
            return False

    def _on_connect(self, client):
        """Store client socket and send initial settings request"""
        self.client = client
        self.next_request_time = time.time()
        
        if not self.settings_received:
            request = self._create_packet(0x02, 0x01)
            self.client.send(request)
            print("Requesting settings...")

    def _handle_packet(self, id_, typ, payload):
        """Handle settings packets"""
        if id_ != 0x02:  # Not a settings packet
            return

        if typ == 0x00 and len(payload) == 9:  # Settings response
            try:
                # Get raw values from payload
                gain = payload[0]  # Direct value
                exposure = float(payload[1]) / 10.0  # Multiply by 10 on server
                awb_red = float(payload[2]) / 10.0
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
                self.settings_received = True
            except Exception as e:
                print(f"Error unpacking settings: {e}")
                self.settings_received = False

    def get_settings(self):
        return self.settings