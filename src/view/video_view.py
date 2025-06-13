import customtkinter as ctk

class VideoView:
    """Video View - Pure UI component for displaying video frames"""
    
    def __init__(self, master):
        
        # Video display label with clean styling
        self.video_label = ctk.CTkLabel(
            master,
            text="",
            font=ctk.CTkFont(size=14),
            text_color=("gray40", "gray60"),
            corner_radius=8,
            fg_color=("gray95", "gray25"),
            anchor="center"
        )
        self.video_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
    def get_widget(self):
        """Get the video label widget for compatibility"""
        return self.video_label
    
    def update_video_frame(self, ctk_image):
        """Update video frame display"""
        try:
            self.video_label.configure(
                image=ctk_image,
                text="",
                fg_color="transparent"
            )
        except Exception as e:
            print(f"Error updating video frame: {e}")
    
    def update_connection_status(self, connected):
        """Update connection status display"""
        if connected:
            # Clear any text when connected but no video yet
            self.video_label.configure(
                text="",
                fg_color="transparent"
            )
        else:
            # Show disconnected message
            self.video_label.configure(
                text="📡 Video Stream Disconnected\n\nCheck your connection settings",
                image=None,
                fg_color=("gray90", "gray30")
            )
            