# VirtualLife CLI Usage Guide

VirtualLife provides a command-line interface (CLI) for running simulations, configuring simulations, and visualizing results. This guide explains how to use the CLI effectively.

## Installation

Before using the CLI, make sure VirtualLife is installed and available in your environment:

```bash
# If using Poetry (recommended)
poetry install

# If using pip
pip install -e .
```

## Basic Commands

VirtualLife CLI provides the following commands:

- `run`: Run a simulation with specified settings
- `info`: Display information about a configuration
- `create-config`: Create a new configuration file with custom settings

## Running Simulations

### Basic Usage

To run a simulation with default settings:

```bash
virtuallife run
```

This will start a simulation with default parameters and console visualization, running indefinitely until you press Ctrl+C.

### Specifying Step Count

To run a simulation for a specific number of steps:

```bash
virtuallife run --steps 100
```

This will run the simulation for 100 steps and then stop.

### Using a Configuration File

To run a simulation with a custom configuration:

```bash
virtuallife run --config examples/configs/default.yaml
```

### Visualization Options

VirtualLife supports different visualization methods:

#### Console Visualization (default)

```bash
virtuallife run --visualizer console
```

This displays the simulation as a text grid in the console.

#### Matplotlib Visualization

```bash
virtuallife run --visualizer matplotlib
```

This shows the simulation using matplotlib, providing a more visual representation.

#### No Visualization

```bash
virtuallife run --no-vis
```

This runs the simulation without any visualization, which is useful for headless environments or when performance is critical.

### Additional Options

#### Setting a Random Seed

For reproducible simulations, you can set a random seed:

```bash
virtuallife run --seed 42
```

#### Adding a Delay Between Steps

To slow down the simulation for better visualization:

```bash
virtuallife run --delay 0.1
```

This adds a 0.1-second delay between simulation steps.

## Viewing Configuration Information

To view details about a configuration:

```bash
# View default configuration
virtuallife info

# View a specific configuration file
virtuallife info --config examples/configs/default.yaml
```

This command displays information about the environment, energy settings, movement parameters, reproduction settings, and resource parameters.

## Creating Configuration Files

To create a new configuration file with custom settings:

```bash
virtuallife create-config my_config.yaml --width 200 --height 200 --boundary wrapped --entities 50 --seed 123
```

This creates a new configuration file with the specified parameters. Available options include:

- `--width`: Width of the environment (default: 100)
- `--height`: Height of the environment (default: 100)
- `--boundary`: Boundary condition, "wrapped" or "bounded" (default: "wrapped")
- `--entities`: Initial number of entities (default: 10)
- `--delay`: Delay between steps (default: 0.1)
- `--seed`: Random seed for reproducible results

## Complete Examples

### Running a Predator-Prey Scenario

```bash
# Create a custom configuration
virtuallife create-config predator_prey.yaml --width 150 --height 150 --entities 30 --seed 42

# Run the simulation with matplotlib visualization
virtuallife run --config predator_prey.yaml --visualizer matplotlib --steps 500
```

### Running a Long Performance Test

```bash
# Run a simulation without visualization for 10,000 steps
virtuallife run --no-vis --steps 10000
```

### Interactive Exploration

```bash
# Run an indefinite simulation with a slow step delay to observe behavior
virtuallife run --visualizer matplotlib --delay 0.2
```

## Troubleshooting

### Common Issues

1. **Command not found**: Ensure that VirtualLife is installed properly and that the CLI script is in your PATH.

2. **Visualization errors**: If you encounter errors with matplotlib visualization, ensure you have the required dependencies installed and that you're running in an environment with display support.

3. **Configuration errors**: If you get validation errors when loading a configuration file, check that all parameters are within valid ranges and of the correct types.

## Advanced Usage

### Combining CLI Options

You can combine multiple options to customize your simulation:

```bash
virtuallife run --config my_config.yaml --visualizer matplotlib --steps 100 --delay 0.05 --seed 42
```

### Creating Complex Configurations

For more complex configurations, create a basic configuration file first and then edit it manually:

```bash
# Create a basic config
virtuallife create-config base_config.yaml

# Edit it in your editor
# Then run with the modified config
virtuallife run --config base_config.yaml
```

## Next Steps

- Explore different parameter combinations to observe emergent behaviors
- Create custom configurations for specific scenarios
- Use the API for more advanced integration and analysis 