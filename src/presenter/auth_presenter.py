from src.model import AuthReceiver
import time

class AuthPresenter:
    """Auth Presenter - Controls authentication interactions"""
    def __init__(self, view, auth_model):
        self.view = view
        self.auth_model = auth_model
        self.auth_receiver = None
        
        # Setup as observer of auth model
        self.auth_model.add_observer(self)
    
    def on_auth_status_changed(self, is_authenticated):
        """Called when auth model status changes"""
        if is_authenticated:
            self.view.show_auth_success()
        else:
            self.view.show_auth_error()
    
    def authenticate(self, server_ip, password):
        """Start authentication process"""
        try:
            # Set credentials in model
            self.auth_model.set_credentials(server_ip, password)
            
            # Create auth receiver and connect
            self.auth_receiver = AuthReceiver(server_ip, port=5002)
            self.auth_receiver.start()
            
            # Wait for connection
            max_wait = 5.0  # 5 seconds
            wait_time = 0.0
            while not self.auth_receiver.is_connected() and wait_time < max_wait:
                time.sleep(0.1)
                wait_time += 0.1
            
            if not self.auth_receiver.is_connected():
                print("AUTH: Failed to connect to auth server")
                self.auth_model.set_authenticated(False)
                return False
            
            print(f"AUTH: Connected to auth server, sending password: {password}")
            
            # Send authentication request
            if self.auth_receiver.authenticate(password):
                # Wait for auth response
                wait_time = 0.0
                max_auth_wait = 5.0  # 5 seconds for auth response
                
                while not self.auth_receiver.is_auth_completed() and wait_time < max_auth_wait:
                    time.sleep(0.1)
                    wait_time += 0.1
                
                if self.auth_receiver.is_auth_completed():
                    auth_result = self.auth_receiver.get_auth_status()
                    print(f"AUTH: Authentication completed, result: {auth_result}")
                    self.auth_model.set_authenticated(auth_result)
                    
                    # Stop auth receiver immediately after getting result
                    self.auth_receiver.stop()
                    return auth_result
                else:
                    # Timeout
                    print("AUTH: Authentication timeout")
                    self.auth_model.set_authenticated(False)
                    return False
            else:
                print("AUTH: Failed to send auth request")
                self.auth_model.set_authenticated(False)
                return False
                
        except Exception as e:
            print(f"Authentication error: {e}")
            self.auth_model.set_authenticated(False)
            return False
        finally:
            # Clean up auth receiver
            if self.auth_receiver:
                self.auth_receiver.stop()
                self.auth_receiver = None
    
    def get_auth_status(self):
        """Get current authentication status"""
        return self.auth_model.get_auth_status()
    
    def reset_auth(self):
        """Reset authentication"""
        self.auth_model.reset_auth()
        if self.auth_receiver:
            self.auth_receiver.stop()
            self.auth_receiver = None
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self.auth_model, 'remove_observer'):
            self.auth_model.remove_observer(self)
        if self.auth_receiver:
            self.auth_receiver.stop()
            