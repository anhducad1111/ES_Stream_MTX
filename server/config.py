"""
Server Configuration Module
Contains configuration settings and constants for the server application.
"""

# Standard library imports
import os
from typing import Dict, Any

# Third-party imports

# Local application imports


# Default configuration settings
DEFAULT_CONFIG = {
    'server': {
        'host': '0.0.0.0',
        'data_port': 5000,
        'settings_port': 5001,
        'auth_port': 5002
    },
    'camera': {
        'width': 640,
        'height': 480,
        'framerate': 24,
        'codec': 'h264',
        'rtsp_url': 'rtsp://localhost:8554/ES_MTX',
        'default_settings': {
            'shutter': 10000,
            'gain': 1,
            'awb_red': 1.0,
            'awb_blue': 1.0,
            'contrast': 1.0,
            'brightness': 0.0
        }
    },
    'auth': {
        'default_password': '1111'
    },
    'paths': {
        'config_dir': 'config',
        'camera_settings': 'config/camera_settings.json'
    },
    'logging': {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': 'server.log'
    }
}


class ServerConfig:
    """
    Server configuration manager.
    
    Provides centralized access to configuration settings with
    environment variable override support.
    """

    def __init__(self, config_dict: Dict[str, Any] = None):
        """
        Initialize configuration.
        
        Args:
            config_dict: Optional custom configuration dictionary
        """
        self.config = config_dict or DEFAULT_CONFIG.copy()
        self._load_environment_overrides()

    def _load_environment_overrides(self) -> None:
        """Load configuration overrides from environment variables."""
        # Server configuration
        if os.getenv('SERVER_HOST'):
            self.config['server']['host'] = os.getenv('SERVER_HOST')
        
        if os.getenv('DATA_PORT'):
            self.config['server']['data_port'] = int(os.getenv('DATA_PORT'))
            
        if os.getenv('SETTINGS_PORT'):
            self.config['server']['settings_port'] = int(os.getenv('SETTINGS_PORT'))
            
        if os.getenv('AUTH_PORT'):
            self.config['server']['auth_port'] = int(os.getenv('AUTH_PORT'))

        # Authentication
        if os.getenv('AUTH_PASSWORD'):
            self.config['auth']['default_password'] = os.getenv('AUTH_PASSWORD')

        # Logging
        if os.getenv('LOG_LEVEL'):
            self.config['logging']['level'] = os.getenv('LOG_LEVEL')

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated key path.
        
        Args:
            key_path: Dot-separated configuration key path (e.g., 'server.host')
            default: Default value if key not found
            
        Returns:
            Any: Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value

    def get_server_config(self) -> Dict[str, Any]:
        """
        Get server configuration section.
        
        Returns:
            Dict[str, Any]: Server configuration
        """
        return self.config.get('server', {})

    def get_camera_config(self) -> Dict[str, Any]:
        """
        Get camera configuration section.
        
        Returns:
            Dict[str, Any]: Camera configuration
        """
        return self.config.get('camera', {})

    def get_auth_config(self) -> Dict[str, Any]:
        """
        Get authentication configuration section.
        
        Returns:
            Dict[str, Any]: Authentication configuration
        """
        return self.config.get('auth', {})

    def get_logging_config(self) -> Dict[str, Any]:
        """
        Get logging configuration section.
        
        Returns:
            Dict[str, Any]: Logging configuration
        """
        return self.config.get('logging', {})

    def get_camera_settings_path(self) -> str:
        """
        Get camera settings file path.
        
        Returns:
            str: Path to camera settings file
        """
        return self.get('paths.camera_settings', 'config/camera_settings.json')

    def update(self, key_path: str, value: Any) -> None:
        """
        Update configuration value by dot-separated key path.
        
        Args:
            key_path: Dot-separated configuration key path
            value: New value to set
        """
        keys = key_path.split('.')
        config_ref = self.config
        
        # Navigate to parent dictionary
        for key in keys[:-1]:
            if key not in config_ref:
                config_ref[key] = {}
            config_ref = config_ref[key]
        
        # Set the final value
        config_ref[keys[-1]] = value


# Global configuration instance
config = ServerConfig()