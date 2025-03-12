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
    """
    
    def __init__(self, entity_symbols: Dict[str, str] = None) -> None:
        """Initialize the console visualizer.
        
        Args:
            entity_symbols: Optional dictionary mapping entity types to display symbols.
                          Defaults to basic symbols if not provided.
        """
        self.entity_symbols = entity_symbols or {
            "default": "○",
            "plant": "♣",
            "herbivore": "□",
            "predator": "△"
        }
        self.empty_symbol = "·"
    
    def setup(self, runner: SimulationRunner) -> None:
        """Set up the visualizer and attach to simulation events.
        
        Args:
            runner: The simulation runner to visualize
        """
        runner.add_listener("step_end", self.update)
    
    def update(self, runner: SimulationRunner, **kwargs: Any) -> None:
        """Update the console display with the current simulation state.
        
        Args:
            runner: The simulation runner being visualized
            **kwargs: Additional data passed from simulation events
        """
        # Clear screen (works on both Windows and Unix-like systems)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        env = runner.environment
        width, height = env.width, env.height
        
        # Print simulation info
        print(f"Step: {runner.current_step}")
        print(f"Entities: {len(env.entities)}")
        print()
        
        # Create the grid display
        grid: List[List[str]] = [[self.empty_symbol for _ in range(width)] for _ in range(height)]
        
        # Fill in entities
        for pos, entity_ids in env.entity_positions.items():
            if entity_ids:  # Only process positions with entities
                x, y = pos
                entity = env.entities[next(iter(entity_ids))]  # Get first entity at position
                # Get entity type from components or use default
                entity_type = "default"
                for component_type in ["plant", "herbivore", "predator"]:
                    if entity.has_component(component_type):
                        entity_type = component_type
                        break
                grid[y][x] = self.entity_symbols.get(entity_type, self.entity_symbols["default"])
        
        # Print the grid
        border = "+" + "-" * (width * 2 + 1) + "+"
        print(border)
        for row in grid:
            print("| " + " ".join(row) + " |")
        print(border)
        print()
        
        # Ensure output is displayed immediately
        sys.stdout.flush()
    
    def cleanup(self) -> None:
        """Clean up any resources used by the visualizer."""
        pass  # No cleanup needed for console visualization 