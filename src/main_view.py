import customtkinter as ctk
from PIL import Image
from .video_view import VideoThread
from .graph_view import GraphView
from .setting_view import SettingView
from .tcp_server import NumberDataReceiver, SettingsReceiver
import time

# Constants
SERVER_IP = "192.168.137.112"
TCP_PORT = 5000
RTSP_URL = f"rtsp://{SERVER_IP}:8554/ES_MTX"
width, height = 640, 480

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RTSP Stream + TCP Data")
        
        # Get screen dimensions and set window size
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        self.after(0, lambda: self.state('zoomed'))

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)  # For status bar

        # Left frame setup
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.left_frame.grid_rowconfigure(0, weight=3)
        self.left_frame.grid_rowconfigure(1, weight=1)
        
        # Video label setup
        self.video_label = ctk.CTkLabel(self.left_frame, text="")
        self.video_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Graph setup
        self.graph_view = GraphView(self.left_frame)
        self.graph_view.get_widget().grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Settings setup
        self.settings_view = SettingView(self)
        self.settings_view.get_frame().grid(row=0, column=1, padx=20, pady=20, sticky="ew")

        # Status bar setup
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.status_frame.grid_columnconfigure(0, weight=1)
        self.status_frame.grid_columnconfigure(1, weight=1)
        self.status_frame.grid_columnconfigure(2, weight=1)
        
        self.tcp_status = ctk.CTkLabel(self.status_frame, text="Data: Initializing...", fg_color="yellow")
        self.tcp_status.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        
        self.settings_status = ctk.CTkLabel(self.status_frame, text="Settings: Initializing...", fg_color="yellow")
        self.settings_status.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        self.video_status = ctk.CTkLabel(self.status_frame, text="Video: Initializing...", fg_color="yellow")
        self.video_status.grid(row=0, column=2, padx=5, pady=2, sticky="w")
        
        # Start components
        # Start TCP connections
        self.data_receiver = NumberDataReceiver(SERVER_IP, TCP_PORT)
        self.settings_receiver = SettingsReceiver(SERVER_IP, TCP_PORT + 1)
        self.data_receiver.start()
        self.settings_receiver.start()
        
        # Start video stream
        self.video_thread = VideoThread(RTSP_URL)
        self.video_thread.start()
        
        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start update loops
        self.update_status()
        self.update_video()
        self.update_graph()

    def update_status(self):
        # Update TCP Data status
        if self.data_receiver.is_connected():
            self.tcp_status.configure(text="Data: Connected", fg_color="green")
        else:
            self.tcp_status.configure(text="Data: Connecting...", fg_color="yellow")

        # Update Settings status
        # Update status indicators
        if self.settings_receiver.is_connected():
            self.settings_status.configure(text="Settings: Connected", fg_color="green")
            # Update settings UI if new data available
            settings = self.settings_receiver.get_settings()
            if settings:
                try:
                    sliders = self.settings_view.sliders
                    entries = self.settings_view.entries
                    
                    # Update sliders and entries
                    for name, value in settings.items():
                        slider_name = {
                            'exposure': 'Exposure',
                            'gain': 'Gain',
                            'awb_red': 'AWB Red',
                            'awb_green': 'AWB Green',
                            'awb_blue': 'AWB Blue'
                        }.get(name)
                        
                        if slider_name and slider_name in sliders:
                            sliders[slider_name].set(value)
                            entries[slider_name].delete(0, 'end')
                            if slider_name == 'Gain':
                                entries[slider_name].insert(0, str(int(value)))
                            else:
                                entries[slider_name].insert(0, f"{float(value):.1f}")
                except Exception as e:
                    print(f"Error updating settings UI: {e}")
        else:
            self.settings_status.configure(text="Settings: Connecting...", fg_color="yellow")

        if self.video_thread.is_connected():
            self.video_status.configure(text="Video: Streaming", fg_color="green")
        else:
            self.video_status.configure(text="Video: Connecting...", fg_color="yellow")

        # Update data connection status
        if self.data_receiver.is_connected():
            self.tcp_status.configure(text="Data: Connected", fg_color="green")
        else:
            self.tcp_status.configure(text="Data: Connecting...", fg_color="yellow")

        self.after(500, self.update_status)
        
    def update_video(self):
        if not self.data_receiver.run:
            self.on_closing()
            return
            
        frame = self.video_thread.get_frame()
        if frame is not None:
            img = Image.fromarray(frame)
            ctk_image = ctk.CTkImage(light_image=img, 
                                 dark_image=img,
                                 size=(width, height))
            self.video_label.configure(image=ctk_image)
        
        self.after(1, self.update_video)
        
    def update_graph(self):
        if not self.data_receiver.run:
            return
            
        count = self.data_receiver.get_finger_count()
        timestamp = self.data_receiver.get_timestamp_ms()
        self.graph_view.update(count, timestamp)
        
        self.after(1, self.update_graph)
    
    def on_closing(self):
        self.data_receiver.stop()
        self.settings_receiver.stop()
        if hasattr(self, 'video_thread'):
            self.video_thread.stop()
        self.graph_view.cleanup()
        self.quit()
        self.destroy()
        import os
        os._exit(0)