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
        self.modal.geometry("400x300")
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
        modal_height = 300
        
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
        self.ip_entry.pack(fill="x", pady=(0, 20))
        self.ip_entry.insert(0, "192.168.137.112")  # Default IP
        
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
        
    def _on_connect_clicked(self):
        """Handle connect button click"""
        ip_address = self.ip_entry.get().strip()
        
        if not ip_address:
            self._show_error("Please enter an IP address")
            return
            
        if not self._validate_ip(ip_address):
            self._show_error("Please enter a valid IP address")
            return
            
        # Start connection process
        self._start_connection(ip_address)
        
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
            
    def _start_connection(self, ip_address):
        """Start the connection process"""
        # Disable UI elements
        self.connect_button.configure(state="disabled")
        self.ip_entry.configure(state="disabled")
        
        # Show connecting status
        self._show_connecting()
        
        # Start connection test in background thread
        connection_thread = threading.Thread(
            target=self._test_connection,
            args=(ip_address,),
            daemon=True
        )
        connection_thread.start()
        
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
        
    def _show_connected(self):
        """Show connected status and start countdown"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        
        self.status_label.configure(
            text="✅ Connected successfully!",
            text_color=("green", "lightgreen")
        )
        
        self.countdown_label.pack(pady=(5, 0))
        
        # Start countdown
        self._start_countdown()
        
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
        
        # Re-enable UI elements
        self.connect_button.configure(state="normal")
        self.ip_entry.configure(state="normal")
        
        # Hide error after 3 seconds
        self.modal.after(3000, self._hide_status)
        
    def _hide_status(self):
        """Hide status messages"""
        self.status_label.pack_forget()
        if self.progress_bar.winfo_viewable():
            self.progress_bar.pack_forget()
        if self.countdown_label.winfo_viewable():
            self.countdown_label.pack_forget()
            
    def _test_connection(self, ip_address):
        """Test connection to server (runs in background thread)"""
        try:
            import socket
            
            # Test data port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            result = sock.connect_ex((ip_address, 5000))
            sock.close()
            
            if result == 0:
                # Test settings port
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5.0)
                result = sock.connect_ex((ip_address, 5001))
                sock.close()
                
                if result == 0:
                    # Connection successful
                    self.modal.after(0, self._show_connected)
                else:
                    self.modal.after(0, lambda: self._show_error("Settings port (5001) not accessible"))
            else:
                self.modal.after(0, lambda: self._show_error("Data port (5000) not accessible"))
                
        except Exception as e:
            self.modal.after(0, lambda: self._show_error(f"Connection failed: {str(e)}"))
            
    def _start_countdown(self):
        """Start 3-second countdown before closing modal"""
        self.countdown_time = 3
        self._update_countdown()
        
    def _update_countdown(self):
        """Update countdown display"""
        if self.countdown_time > 0:
            self.countdown_label.configure(
                text=f"Starting application in {self.countdown_time} seconds..."
            )
            self.countdown_time -= 1
            self.modal.after(1000, self._update_countdown)
        else:
            # Countdown finished - close modal and start app
            self._close_modal_and_start_app()
            
    def _close_modal_and_start_app(self):
        """Close modal and start the main application"""
        ip_address = self.ip_entry.get().strip()
        
        # Call the callback with the IP address
        if self.on_connected_callback:
            self.on_connected_callback(ip_address)
            
        # Close modal
        self.modal.grab_release()
        self.modal.destroy()
        
    def _on_close_attempt(self):
        """Handle attempt to close modal (prevent closing)"""
        # Show message that connection is required
        self._show_error("Connection required to continue")
        
    def set_connection_test_callback(self, callback):
        """Set callback for connection testing"""
        self.connection_test_callback = callback
        
    def show(self):
        """Show the modal"""
        self.modal.deiconify()
        self.modal.focus()