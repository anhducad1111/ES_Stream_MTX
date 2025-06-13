from PIL import Image
import customtkinter as ctk

class VideoPresenter:
    """Video Presenter - Controls video display and stream management"""
    
    def __init__(self, view, video_model):
        self.view = view
        self.video_model = video_model
        self.width = 640
        self.height = 480
        
        # Setup as observer of video model
        self.video_model.add_observer(self)
        
    def on_frame_available(self):
        """Called when new frame is available from video model"""
        frame = self.video_model.get_frame()
        if frame is not None:
            self._update_video_display(frame)
    
    def on_video_connection_changed(self, connected):
        """Called when video connection status changes"""
        if hasattr(self.view, 'update_connection_status'):
            self.view.update_connection_status(connected)
    
    def _update_video_display(self, frame):
        """Update video display with new frame"""
        try:
            # Convert numpy array to PIL Image
            img = Image.fromarray(frame)
            
            # Create CTk image
            ctk_image = ctk.CTkImage(
                light_image=img, 
                dark_image=img,
                size=(self.width, self.height)
            )
            
            # Update view
            self.view.update_video_frame(ctk_image)
            
        except Exception as e:
            print(f"Error updating video display: {e}")
    
    def get_connection_status(self):
        """Get current video connection status"""
        return self.video_model.is_connected()
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self.video_model, 'remove_observer'):
            self.video_model.remove_observer(self)
            