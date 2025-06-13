import customtkinter as ctk
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


class AppManager:
    """Manages application startup with connection modal"""

    def __init__(self):
        self.app = None
        self.main_presenter = None
        self.connection_modal = None
        self.connection_presenter = None
        self.auth_model = None

    def start_application(self):
        """Start the application with connection modal"""
        # Create a temporary root window for the modal
        temp_root = ctk.CTk()
        temp_root.withdraw()  # Hide the temporary window

        # Create auth model
        self.auth_model = AuthModel()

        # Create connection modal
        self.connection_modal = ConnectionModal(temp_root, self._on_connected)

        # Create connection presenter
        self.connection_presenter = ConnectionPresenter(
            self.connection_modal,
            self.auth_model,
            self._on_connected
        )

        # Show connection modal
        self.connection_modal.show()

        # Start the event loop
        temp_root.mainloop()

    def _on_connected(self, server_ip):
        """Called when connection is successful"""
        # Clean up connection components
        if self.connection_presenter:
            self.connection_presenter.cleanup()

        # Destroy the temporary root
        if self.connection_modal:
            self.connection_modal.modal.master.quit()
            self.connection_modal.modal.master.destroy()

        # Now create the actual app with the server IP
        self._create_app(server_ip)

    def _create_app(self, server_ip):
        """Create and initialize the main application"""
        # Create main view
        self.app = App()

        # Create main presenter with the connected server IP
        self.main_presenter = MainPresenter(self.app, server_ip)

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

        # Store presenters in app for cleanup
        self.app.main_presenter = self.main_presenter
        self.app.graph_presenter = graph_presenter
        self.app.settings_presenter = settings_presenter

        # Start the main application loop
        self.app.mainloop()


def main():
    """Initialize and start application with connection modal"""
    app_manager = AppManager()
    app_manager.start_application()


if __name__ == "__main__":
    try:
        main()  # Fixed: removed incorrect app.mainloop()
    except KeyboardInterrupt:
        print("Keyboard interrupt received")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Application terminated")
    