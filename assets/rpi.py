import subprocess
import socket
import threading
import time
import random
import struct

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

class TCPServer:
    def __init__(self, host='0.0.0.0', port=5000):
        # Start RTSP
        self.libcamera_proc = subprocess.Popen(libcamera_cmd, stdout=subprocess.PIPE)
        self.ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdin=self.libcamera_proc.stdout)
        print("Streaming to rtsp://<IP_RPI>:8554/ES_MTX")

        # TCP server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(1)
        self.running = True
        print(f"TCP Server listening on {host}:{port}")

    def calculate_checksum(self, data):
        # Calculate checksum from all bytes except the last one (checksum byte)
        result = 0
        for b in data[:-1]:
            result ^= b
        return result

    def handle_client(self, client_socket):
        try:
            while self.running:
                random_value = random.randint(0, 10)
                
                # Get current timestamp in milliseconds
                timestamp_ms = int(time.time() * 1000)
                
                # Create packet format:
                # [P(1)][N(1)][id(1)][type(1)][payload_len(2)][payload(9)][checksum(1)]
                
                # Convert timestamp to 8 bytes
                timestamp_bytes = struct.pack('>Q', timestamp_ms)  # big-endian 8-byte unsigned long long
                
                # Create payload (1B value + 8B timestamp)
                payload = bytes([random_value]) + timestamp_bytes
                
                # Create packet with fixed P=0x00, N=0xFF
                packet = bytes([
                    0x00,           # P (fixed value)
                    0xFF,           # N (fixed value)
                    0x01,           # ID (Data)
                    0x00,           # Type (Response)
                    0x00, 0x09      # Payload Length (2 bytes = 9)
                ]) + payload + bytes([0])
                
                # Calculate and set checksum
                packet = packet[:-1] + bytes([self.calculate_checksum(packet)])
                
                client_socket.send(packet)
                
                time.sleep(1 / 24)  # Send 24 packets/s
        except (socket.error, ConnectionResetError):
            print("Client disconnected.")
        finally:
            client_socket.close()

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
        self.libcamera_proc.terminate()
        self.ffmpeg_proc.terminate()

if __name__ == "__main__":
    server = TCPServer()
    try:
        server.run()
    except KeyboardInterrupt:
        print("Stopping server...")
        server.cleanup()