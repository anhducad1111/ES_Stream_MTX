import socket
import threading
import ffmpeg
import numpy as np
import cv2
import customtkinter as ctk
from PIL import Image

# === CẤU HÌNH ===
SERVER_IP = "192.168.137.112"
TCP_PORT = 5000
RTSP_URL = f"rtsp://{SERVER_IP}:8554/ES_MTX"

width, height = 640, 480

# === Biến dùng chung để lưu dữ liệu nhận được ===
finger_count = 0
run = True

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("RTSP Stream + TCP Data")
        self.geometry(f"{width}x{height+50}")
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Set window size to screen size
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        self.after(0, lambda: self.state('zoomed'))

        # Create frame to hold video
        self.video_frame = ctk.CTkLabel(self, text="")
        self.video_frame.pack(pady=5)
        
        # Create label for finger count
        self.data_label = ctk.CTkLabel(self, 
                                     text="Random value: 0",
                                     font=("Helvetica", 20))
        self.data_label.pack(pady=5)
        
        # Initialize video capture
        self.setup_video_stream()
        
        # Start update loop
        self.update()
        
    def setup_video_stream(self):
        self.process = (
            ffmpeg
            .input(RTSP_URL, rtsp_transport='udp', flags='low_delay', 
                fflags='nobuffer', probesize='500000', analyzeduration='1000000', r='24')
            .output('pipe:', format='rawvideo', pix_fmt='bgr24')
            .run_async(pipe_stdout=True)
        )
        
    def update(self):
        if not run:
            self.process.stdout.close()
            self.quit()
            return
            
        # Read frame
        in_bytes = self.process.stdout.read(width * height * 3)
        if not in_bytes:
            self.after(1, self.update)
            return
            
        # Convert frame to format for CTk
        frame = np.frombuffer(in_bytes, np.uint8).reshape([height, width, 3])
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
        img = Image.fromarray(frame)
        
        # Convert to CTkImage
        ctk_image = ctk.CTkImage(light_image=img, 
                                dark_image=img,
                                size=(width, height))
        
        # Update video frame
        self.video_frame.configure(image=ctk_image)
        
        # Update data label
        self.data_label.configure(text=f"Random value: {finger_count}")
        
        # Schedule next update
        self.after(1, self.update)

# === Hàm tính checksum ===
def is_valid_packet(data):
    if len(data) != 4:
        return False
    checksum = data[0] ^ data[1] ^ data[2]
    return checksum == data[3]

# === Thread nhận TCP data từ server ===
def tcp_receiver():
    global finger_count, run
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_IP, TCP_PORT))
    try:
        while run:
            data = client.recv(4)
            if is_valid_packet(data):
                typ, id_, value, _ = data
                if typ == 1 and id_ == 0x02:
                    finger_count = value  # Cập nhật số ngón tay nhận được
    except Exception as e:
        print("TCP Receive Error:", e)
    finally:
        client.close()

if __name__ == "__main__":
    # === Khởi chạy thread TCP song song ===
    tcp_thread = threading.Thread(target=tcp_receiver, daemon=True)
    tcp_thread.start()
    
    # === Khởi chạy giao diện ===
    app = App()
    app.mainloop()