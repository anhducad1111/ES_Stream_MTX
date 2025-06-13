from src.view.main_view import App
from src.presenter.main_presenter import MainPresenter
from src.presenter.graph_presenter import GraphPresenter
from src.presenter.settings_presenter import SettingsPresenter
# from src.presenter.video_presenter import VideoPresenter  # Tạm bỏ để tránh conflict

def main():
    """Initialize MVP architecture and start application"""
    # Create main view
    app = App()
    
    # Create main presenter with models
    main_presenter = MainPresenter(app)
    
    # Create specialized presenters
    graph_presenter = GraphPresenter(
        app.get_graph_view(), 
        main_presenter.get_graph_model()
    )
    
    settings_presenter = SettingsPresenter(
        app.get_settings_view(),
        main_presenter.get_settings_model(),
        main_presenter
    )
    
    # video_presenter = VideoPresenter(
    #     app.get_video_view(),
    #     main_presenter.get_video_model()
    # )
    
    # Store presenters in app for cleanup
    app.main_presenter = main_presenter
    app.graph_presenter = graph_presenter
    app.settings_presenter = settings_presenter
    # app.video_presenter = video_presenter  # Tạm bỏ
    
    # Start the application
    return app

if __name__ == "__main__":
    try:
        app = main()
        app.mainloop()
    except KeyboardInterrupt:
        print("Keyboard interrupt received")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Application terminated")