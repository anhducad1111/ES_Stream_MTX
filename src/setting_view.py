import customtkinter as ctk

class SettingView:
    def __init__(self, master):
        self.frame = ctk.CTkFrame(master)
        self.sliders = {}
        
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
            
            # Value label
            value_label = ctk.CTkLabel(self.frame, text=str(config["default"]))
            value_label.grid(row=i*2, column=1, padx=(0,20), pady=(20,0), sticky="e")
            
            # Slider
            slider = ctk.CTkSlider(self.frame, 
                               from_=config["range"][0],
                               to=config["range"][1],
                               command=lambda v, l=value_label: l.configure(text=str(int(v))))
            slider.grid(row=i*2+1, column=0, columnspan=2, padx=20, pady=(0,20), sticky="ew")
            slider.set(config["default"])
            self.sliders[name] = slider

    def get_frame(self):
        return self.frame

    def get_settings(self):
        return {name: slider.get() for name, slider in self.sliders.items()}