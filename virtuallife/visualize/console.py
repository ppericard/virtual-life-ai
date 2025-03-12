"""Console-based visualization for the simulation."""

import os
import sys
from typing import Any, Dict, List

from virtuallife.visualize.base import Visualizer
from virtuallife.simulation.runner import SimulationRunner


class ConsoleVisualizer(Visualizer):
    """A simple console-based visualizer for the simulation.
    
    This visualizer displays the simulation state in the console using ASCII characters.
    It clears the screen between updates to create a simple animation effect.
    
    Attributes:
        entity_symbols: Dictionary mapping entity types to display symbols
        empty_symbol: Symbol to use for empty cells
        runner: The simulation runner being visualized
    """
    
    def __init__(self) -> None:
        """Initialize the console visualizer."""
        self.entity_symbols = {
            "default": "○",
            "plant": "♣",
            "herbivore": "□",
            "predator": "△"
        }
        self.empty_symbol = "·"
        self.runner = None
    
    def setup(self, runner: SimulationRunner) -> None:
        """Set up the visualizer and attach to simulation events.
        
        Args:
            runner: The simulation runner to visualize
        """
        self.runner = runner
        runner.add_listener("step_end", self.update)
    
    def clear_screen(self) -> None:
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def update(self, simulation: SimulationRunner, **kwargs: Any) -> None:
        """Update the visualization.
        
        Args:
            simulation: The simulation runner
            **kwargs: Additional keyword arguments
        """
        if not self.runner:
            return
            
        self.clear_screen()
        env = simulation.environment
        
        # Print simulation info
        print(f"Step: {simulation.current_step}")
        print(f"Entities: {len(env.entities)}")
        print()
        
        # Print grid
        for y in range(env.height - 1, -1, -1):  # Print from top to bottom
            for x in range(env.width):
                pos = (x, y)
                entities = env.get_entities_at(pos)
                if entities:
                    # For now, just print the first entity at each position
                    entity = entities[0]
                    # Determine entity type based on components
                    if entity.has_component("predator"):
                        symbol = self.entity_symbols["predator"]
                    elif entity.has_component("herbivore"):
                        symbol = self.entity_symbols["herbivore"]
                    elif entity.has_component("plant"):
                        symbol = self.entity_symbols["plant"]
                    else:
                        symbol = self.entity_symbols["default"]
                    print(symbol, end=" ")
                else:
                    print(self.empty_symbol, end=" ")
            print()  # New line at end of row
        print()  # Extra line after grid
    
    def cleanup(self) -> None:
        """Clean up any resources used by the visualizer."""
        pass  # No cleanup needed for console visualization 