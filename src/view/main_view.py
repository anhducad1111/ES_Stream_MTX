import customtkinter as ctk
from .video_view import VideoView
from .graph_view import GraphView
from .setting_view import SettingView

class App(ctk.CTk):
    """Main Application View - Pure UI layout and components"""
    def __init__(self):
        super().__init__()
        
        # Set modern theme and appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.title("🎥 RTSP Stream + TCP Data Monitor")
        
        # Get screen dimensions and set window size
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        self.after(0, lambda: self.state('zoomed'))

        # Configure main grid with better spacing
        self.grid_columnconfigure(0, weight=2)  # Video/graph section gets more space
        self.grid_columnconfigure(1, weight=1)  # Settings section
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)  # For status bar

        # Setup UI components
        self._setup_layout()
        
        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _setup_layout(self):
        """Setup the main UI layout with modern styling"""
        # Main content frame with subtle shadow effect
        self.main_content = ctk.CTkFrame(self, corner_radius=15, fg_color=("gray92", "gray14"))
        self.main_content.grid(row=0, column=0, columnspan=2, padx=15, pady=15, sticky="nsew")
        self.main_content.grid_columnconfigure(0, weight=2)
        self.main_content.grid_columnconfigure(1, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)
        
        # Left section for video and graph
        self.left_section = ctk.CTkFrame(self.main_content, corner_radius=12, fg_color=("gray88", "gray18"))
        self.left_section.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.left_section.grid_columnconfigure(0, weight=1)
        self.left_section.grid_rowconfigure(0, weight=3)  # Video gets more space
        self.left_section.grid_rowconfigure(1, weight=1)  # Graph gets less space
        
        # Video section with header
        self.video_header = ctk.CTkLabel(
            self.left_section,
            text="📹 Live Video Stream",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("gray10", "gray90")
        )
        self.video_header.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="nw")
        
        # Video view container
        self.video_container = ctk.CTkFrame(self.left_section, corner_radius=10, fg_color=("gray85", "gray21"))
        self.video_container.grid(row=0, column=0, padx=15, pady=(40, 10), sticky="nsew")
        self.video_container.grid_columnconfigure(0, weight=1)
        self.video_container.grid_rowconfigure(0, weight=1)
        
        self.video_view = VideoView(self.video_container)
        self.video_view.get_widget().grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Graph section with header
        self.graph_header = ctk.CTkLabel(
            self.left_section,
            text="📊 Data Visualization",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("gray10", "gray90")
        )
        self.graph_header.grid(row=1, column=0, padx=15, pady=(5, 5), sticky="nw")
        
        # Graph view container
        self.graph_container = ctk.CTkFrame(self.left_section, corner_radius=10, fg_color=("gray85", "gray21"))
        self.graph_container.grid(row=1, column=0, padx=15, pady=(30, 15), sticky="nsew")
        self.graph_container.grid_columnconfigure(0, weight=1)
        self.graph_container.grid_rowconfigure(0, weight=1)
        
        self.graph_view = GraphView(self.graph_container)
        self.graph_view.get_widget().grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Right section for settings
        self.right_section = ctk.CTkFrame(self.main_content, corner_radius=12, fg_color=("gray88", "gray18"))
        self.right_section.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        # Settings header
        self.settings_header = ctk.CTkLabel(
            self.right_section,
            text="⚙️ Camera Controls",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("gray10", "gray90")
        )
        self.settings_header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Settings view setup
        self.settings_view = SettingView(self.right_section)
        self.settings_view.get_frame().grid(row=1, column=0, padx=10, pady=(0, 20), sticky="nsew")
        
        # Configure right section grid
        self.right_section.grid_columnconfigure(0, weight=1)
        self.right_section.grid_rowconfigure(1, weight=1)

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