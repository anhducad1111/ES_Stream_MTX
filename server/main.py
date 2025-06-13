"""
Server Main Module
Entry point for the TCP server application with camera streaming functionality.
"""

# Standard library imports
import logging
import logging.handlers
import os
import sys

# Third-party imports

# Local application imports
from src.presenter.server_presenter import ServerPresenter, ServerPresenterError
from config import config


def setup_logging() -> None:
    """
    Configure logging according to standards.
    
    Sets up both file and console logging with proper formatting.
    """
    log_config = config.get_logging_config()
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_config.get('file', 'server.log'))
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_config.get('level', 'INFO')),
        format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        handlers=[
            logging.FileHandler(log_config.get('file', 'server.log')),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific logger levels
    logging.getLogger('src.model.camera_model').setLevel(logging.INFO)
    logging.getLogger('src.model.tcp_server_model').setLevel(logging.INFO)
    logging.getLogger('src.presenter.server_presenter').setLevel(logging.INFO)


def create_config_directory() -> None:
    """Create configuration directory if it doesn't exist."""
    config_dir = config.get('paths.config_dir', 'config')
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)
        logging.info(f"Created configuration directory: {config_dir}")


def validate_environment() -> None:
    """
    Validate the runtime environment and dependencies.
    
    Raises:
        SystemExit: If environment validation fails
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Check if running on appropriate system
        if sys.platform not in ['linux', 'linux2']:
            logger.warning(f"System platform '{sys.platform}' may not support camera operations")
        
        # Validate configuration
        server_config = config.get_server_config()
        if not server_config:
            raise ValueError("Server configuration is missing")
        
        camera_config = config.get_camera_config()
        if not camera_config:
            raise ValueError("Camera configuration is missing")
        
        logger.info("Environment validation completed successfully")
        
    except Exception as e:
        logger.error(f"Environment validation failed: {e}")
        sys.exit(1)


def main() -> None:
    """
    Main application entry point.
    
    Initializes and runs the TCP server application with proper error handling
    and resource cleanup.
    """
    # Setup logging first
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting TCP Server Application")
        logger.info(f"Python version: {sys.version}")
        
        # Validate environment
        validate_environment()
        
        # Create necessary directories
        create_config_directory()
        
        # Get camera settings path
        camera_settings_path = config.get_camera_settings_path()
        
        # Initialize server presenter
        logger.info("Initializing server presenter")
        server_presenter = ServerPresenter(config_path=camera_settings_path)
        
        # Display configuration information
        server_config = config.get_server_config()
        logger.info(f"Server configuration:")
        logger.info(f"  - Data server: {server_config['host']}:{server_config['data_port']}")
        logger.info(f"  - Settings server: {server_config['host']}:{server_config['settings_port']}")
        logger.info(f"  - Auth server: {server_config['host']}:{server_config['auth_port']}")
        
        # Run servers
        server_presenter.run_forever()
        
    except ServerPresenterError as e:
        logger.error(f"Server presenter error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.critical(f"Unexpected error in main application: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("TCP Server Application shutdown complete")


if __name__ == "__main__":
    main()