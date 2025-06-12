import customtkinter as ctk

class SettingView:
    def __init__(self, master):
        self.frame = ctk.CTkFrame(master)
        self.sliders = {}
        self.entries = {}
        
        # Camera control sliders configuration
        self.slider_configs = {
            "Exposure": {"range": (0, 100), "default": 50},
            "Gain": {"range": (0, 100), "default": 50},
            "AWB Red": {"range": (0, 255), "default": 128},
            "AWB Green": {"range": (0, 255), "default": 128},
            "AWB Blue": {"range": (0, 255), "default": 128}
        }
        
        self._create_sliders()
    
    def _create_sliders(self):
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
                                command=lambda v, e=entry: self._on_slider_change(v, e))
            slider.grid(row=i*2+1, column=0, columnspan=2, padx=20, pady=(0,20), sticky="ew")
            slider.set(config["default"])
            
            # Store references
            self.sliders[name] = slider
            self.entries[name] = entry
            
            # Bind entry validation
            entry.bind('<FocusOut>', lambda e, s=slider, name=name: self._validate_entry(name))
            entry.bind('<Return>', lambda e, s=slider, name=name: self._validate_entry(name))
            
        # Add Apply button
        self.apply_button = ctk.CTkButton(self.frame, text="Apply", command=self._on_apply)
        self.apply_button.grid(row=len(self.slider_configs)*2, column=1, padx=20, pady=20, sticky="e")

    def _on_slider_change(self, value, entry):
        entry.delete(0, 'end')
        entry.insert(0, str(int(value)))
    
    def _validate_entry(self, name):
        entry = self.entries[name]
        slider = self.sliders[name]
        config = self.slider_configs[name]
        
        try:
            value = int(entry.get())
            min_val = config["range"][0]
            max_val = config["range"][1]
            
            if value < min_val:
                value = min_val
            elif value > max_val:
                value = max_val
                
            entry.delete(0, 'end')
            entry.insert(0, str(value))
            slider.set(value)
            
        except ValueError:
            # Reset to current slider value if invalid input
            value = int(slider.get())
            entry.delete(0, 'end')
            entry.insert(0, str(value))
    
    def _on_apply(self):
        # Validate all entries before applying
        for name in self.slider_configs.keys():
            self._validate_entry(name)
    
    def get_frame(self):
        return self.frame

    def get_settings(self):
        return {name: slider.get() for name, slider in self.sliders.items()}