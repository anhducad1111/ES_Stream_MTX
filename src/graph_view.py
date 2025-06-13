import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
from datetime import datetime, timedelta
import time

class GraphView:
    def __init__(self, master):
        self.times = deque(maxlen=100)
        self.values = deque(maxlen=100)
        self.smoothed_values = deque(maxlen=100)
        self.window_size = 24  # Moving average window
        self.last_update = 0
        self.last_print = 0
        self.last_value = None
        self.last_time = None

        # Setup matplotlib figure
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(14, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.draw()

        # Plot placeholders
        self.line_raw, = self.ax.plot([], [], color="#00C900", alpha=0.3, linewidth=1.5)
        self.line_smooth, = self.ax.plot([], [], color='#00ff00', linewidth=2)

        # Format and layout
        self.ax.grid(True, alpha=0.3)
        plt.setp(self.ax.get_xticklabels(), rotation=45)
        self.ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M:%S'))
        self.fig.tight_layout()

        print("GraphView initialized")

    def get_widget(self):
        return self.canvas.get_tk_widget()

    def update(self, value, timestamp_ms):
        # Skip if no new data
        if value == self.last_value and timestamp_ms == self.last_time:
            return

        self.last_value = value
        self.last_time = timestamp_ms
        current_time = time.time()

        if current_time - self.last_print >= 1.0:
            self.last_print = current_time

        # Add new data
        if timestamp_ms > 0:
            dt = datetime.fromtimestamp(timestamp_ms / 1000.0)
            self.times.append(dt)
            self.values.append(value)

            # Smoothing
            values_list = list(self.values)
            if len(values_list) >= self.window_size:
                window = values_list[-self.window_size:]
                smoothed = sum(window) / self.window_size
            else:
                smoothed = value
            self.smoothed_values.append(smoothed)

        # Update plot every 100ms
        if current_time - self.last_update >= 0.1 and len(self.times) > 0:
            dates = plt.matplotlib.dates.date2num(list(self.times))
            self.line_raw.set_data(dates, list(self.values))
            self.line_smooth.set_data(dates, list(self.smoothed_values))

            # Fixed X-axis window (last 5 seconds)
            end_time = self.times[-1]
            start_time = end_time - timedelta(seconds=5)
            self.ax.set_xlim(start_time, end_time)

            # Adjust Y-axis automatically
            self.ax.relim()
            self.ax.autoscale_view(scalex=False, scaley=True)

            self.canvas.draw()
            self.last_update = current_time

    def cleanup(self):
        plt.close(self.fig)
