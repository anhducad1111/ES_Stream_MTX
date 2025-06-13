class SettingsModel:
    """Model for managing camera settings data"""

    def __init__(self):
        # Default settings
        self.settings = {
            'shutter': 10000,
            'gain': 1,
            'awb_red': 1.0,
            'awb_blue': 1.0,
            'contrast': 1.0,
            'brightness': 0.0
        }
        self._observers = []

    def update_settings(self, new_settings):
        """Update settings and notify observers"""
        settings_changed = False
        for key, value in new_settings.items():
            if key in self.settings and self.settings[key] != value:
                self.settings[key] = value
                settings_changed = True
        
        if settings_changed:
            self._notify_observers()

    def get_settings(self):
        """Get current settings"""
        return self.settings.copy()

    def get_setting(self, key):
        """Get specific setting value"""
        return self.settings.get(key)

    def validate_settings(self, settings):
        """Validate settings values"""
        valid_settings = {}
        
        # Validation rules
        validation_rules = {
            'shutter': {'min': 100, 'max': 10000, 'type': int},
            'gain': {'min': 1, 'max': 16, 'type': int},
            'awb_red': {'min': 0.1, 'max': 5.0, 'type': float},
            'awb_blue': {'min': 0.1, 'max': 5.0, 'type': float},
            'contrast': {'min': 0.0, 'max': 2.0, 'type': float},
            'brightness': {'min': -1.0, 'max': 1.0, 'type': float}
        }
        
        for key, value in settings.items():
            if key in validation_rules:
                rule = validation_rules[key]
                try:
                    # Convert to correct type
                    converted_value = rule['type'](value)
                    # Clamp to valid range
                    clamped_value = max(rule['min'], min(rule['max'], converted_value))
                    valid_settings[key] = clamped_value
                except (ValueError, TypeError):
                    # Use current value if conversion fails
                    valid_settings[key] = self.settings[key]
        
        return valid_settings

    def add_observer(self, observer):
        """Add observer for settings changes"""
        self._observers.append(observer)

    def remove_observer(self, observer):
        """Remove observer"""
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(self):
        """Notify all observers of settings changes"""
        for observer in self._observers:
            if hasattr(observer, 'on_settings_updated'):
                observer.on_settings_updated(self.settings.copy())
                