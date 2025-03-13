"""Matplotlib-based visualization for the simulation."""

from typing import Any, Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np

from virtuallife.visualize.base import Visualizer
from virtuallife.simulation.runner import SimulationRunner


class MatplotlibVisualizer(Visualizer):
    """A matplotlib-based visualizer for the simulation.
    
    This visualizer creates a graphical display of the simulation using matplotlib.
    It shows entities as colored markers on a grid and can display additional
    information like resource levels.
    
    Attributes:
        entity_colors: Dictionary mapping entity types to display colors
        fig: The matplotlib figure
        ax: The matplotlib axis
        scatter_plots: Dictionary of scatter plots for each entity type
        resource_plot: Optional imshow plot for resource levels
    """
    
    def __init__(self, entity_colors: Dict[str, str] = None) -> None:
        """Initialize the matplotlib visualizer.
        
        Args:
            entity_colors: Optional dictionary mapping entity types to colors.
                         Defaults to basic colors if not provided.
        """
        # Only include colors for actual entity types (no default)
        self.entity_colors = entity_colors or {
            "plant": "green",
            "herbivore": "blue",
            "predator": "red"
        }
        self.fig = None
        self.ax = None
        self.scatter_plots = {}
        self.resource_plot = None
    
    def setup(self, runner: SimulationRunner) -> None:
        """Set up the visualizer and attach to simulation events.
        
        Args:
            runner: The simulation runner to visualize
        """
        # Create figure and axis
        plt.ion()  # Enable interactive mode
        
        # Calculate figure size based on grid dimensions
        grid_ratio = runner.environment.width / runner.environment.height
        base_height = 8  # Base figure height
        
        # Add extra width for the legend (20% of the plot width for wide grids, 25% for others)
        plot_width = base_height * grid_ratio
        legend_width = plot_width * (0.20 if grid_ratio > 2 else 0.25)
        total_width = plot_width + legend_width
        
        # Create figure with adaptive size
        self.fig = plt.figure(figsize=(total_width, base_height))
        
        # Create main plot area with proper margins for legend
        # Left margin: 8%, Right margin: legend width + 2%, Top/Bottom: 10%
        left_margin = 0.08
        right_margin = legend_width / total_width + 0.02
        self.ax = self.fig.add_axes([left_margin, 0.1, 1 - (left_margin + right_margin), 0.8], aspect='equal')
        
        self.ax.set_xlim(-0.5, runner.environment.width - 0.5)
        self.ax.set_ylim(-0.5, runner.environment.height - 0.5)
        self.ax.grid(True)
        
        # Create initial scatter plots for each entity type
        for entity_type, color in self.entity_colors.items():
            self.scatter_plots[entity_type] = self.ax.scatter([], [], c=color, label=entity_type)
        
        # Create resource plot if environment has resources
        if runner.environment.resources:
            self.resource_plot = self.ax.imshow(
                np.zeros((runner.environment.height, runner.environment.width)),
                cmap='YlGn',
                alpha=0.3,
                extent=(-0.5, runner.environment.width - 0.5, -0.5, runner.environment.height - 0.5)
            )
        
        # Place legend completely outside the plot with adaptive positioning
        bbox_x = 1.02 if grid_ratio <= 2 else 1.01  # Closer to plot for wide grids
        self.ax.legend(bbox_to_anchor=(bbox_x, 1), loc='upper left')
        plt.title("VirtualLife Simulation")
        
        # Attach to simulation events
        runner.add_listener("step_end", self.update)
    
    def update(self, runner: SimulationRunner, **kwargs: Any) -> None:
        """Update the visualization with the current simulation state.
        
        Args:
            runner: The simulation runner being visualized
            **kwargs: Additional data passed from simulation events
        """
        env = runner.environment
        
        # Update title with simulation info
        plt.title(f"VirtualLife Simulation - Step {runner.current_step}")
        
        # Collect entity positions by type
        positions: Dict[str, List[Tuple[float, float]]] = {
            entity_type: [] for entity_type in self.entity_colors
        }
        
        # Group entities by type
        for pos, entity_ids in env.entity_positions.items():
            if entity_ids:
                x, y = pos
                entity = env.entities[next(iter(entity_ids))]
                entity_type = None
                for component_type in ["plant", "herbivore", "predator"]:
                    if entity.has_component(component_type):
                        entity_type = component_type
                        break
                if entity_type in self.entity_colors:
                    positions[entity_type].append((x, y))
        
        # Update scatter plots
        for entity_type, pos_list in positions.items():
            if pos_list:
                x, y = zip(*pos_list)
            else:
                x, y = [], []
            self.scatter_plots[entity_type].set_offsets(np.c_[x, y])
        
        # Update resource plot if available
        if self.resource_plot is not None and "food" in env.resources:
            # Convert resources to numpy array
            resource_array = np.zeros((env.height, env.width))
            for (x, y), value in env.resources["food"].items():
                resource_array[y, x] = value
            self.resource_plot.set_array(resource_array)
        
        # Redraw
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def cleanup(self) -> None:
        """Clean up any resources used by the visualizer."""
        if self.fig is not None:
            plt.close(self.fig)
            self.fig = None
            self.ax = None 