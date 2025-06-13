import customtkinter as ctk
import threading
import time

class ConnectionModal:
    """Connection Modal - Handles server connection setup"""
    def __init__(self, master, on_connected_callback):
        self.master = master
        self.on_connected_callback = on_connected_callback
        self.connection_test_callback = None
        
        # Create modal window
        self.modal = ctk.CTkToplevel(master)
        self.modal.title("Server Connection")
        self.modal.geometry("400x380")
        self.modal.resizable(False, False)
        
        # Make modal always on top and block main window
        self.modal.transient(master)
        self.modal.grab_set()
        self.modal.focus()
        
        # Center the modal
        self._center_modal()
        
        # Create UI
        self._create_ui()
        
        # Prevent closing with X button
        self.modal.protocol("WM_DELETE_WINDOW", self._on_close_attempt)
        
    def _center_modal(self):
        """Center the modal on the screen"""
        # Update modal to get actual dimensions
        self.modal.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.modal.winfo_screenwidth()
        screen_height = self.modal.winfo_screenheight()
        
        # Modal dimensions
        modal_width = 400
        modal_height = 380
        
        # Calculate center position on screen
        x = (screen_width // 2) - (modal_width // 2)
        y = (screen_height // 2) - (modal_height // 2)
        
        # Ensure modal stays within screen bounds
        x = max(0, min(x, screen_width - modal_width))
        y = max(0, min(y, screen_height - modal_height))
        
        # Set the geometry
        self.modal.geometry(f"{modal_width}x{modal_height}+{x}+{y}")
        
    def _create_ui(self):
        """Create the connection modal UI"""
        # Main container
        main_frame = ctk.CTkFrame(self.modal)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🌐 Connect to Camera Server",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("gray10", "gray90")
        )
        title_label.pack(pady=(20, 30))
        
        # Connection form frame
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=20)
        
        # IP Address input
        ip_label = ctk.CTkLabel(
            form_frame,
            text="Server IP Address:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        ip_label.pack(anchor="w", pady=(0, 5))
        
        self.ip_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="192.168.137.112",
            font=ctk.CTkFont(size=12),
            height=35
        )
        self.ip_entry.pack(fill="x", pady=(0, 15))
        self.ip_entry.insert(0, "192.168.137.112")  # Default IP
        
        # Password input
        password_label = ctk.CTkLabel(
            form_frame,
            text="Password:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter password",
            font=ctk.CTkFont(size=12),
            height=35,
            show="*"
        )
        self.password_entry.pack(fill="x", pady=(0, 20))
        # No default password - user must enter manually
        
        # Connect button
        self.connect_button = ctk.CTkButton(
            form_frame,
            text="🔗 Connect",
            command=self._on_connect_clicked,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color=("blue", "darkblue"),
            hover_color=("darkblue", "blue")
        )
        self.connect_button.pack(fill="x", pady=(0, 15))
        
        # Store callback for connect action
        self.connect_callback = None
        
        # Status frame
        self.status_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        self.status_frame.pack(fill="x")
        
        # Status label (initially hidden)
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        
        # Progress bar (initially hidden)
        self.progress_bar = ctk.CTkProgressBar(
            self.status_frame,
            width=300,
            height=8
        )
        
        # Countdown label (initially hidden)
        self.countdown_label = ctk.CTkLabel(
            self.status_frame,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("green", "lightgreen")
        )
        
        # Bind Enter key to connect
        self.ip_entry.bind('<Return>', lambda e: self._on_connect_clicked())
        self.password_entry.bind('<Return>', lambda e: self._on_connect_clicked())
        
    def _on_connect_clicked(self):
        """Handle connect button click - delegate to presenter"""
        if self.connect_callback:
            ip_address = self.ip_entry.get().strip()
            password = self.password_entry.get().strip()
            self.connect_callback(ip_address, password)
        
    def _validate_ip(self, ip):
        """Validate IP address format"""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                if not 0 <= int(part) <= 255:
                    return False
            return True
        except:
            return False
            
    def set_connect_callback(self, callback):
        """Set callback for connect button"""
        self.connect_callback = callback
    
    def disable_inputs(self):
        """Disable input fields during connection"""
        self.connect_button.configure(state="disabled")
        self.ip_entry.configure(state="disabled")
        self.password_entry.configure(state="disabled")
    
    def enable_inputs(self):
        """Enable input fields"""
        self.connect_button.configure(state="normal")
        self.ip_entry.configure(state="normal")
        self.password_entry.configure(state="normal")
    
    def get_credentials(self):
        """Get current IP and password"""
        return self.ip_entry.get().strip(), self.password_entry.get().strip()
        
    def _show_connecting(self):
        """Show connecting status"""
        self.status_label.configure(
            text="🔄 Connecting to server...",
            text_color=("orange", "yellow")
        )
        self.status_label.pack(pady=(10, 5))
        
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        
    # Removed _show_connected() - now using show_auth_success() + start_countdown() from presenter
        
    def _show_error(self, message):
        """Show error message"""
        # Stop progress bar if running
        if self.progress_bar.winfo_viewable():
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
        
        self.status_label.configure(
            text=f"❌ {message}",
            text_color=("red", "lightcoral")
        )
        self.status_label.pack(pady=(10, 0))
        
        # Re-enable UI elements after error
        self.enable_inputs()
        
        # Hide error after 3 seconds
        self.modal.after(3000, self._hide_status)
        
    def _hide_status(self):
        """Hide status messages"""
        self.status_label.pack_forget()
        if self.progress_bar.winfo_viewable():
            self.progress_bar.pack_forget()
        if self.countdown_label.winfo_viewable():
            self.countdown_label.pack_forget()
            
    def show_auth_success(self):
        """Show authentication success (called by presenter)"""
        # Just show success message, don't start countdown here
        # Countdown will be started by presenter via start_countdown()
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        
        self.status_label.configure(
            text="✅ Connected successfully!",
            text_color=("green", "lightgreen")
        )
        self.status_label.pack(pady=(10, 5))
    
    def show_auth_error(self, message="Authentication failed"):
        """Show authentication error (called by presenter)"""
        self._show_error(message)
    
    def update_status(self, message):
        """Update status message (called by presenter)"""
        self.status_label.configure(
            text=message,
            text_color=("orange", "yellow")
        )
        if not self.status_label.winfo_viewable():
            self.status_label.pack(pady=(10, 5))
            
    def start_countdown(self, callback):
        """Start 3-second countdown before calling callback"""
        self.app_callback = callback
        self.countdown_time = 3
        self._update_countdown()
        
    def _update_countdown(self):
        """Update countdown display"""
        if self.countdown_time > 0:
            self.countdown_label.configure(
                text=f"Starting application in {self.countdown_time} seconds..."
            )
            self.countdown_label.pack(pady=(5, 0))
            self.countdown_time -= 1
            self.modal.after(1000, self._update_countdown)
        else:
            # Countdown finished - close modal and start app
            self._close_modal_and_start_app()
            
    def _close_modal_and_start_app(self):
        """Close modal and start the main application"""
        # Call the callback to enter app
        if hasattr(self, 'app_callback') and self.app_callback:
            self.app_callback()
            
        # Close modal
        self.modal.grab_release()
        self.modal.destroy()
        
    def _on_close_attempt(self):
        """Handle attempt to close modal - allow closing to exit app"""
        # Allow user to close modal and exit application
        self.modal.grab_release()
        self.modal.destroy()
        # Exit the entire application
        import sys
        sys.exit(0)
        
    def set_connection_test_callback(self, callback):
        """Set callback for connection testing"""
        self.connection_test_callback = callback
        
    def show(self):
        """Show the modal"""
        self.modal.deiconify()
        self.modal.focus()