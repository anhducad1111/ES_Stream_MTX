import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import customtkinter as ctk

class GraphView:
    """Graph View - Pure UI component for displaying matplotlib graph"""
    def __init__(self, master):
        self.master = master
        # Setup matplotlib figure with modern styling
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(12, 3.5), facecolor='#212121')
        self.fig.patch.set_facecolor('#212121')
        self.ax.set_facecolor('#2b2b2b')

        # Create canvas and embed in master
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Enhanced plot styling
        self.line_raw, = self.ax.plot([], [],
                                     color="#4CAF50",
                                     alpha=0.4,
                                     linewidth=1.5,
                                     label="Raw Data",
                                     marker='o',
                                     markersize=2,
                                     markerfacecolor="#4CAF50",
                                     markeredgecolor="none")
        
        self.line_smooth, = self.ax.plot([], [],
                                        color='#00E676',
                                        linewidth=3,
                                        label="Smoothed")

        # Modern grid and styling
        self.ax.grid(True, alpha=0.2, color='#555555', linestyle='-', linewidth=0.5)
        self.ax.set_xlabel('Time', fontsize=11, color='#E0E0E0', fontweight='bold')
        self.ax.set_ylabel('Value', fontsize=11, color='#E0E0E0', fontweight='bold')
        
        # Format time axis
        plt.setp(self.ax.get_xticklabels(), rotation=45, fontsize=9, color='#BDBDBD')
        plt.setp(self.ax.get_yticklabels(), fontsize=9, color='#BDBDBD')
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax.xaxis.set_major_locator(mdates.SecondLocator(interval=30))
        
        # Style the spines
        for spine in self.ax.spines.values():
            spine.set_color('#555555')
            spine.set_linewidth(1)
        
        # Add legend with modern styling
        legend = self.ax.legend(loc='upper left',
                               frameon=True,
                               fancybox=True,
                               shadow=True,
                               fontsize=9,
                               facecolor='#333333',
                               edgecolor='#555555')
        legend.get_frame().set_alpha(0.8)
        for text in legend.get_texts():
            text.set_color('#E0E0E0')
        
        # Tight layout with padding
        self.fig.tight_layout(pad=2.0)
        self.canvas.draw()

        print("GraphView initialized with modern styling")

    def get_widget(self):
        """Get the master widget for embedding in UI"""
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
