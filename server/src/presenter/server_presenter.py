"""
Server Presenter Module
Coordinates server operations and manages multiple TCP server instances.
"""

# Standard library imports
import logging
import threading
import time
from typing import List, Optional

# Third-party imports

# Local application imports
from ..model.camera_model import CameraModel, CameraConfigurationError
from ..model.tcp_server_model import (
    DataServerModel, 
    SettingsServerModel, 
    AuthServerModel,
    TCPServerError
)


# Configure logging
logger = logging.getLogger(__name__)


class ServerPresenterError(Exception):
    """Raised when server presenter operations fail."""
    pass


class ServerPresenter:
    """
    Manages multiple TCP servers and coordinates their operations.
    
    Implements the presenter pattern by mediating between server models
    and providing a unified interface for server management.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize server presenter.
        
        Args:
            config_path: Optional path to camera configuration file
            
        Raises:
            ServerPresenterError: If initialization fails
        """
        try:
            # Initialize camera model and load settings if provided
            self.camera_model = CameraModel()
            if config_path:
                try:
                    self.camera_model.load_settings(config_path)
                except CameraConfigurationError as e:
                    logger.warning(f"Using default camera settings: {e}")
            
            # Initialize server models
            self.data_server = DataServerModel(port=5000)
            self.settings_server = SettingsServerModel(port=5001)
            self.auth_server = AuthServerModel(port=5002)
            
            # Server threads
            self.server_threads: List[threading.Thread] = []
            self.running = False
            
            logger.info("Server presenter initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize server presenter: {e}")
            raise ServerPresenterError(f"Initialization failed: {e}")

    def start_servers(self) -> None:
        """
        Start all TCP servers in separate daemon threads.
        
        Raises:
            ServerPresenterError: If servers fail to start
        """
        try:
            logger.info("Starting all TCP servers")
            
            # Start camera streaming for data server
            self.data_server.start_camera_streaming()
            
            # Create and start server threads
            self.server_threads = [
                threading.Thread(target=self.data_server.run, daemon=True),
                threading.Thread(target=self.settings_server.run, daemon=True),
                threading.Thread(target=self.auth_server.run, daemon=True)
            ]
            
            # Start all threads
            for thread in self.server_threads:
                thread.start()
            
            self.running = True
            
            logger.info("All servers started successfully:")
            logger.info("- Data server: port 5000")
            logger.info("- Settings server: port 5001") 
            logger.info("- Auth server: port 5002")
            
        except Exception as e:
            logger.error(f"Failed to start servers: {e}")
            self.cleanup()
            raise ServerPresenterError(f"Server startup failed: {e}")

    def stop_servers(self) -> None:
        """Stop all running servers and clean up resources."""
        logger.info("Stopping all servers")
        self.cleanup()

    def cleanup(self) -> None:
        """Clean up all server resources."""
        try:
            self.running = False
            
            # Stop all servers
            if hasattr(self, 'data_server'):
                self.data_server.cleanup()
            if hasattr(self, 'settings_server'):
                self.settings_server.cleanup()
            if hasattr(self, 'auth_server'):
                self.auth_server.cleanup()
            
            logger.info("Server cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def run_forever(self) -> None:
        """
        Run servers indefinitely until interrupted.
        
        Blocks the current thread and handles KeyboardInterrupt gracefully.
        """
        try:
            self.start_servers()
            
            logger.info("Servers running. Press Ctrl+C to stop.")
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Unexpected error in server loop: {e}")
        finally:
            self.stop_servers()

    def is_running(self) -> bool:
        """
        Check if servers are currently running.
        
        Returns:
            bool: True if servers are running, False otherwise
        """
        return self.running

    def get_server_status(self) -> dict:
        """
        Get status information for all servers.
        
        Returns:
            dict: Server status information
        """
        return {
            'running': self.running,
            'data_server': {
                'host': self.data_server.host,
                'port': self.data_server.port,
                'running': self.data_server.running
            },
            'settings_server': {
                'host': self.settings_server.host,
                'port': self.settings_server.port,
                'running': self.settings_server.running
            },
            'auth_server': {
                'host': self.auth_server.host,
                'port': self.auth_server.port,
                'running': self.auth_server.running
            },
            'camera_settings': self.camera_model.get_settings()
        }

    def update_camera_settings(self, new_settings: dict, config_path: Optional[str] = None) -> None:
        """
        Update camera settings and optionally save to file.
        
        Args:
            new_settings: New camera settings dictionary
            config_path: Optional path to save settings file
            
        Raises:
            ServerPresenterError: If settings update fails
        """
        try:
            self.camera_model.update_settings(new_settings)
            
            if config_path:
                self.camera_model.save_settings(config_path)
                
            logger.info("Camera settings updated via presenter")
            
        except Exception as e:
            logger.error(f"Failed to update camera settings: {e}")
            raise ServerPresenterError(f"Settings update failed: {e}")

    def set_auth_password(self, new_password: str) -> None:
        """
        Update the authentication password.
        
        Args:
            new_password: New authentication password
        """
        try:
            self.auth_server.set_password(new_password)
            logger.info("Authentication password updated via presenter")
        except Exception as e:
            logger.error(f"Failed to update auth password: {e}")
            raise ServerPresenterError(f"Password update failed: {e}")