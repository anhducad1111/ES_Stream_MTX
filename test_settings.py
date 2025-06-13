import subprocess
import json
import customtkinter as ctk
import cv2
import numpy as np
import threading

class CameraControl:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Camera Settings")
        
        # Load saved settings or use defaults
        self.settings = self.load_settings()
        
        # Setup GUI
        self.setup_gui()
        
        # Camera control
        self.camera_running = True
        self.start_camera()
        
        # Start update loop
        self.update_thread = threading.Thread(target=self.update_frame, daemon=True)
        self.update_thread.start()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def load_settings(self):
        try:
            with open('config/camera_settings.json', 'r') as f:
                return json.load(f)
        except:
            return {
                'shutter': 10000,  # microseconds
                'gain': 1,
                'awb_red': 1.0,
                'awb_blue': 1.0,
                'contrast': 1.0,
                'brightness': 0.0
            }
    
    def save_settings(self):
        settings = {
            'shutter': int(self.shutter_slider.get()),
            'gain': int(self.gain_slider.get()),
            'awb_red': float(self.awb_r_slider.get()),
            'awb_blue': float(self.awb_b_slider.get()),
            'contrast': float(self.contrast_slider.get()),
            'brightness': float(self.brightness_slider.get())
        }
        with open('/home/ad/Desktop/WS/stream_rtsp/config/camera_settings.json', 'w') as f:
            json.dump(settings, f)

    def update_shutter_label(self, value):
        self.shutter_label.configure(text=f"{int(float(value))}")
        
    def update_gain_label(self, value):
        self.gain_label.configure(text=f"{int(float(value))}")
        
    def update_awb_r_label(self, value):
        self.awb_r_label.configure(text=f"{float(value):.2f}")
        
    def update_awb_b_label(self, value):
        self.awb_b_label.configure(text=f"{float(value):.2f}")
        
    def update_contrast_label(self, value):
        self.contrast_label.configure(text=f"{float(value):.2f}")
        
    def update_brightness_label(self, value):
        self.brightness_label.configure(text=f"{float(value):.2f}")
    
    def setup_gui(self):
        # Control frame
        self.control_frame = ctk.CTkFrame(self.root)
        self.control_frame.pack(padx=10, pady=10)
        
        # Control sliders with value labels
        # Shutter Speed (microseconds)
        shutter_frame = ctk.CTkFrame(self.control_frame)
        shutter_frame.pack(fill='x', padx=5, pady=5)
        ctk.CTkLabel(shutter_frame, text="Shutter (μs)").pack(side='left', padx=5)
        self.shutter_label = ctk.CTkLabel(shutter_frame, text=f"{self.settings.get('shutter', 100)}")
        self.shutter_label.pack(side='right', padx=5)
        self.shutter_slider = ctk.CTkSlider(self.control_frame, from_=100, to=10000,
                                           number_of_steps=100, command=self.update_shutter_label)
        self.shutter_slider.set(self.settings.get('shutter', 100))
        self.shutter_slider.pack(padx=5, pady=(0,10))
        
        # ISO Gain
        gain_frame = ctk.CTkFrame(self.control_frame)
        gain_frame.pack(fill='x', padx=5, pady=5)
        ctk.CTkLabel(gain_frame, text="ISO Gain").pack(side='left', padx=5)
        self.gain_label = ctk.CTkLabel(gain_frame, text=str(self.settings['gain']))
        self.gain_label.pack(side='right', padx=5)
        self.gain_slider = ctk.CTkSlider(self.control_frame, from_=1, to=16,
                                        number_of_steps=15, command=self.update_gain_label)
        self.gain_slider.set(self.settings['gain'])
        self.gain_slider.pack(padx=5, pady=(0,10))
        
        # AWB Red Gain
        awb_r_frame = ctk.CTkFrame(self.control_frame)
        awb_r_frame.pack(fill='x', padx=5, pady=5)
        ctk.CTkLabel(awb_r_frame, text="AWB Red").pack(side='left', padx=5)
        self.awb_r_label = ctk.CTkLabel(awb_r_frame, text=f"{self.settings['awb_red']:.2f}")
        self.awb_r_label.pack(side='right', padx=5)
        self.awb_r_slider = ctk.CTkSlider(self.control_frame, from_=0.1, to=5.0,
                                         number_of_steps=40, command=self.update_awb_r_label)
        self.awb_r_slider.set(self.settings['awb_red'])
        self.awb_r_slider.pack(padx=5, pady=(0,10))
        
        # AWB Blue Gain
        awb_b_frame = ctk.CTkFrame(self.control_frame)
        awb_b_frame.pack(fill='x', padx=5, pady=5)
        ctk.CTkLabel(awb_b_frame, text="AWB Blue").pack(side='left', padx=5)
        self.awb_b_label = ctk.CTkLabel(awb_b_frame, text=f"{self.settings['awb_blue']:.2f}")
        self.awb_b_label.pack(side='right', padx=5)
        self.awb_b_slider = ctk.CTkSlider(self.control_frame, from_=0.1, to=5.0,
                                         number_of_steps=40, command=self.update_awb_b_label)
        self.awb_b_slider.set(self.settings['awb_blue'])
        self.awb_b_slider.pack(padx=5, pady=(0,10))
        
        # Contrast
        contrast_frame = ctk.CTkFrame(self.control_frame)
        contrast_frame.pack(fill='x', padx=5, pady=5)
        ctk.CTkLabel(contrast_frame, text="Contrast").pack(side='left', padx=5)
        self.contrast_label = ctk.CTkLabel(contrast_frame, text=f"{self.settings.get('contrast', 1.0):.2f}")
        self.contrast_label.pack(side='right', padx=5)
        self.contrast_slider = ctk.CTkSlider(self.control_frame, from_=0.0, to=2.0,
                                           number_of_steps=200, command=self.update_contrast_label)
        self.contrast_slider.set(self.settings.get('contrast', 1.0))
        self.contrast_slider.pack(padx=5, pady=(0,10))
        
        # Brightness
        brightness_frame = ctk.CTkFrame(self.control_frame)
        brightness_frame.pack(fill='x', padx=5, pady=5)
        ctk.CTkLabel(brightness_frame, text="Brightness").pack(side='left', padx=5)
        self.brightness_label = ctk.CTkLabel(brightness_frame, text=f"{self.settings.get('brightness', 0.0):.2f}")
        self.brightness_label.pack(side='right', padx=5)
        self.brightness_slider = ctk.CTkSlider(self.control_frame, from_=-1.0, to=1.0,
                                             number_of_steps=200, command=self.update_brightness_label)
        self.brightness_slider.set(self.settings.get('brightness', 0.0))
        self.brightness_slider.pack(padx=5, pady=(0,10))
        
        # Apply button
        self.apply_btn = ctk.CTkButton(self.control_frame, text="Apply Settings", command=self.apply_settings)
        self.apply_btn.pack(pady=15)
    
    def get_camera_cmd(self):
        return [
            "libcamera-vid",
            "-t", "0",
            "--width", "640",
            "--height", "480",
            "--framerate", "24",
            "--codec", "h264",
            "--inline",
            "--profile", "baseline",
            "--level", "4.2",
            "--vflip",
            "--nopreview",
            "--shutter", str(int(self.shutter_slider.get())),
            "--gain", str(int(self.gain_slider.get())),
            "--awbgains", f"{self.awb_r_slider.get():.2f},{self.awb_b_slider.get():.2f}",
            "--contrast", str(self.contrast_slider.get()),
            "--brightness", str(self.brightness_slider.get()),
            "-o", "-"
        ]
    
    def get_ffmpeg_cmd(self):
        return [
            "ffmpeg",
            "-fflags", "nobuffer",
            "-flags", "low_delay",
            "-probesize", "32",
            "-analyzeduration", "0",
            "-r", "24",
            "-f", "h264",
            "-i", "-",
            "-vcodec", "rawvideo",
            "-pix_fmt", "bgr24",
            "-f", "rawvideo",
            "-"
        ]
    
    def start_camera(self):
        self.camera_proc = subprocess.Popen(self.get_camera_cmd(), stdout=subprocess.PIPE)
        self.ffmpeg_proc = subprocess.Popen(self.get_ffmpeg_cmd(), 
                                          stdin=self.camera_proc.stdout,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
        self.camera_proc.stdout.close()
    
    def stop_camera(self):
        if hasattr(self, 'ffmpeg_proc'):
            self.ffmpeg_proc.terminate()
        if hasattr(self, 'camera_proc'):
            self.camera_proc.terminate()
    
    def restart_camera(self):
        self.stop_camera()
        self.start_camera()
    
    def update_frame(self):
        cv2.namedWindow('Camera Feed', cv2.WINDOW_NORMAL)
        frame_size = 640 * 480 * 3  # width * height * 3 channels (BGR)
        
        while self.camera_running:
            raw_frame = self.ffmpeg_proc.stdout.read(frame_size)
            if len(raw_frame) == frame_size:
                frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((480, 640, 3))
                cv2.imshow('Camera Feed', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    
    def apply_settings(self):
        self.restart_camera()
    
    def on_closing(self):
        self.camera_running = False
        self.save_settings()
        self.stop_camera()
        cv2.destroyAllWindows()
        self.root.destroy()

if __name__ == "__main__":
    app = CameraControl()