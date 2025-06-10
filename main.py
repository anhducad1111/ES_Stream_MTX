import socket
import threading
import ffmpeg
import numpy as np
import cv2
import customtkinter as ctk
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import time
import queue

# === CẤU HÌNH ===
SERVER_IP = "192.168.137.112"
TCP_PORT = 5000
RTSP_URL = f"rtsp://{SERVER_IP}:8554/ES_MTX"
width, height = 640, 480

# === Biến dùng chung ===
finger_count = 0
run = True

class VideoThread(threading.Thread):
    def __init__(self, rtsp_url):
        super().__init__(daemon=True)
        self.rtsp_url = rtsp_url
        self.frame_queue = queue.Queue(maxsize=2)
        self.running = True
        
    def run(self):
        process = (
            ffmpeg
            .input(self.rtsp_url, rtsp_transport='udp', flags='low_delay', 
                fflags='nobuffer', probesize='500000', analyzeduration='1000000', r='24')
            .output('pipe:', format='rawvideo', pix_fmt='bgr24')
            .run_async(pipe_stdout=True)
        )
        
        while self.running:
            in_bytes = process.stdout.read(width * height * 3)
            if not in_bytes:
                continue
                
            frame = np.frombuffer(in_bytes, np.uint8).reshape([height, width, 3])
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            try:
                self.frame_queue.put_nowait(frame)
            except queue.Full:
                self.frame_queue.get_nowait()  # Remove old frame
                self.frame_queue.put_nowait(frame)  # Add new frame
                    
        process.stdout.close()
        
    def get_frame(self):
        try:
            return self.frame_queue.get_nowait()
        except queue.Empty:
            return None

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RTSP Stream + TCP Data")
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Set window size to screen size
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        self.after(0, lambda: self.state('zoomed'))

        # Configure left frame
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.left_frame.grid_rowconfigure(0, weight=3)
        self.left_frame.grid_rowconfigure(1, weight=1)
        
        # Video frame
        self.video_label = ctk.CTkLabel(self.left_frame, text="")
        self.video_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Setup chart
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(6, 2))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.left_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Initialize data
        self.times = deque(maxlen=100)
        self.values = deque(maxlen=100)
        self.start_time = time.time()
        self.last_chart_update = 0
        
        # Start video thread
        self.video_thread = VideoThread(RTSP_URL)
        self.video_thread.start()
        
        self.update()
        
    def update_chart(self):
        current_time = time.time()
        if current_time - self.last_chart_update >= 0.1:  # Update every 100ms
            self.times.append(current_time - self.start_time)
            self.values.append(finger_count)
            
            self.ax.clear()
            self.ax.plot(list(self.times), list(self.values), color='#00ff00')
            self.ax.grid(True, alpha=0.3)
            
            self.fig.tight_layout()
            self.canvas.draw()
            self.last_chart_update = current_time
        
    def update(self):
        if not run:
            self.video_thread.running = False
            self.quit()
            return
            
        frame = self.video_thread.get_frame()
        if frame is not None:
            img = Image.fromarray(frame)
            ctk_image = ctk.CTkImage(light_image=img, 
                                   dark_image=img,
                                   size=(width, height))
            self.video_label.configure(image=ctk_image)
        
        self.update_chart()
        self.after(1, self.update)

def tcp_receiver():
    global finger_count, run
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_IP, TCP_PORT))
    try:
        while run:
            data = client.recv(4)
            if len(data) == 4 and data[0] ^ data[1] ^ data[2] == data[3]:
                typ, id_, value, _ = data
                if typ == 1 and id_ == 0x02:
                    finger_count = value
    except Exception as e:
        print("TCP Error:", e)
    finally:
        client.close()

if __name__ == "__main__":
    threading.Thread(target=tcp_receiver, daemon=True).start()
    App().mainloop()