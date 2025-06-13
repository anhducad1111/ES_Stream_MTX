import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GraphView:
    """Graph View - Pure UI component for displaying matplotlib graph"""
    def __init__(self, master):
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
        """Get the tkinter widget for embedding in UI"""
        return self.canvas.get_tk_widget()

    def update_plot_data(self, dates, values, smoothed_values, time_window):
        """Update plot with new data from presenter"""
        try:
            # Update plot lines
            self.line_raw.set_data(dates, values)
            self.line_smooth.set_data(dates, smoothed_values)

            # Set time window
            start_time, end_time = time_window
            self.ax.set_xlim(start_time, end_time)

            # Adjust Y-axis automatically
            self.ax.relim()
            self.ax.autoscale_view(scalex=False, scaley=True)

            # Redraw canvas
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error updating plot: {e}")

    def cleanup(self):
        """Clean up matplotlib resources"""
        plt.close(self.fig)
