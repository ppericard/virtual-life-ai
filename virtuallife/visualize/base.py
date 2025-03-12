"""Base visualization module defining visualization interfaces."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from virtuallife.simulation.runner import SimulationRunner


class Visualizer(ABC):
    """Abstract base class for simulation visualizers.
    
    This class defines the interface that all visualizers must implement.
    Visualizers are responsible for displaying the current state of the
    simulation in some form (console, graphical, etc.).
    """
    
    @abstractmethod
    def setup(self, runner: SimulationRunner) -> None:
        """Set up the visualizer and attach to simulation events.
        
        Args:
            runner: The simulation runner to visualize
        """
        pass
    
    @abstractmethod
    def update(self, runner: SimulationRunner, **kwargs: Any) -> None:
        """Update the visualization with the current simulation state.
        
        Args:
            runner: The simulation runner being visualized
            **kwargs: Additional data passed from simulation events
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up any resources used by the visualizer."""
        pass 