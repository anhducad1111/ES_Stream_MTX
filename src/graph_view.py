import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
from datetime import datetime
import time

class GraphView:
    def __init__(self, master):
        self.times = deque(maxlen=100)
        self.values = deque(maxlen=100)
        self.last_update = 0
        self.last_print = 0
        self.last_value = None
        self.last_time = None
        
        # Setup chart
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(15, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.draw()

        # Configure time format
        self.ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M:%S.%f'))
        print("Graph initialized")
        
    def get_widget(self):
        return self.canvas.get_tk_widget()
    
    def update(self, value, timestamp_ms):
        # Skip if no new data
        if value == self.last_value and timestamp_ms == self.last_time:
            return
            
        self.last_value = value
        self.last_time = timestamp_ms

        # Print debug info every second
        current_time = time.time()
        if current_time - self.last_print >= 1.0:
            # print(f"Graph Update - Value: {value}, Points: {len(self.values)}")
            self.last_print = current_time

        # Store data at full rate
        if timestamp_ms > 0:  # Only add if timestamp is valid
            dt = datetime.fromtimestamp(timestamp_ms / 1000.0)
            self.times.append(dt)
            self.values.append(value)
            
            # Only redraw every 200ms
            if current_time - self.last_update >= 0.2:
                # Plot all collected data
                self.ax.clear()
                if len(self.times) > 0:  # Only plot if we have data
                    dates = plt.matplotlib.dates.date2num(list(self.times))
                    self.ax.plot(dates, list(self.values), color='#00ff00')
                    
                    # Format x-axis
                    self.ax.grid(True, alpha=0.3)
                    plt.setp(self.ax.get_xticklabels(), rotation=45)
                    self.ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M:%S.%f'))
                    
                    self.fig.tight_layout()
                    self.canvas.draw()
                    self.last_update = current_time
    
    def cleanup(self):
        plt.close(self.fig)