import socket
import threading
import struct
import time

class TCPReceiver:
    def __init__(self, server_ip, port):
        self.server_ip = server_ip
        self.port = port
        self.finger_count = 0
        self.timestamp_ms = 0
        self.run = True
        self.thread = None
        self.connected = False
        self.last_data_time = 0
        self.last_reconnect = 0
        self.reconnect_delay = 1.0
        self.data_timeout = 2.0  # Consider connection dead if no data for 2 seconds

    def start(self):
        self.thread = threading.Thread(target=self._tcp_receiver, daemon=True)
        self.thread.start()

    def _connect(self):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(1.0)
            client.connect((self.server_ip, self.port))
            print(f"TCP connected to {self.server_ip}:{self.port}")
            self.last_data_time = time.time()  # Reset data timer on connection
            return client
        except Exception as e:
            print(f"TCP connection failed: {e}")
            return None

    def _tcp_receiver(self):
        while self.run:
            try:
                # Check for stale connection
                if self.connected and time.time() - self.last_data_time > self.data_timeout:
                    print("TCP connection stale, reconnecting...")
                    self.connected = False
                    continue

                # Try to connect if not connected
                if not self.connected:
                    current_time = time.time()
                    if current_time - self.last_reconnect >= self.reconnect_delay:
                        print(f"Attempting to connect to TCP {self.server_ip}:{self.port}")
                        client = self._connect()
                        if not client:
                            self.last_reconnect = current_time
                            time.sleep(self.reconnect_delay)
                            continue
                        self.connected = True
                
                # Read data
                while self.run and self.connected:
                    try:
                        # Read full packet (16 bytes)
                        data = client.recv(16)
                        if not data:  # Connection closed by server
                            print("TCP connection lost - no data")
                            self.connected = False
                            break
                            
                        if len(data) != 16:
                            continue

                        # Validate packet header
                        if data[0] != 0x00 or data[1] != 0xFF:  # Check P and N
                            print("Invalid packet header")
                            continue

                        # Extract fields
                        id_ = data[2]
                        typ = data[3]
                        payload_len = (data[4] << 8) | data[5]  # Convert 2 bytes to length
                        
                        if payload_len != 9:
                            print("Invalid payload length")
                            continue

                        # Extract payload (1B value + 8B timestamp)
                        value = data[6]
                        timestamp_bytes = data[7:15]
                        timestamp = struct.unpack('>Q', timestamp_bytes)[0]

                        # Verify checksum
                        calc_checksum = 0
                        for b in data[:-1]:
                            calc_checksum ^= b
                        if calc_checksum != data[15]:
                            print("Checksum mismatch")
                            continue
                        
                        # Update values and last data time
                        if id_ == 0x01 and typ == 0x00:  # Data Response packet
                            self.finger_count = value
                            self.timestamp_ms = timestamp
                            self.last_data_time = time.time()

                    except socket.timeout:
                        # Check for stale connection on timeout
                        if time.time() - self.last_data_time > self.data_timeout:
                            print("TCP timeout - no recent data")
                            self.connected = False
                            break
                        continue
                    except Exception as e:
                        print(f"TCP read error: {e}")
                        self.connected = False
                        break

            except Exception as e:
                print(f"TCP connection error: {e}")
                self.connected = False
                
            finally:
                if client:
                    try:
                        client.close()
                    except:
                        pass
                time.sleep(self.reconnect_delay)

    def is_connected(self):
        # Only report connected if we're getting data regularly
        return self.connected and time.time() - self.last_data_time < self.data_timeout

    def stop(self):
        self.run = False
        if self.thread:
            self.thread.join(timeout=2)

    def get_finger_count(self):
        return self.finger_count

    def get_timestamp_ms(self):
        return self.timestamp_ms