import time
from src.model.tcp_model import NumberDataReceiver, SettingsReceiver
from src.model.data_model import DataModel
from src.model.settings_model import SettingsModel
from src.model.video_model import VideoModel
from src.model.graph_model import GraphModel

class MainPresenter:
    """Main Presenter - Controls main application logic and coordinates components"""
    def __init__(self, view, server_ip="192.168.137.112", tcp_port=5000):
        self.view = view
        self.server_ip = server_ip
        self.tcp_port = tcp_port
        
        # Initialize models
        self.data_model = DataModel()
        self.settings_model = SettingsModel()
        self.graph_model = GraphModel()
        
        # Initialize TCP connections
        self.data_receiver = NumberDataReceiver(server_ip, tcp_port)
        self.settings_receiver = SettingsReceiver(server_ip, tcp_port + 1)
        
        # Initialize video model
        rtsp_url = f"rtsp://{server_ip}:8554/ES_MTX"
        self.video_model = VideoModel(rtsp_url)
        
        # Setup observers
        self._setup_observers()
        
        # Start components
        self._start_components()
        
    def _setup_observers(self):
        """Setup observer relationships between models"""
        # Models will notify presenters via callbacks
        pass
        
    def _start_components(self):
        """Start all background components"""
        # Start TCP connections
        self.data_receiver.start()
        self.settings_receiver.start()
        
        # Start video stream
        self.video_model.start()
        
        # Start update loops
        self._start_update_loops()
        
    def _start_update_loops(self):
        """Start all update loops"""
        self.view.after(500, self._update_status_loop)
        self.view.after(1, self._update_video_loop)
        self.view.after(1, self._update_graph_loop)
        
    def _update_status_loop(self):
        """Update status indicators and settings synchronization"""
        # Update settings UI if new data available
        if self.settings_receiver.is_connected():
            settings = self.settings_receiver.get_settings()
            if settings:
                try:
                    # Update settings model
                    self.settings_model.update_settings(settings)
                    
                    # Update view with new settings
                    self.view.update_settings_display(settings)
                    
                except Exception as e:
                    print(f"Error updating settings UI: {e}")
        
        # Schedule next update
        if self.data_receiver.run:
            self.view.after(500, self._update_status_loop)
        
    def _update_video_loop(self):
        """Update video display"""
        if not self.data_receiver.run:
            self._on_closing()
            return
            
        # Get frame from video model
        frame = self.video_model.get_frame()
        if frame is not None:
            # Update view with new frame - direct update như code cũ
            from PIL import Image
            import customtkinter as ctk
            width, height = 640, 480
            
            img = Image.fromarray(frame)
            ctk_image = ctk.CTkImage(light_image=img,
                                 dark_image=img,
                                 size=(width, height))
            self.view.get_video_view().get_widget().configure(image=ctk_image)
        
        # Schedule next update
        self.view.after(1, self._update_video_loop)

    def _update_graph_loop(self):
        """Update graph display"""
        if not self.data_receiver.run:
            return
            
        # Get data from TCP receiver
        count = self.data_receiver.get_finger_count()
        timestamp = self.data_receiver.get_timestamp_ms()
        
        # Update data model
        self.data_model.update_data(count, timestamp)
        
        # Add data to graph model
        if self.graph_model.add_data_point(count, timestamp):
            # Check if graph should be updated
            if self.graph_model.should_update_plot():
                # Get plot data and update view
                times, values, smoothed, time_window = self.graph_model.get_plot_data()
                if times and values and smoothed and time_window:
                    self.view.update_graph_display(times, values, smoothed, time_window)
        
        # Schedule next update
        self.view.after(1, self._update_graph_loop)
    
    def send_settings(self, settings):
        """Send settings to TCP server (called by settings presenter)"""
        if self.settings_receiver.send_command(settings):
            print("Settings command sent successfully")
            return True
        else:
            print("Failed to send settings command")
            return False
    
    def get_data_model(self):
        """Get data model for other presenters"""
        return self.data_model
    
    def get_settings_model(self):
        """Get settings model for other presenters"""
        return self.settings_model
    
    def get_graph_model(self):
        """Get graph model for other presenters"""
        return self.graph_model
    
    def get_video_model(self):
        """Get video model for other presenters"""
        return self.video_model
        
    def _on_closing(self):
        """Handle application closing"""
        self.data_receiver.stop()
        self.settings_receiver.stop()
        if hasattr(self, 'video_model'):
            self.video_model.stop()
        self.view.on_closing()