import customtkinter as ctk

class SettingView:
    """Setting View - Pure UI component for camera settings"""
    def __init__(self, master):
        # Main container - non-scrollable, compact design
        self.frame = ctk.CTkFrame(
            master,
            corner_radius=10,
            fg_color=("gray95", "gray20")
        )
        
        self.sliders = {}
        self.entries = {}
        self.value_labels = {}
        self.apply_callback = None
        
        # Enhanced camera control configuration with icons and descriptions
        self.slider_configs = {
            "Shutter": {
                "range": (100, 10000),
                "steps": 100,
                "default": 10000,
                "icon": "📸",
                "description": "Shutter speed in microseconds",
                "unit": "μs"
            },
            "Gain": {
                "range": (1, 16),
                "steps": 15,
                "default": 1,
                "icon": "📈",
                "description": "ISO sensor gain",
                "unit": "x"
            },
            "AWB Red": {
                "range": (0.1, 5.0),
                "steps": 50,
                "default": 1.0,
                "icon": "🔴",
                "description": "Auto white balance red gain",
                "unit": ""
            },
            "AWB Blue": {
                "range": (0.1, 5.0),
                "steps": 50,
                "default": 1.0,
                "icon": "🔵",
                "description": "Auto white balance blue gain",
                "unit": ""
            },
            "Contrast": {
                "range": (0.0, 2.0),
                "steps": 200,
                "default": 1.0,
                "icon": "🌓",
                "description": "Image contrast adjustment",
                "unit": ""
            },
            "Brightness": {
                "range": (-1.0, 1.0),
                "steps": 200,
                "default": 0.0,
                "icon": "💡",
                "description": "Image brightness adjustment",
                "unit": ""
            }
        }
        
        self._create_sliders()
    
    def _create_sliders(self):
        """Create compact UI layout with all settings visible"""
        # Configure main frame grid
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self.frame,
            text="📷 Camera Settings",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("gray10", "gray90")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(15, 10), sticky="ew")
        
        # Create compact controls in a 2-column layout
        row = 1
        for i, (name, config) in enumerate(self.slider_configs.items()):
            # Determine column (alternate between 0 and 1)
            col = i % 2
            if i > 0 and col == 0:
                row += 4  # Move to next row pair
            
            # Control container
            control_frame = ctk.CTkFrame(
                self.frame,
                corner_radius=6,
                fg_color=("gray88", "gray22"),
                height=140
            )
            control_frame.grid(row=row, column=col, rowspan=4,
                             padx=8, pady=5, sticky="nsew")
            control_frame.grid_columnconfigure(0, weight=1)
            
            # Header with icon and name
            header_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
            header_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 2))
            header_frame.grid_columnconfigure(1, weight=1)
            
            # Icon
            icon_label = ctk.CTkLabel(
                header_frame,
                text=config["icon"],
                font=ctk.CTkFont(size=14),
                width=25
            )
            icon_label.grid(row=0, column=0, sticky="w")
            
            # Name
            name_label = ctk.CTkLabel(
                header_frame,
                text=name,
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            )
            name_label.grid(row=0, column=1, sticky="w", padx=(3, 0))
            
            # Value display
            value_label = ctk.CTkLabel(
                control_frame,
                text=f"{config['default']}{config['unit']}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("blue", "lightblue"),
                corner_radius=3,
                fg_color=("gray75", "gray30"),
                height=25
            )
            value_label.grid(row=1, column=0, sticky="ew", padx=8, pady=2)
            self.value_labels[name] = value_label
            
            # Slider (more compact)
            slider = ctk.CTkSlider(
                control_frame,
                from_=config["range"][0],
                to=config["range"][1],
                number_of_steps=config["steps"],
                command=lambda v, n=name: self._on_slider_change(v, n),
                progress_color=("blue", "lightblue"),
                button_color=("darkblue", "blue"),
                button_hover_color=("blue", "lightblue"),
                height=16
            )
            slider.grid(row=2, column=0, sticky="ew", padx=8, pady=3)
            slider.set(config["default"])
            
            # Entry (more compact)
            entry = ctk.CTkEntry(
                control_frame,
                height=25,
                justify="center",
                font=ctk.CTkFont(size=10),
                corner_radius=4,
                border_width=1
            )
            entry.grid(row=3, column=0, sticky="ew", padx=8, pady=(3, 8))
            entry.insert(0, str(config["default"]))
            
            # Store references
            self.sliders[name] = slider
            self.entries[name] = entry
            
            # Bind entry validation
            entry.bind('<FocusOut>', lambda e, name=name: self._on_entry_change(name))
            entry.bind('<Return>', lambda e, name=name: self._on_entry_change(name))
        
        # Apply button at bottom
        self.apply_button = ctk.CTkButton(
            self.frame,
            text="🚀 Apply All Settings",
            command=self._on_apply,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=35,
            corner_radius=6,
            fg_color=("green", "darkgreen"),
            hover_color=("darkgreen", "green")
        )
        self.apply_button.grid(row=row+5, column=0, columnspan=2,
                              sticky="ew", padx=15, pady=(15, 15))

    def _on_slider_change(self, value, name):
        """Handle slider value change - update entry and value display"""
        entry = self.entries[name]
        value_label = self.value_labels[name]
        config = self.slider_configs[name]
        
        # Update entry
        entry.delete(0, 'end')
        if name in ["Gain", "Shutter"]:
            formatted_value = str(int(float(value)))
            entry.insert(0, formatted_value)
            value_label.configure(text=f"{formatted_value}{config['unit']}")
        else:
            formatted_value = f"{float(value):.1f}"
            entry.insert(0, formatted_value)
            value_label.configure(text=f"{formatted_value}{config['unit']}")
    
    def _on_entry_change(self, name):
        """Handle entry value change - update slider and value display"""
        entry = self.entries[name]
        value_label = self.value_labels[name]
        config = self.slider_configs[name]
        
        try:
            value = float(entry.get())
            # Update slider to match entry
            self.sliders[name].set(value)
            
            # Update value display
            if name in ["Gain", "Shutter"]:
                formatted_value = str(int(value))
                value_label.configure(text=f"{formatted_value}{config['unit']}")
            else:
                formatted_value = f"{value:.1f}"
                value_label.configure(text=f"{formatted_value}{config['unit']}")
                
        except ValueError:
            # Reset entry to current slider value if invalid
            current_value = self.sliders[name].get()
            entry.delete(0, 'end')
            if name in ["Gain", "Shutter"]:
                formatted_value = str(int(current_value))
                entry.insert(0, formatted_value)
                value_label.configure(text=f"{formatted_value}{config['unit']}")
            else:
                formatted_value = f"{current_value:.1f}"
                entry.insert(0, formatted_value)
                value_label.configure(text=f"{formatted_value}{config['unit']}")

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
            'shutter': int(self.sliders['Shutter'].get()),
            'gain': int(self.sliders['Gain'].get()),
            'awb_red': float(self.sliders['AWB Red'].get()),
            'awb_blue': float(self.sliders['AWB Blue'].get()),
            'contrast': float(self.sliders['Contrast'].get()),
            'brightness': float(self.sliders['Brightness'].get())
        }

    def update_settings_values(self, settings):
        """Update UI with new settings values (called by presenter)"""
        try:
            for name, value in settings.items():
                slider_name = {
                    'shutter': 'Shutter',
                    'gain': 'Gain',
                    'awb_red': 'AWB Red',
                    'awb_blue': 'AWB Blue',
                    'contrast': 'Contrast',
                    'brightness': 'Brightness'
                }.get(name)
                
                if slider_name and slider_name in self.sliders:
                    # Update slider
                    self.sliders[slider_name].set(value)
                    
                    # Update entry
                    self.entries[slider_name].delete(0, 'end')
                    
                    # Update value label and entry
                    config = self.slider_configs[slider_name]
                    if slider_name in ['Gain', 'Shutter']:
                        formatted_value = str(int(value))
                        self.entries[slider_name].insert(0, formatted_value)
                        self.value_labels[slider_name].configure(text=f"{formatted_value}{config['unit']}")
                    else:
                        formatted_value = f"{float(value):.1f}"
                        self.entries[slider_name].insert(0, formatted_value)
                        self.value_labels[slider_name].configure(text=f"{formatted_value}{config['unit']}")
        except Exception as e:
            print(f"Error updating settings UI: {e}")

    def update_setting_value(self, setting_name, value):
        """Update single setting value in UI"""
        slider_name = {
            'shutter': 'Shutter',
            'gain': 'Gain',
            'awb_red': 'AWB Red',
            'awb_blue': 'AWB Blue',
            'contrast': 'Contrast',
            'brightness': 'Brightness'
        }.get(setting_name)
        
        if slider_name and slider_name in self.sliders:
            # Update slider
            self.sliders[slider_name].set(value)
            
            # Update entry
            self.entries[slider_name].delete(0, 'end')
            
            # Update value label and entry
            config = self.slider_configs[slider_name]
            if slider_name in ['Gain', 'Shutter']:
                formatted_value = str(int(value))
                self.entries[slider_name].insert(0, formatted_value)
                self.value_labels[slider_name].configure(text=f"{formatted_value}{config['unit']}")
            else:
                formatted_value = f"{float(value):.1f}"
                self.entries[slider_name].insert(0, formatted_value)
                self.value_labels[slider_name].configure(text=f"{formatted_value}{config['unit']}")