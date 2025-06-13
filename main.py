# Standard library imports
import logging
import logging.handlers
import os
import sys

# Third-party imports
import customtkinter as ctk

# Local application imports
from src.view import (
    App,
    ConnectionModal
)
from src.model import AuthModel
from src.presenter import (
    ConnectionPresenter,
    MainPresenter,
    GraphPresenter,
    SettingsPresenter
)


def setup_logging() -> None:
    """
    Configure logging according to standards.
    
    Sets up both file and console logging with proper formatting.
    """
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


class AppManager:
    """Manages application startup with connection modal."""

    def __init__(self):
        """Initialize AppManager with component references."""
        self.app = None
        self.main_presenter = None
        self.connection_modal = None
        self.connection_presenter = None
        self.auth_model = None
        self.logger = logging.getLogger(__name__)

    def start_application(self):
        """Start the application with connection modal."""
        self.logger.info("Starting ES IoT Tutorial MTX application")
        
        try:
            # Create a temporary root window for the modal
            temp_root = ctk.CTk()
            temp_root.withdraw()  # Hide the temporary window

            # Create auth model
            self.auth_model = AuthModel()
            self.logger.info("Authentication model initialized")

            # Create connection modal
            self.connection_modal = ConnectionModal(temp_root, self._on_connected)

            # Create connection presenter
            self.connection_presenter = ConnectionPresenter(
                self.connection_modal,
                self.auth_model,
                self._on_connected
            )
            self.logger.info("Connection components initialized")

            # Show connection modal
            self.connection_modal.show()

            # Start the event loop
            temp_root.mainloop()
            
        except Exception as e:
            self.logger.error(f"Failed to start application: {e}")
            raise

    def _on_connected(self, server_ip):
        """
        Called when connection is successful.
        
        Args:
            server_ip: IP address of the connected server
        """
        self.logger.info(f"Successfully connected to server: {server_ip}")
        
        try:
            # Clean up connection components
            if self.connection_presenter:
                self.connection_presenter.cleanup()

            # Destroy the temporary root
            if self.connection_modal:
                self.connection_modal.modal.master.quit()
                self.connection_modal.modal.master.destroy()

            # Now create the actual app with the server IP
            self._create_app(server_ip)
            
        except Exception as e:
            self.logger.error(f"Failed to handle connection: {e}")
            raise

    def _create_app(self, server_ip):
        """
        Create and initialize the main application.
        
        Args:
            server_ip: IP address of the connected server
        """
        self.logger.info("Creating main application interface")
        
        try:
            # Create main view
            self.app = App()
            self.logger.info("Main application view created")

            # Create main presenter with the connected server IP
            self.main_presenter = MainPresenter(self.app, server_ip)
            self.logger.info("Main presenter initialized")

            # Create specialized presenters
            graph_presenter = GraphPresenter(
                self.app.get_graph_view(),
                self.main_presenter.get_graph_model()
            )

            settings_presenter = SettingsPresenter(
                self.app.get_settings_view(),
                self.main_presenter.get_settings_model(),
                self.main_presenter
            )
            self.logger.info("Specialized presenters created")

            # Store presenters in app for cleanup
            self.app.main_presenter = self.main_presenter
            self.app.graph_presenter = graph_presenter
            self.app.settings_presenter = settings_presenter

            # Start the main application loop
            self.logger.info("Starting main application loop")
            self.app.mainloop()
            
        except Exception as e:
            self.logger.error(f"Failed to create main application: {e}")
            raise


def main():
    """
    Initialize and start application with connection modal.
    
    Main entry point for the ES IoT Tutorial MTX application.
    Configures logging and starts the application manager.
    """
    # Setup logging first
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("ES IoT Tutorial MTX starting up")
        logger.info(f"Python version: {sys.version}")
        
        # Create and start application manager
        app_manager = AppManager()
        app_manager.start_application()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.critical(f"Critical error in main application: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("ES IoT Tutorial MTX application terminated")


if __name__ == "__main__":
    main()