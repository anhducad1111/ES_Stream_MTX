import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
from datetime import datetime
import time

class GraphView:
    def __init__(self, master):
        self.times = deque(maxlen=100)
        self.values = deque(maxlen=100)
        self.smoothed_values = deque(maxlen=100)  # For storing smoothed values
        self.window_size = 5  # Smoothing window size
        self.last_update = 0
        self.last_print = 0
        self.last_value = None
        self.last_time = None
        
        # Setup chart
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(14, 4))
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
            
            # Calculate smoothed value using moving average
            values_list = list(self.values)
            if len(values_list) >= self.window_size:
                # Calculate moving average for the latest window
                window = values_list[-self.window_size:]
                smoothed = sum(window) / self.window_size
            else:
                # Use actual value if not enough data points
                smoothed = value
            self.smoothed_values.append(smoothed)

            # Only redraw every 100ms
            if current_time - self.last_update >= 0.1:
                # Plot all collected data
                self.ax.clear()
                if len(self.times) > 0:  # Only plot if we have data
                    dates = plt.matplotlib.dates.date2num(list(self.times))
                    # Plot both raw and smoothed data
                    self.ax.plot(dates, list(self.values), color="#00C900", alpha=0.3, linewidth=1.5)  # Raw data
                    self.ax.plot(dates, list(self.smoothed_values), color='#00ff00', linewidth=2)  # Smoothed data
                    
                    # Format x-axis
                    self.ax.grid(True, alpha=0.3)
                    plt.setp(self.ax.get_xticklabels(), rotation=45)
                    self.ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M:%S.%f'))
                    
                    self.fig.tight_layout()
                    self.canvas.draw()
                    self.last_update = current_time
    
    def cleanup(self):
        plt.close(self.fig)