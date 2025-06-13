import subprocess
import socket
import threading
import time
import random
import struct
import json

class CameraManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not CameraManager._initialized:
            # Load settings
            try:
                with open('/home/ad/Desktop/WS/stream_rtsp/config/camera_settings.json', 'r') as f:
                    self.settings = json.load(f)
                    print("Loaded camera settings:", self.settings)
            except Exception as e:
                print(f"Error loading settings: {e}, using defaults")
                self.settings = {
                    'shutter': 10000,
                    'gain': 1,
                    'awb_red': 1.0,
                    'awb_blue': 1.0,
                    'contrast': 1.0,
                    'brightness': 0.0
                }
            
            self.libcamera_proc = None
            self.ffmpeg_proc = None
            CameraManager._initialized = True

    def get_camera_cmd(self):
        return [
            "libcamera-vid",
            "-t", "0",
            "--width", "640",
            "--height", "480",
            "--framerate", "24",
            "--codec", "h264",
            "--inline",
            "--profile", "baseline",
            "--level", "4.2",
            "--vflip",
            "--nopreview",
            "--shutter", str(self.settings['shutter']),
            "--gain", str(self.settings['gain']),
            "--awbgains", f"{self.settings['awb_red']:.2f},{self.settings['awb_blue']:.2f}",
            "--contrast", str(self.settings['contrast']),
            "--brightness", str(self.settings['brightness']),
            "-o", "-"
        ]

    def get_ffmpeg_cmd(self):
        return [
            "ffmpeg",
            "-fflags", "nobuffer",
            "-flags", "low_delay",
            "-probesize", "32",
            "-analyzeduration", "0",
            "-r", "24",
            "-f", "h264",
            "-i", "-",
            "-c:v", "copy",
            "-f", "rtsp",
            "rtsp://localhost:8554/ES_MTX"
        ]

    def start_camera(self):
        print("Starting camera...")
        self.libcamera_proc = subprocess.Popen(self.get_camera_cmd(), stdout=subprocess.PIPE)
        self.ffmpeg_proc = subprocess.Popen(self.get_ffmpeg_cmd(), stdin=self.libcamera_proc.stdout)

    def stop_camera(self):
        if self.libcamera_proc:
            self.libcamera_proc.terminate()
        if self.ffmpeg_proc:
            self.ffmpeg_proc.terminate()

    def update_settings(self, new_settings):
        print("Updating camera settings:", new_settings)
        self.settings.update(new_settings)
        with open('/home/ad/Desktop/WS/stream_rtsp/config/camera_settings.json', 'w') as f:
            json.dump(self.settings, f)
        self.stop_camera()
        time.sleep(0.5)  # Wait for processes to close
        self.start_camera()

class TCPServerBase:
    """Base class for TCP servers"""
    def __init__(self, host='0.0.0.0', port=5000):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(1)
        self.running = True
        print(f"TCP Server listening on {host}:{port}")

    def calculate_checksum(self, data):
        result = 0
        for b in data:
            result ^= b
        return result

    def run(self):
        while self.running:
            try:
                client_socket, addr = self.server.accept()
                print(f"Client connected from {addr}")
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True)
                client_thread.start()
            except:
                break
        self.server.close()

    def cleanup(self):
        self.running = False

class DataServer(TCPServerBase):
    """Handles numeric data streaming"""
    def __init__(self, host='0.0.0.0', port=5000):
        super().__init__(host, port)
        self.camera_mgr = CameraManager()
        self.camera_mgr.start_camera()
        print("Streaming to rtsp://<IP_RPI>:8554/ES_MTX")

    def handle_client(self, client_socket):
        try:
            while self.running:
                # Send data packet
                random_value = random.randint(0, 10)
                timestamp_ms = int(time.time() * 1000)
                
                # Create data packet
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
                time.sleep(1 / 24)  # 24 Hz

        except (socket.error, ConnectionResetError) as e:
            print(f"Data client disconnected: {e}")
        finally:
            client_socket.close()

    def cleanup(self):
        super().cleanup()
        self.camera_mgr.stop_camera()

class SettingsServer(TCPServerBase):
    """Handles settings requests"""
    def __init__(self, host='0.0.0.0', port=5001):
        super().__init__(host, port)
        self.camera_mgr = CameraManager()

    def handle_client(self, client_socket):
        client_socket.settimeout(1.0)
        print("Settings client connected")

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

                    # Handle settings requests and commands
                    if id_ == 0x02 and typ == 0x01:
                        try:
                            print(f"Got settings packet: len={payload_len}")
                            if payload_len == 0:  # Request current settings
                                # Send current settings (6 parameters)
                                settings_data = bytes([
                                    (self.camera_mgr.settings['shutter'] // 100) & 0xFF,  # shutter / 100
                                    int(self.camera_mgr.settings['gain']),
                                    int(self.camera_mgr.settings['awb_red'] * 10),
                                    int(self.camera_mgr.settings['awb_blue'] * 10),
                                    int(self.camera_mgr.settings['contrast'] * 10),
                                    int((self.camera_mgr.settings['brightness'] + 1.0) * 127.5),  # map -1,1 to 0,255
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
                                print("Sent current settings")

                            elif payload_len == 6:  # Update settings command (6 parameters)
                                print("Processing settings update command")
                                # Update settings
                                new_settings = {
                                    'shutter': payload[0] * 100,  # multiply by 100 to get microseconds
                                    'gain': payload[1],
                                    'awb_red': payload[2] / 10.0,
                                    'awb_blue': payload[3] / 10.0,
                                    'contrast': payload[4] / 10.0,
                                    'brightness': (payload[5] / 127.5) - 1.0  # map 0,255 to -1,1
                                }
                                self.camera_mgr.update_settings(new_settings)

                        except Exception as e:
                            print(f"Error handling settings: {e}")

                except socket.timeout:
                    pass  # Normal timeout
                except Exception as e:
                    print(f"Error handling client: {e}")
                    break

        except (socket.error, ConnectionResetError) as e:
            print(f"Settings client disconnected: {e}")
        finally:
            client_socket.close()

if __name__ == "__main__":
    data_server = DataServer(port=5000)
    settings_server = SettingsServer(port=5001)

    data_thread = threading.Thread(target=data_server.run, daemon=True)
    settings_thread = threading.Thread(target=settings_server.run, daemon=True)

    try:
        data_thread.start()
        settings_thread.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping servers...")
        data_server.cleanup()
        settings_server.cleanup()