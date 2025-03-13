# VirtualLife

VirtualLife is an artificial life simulator designed to model the emergence of complex behaviors from simple rules. Unlike detailed biological simulations, VirtualLife focuses on computational generations/turns within a virtual environment, starting with simple cells and parameterized rules to observe emergent patterns and behaviors.

## Project Vision

VirtualLife aims to create a flexible framework capable of simulating scenarios ranging from simple predator-prey ecosystems to complex ecological systems featuring mutualism, territorial behaviors, and other emergent phenomena.

## Key Features

- Grid-based environment with customizable rules
- Modern Entity-Component-System (ECS) architecture
- Specialized systems for different simulation aspects (movement, energy, reproduction)
- Efficient spatial partitioning for large-scale simulations
- Type-safe configuration using Pydantic
- Modular, event-driven architecture with observer pattern
- Comprehensive test suite with property-based testing
- Progressive visualization options (CLI → matplotlib → web)
- **Comprehensive test suite with exhaustive coverage**

## Development Principles

VirtualLife follows these core principles:

- **Incremental Development**: Start simple, add complexity progressively
- **Domain-Driven Design**: Organize by simulation concepts rather than technical layers
- **System-Based Processing**: Process entities by component type for better performance
- **Type Safety**: Leverage Python's type system and protocols for documentation and validation
- **Exhaustive Testing**: Every component must have comprehensive test coverage
- **Detailed Documentation**: Each function, class, and module must be thoroughly documented

## AI Development Requirements

Since this project will be implemented by an AI agent, the following additional requirements apply:

- **Test-First Approach**: Tests must be written before or alongside implementation
- **Edge Case Coverage**: All edge cases must be explicitly identified, handled, and tested
- **Complete Type Annotations**: All functions, methods, and variables must have type annotations
- **Comprehensive Docstrings**: Documentation must explain not just what code does, but why and how
- **Fail-Fast Design**: Functions should validate inputs early and fail with clear error messages
- **Example-Driven Development**: Examples of usage should be included in docstrings

## Improved Architecture

VirtualLife is built with a modular, ECS-based architecture:

```
virtuallife/
├── ecs/                  # Entity-Component-System core
│   ├── entity.py         # Entity implementation
│   ├── component.py      # Component base and registry
│   ├── system.py         # System base and implementation
│   └── world.py          # World container for entities/systems
├── environment/          # Environment implementation
│   ├── grid.py           # Spatial grid and queries
│   ├── resources.py      # Resource management
│   └── boundary.py       # Boundary condition handlers
├── components/           # Component implementations
│   ├── energy.py         # Energy components
│   ├── movement.py       # Movement components 
│   └── reproduction.py   # Reproduction components
├── systems/              # System implementations
│   ├── movement.py       # Movement processing
│   ├── lifecycle.py      # Entity lifecycle management
│   └── resource.py       # Resource system
├── events/               # Event system
│   └── dispatcher.py     # Event dispatcher
├── config/               # Configuration
│   ├── models.py         # Pydantic models
│   └── loader.py         # Configuration loading
├── types/                # Type definitions
│   └── core.py           # Core type definitions
├── visualize/            # Visualization tools
│   ├── console.py        # Console visualization
│   ├── plotting.py       # Matplotlib visualization
│   └── web/              # Web visualization (Phase 2+)
├── simulation/           # Simulation runner
├── cli.py                # Command-line interface
└── api/                  # API layer (Phase 2+)
```

## Implementation Phases

### Phase 1: Core Refactoring (Weeks 1-2)
- Implement ECS architecture with systems
- Refactor Environment into specialized components
- Add event system
- Create domain-specific type definitions
- **Comprehensive unit tests for new architecture**

### Phase 2: Code Organization and Performance (Weeks 3-4)
- Complete modular package structure
- Implement spatial partitioning for entity lookups
- Optimize resource management
- Add system-based processing for entity updates
- **Performance tests for optimizations**

### Phase 3: API and Visualization Enhancements (Weeks 5-6)
- Implement REST API with FastAPI
- Create improved web visualization
- Add more entity behaviors
- Data collection and analysis enhancements
- **API documentation and tests**

### Phase 4: Advanced Features (Weeks 7-10)
- Species and genetics implementation
- Complex behaviors using component composition
- Enhanced web visualization
- Real-time updates with WebSockets
- **Property-based tests for genetic algorithms**

### Phase 5: Evolution and Analysis (Weeks 11-12)
- Evolutionary mechanisms
- Advanced data analysis
- Comprehensive visualization dashboards
- Performance optimization
- **End-to-end test scenarios**

## Quick Start

*Coming soon*

## Examples

### Running Basic Simulation with CLI Visualization

```bash
# Run predator-prey with console output
virtuallife run predator-prey --console

# Run with matplotlib visualization
virtuallife run predator-prey --plot
```

### Running with Web Interface (Phase 3+)

```bash
# Start the API server
virtuallife serve

# In another terminal or browser, connect to http://localhost:8000
```

## Development Status

This project is in active refactoring. See [ROADMAP.md](ROADMAP.md) for the detailed development plan.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.