import subprocess
import socket
import threading
import time
import random
import struct
import json

# Load camera settings first
try:
    with open('config/camera_settings.json', 'r') as f:
        settings = json.load(f)
        print("Loaded camera settings:", settings)
except Exception as e:
    print(f"Error loading settings: {e}, using defaults")
    settings = {
        'exposure': 1.0,
        'gain': 1,
        'awb_red': 1.0,
        'awb_green': 1.0,
        'awb_blue': 1.0
    }

# Create camera command with settings
libcamera_cmd = [
    "libcamera-vid",
    "-t", "0",
    "--width", "640",
    "--height", "480",
    "--framerate", "24",
    "--bitrate", "1500000",
    "--codec", "h264",
    "--inline",
    "--profile", "baseline",
    "--level", "4.2",
    "--intra", "15",
    "--vflip",
    "--nopreview",
    "--exposure", "normal",
    "--ev", str(settings['exposure']),
    "--gain", str(settings['gain']),
    "--awbgains", f"{settings['awb_red']},{settings['awb_green']},{settings['awb_blue']}",
    "-o", "-"
]

ffmpeg_cmd = [
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
        # Start RTSP
        self.libcamera_proc = subprocess.Popen(libcamera_cmd, stdout=subprocess.PIPE)
        self.ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdin=self.libcamera_proc.stdout)
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
        self.libcamera_proc.terminate()
        self.ffmpeg_proc.terminate()

class SettingsServer(TCPServerBase):
    """Handles settings requests"""
    def __init__(self, host='0.0.0.0', port=5001):
        super().__init__(host, port)
        self.settings_file = 'config/camera_settings.json'

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

                    # Handle settings request
                    if id_ == 0x02 and typ == 0x01:
                        try:
                            # Use the global settings loaded at startup
                            settings_data = bytes([
                                int(settings['gain']),  # gain as-is
                                int(settings['exposure'] * 10),  # exposure * 10 to preserve 1 decimal
                                int(settings['awb_red'] * 10),  # awb * 10 to preserve 1 decimal
                                int(settings['awb_green'] * 10),
                                int(settings['awb_blue'] * 10),
                                0, 0, 0, 0  # padding
                            ])

                            # Create response packet
                            packet = bytes([
                                0x00,           # P
                                0xFF,           # N
                                0x02,           # ID (Settings)
                                0x00,           # Type (Response)
                                0x00, 0x09      # Payload Length
                            ]) + settings_data + bytes([0])

                            packet = packet[:-1] + bytes([self.calculate_checksum(packet[:-1])])
                            client_socket.send(packet)
                            print("Sent settings")

                        except Exception as e:
                            print(f"Error reading settings: {e}")

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