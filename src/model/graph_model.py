from collections import deque
from datetime import datetime, timedelta
import time

class GraphModel:
    """Model for managing graph data processing and smoothing"""
    def __init__(self, max_length=100, window_size=12):
        self.times = deque(maxlen=max_length)
        self.values = deque(maxlen=max_length)
        self.smoothed_values = deque(maxlen=max_length)
        self.window_size = window_size  # Moving average window
        self.last_update = 0
        self.last_print = 0
        self.last_value = None
        self.last_time = None
        self._observers = []

    def add_data_point(self, value, timestamp_ms):
        """Add new data point and process it"""
        # Skip if no new data
        if value == self.last_value and timestamp_ms == self.last_time:
            return False

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

            # Calculate smoothed value
            smoothed = self._calculate_smoothed_value(value)
            self.smoothed_values.append(smoothed)
            
            # Notify observers
            self._notify_observers()
            return True
        
        return False

    def _calculate_smoothed_value(self, current_value):
        """Calculate smoothed value using moving average"""
        values_list = list(self.values)
        if len(values_list) >= self.window_size:
            window = values_list[-self.window_size:]
            return sum(window) / self.window_size
        else:
            return current_value

    def get_plot_data(self):
        """Get data formatted for plotting"""
        if len(self.times) == 0:
            return None, None, None, None
            
        times_list = list(self.times)
        values_list = list(self.values)
        smoothed_list = list(self.smoothed_values)
        
        # Calculate time window (last 5 seconds)
        end_time = times_list[-1]
        start_time = end_time - timedelta(seconds=5)
        
        return times_list, values_list, smoothed_list, (start_time, end_time)

    def should_update_plot(self, update_interval=0.1):
        """Check if plot should be updated based on time interval"""
        current_time = time.time()
        if current_time - self.last_update >= update_interval and len(self.times) > 0:
            self.last_update = current_time
            return True
        return False

    def get_data_length(self):
        """Get current number of data points"""
        return len(self.times)

    def clear_data(self):
        """Clear all data"""
        self.times.clear()
        self.values.clear()
        self.smoothed_values.clear()
        self.last_value = None
        self.last_time = None
        self._notify_observers()

    def add_observer(self, observer):
        """Add observer for data changes"""
        self._observers.append(observer)

    def remove_observer(self, observer):
        """Remove observer"""
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(self):
        """Notify all observers of data changes"""
        for observer in self._observers:
            if hasattr(observer, 'on_graph_data_updated'):
                observer.on_graph_data_updated()
                