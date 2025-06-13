class DataModel:
    """Model for managing numeric data from TCP stream"""
    def __init__(self):
        self.finger_count = 0
        self.timestamp_ms = 0
        self._observers = []

    def update_data(self, finger_count, timestamp_ms):
        """Update data and notify observers"""
        if finger_count != self.finger_count or timestamp_ms != self.timestamp_ms:
            self.finger_count = finger_count
            self.timestamp_ms = timestamp_ms
            self._notify_observers()

    def get_finger_count(self):
        return self.finger_count

    def get_timestamp_ms(self):
        return self.timestamp_ms

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
            if hasattr(observer, 'on_data_updated'):
                observer.on_data_updated(self.finger_count, self.timestamp_ms)