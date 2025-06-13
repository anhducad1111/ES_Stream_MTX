import customtkinter as ctk

class VideoView:
    """Video View - Pure UI component for displaying video frames"""
    def __init__(self, master):
        self.video_label = ctk.CTkLabel(master, text="")
        
    def get_widget(self):
        """Get the video label widget"""
        return self.video_label
    
    def update_video_frame(self, ctk_image):
        """Update video frame display"""
        try:
            self.video_label.configure(image=ctk_image)
        except Exception as e:
            print(f"Error updating video frame: {e}")
    
    def update_connection_status(self, connected):
        """Update connection status display"""
        if connected:
            self.video_label.configure(text="")
        else:
            self.video_label.configure(text="Video Disconnected")