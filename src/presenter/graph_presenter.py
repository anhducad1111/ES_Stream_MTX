import matplotlib.pyplot as plt

class GraphPresenter:
    """Graph Presenter - Controls graph updates and interactions"""
    def __init__(self, view, graph_model):
        self.view = view
        self.graph_model = graph_model
        
        # Setup as observer of graph model
        self.graph_model.add_observer(self)
        
    def on_graph_data_updated(self):
        """Called when graph model data is updated"""
        if self.graph_model.should_update_plot():
            self._update_graph_display()
    
    def _update_graph_display(self):
        """Update the graph display with new data"""
        times, values, smoothed, time_window = self.graph_model.get_plot_data()
        
        if times and values and smoothed and time_window:
            # Convert times to matplotlib format
            dates = plt.matplotlib.dates.date2num(times)
            
            # Update view with plot data
            self.view.update_plot_data(dates, values, smoothed, time_window)
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self.graph_model, 'remove_observer'):
            self.graph_model.remove_observer(self)