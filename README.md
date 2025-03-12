# VirtualLife

VirtualLife is an artificial life simulator designed to model the emergence of complex behaviors from simple rules. Unlike detailed biological simulations, VirtualLife focuses on computational generations/turns within a virtual environment, starting with simple cells and parameterized rules to observe emergent patterns and behaviors.

## Project Vision

VirtualLife aims to create a flexible framework capable of simulating scenarios ranging from Conway's Game of Life to complex ecological systems featuring predator-prey relationships, mutualism, and other emergent behaviors.

## Key Features

- Grid-based environment with customizable rules
- Component-based entity system for flexible behavior composition
- Protocol-defined interfaces for clean module boundaries
- Species concept with trait inheritance and evolution
- Resource system with generation and consumption mechanics
- Data collection and analysis tools for emergent behaviors
- Multiple visualization options (terminal, GUI)
- Comprehensive test suite with minimum 90% coverage

## Development Principles

VirtualLife follows these core principles:

- **Test-First Development**: Every feature is built using TDD
- **Small, Focused Modules**: Each file has a single responsibility and is kept under 300 lines
- **Interface Contracts**: Explicit interfaces define module boundaries
- **Strict Dependency Hierarchy**: Prevents circular dependencies
- **Continuous Testing**: Automated tests run on every change
- **Comprehensive Documentation**: All code is well-documented

## Architecture

VirtualLife is built with a modular, component-based architecture:

```
virtuallife/
├── core/                  # Core simulation components
│   ├── interfaces/        # Protocol definitions
│   │   ├── entity.py      # Entity interface
│   │   └── environment.py # Environment interface
│   ├── environment/       # Environment implementation
│   ├── entity.py          # Entity implementation
│   ├── species.py         # Species definitions
│   └── simulation.py      # Simulation engine
├── components/            # Entity component implementations
├── behaviors/             # Entity behavior implementations
├── visualization/         # Visualization components
│   ├── terminal.py        # Terminal-based visualization
│   ├── gui.py             # GUI visualization (Pygame)
└── cli.py                 # Command-line interface
```

## Implementation Phases

1. **Core Simulation Framework**: Environment, entities, simulation engine, and Conway's Game of Life
2. **Resources and Behaviors**: Resource generation/consumption, entity behaviors, enhanced visualization
3. **Species and Genetics**: Species templates, trait inheritance, simple evolution
4. **Advanced Ecology**: Environmental factors, complex entity interactions, analysis tools
5. **Advanced Genetics**: Genetic systems, evolutionary dynamics, phylogenetic tracking

## Testing Approach

VirtualLife uses a comprehensive testing approach:

- **Unit Tests**: Each module is thoroughly tested in isolation
- **Integration Tests**: Component interactions are verified
- **Functional Tests**: End-to-end tests for complete scenarios
- **Property-Based Tests**: Verify complex behaviors across many inputs

Test coverage requirements:
- Minimum 90% line coverage
- Minimum 80% branch coverage
- All module interactions tested
- All user-facing features tested

## Quick Start

*Coming soon*

## Examples

### Conway's Game of Life

```bash
# Run Conway's Game of Life with a random initial pattern
virtuallife conway --width 50 --height 50 --pattern random

# Run Conway's Game of Life with a glider pattern
virtuallife conway --width 50 --height 50 --pattern glider
```

### Custom Simulation

```bash
# Run a custom simulation from a configuration file
virtuallife run --config examples/predator_prey.yaml --output results.json
```

## Development Status

This project is in early development. See [ROADMAP.md](ROADMAP.md) for the detailed development plan.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.