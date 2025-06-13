class SettingsPresenter:
    """Settings Presenter - Controls settings interactions and communication"""
    
    def __init__(self, view, settings_model, main_presenter):
        self.view = view
        self.settings_model = settings_model
        self.main_presenter = main_presenter
        
        # Setup as observer of settings model
        self.settings_model.add_observer(self)
        
        # Connect view events to presenter methods
        self.view.set_apply_callback(self.on_apply_clicked)
        
    def on_settings_updated(self, settings):
        """Called when settings model is updated"""
        # Update view with new settings
        self.view.update_settings_values(settings)
    
    def on_apply_clicked(self):
        """Handle apply button click from view"""
        # Get current settings from view
        view_settings = self.view.get_current_settings()
        
        # Validate settings using model
        validated_settings = self.settings_model.validate_settings(view_settings)
        
        # Update model with validated settings
        self.settings_model.update_settings(validated_settings)
        
        # Send settings via main presenter
        success = self.main_presenter.send_settings(validated_settings)
        
        if success:
            print("Settings applied successfully")
        else:
            print("Failed to apply settings")
        
        return success
    
    def on_slider_changed(self, setting_name, value):
        """Handle slider value change from view"""
        # Update model with single setting
        self.settings_model.update_settings({setting_name: value})
    
    def on_entry_changed(self, setting_name, value):
        """Handle entry value change from view"""
        # Validate single setting
        validated = self.settings_model.validate_settings({setting_name: value})
        
        if setting_name in validated:
            # Update model with validated value
            self.settings_model.update_settings({setting_name: validated[setting_name]})
            
            # Update view if value was clamped
            if validated[setting_name] != value:
                self.view.update_setting_value(setting_name, validated[setting_name])
    
    def get_current_settings(self):
        """Get current settings from model"""
        return self.settings_model.get_settings()
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self.settings_model, 'remove_observer'):
            self.settings_model.remove_observer(self)
            