# VirtualLife

VirtualLife is an artificial life simulator designed to model the emergence of complex behaviors from simple rules. Unlike detailed biological simulations, VirtualLife focuses on computational generations/turns within a virtual environment, starting with simple cells and parameterized rules to observe emergent patterns and behaviors.

## Project Vision

VirtualLife aims to create a flexible framework capable of simulating scenarios ranging from simple predator-prey ecosystems to complex ecological systems featuring mutualism, territorial behaviors, and other emergent phenomena.

## Key Features

- Grid-based environment with customizable rules
- Component-based entity system for flexible behavior composition
- Resource system with generation and consumption mechanics
- Data collection and analysis tools
- Progressive visualization options (CLI → matplotlib → web)
- **Comprehensive test suite with exhaustive coverage**

## Development Principles

VirtualLife follows these core principles:

- **Incremental Development**: Start simple, add complexity progressively
- **Domain-Driven Design**: Organize by simulation concepts rather than technical layers
- **Composition Over Inheritance**: Use a flat component system with minimal inheritance
- **Type Safety**: Leverage Python's type system for documentation and validation
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

## Simplified Architecture

VirtualLife is built with a modular, component-based architecture:

```
virtuallife/
├── simulation/             # Core simulation engine
│   ├── environment.py      # Environment implementation
│   ├── entity.py           # Entity implementation
│   ├── component.py        # Components for entities
│   └── runner.py           # Simulation runner
├── models/                 # Data models using Pydantic
│   ├── config.py           # Configuration schemas
│   ├── entity.py           # Entity schemas
│   └── state.py            # Simulation state models
├── visualize/              # Visualization tools (progressive complexity)
│   ├── console.py          # Console output (Phase 1)
│   ├── plotting.py         # Matplotlib visualization (Phase 1)
│   └── web/                # Web visualization (Phase 2+)
├── api/                    # API layer (Phase 2+)
├── cli.py                  # Command-line interface
└── config/                 # Default configurations
```

## Implementation Phases

### Phase 1: Core Simulation Engine (Weeks 1-2)
- Basic environment and entity system
- Simple predator-prey mechanics
- CLI interface and matplotlib visualization
- Core algorithms and data structures
- **Comprehensive unit tests for all components**
- **Detailed documentation with examples**

### Phase 2: API and Enhanced Visualization (Weeks 3-4)
- REST API with FastAPI
- Simple web visualization
- More entity behaviors
- Data collection and basic analysis
- **Integration tests for API endpoints**
- **API documentation with usage examples**

### Phase 3: Advanced Features (Weeks 5-8)
- Species and simple genetics
- More complex behaviors
- Enhanced web visualization
- Real-time updates with WebSockets
- **Property-based tests for genetic algorithms**
- **Technical design documentation**

### Phase 4: Evolution and Analysis (Weeks 9-12)
- Evolutionary mechanisms
- Advanced data analysis
- Comprehensive visualization dashboards
- Performance optimization
- **End-to-end test scenarios**
- **User and developer documentation**

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

### Running with Web Interface (Phase 2+)

```bash
# Start the API server
virtuallife serve

# In another terminal or browser, connect to http://localhost:8000
```

## Development Status

This project is in early development. See [ROADMAP.md](ROADMAP.md) for the detailed development plan.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.