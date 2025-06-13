import customtkinter as ctk
from .video_view import VideoView
from .graph_view import GraphView
from .setting_view import SettingView

class App(ctk.CTk):
    """Main Application View - Pure UI layout and components"""
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

        # Setup UI components
        self._setup_layout()
        
        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _setup_layout(self):
        """Setup the main UI layout"""
        # Left frame setup
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.left_frame.grid_rowconfigure(0, weight=3)
        self.left_frame.grid_rowconfigure(1, weight=1)
        
        # Video view setup
        self.video_view = VideoView(self.left_frame)
        self.video_view.get_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Graph view setup
        self.graph_view = GraphView(self.left_frame)
        self.graph_view.get_widget().grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Settings view setup
        self.settings_view = SettingView(self)
        self.settings_view.get_frame().grid(row=0, column=1, padx=20, pady=20, sticky="ew")

    def get_video_view(self):
        """Get video view component"""
        return self.video_view

    def get_graph_view(self):
        """Get graph view component"""
        return self.graph_view

    def get_settings_view(self):
        """Get settings view component"""
        return self.settings_view

    # def update_video_display(self, frame):
    #     """Update video display with new frame (called by presenter)"""
    #     # Bỏ để tránh double update
    #     pass

    def update_graph_display(self, times, values, smoothed, time_window):
        """Update graph display (called by presenter)"""
        import matplotlib.pyplot as plt
        dates = plt.matplotlib.dates.date2num(times)
        self.graph_view.update_plot_data(dates, values, smoothed, time_window)

    def update_settings_display(self, settings):
        """Update settings display (called by presenter)"""
        self.settings_view.update_settings_values(settings)

    def on_closing(self):
        """Handle window closing"""
        # Clean up views
        if hasattr(self, 'graph_view'):
            self.graph_view.cleanup()
        
        self.quit()
        self.destroy()
        import os
        os._exit(0)