import customtkinter as ctk

class SettingView:
    """Setting View - Pure UI component for camera settings"""
    def __init__(self, master):
        self.frame = ctk.CTkFrame(master)
        self.sliders = {}
        self.entries = {}
        self.apply_callback = None
        
        # Camera control sliders configuration
        self.slider_configs = {
            "Exposure": {"range": (0.1, 1.0), "steps": 99, "default": 1.0},
            "Gain": {"range": (1, 10), "steps": 20, "default": 1},
            "AWB Red": {"range": (0.0, 5.0), "steps": 50, "default": 1.0},
            "AWB Green": {"range": (0.0, 5.0), "steps": 50, "default": 1.0},
            "AWB Blue": {"range": (0.0, 5.0), "steps": 50, "default": 1.0}
        }
        
        self._create_sliders()
    
    def _create_sliders(self):
        """Create UI sliders and entries"""
        for i, (name, config) in enumerate(self.slider_configs.items()):
            # Label
            label = ctk.CTkLabel(self.frame, text=name, anchor="w")
            label.grid(row=i*2, column=0, padx=20, pady=(20,0), sticky="w")
            
            # Entry for number input
            entry = ctk.CTkEntry(self.frame, width=60, justify="right")
            entry.grid(row=i*2, column=1, padx=(0,20), pady=(20,0), sticky="e")
            entry.insert(0, str(config["default"]))
            
            # Slider
            slider = ctk.CTkSlider(self.frame,
                                from_=config["range"][0],
                                to=config["range"][1],
                                number_of_steps=config["steps"],
                                command=lambda v, e=entry, n=name: self._on_slider_change(v, e, n))
            slider.grid(row=i*2+1, column=0, columnspan=2, padx=20, pady=(0,20), sticky="ew")
            slider.set(config["default"])
            
            # Store references
            self.sliders[name] = slider
            self.entries[name] = entry
            
            # Bind entry validation
            entry.bind('<FocusOut>', lambda e, name=name: self._on_entry_change(name))
            entry.bind('<Return>', lambda e, name=name: self._on_entry_change(name))
            
        # Add Apply button
        self.apply_button = ctk.CTkButton(self.frame, text="Apply", command=self._on_apply)
        self.apply_button.grid(row=len(self.slider_configs)*2, column=1, padx=20, pady=20, sticky="e")

    def _on_slider_change(self, value, entry, name):
        """Handle slider value change - update entry display"""
        entry.delete(0, 'end')
        if name == "Gain":
            entry.insert(0, str(int(float(value))))
        else:
            entry.insert(0, f"{float(value):.1f}")
    
    def _on_entry_change(self, name):
        """Handle entry value change"""
        entry = self.entries[name]
        try:
            value = float(entry.get())
            # Update slider to match entry
            self.sliders[name].set(value)
        except ValueError:
            # Reset entry to current slider value if invalid
            current_value = self.sliders[name].get()
            entry.delete(0, 'end')
            if name == "Gain":
                entry.insert(0, str(int(current_value)))
            else:
                entry.insert(0, f"{current_value:.1f}")

    def _on_apply(self):
        """Handle apply button click - delegate to presenter"""
        if self.apply_callback:
            self.apply_callback()

    def set_apply_callback(self, callback):
        """Set callback function for apply button"""
        self.apply_callback = callback

    def get_frame(self):
        """Get the main frame widget"""
        return self.frame

    def get_current_settings(self):
        """Get current settings values from UI"""
        return {
            'gain': int(self.sliders['Gain'].get()),
            'exposure': float(self.sliders['Exposure'].get()),
            'awb_red': float(self.sliders['AWB Red'].get()),
            'awb_green': float(self.sliders['AWB Green'].get()),
            'awb_blue': float(self.sliders['AWB Blue'].get())
        }

    def update_settings_values(self, settings):
        """Update UI with new settings values (called by presenter)"""
        try:
            for name, value in settings.items():
                slider_name = {
                    'exposure': 'Exposure',
                    'gain': 'Gain',
                    'awb_red': 'AWB Red',
                    'awb_green': 'AWB Green',
                    'awb_blue': 'AWB Blue'
                }.get(name)
                
                if slider_name and slider_name in self.sliders:
                    self.sliders[slider_name].set(value)
                    self.entries[slider_name].delete(0, 'end')
                    if slider_name == 'Gain':
                        self.entries[slider_name].insert(0, str(int(value)))
                    else:
                        self.entries[slider_name].insert(0, f"{float(value):.1f}")
        except Exception as e:
            print(f"Error updating settings UI: {e}")

    def update_setting_value(self, setting_name, value):
        """Update single setting value in UI"""
        slider_name = {
            'exposure': 'Exposure',
            'gain': 'Gain',
            'awb_red': 'AWB Red',
            'awb_green': 'AWB Green',
            'awb_blue': 'AWB Blue'
        }.get(setting_name)
        
        if slider_name and slider_name in self.sliders:
            self.sliders[slider_name].set(value)
            self.entries[slider_name].delete(0, 'end')
            if slider_name == 'Gain':
                self.entries[slider_name].insert(0, str(int(value)))
            else:
                self.entries[slider_name].insert(0, f"{float(value):.1f}")