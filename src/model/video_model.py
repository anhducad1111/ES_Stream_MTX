import threading
import queue
import ffmpeg
import numpy as np
import cv2
import time

# Constants
width, height = 640, 480

class VideoModel(threading.Thread):
    """Model for handling video stream data and processing"""
    def __init__(self, rtsp_url):
        super().__init__(daemon=True)
        self.rtsp_url = rtsp_url
        self.frame_queue = queue.Queue(maxsize=3)
        self.running = True
        self.process = None
        self.connected = False
        self.last_frame_time = 0
        self.reconnect_delay = 1.0
        self._observers = []
        
    def _start_ffmpeg(self):
        if self.process:
            self.cleanup()
            
        try:
            # Using exact same configuration as working code
            self.process = (
                ffmpeg
                .input(
                    self.rtsp_url,
                    rtsp_transport='udp',
                    flags='low_delay',
                    fflags='nobuffer',
                    probesize='32',
                    analyzeduration='0',
                    r='24'
                )
                .output('pipe:', format='rawvideo', pix_fmt='bgr24')
                .run_async(pipe_stdout=True)
            )
            print(f"[{time.strftime('%H:%M:%S')}] RTSP stream connected")
            self.connected = True
            self.last_frame_time = time.time()
            self._notify_connection_status()
            return True
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Failed to connect to RTSP: {e}")
            return False
        
    def run(self):
        print(f"[{time.strftime('%H:%M:%S')}] Starting video thread")
        while self.running:
            try:
                # Try to connect if not connected
                if not self.process:
                    if not self._start_ffmpeg():
                        time.sleep(self.reconnect_delay)
                        continue
                
                # Read frames
                in_bytes = self.process.stdout.read(width * height * 3)
                if not in_bytes:
                    print(f"[{time.strftime('%H:%M:%S')}] No data from RTSP stream")
                    self.cleanup()
                    continue
                    
                frame = np.frombuffer(in_bytes, np.uint8).reshape([height, width, 3])
                
                # Update last frame time
                self.last_frame_time = time.time()
                
                try:
                    # Only drop frames if queue is full
                    if self.frame_queue.full():
                        try:
                            self.frame_queue.get_nowait()  # Remove oldest frame
                        except queue.Empty:
                            pass
                    self.frame_queue.put_nowait(frame)
                    # self._notify_frame_available()  # Bỏ notification để tránh conflict
                except:
                    pass
                        
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] Video thread error: {e}")
                self.cleanup()
                time.sleep(self.reconnect_delay)
                
    def cleanup(self):
        if self.process:
            try:
                self.process.stdout.close()
            except:
                pass
            finally:
                self.process = None
                self.connected = False
                self._notify_connection_status()
        
    def get_frame(self):
        """Get latest frame, converted to RGB"""
        try:
            frame = self.frame_queue.get_nowait()
            if frame is not None:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return frame
        except queue.Empty:
            return None
            
    def is_connected(self):
        return self.process is not None and self.connected
            
    def stop(self):
        print(f"[{time.strftime('%H:%M:%S')}] Stopping video thread")
        self.running = False
        self.cleanup()

    def add_observer(self, observer):
        """Add observer for video events"""
        self._observers.append(observer)

    def remove_observer(self, observer):
        """Remove observer"""
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_frame_available(self):
        """Notify observers that new frame is available"""
        for observer in self._observers:
            if hasattr(observer, 'on_frame_available'):
                observer.on_frame_available()

    def _notify_connection_status(self):
        """Notify observers of connection status change"""
        for observer in self._observers:
            if hasattr(observer, 'on_video_connection_changed'):
                observer.on_video_connection_changed(self.connected)