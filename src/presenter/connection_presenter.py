import threading
import socket

class ConnectionPresenter:
    """Connection Presenter - Handles connection logic and authentication"""
    
    def __init__(self, view, auth_model, on_connected_callback):
        self.view = view
        self.auth_model = auth_model
        self.on_connected_callback = on_connected_callback
        
        # Set view callbacks
        self.view.set_connect_callback(self.on_connect_clicked)
        
        # Auth presenter will be created when needed
        self.auth_presenter = None
    
    def on_connect_clicked(self, ip_address, password):
        """Handle connect button click from view"""
        # Validate inputs
        if not ip_address:
            self.view.show_auth_error("Please enter an IP address")
            return
            
        if not password:
            self.view.show_auth_error("Please enter a password")
            return
            
        if not self._validate_ip(ip_address):
            self.view.show_auth_error("Please enter a valid IP address")
            return
        
        # Start connection process
        self._start_connection(ip_address, password)
    
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
    
    def _start_connection(self, ip_address, password):
        """Start the connection process"""
        # Disable UI
        self.view.disable_inputs()
        self.view.update_status("🔄 Connecting...")
        
        # Start connection test in background thread
        connection_thread = threading.Thread(
            target=self._test_connection,
            args=(ip_address, password),
            daemon=True
        )
        connection_thread.start()
    
    def _test_connection(self, ip_address, password):
        """Test connection and authenticate (runs in background thread)"""
        try:
            # Test basic connectivity first
            self.view.modal.after(0, lambda: self.view.update_status("🔍 Testing connectivity..."))
            
            # Test data port (5000)
            if not self._test_port(ip_address, 5000):
                self.view.modal.after(0, lambda: self._connection_failed("Data port (5000) not accessible"))
                return
                
            # Test settings port (5001)
            if not self._test_port(ip_address, 5001):
                self.view.modal.after(0, lambda: self._connection_failed("Settings port (5001) not accessible"))
                return
            
            # Test authentication port (5002)
            if not self._test_port(ip_address, 5002):
                self.view.modal.after(0, lambda: self._connection_failed("Auth port (5002) not accessible"))
                return
            
            # Start authentication
            self.view.modal.after(0, lambda: self.view.update_status("🔐 Authenticating..."))
            
            # Import and create auth presenter here to avoid circular imports
            from src.presenter.auth_presenter import AuthPresenter
            self.auth_presenter = AuthPresenter(self.view, self.auth_model)
            
            # Authenticate
            auth_result = self.auth_presenter.authenticate(ip_address, password)
            
            print(f"CONNECTION: Auth result = {auth_result}")
            print(f"CONNECTION: Auth model status = {self.auth_model.get_auth_status()}")
            
            if auth_result and self.auth_model.get_auth_status():
                self.view.modal.after(0, self._connection_success)
            else:
                self.view.modal.after(0, lambda: self._connection_failed("Authentication failed - Invalid password"))
                
        except Exception as e:
            self.view.modal.after(0, lambda: self._connection_failed(f"Connection failed: {str(e)}"))
    
    def _test_port(self, ip_address, port):
        """Test if a specific port is accessible"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3.0)
            result = sock.connect_ex((ip_address, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def _connection_success(self):
        """Handle successful connection and authentication"""
        self.view.show_auth_success()
        
        # Start countdown before entering app
        self.view.start_countdown(self._enter_app)
    
    def _enter_app(self):
        """Enter the main application after countdown"""
        # Get credentials for main app
        ip_address, _ = self.view.get_credentials()
        
        # Callback to main app with IP address
        if self.on_connected_callback:
            self.on_connected_callback(ip_address)
    
    def _connection_failed(self, message):
        """Handle connection failure"""
        self.view.show_auth_error(message)
        self.view.enable_inputs()
        
        # Clean up auth presenter
        if self.auth_presenter:
            self.auth_presenter.cleanup()
            self.auth_presenter = None
    
    def cleanup(self):
        """Clean up resources"""
        if self.auth_presenter:
            self.auth_presenter.cleanup()
            