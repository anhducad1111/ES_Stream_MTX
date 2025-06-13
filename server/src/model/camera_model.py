"""
Camera Model Module
Handles camera configuration and process management.
"""

# Standard library imports
import json
import logging
import subprocess
import time
from typing import Dict, Any, Optional

# Third-party imports

# Local application imports


# Configure logging
logger = logging.getLogger(__name__)


class CameraConfigurationError(Exception):
    """Raised when camera configuration fails."""
    pass


class CameraProcessError(Exception):
    """Raised when camera process operations fail."""
    pass


class CameraModel:
    """
    Manages camera settings and streaming processes.
    
    Implements singleton pattern to ensure only one camera instance.
    Handles libcamera and ffmpeg process management for RTSP streaming.
    """
    
    _instance = None
    _initialized = False

    def __new__(cls):
        """
        Create singleton instance.
        
        Returns:
            CameraModel: The singleton camera model instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize camera model with default settings."""
        if not CameraModel._initialized:
            self.settings = self._load_default_settings()
            self.libcamera_proc: Optional[subprocess.Popen] = None
            self.ffmpeg_proc: Optional[subprocess.Popen] = None
            CameraModel._initialized = True

    def _load_default_settings(self) -> Dict[str, Any]:
        """
        Load default camera settings.
        
        Returns:
            Dict[str, Any]: Default camera configuration
        """
        return {
            'shutter': 10000,
            'gain': 1,
            'awb_red': 1.0,
            'awb_blue': 1.0,
            'contrast': 1.0,
            'brightness': 0.0
        }

    def load_settings(self, config_path: str) -> None:
        """
        Load camera settings from configuration file.
        
        Args:
            config_path: Path to camera settings JSON file
            
        Raises:
            CameraConfigurationError: If settings file cannot be loaded
        """
        try:
            with open(config_path, 'r') as f:
                self.settings = json.load(f)
            logger.info(f"Loaded camera settings from {config_path}")
        except FileNotFoundError as e:
            logger.warning(f"Settings file not found: {config_path}, using defaults")
            raise CameraConfigurationError(f"Settings file not found: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in settings file: {e}")
            raise CameraConfigurationError(f"Invalid JSON format: {e}")
        except IOError as e:
            logger.error(f"Failed to read settings file: {e}")
            raise CameraConfigurationError(f"Failed to read file: {e}")

    def save_settings(self, config_path: str) -> None:
        """
        Save current camera settings to configuration file.
        
        Args:
            config_path: Path to save camera settings JSON file
            
        Raises:
            CameraConfigurationError: If settings cannot be saved
        """
        try:
            with open(config_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
            logger.info(f"Saved camera settings to {config_path}")
        except IOError as e:
            logger.error(f"Failed to save settings: {e}")
            raise CameraConfigurationError(f"Failed to save settings: {e}")

    def get_camera_command(self) -> list[str]:
        """
        Generate libcamera command with current settings.
        
        Returns:
            list[str]: Complete libcamera-vid command
        """
        return [
            "libcamera-vid",
            "-t", "0",
            "--width", "640",
            "--height", "480",
            "--framerate", "24",
            "--codec", "h264",
            "--inline",
            "--profile", "baseline",
            "--level", "4.2",
            "--vflip",
            "--nopreview",
            "--shutter", str(self.settings['shutter']),
            "--gain", str(self.settings['gain']),
            "--awbgains", f"{self.settings['awb_red']:.2f},{self.settings['awb_blue']:.2f}",
            "--contrast", str(self.settings['contrast']),
            "--brightness", str(self.settings['brightness']),
            "-o", "-"
        ]

    def get_ffmpeg_command(self) -> list[str]:
        """
        Generate ffmpeg command for RTSP streaming.
        
        Returns:
            list[str]: Complete ffmpeg command
        """
        return [
            "ffmpeg",
            "-fflags", "nobuffer",
            "-flags", "low_delay",
            "-probesize", "32",
            "-analyzeduration", "0",
            "-r", "24",
            "-f", "h264",
            "-i", "-",
            "-c:v", "copy",
            "-f", "rtsp",
            "rtsp://localhost:8554/ES_MTX"
        ]

    def start_camera(self) -> None:
        """
        Start camera streaming processes.
        
        Raises:
            CameraProcessError: If camera processes fail to start
        """
        try:
            logger.info("Starting camera streaming")
            self.libcamera_proc = subprocess.Popen(
                self.get_camera_command(), 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.ffmpeg_proc = subprocess.Popen(
                self.get_ffmpeg_command(), 
                stdin=self.libcamera_proc.stdout,
                stderr=subprocess.PIPE
            )
            logger.info("Camera streaming started successfully")
        except OSError as e:
            logger.error(f"Failed to start camera processes: {e}")
            raise CameraProcessError(f"Failed to start camera: {e}")

    def stop_camera(self) -> None:
        """Stop camera streaming processes."""
        try:
            if self.libcamera_proc:
                self.libcamera_proc.terminate()
                logger.debug("Terminated libcamera process")
            if self.ffmpeg_proc:
                self.ffmpeg_proc.terminate()
                logger.debug("Terminated ffmpeg process")
            logger.info("Camera streaming stopped")
        except Exception as e:
            logger.error(f"Error stopping camera processes: {e}")

    def update_settings(self, new_settings: Dict[str, Any]) -> None:
        """
        Update camera settings and restart streaming.
        
        Args:
            new_settings: Dictionary with new camera settings
            
        Raises:
            CameraConfigurationError: If settings update fails
        """
        try:
            logger.info(f"Updating camera settings: {new_settings}")
            self.settings.update(new_settings)
            self.stop_camera()
            time.sleep(0.5)  # Wait for processes to close
            self.start_camera()
            logger.info("Camera settings updated successfully")
        except Exception as e:
            logger.error(f"Failed to update camera settings: {e}")
            raise CameraConfigurationError(f"Settings update failed: {e}")

    def get_settings(self) -> Dict[str, Any]:
        """
        Get current camera settings.
        
        Returns:
            Dict[str, Any]: Current camera settings
        """
        return self.settings.copy()