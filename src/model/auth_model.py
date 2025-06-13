class AuthModel:
    """Model for managing authentication state"""

    def __init__(self):
        self.is_authenticated = False
        self.server_ip = None
        self.password = None
        self._observers = []

    def set_credentials(self, server_ip, password):
        """Set authentication credentials"""
        self.server_ip = server_ip
        self.password = password

    def set_authenticated(self, status):
        """Set authentication status and notify observers"""
        if self.is_authenticated != status:
            self.is_authenticated = status
            self._notify_observers()

    def get_auth_status(self):
        """Get current authentication status"""
        return self.is_authenticated

    def get_credentials(self):
        """Get current credentials"""
        return self.server_ip, self.password

    def reset_auth(self):
        """Reset authentication state"""
        self.is_authenticated = False
        self.server_ip = None
        self.password = None
        self._notify_observers()

    def add_observer(self, observer):
        """Add observer for auth state changes"""
        self._observers.append(observer)

    def remove_observer(self, observer):
        """Remove observer"""
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(self):
        """Notify all observers of auth state changes"""
        for observer in self._observers:
            if hasattr(observer, 'on_auth_status_changed'):
                observer.on_auth_status_changed(self.is_authenticated)
    