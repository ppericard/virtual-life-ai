"""Command-line interface for VirtualLife.

This module provides a command-line interface for running simulations,
configuring simulations, and visualizing results.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler

from virtuallife.config.loader import load_or_default, save_config
from virtuallife.config.models import SimulationConfig
from virtuallife.simulation.factory import setup_simulation

# Set up logging with rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("virtuallife")

# Set up the typer app
app = typer.Typer(
    help="VirtualLife: An artificial life simulation framework",
    add_completion=False,
)

# Create a console for rich output
console = Console()


@app.command("run")
def run_simulation(
    config_path: Optional[Path] = typer.Option(
        None,
        "--config", "-c",
        help="Path to the configuration file (YAML). If not provided, uses examples/configs/default.yaml",
        exists=False,
        file_okay=True,
        dir_okay=False,
    ),
    steps: Optional[int] = typer.Option(
        None,
        "--steps", "-s", 
        help="Number of steps to run. Use None for unlimited simulation.",
        min=1,
    ),
    visualizer: str = typer.Option(
        "matplotlib",
        "--visualizer", "-v", 
        help="Visualization method to use. Possible values: [matplotlib, console, none]",
        case_sensitive=False,
    ),
    no_visualization: bool = typer.Option(
        False,
        "--no-vis",
        help="Disable visualization (equivalent to --visualizer none)",
        is_flag=True,
    ),
    step_delay: Optional[float] = typer.Option(
        None,
        "--delay", "-d",
        help="Delay between steps in seconds. Default: 0.5",
        min=0.0,
    ),
    random_seed: Optional[int] = typer.Option(
        None,
        "--seed",
        help="Random seed for reproducible results. Use None for random initialization.",
    ),
):
    """Run a simulation with the specified configuration.
    
    The simulation can be configured using various options:
    
    Visualization:
    - Use --visualizer to choose the visualization method:
      * matplotlib: Graphical display with plots (default)
      * console: Simple ASCII visualization in terminal
      * none: No visualization
    
    Simulation Control:
    - Use --steps to limit the number of steps (default: unlimited)
    - Use --delay to control simulation speed (default: 0.5s)
    - Use --seed for reproducible results
    - Use --no-vis to disable visualization
    
    Configuration:
    - Use --config to specify a custom configuration file
    - Without --config, uses the default configuration
    """
    try:
        # Load configuration
        config = load_or_default(config_path)
        
        # Override config with command-line options
        if steps is not None:
            config.max_steps = steps
        if random_seed is not None:
            config.random_seed = random_seed
        if step_delay is not None:
            config.step_delay = step_delay
        
        # Set up visualizer type
        vis_type = "none" if no_visualization else visualizer.lower()
        if vis_type not in ["console", "matplotlib", "none"]:
            logger.error(f"Unknown visualizer type: {vis_type}")
            logger.info("Available visualizers: console, matplotlib, none")
            sys.exit(1)
            
        # Set up the simulation
        runner, vis = setup_simulation(config, vis_type)
        
        # Log simulation start
        logger.info(f"Starting simulation with {config.environment.width}x{config.environment.height} environment")
        logger.info(f"Using {vis_type} visualization")
        if steps:
            logger.info(f"Running for {steps} steps")
        else:
            logger.info("Running indefinitely (press Ctrl+C to stop)")
        
        # Run the simulation
        try:
            runner.run(steps)
        except KeyboardInterrupt:
            logger.info("Simulation stopped by user")
            runner.stop()
            
        # Print final statistics
        logger.info(f"Simulation completed after {runner.current_step} steps")
        logger.info(f"Entities remaining: {len(runner.environment.entities)}")
        
    except Exception as e:
        logger.exception(f"Error during simulation: {str(e)}")
        sys.exit(1)


@app.command("info")
def show_info(
    config_path: Optional[Path] = typer.Option(
        None,
        "--config", "-c",
        help="Path to the configuration file (YAML)",
        exists=False,
        file_okay=True,
        dir_okay=False,
    ),
):
    """Display information about a configuration."""
    try:
        # Load configuration
        config = load_or_default(config_path)
        
        # Print configuration details
        console.print("[bold green]Configuration Details:[/bold green]")
        console.print(f"Environment: {config.environment.width}x{config.environment.height} ({config.environment.boundary_condition})")
        console.print(f"Initial entities: {config.environment.initial_entities}")
        console.print(f"Random seed: {config.random_seed}")
        console.print(f"Max steps: {config.max_steps}")
        console.print(f"Step delay: {config.step_delay} seconds")
        
        console.print("\n[bold green]Component Configurations:[/bold green]")
        console.print("[bold]Energy:[/bold]")
        console.print(f"  Initial: {config.energy.initial_energy}")
        console.print(f"  Max: {config.energy.max_energy}")
        console.print(f"  Decay rate: {config.energy.decay_rate}")
        console.print(f"  Death threshold: {config.energy.death_threshold}")
        
        console.print("[bold]Movement:[/bold]")
        console.print(f"  Speed: {config.movement.speed}")
        console.print(f"  Cost: {config.movement.movement_cost}")
        
        console.print("[bold]Reproduction:[/bold]")
        console.print(f"  Threshold: {config.reproduction.reproduction_threshold}")
        console.print(f"  Cost: {config.reproduction.reproduction_cost}")
        console.print(f"  Chance: {config.reproduction.reproduction_chance}")
        console.print(f"  Mutation rate: {config.reproduction.mutation_rate}")
        
        console.print("[bold]Resources:[/bold]")
        console.print(f"  Initial density: {config.resources.initial_density}")
        console.print(f"  Regrowth rate: {config.resources.regrowth_rate}")
        console.print(f"  Max resource: {config.resources.max_resource}")
        console.print(f"  Types: {', '.join(config.resources.resource_types.keys())}")
        
    except Exception as e:
        logger.exception(f"Error displaying configuration: {str(e)}")
        sys.exit(1)


@app.command("create-config")
def create_config(
    output_path: Path = typer.Argument(
        ...,
        help="Path to save the configuration file",
    ),
    width: int = typer.Option(
        100,
        "--width", "-w",
        help="Width of the environment",
        min=10,
    ),
    height: int = typer.Option(
        100,
        "--height", "-h",
        help="Height of the environment",
        min=10,
    ),
    boundary: str = typer.Option(
        "wrapped",
        "--boundary", "-b",
        help="Boundary condition (wrapped or bounded)",
    ),
    entities: int = typer.Option(
        10,
        "--entities", "-e",
        help="Initial number of entities",
        min=1,
    ),
    step_delay: Optional[float] = typer.Option(
        0.1,
        "--delay", "-d",
        help="Delay between steps in seconds",
        min=0.0,
    ),
    random_seed: Optional[int] = typer.Option(
        None,
        "--seed",
        help="Random seed for reproducible results",
    ),
):
    """Create a new configuration file with custom settings."""
    try:
        # Create configuration with custom settings
        config = SimulationConfig()
        
        # Override environment settings
        config.environment.width = width
        config.environment.height = height
        if boundary.lower() in ["wrapped", "bounded"]:
            config.environment.boundary_condition = boundary.lower()
        else:
            logger.warning(f"Invalid boundary condition '{boundary}', using 'wrapped'")
            config.environment.boundary_condition = "wrapped"
        config.environment.initial_entities = entities
        
        # Set other options
        config.random_seed = random_seed
        
        # Save the configuration
        save_config(config, output_path)
        logger.info(f"Configuration saved to {output_path}")
        
    except Exception as e:
        logger.exception(f"Error creating configuration: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    app() 