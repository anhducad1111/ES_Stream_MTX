import subprocess
import socket
import threading
import time
import random

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
        # Khởi động RTSP
        self.libcamera_proc = subprocess.Popen(libcamera_cmd, stdout=subprocess.PIPE)
        self.ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdin=self.libcamera_proc.stdout)
        print("Streaming tới rtsp://<IP_RPI>:8554/ES_MTX")

        # TCP server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(1)
        self.running = True
        print(f"TCP Server listening on {host}:{port}")

    def calculate_checksum(self, data):
        return data[0] ^ data[1] ^ data[2]

    def handle_client(self, client_socket):
        try:
            while self.running:
                random_value = random.randint(0, 10)
                response = bytes([1, 0x02, random_value, 0])
                response = response[:-1] + bytes([self.calculate_checksum(response)])
                
                client_socket.send(response)
                
                time.sleep(1 / 24)  # Gửi đúng 24 gói/s
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