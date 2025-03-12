"""Command-line interface for VirtualLife.

This module provides a command-line interface for running simulations,
configuring simulations, and visualizing results.
"""

import logging
import random
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler

from virtuallife.config.loader import load_or_default, save_config
from virtuallife.config.models import SimulationConfig
from virtuallife.simulation.environment import Environment
from virtuallife.simulation.runner import SimulationRunner
from virtuallife.visualize.console import ConsoleVisualizer
from virtuallife.visualize.plotting import MatplotlibVisualizer

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


def setup_simulation(
    config: SimulationConfig,
    visualizer_type: str
) -> tuple[SimulationRunner, Optional[ConsoleVisualizer | MatplotlibVisualizer]]:
    """Set up a simulation with the given configuration and visualizer type.
    
    Args:
        config: The simulation configuration
        visualizer_type: The type of visualizer to use ("console", "matplotlib", or "none")
        
    Returns:
        A tuple containing the simulation runner and visualizer (if any)
    """
    # Set random seed if provided
    if config.random_seed is not None:
        random.seed(config.random_seed)
        logger.info(f"Using random seed: {config.random_seed}")
        
    # Initialize environment
    environment = Environment(
        width=config.environment.width,
        height=config.environment.height,
        boundary_condition=config.environment.boundary_condition
    )
    
    # Create simulation runner
    runner = SimulationRunner(environment=environment, config=config.model_dump())
    
    # Set up visualization if requested
    visualizer = None
    if visualizer_type == "console":
        visualizer = ConsoleVisualizer(runner)
        runner.add_listener("step_end", visualizer.update)
    elif visualizer_type == "matplotlib":
        visualizer = MatplotlibVisualizer(runner)
        runner.add_listener("step_end", visualizer.update)
    
    return runner, visualizer


@app.command("run")
def run_simulation(
    config_path: Optional[Path] = typer.Option(
        None,
        "--config", "-c",
        help="Path to the configuration file (YAML)",
        exists=False,
        file_okay=True,
        dir_okay=False,
    ),
    steps: Optional[int] = typer.Option(
        None,
        "--steps", "-s", 
        help="Number of steps to run (default: unlimited)",
        min=1,
    ),
    visualizer: str = typer.Option(
        "console",
        "--visualizer", "-v", 
        help="Visualization method to use",
        case_sensitive=False,
    ),
    no_visualization: bool = typer.Option(
        False,
        "--no-vis",
        help="Disable visualization",
        is_flag=True,
    ),
    step_delay: Optional[float] = typer.Option(
        None,
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
    """Run a simulation with the specified configuration."""
    try:
        # Load configuration
        config = load_or_default(config_path)
        
        # Override config with command-line options
        if step_delay is not None:
            config.max_steps = steps
        if random_seed is not None:
            config.random_seed = random_seed
        
        # Set up visualizer type
        vis_type = "none" if no_visualization else visualizer.lower()
        if vis_type not in ["console", "matplotlib", "none"]:
            logger.error(f"Unknown visualizer type: {vis_type}")
            logger.info("Available visualizers: console, matplotlib, none")
            sys.exit(1)
            
        # Set up the simulation
        runner, vis = setup_simulation(config, vis_type)
        
        # Add step delay if specified
        if step_delay is not None:
            runner.config["step_delay"] = step_delay
        
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