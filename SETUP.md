# VirtualLife Project Setup (Simplified)

This document provides instructions for setting up the development environment for the VirtualLife project and outlines the project's dependencies and requirements. This project is designed to be implemented by an AI agent, which necessitates strict adherence to testing and documentation standards.

## Development Environment Setup

### Prerequisites

- Python 3.10 or higher
- Git
- Poetry (dependency management)

### Setup Steps

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/virtual-life-ai.git
cd virtual-life-ai
```

2. **Install Poetry**

If you don't have Poetry installed, follow the instructions on the [official Poetry website](https://python-poetry.org/docs/#installation).

3. **Install dependencies**

```bash
poetry install
```

This will create a virtual environment and install the core dependencies.

For optional dependency groups (available in Phase 3+):

```bash
# Web interface dependencies
poetry install --with web

# Data analysis dependencies
poetry install --with data

# Visualization dependencies
poetry install --with viz
```

4. **Activate the virtual environment**

```bash
poetry shell
```

5. **Configure pre-commit hooks**

```bash
pre-commit install
```

## Improved Project Structure

The project has been restructured for better organization, maintainability, and performance:

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
│   └── web/              # Web visualization (Phase 3+)
├── simulation/           # Simulation runner
├── cli.py                # Command-line interface
├── api/                  # API layer (Phase 3+)
│   ├── routes.py         # API endpoints
│   └── models.py         # API data models
└── tests/                # Comprehensive test suite
    ├── unit/             # Unit tests
    │   ├── ecs/          # ECS tests
    │   ├── environment/  # Environment tests
    │   ├── components/   # Component tests
    │   └── systems/      # System tests
    ├── integration/      # Integration tests
    ├── functional/       # Functional tests
    └── performance/      # Performance tests
```

## Development Standards for AI Implementation

### Documentation Standards

Documentation is **critical** for AI development and must be comprehensive:

1. **Module Documentation**
   - Every module must have a docstring explaining its purpose, contents, and usage
   - Include examples of how the module should be used

2. **Function/Method Documentation**
   - Every function and method must have a comprehensive docstring
   - Document all parameters with types and descriptions
   - Document return values with types and descriptions
   - Document exceptions that may be raised
   - Include examples of usage
   - Explain algorithm details for complex functions

3. **Class Documentation**
   - Document the purpose and behavior of each class
   - Explain the initialization parameters
   - Document class attributes
   - Explain the relationships with other classes
   - Document any protocols implemented

4. **Protocol Documentation**
   - Document the purpose of each protocol
   - Explain the methods that must be implemented
   - Provide examples of implementations

5. **Code Comments**
   - Use comments to explain "why" not just "what"
   - Comment complex or non-obvious logic
   - Explain design decisions and tradeoffs

6. **Type Documentation**
   - Document custom type definitions
   - Explain constraints on type parameters
   - Provide usage examples for complex types

### Testing Standards

Testing is **essential** for AI development and must be thorough:

1. **Unit Testing**
   - Every function must have corresponding unit tests
   - Test both normal operation and edge cases
   - Test error conditions
   - Verify input validation
   - Test boundary conditions
   - Aim for 90% line coverage minimum

2. **Integration Testing**
   - Test component interactions
   - Verify system state consistency
   - Test event propagation
   - Test configuration application
   - Test ECS systems with multiple entities

3. **Property-Based Testing**
   - Use property-based testing for algorithms with invariants
   - Test statistically correct behavior for randomized operations
   - Verify genetic algorithms with property tests
   - Test system invariants with randomized inputs

4. **Performance Testing**
   - Benchmark critical operations
   - Test scaling with large numbers of entities
   - Verify spatial partitioning efficiency
   - Test resource management performance

5. **Documentation Testing**
   - Examples in docstrings must be tested
   - README examples must be verified
   - Configuration examples must be tested

### Code Quality Standards

1. **Type Annotations**
   - Every function, method, and variable must have type annotations
   - Use generics where appropriate
   - Use Literal types for constrained values
   - Use Protocol for interface definitions
   - Use TypeVar for generic types
   - Use NewType for domain-specific types

2. **Error Handling**
   - Validate inputs at function boundaries
   - Provide clear error messages
   - Use appropriate exception types
   - Handle edge cases explicitly
   - Log errors with context information

3. **Code Style**
   - Follow Black/isort formatting
   - Use descriptive variable names
   - Keep functions focused on a single task
   - Use appropriate design patterns
   - Keep files under 300 lines

## Phased Development Guidelines

### Phase 1: Core Architecture Refactoring (Weeks 1-2)

Focus on:
- ECS architecture implementation
- Environment refactoring
- Event system implementation
- Type system development
- **Comprehensive testing of all components**
- **Thorough documentation of architectural decisions**

Development workflow:
1. **Document First**: Define interface with detailed docstrings
2. **Test Second**: Write comprehensive tests before implementation
3. **Implement Third**: Implement functionality to match docs and pass tests
4. **Refactor Fourth**: Improve implementation while maintaining tests

### Phase 2: Code Organization and Performance (Weeks 3-4)

Focus on:
- Component reorganization
- System implementations
- Performance optimizations
- Configuration enhancements
- **Integration tests for component interactions**
- **Performance benchmarks for critical operations**

### Phase 3: API and Visualization Enhancements (Weeks 5-6)

Focus on:
- REST API with FastAPI
- Enhanced visualization
- Entity behavior improvements
- Data collection enhancements
- **API documentation with examples**
- **Tests for all API endpoints**

### Phase 4: Advanced Features (Weeks 7-10)

Focus on:
- Species implementation
- Genetics system
- Enhanced web interface
- Advanced behaviors
- **Property-based tests for genetics**
- **Technical design documentation**

### Phase 5: Evolution and Analysis (Weeks 11-12)

Focus on:
- Evolutionary mechanisms
- Advanced data analysis
- Comprehensive dashboards
- Performance optimization
- **End-to-end test scenarios**
- **User and developer documentation**

## Running Tests

Testing is a critical part of the development process:

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run with coverage report
pytest --cov=virtuallife

# Run with detailed coverage report
pytest --cov=virtuallife --cov-report=html

# Run tests on a specific component
pytest tests/unit/ecs/test_entity.py

# Run tests with verbose output
pytest -v

# Run tests and output test duration
pytest --durations=10

# Run performance tests
pytest tests/performance/
```

### Documentation Testing

Verify docstring examples:

```bash
# Test docstrings
pytest --doctest-modules virtuallife

# Check specific module docstrings
pytest --doctest-modules virtuallife/ecs/entity.py
```

## Documentation Guidelines

### Docstring Format (Google Style)

```python
def function_name(param1: type1, param2: type2) -> return_type:
    """Short description of the function.
    
    Detailed description of the function's purpose and behavior.
    Include algorithm details for complex functions.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: Description of when this exception is raised
        
    Examples:
        >>> function_name(1, 'test')
        Expected result
        
    Notes:
        Additional details or implementation notes
    """
    # Implementation
```

### Module Documentation

```python
"""Module name and short description.

Detailed description of the module's purpose and contents.
Describe how the module fits into the overall architecture.

Examples:
    >>> from virtuallife.ecs import entity
    >>> from virtuallife.ecs.world import World
    >>> world = World()
    >>> entity = entity.Entity(position=(10, 10))
    >>> world.add_entity(entity)
    
Attributes:
    MODULE_CONSTANT: Description of any module-level constants
"""
```

### Protocol Documentation

```python
class Movable(Protocol):
    """Protocol for objects that can move.
    
    This protocol defines the interface for any object that can move
    within the environment. It requires position information and a
    move method.
    
    Examples:
        >>> class MovableEntity:
        ...     def __init__(self, position: tuple[int, int]):
        ...         self.position = position
        ...     def move(self, dx: int, dy: int) -> None:
        ...         self.position = (self.position[0] + dx, self.position[1] + dy)
        >>> entity = MovableEntity((0, 0))
        >>> entity.move(1, 2)
        >>> entity.position
        (1, 2)
    """
    position: tuple[int, int]
    
    def move(self, dx: int, dy: int) -> None:
        """Move the object by the specified delta.
        
        Args:
            dx: Change in x position
            dy: Change in y position
        """
        ...
```

### Test Documentation

```python
def test_function_name_scenario():
    """Test that function_name behaves correctly in specific scenario.
    
    Detailed description of what is being tested and why.
    """
    # Test implementation
```

## Code Style

- **Formatting**: Black with line length 88
- **Import Sorting**: isort with Black compatibility
- **Type Annotations**: Required for public APIs
- **Docstrings**: Google-style for public functions
- **Naming Conventions**:
  - Classes: `CamelCase`
  - Functions and variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
  - Type variables: `T`, `U`, etc.
  - Protocols: `HasX`, `CanY`, etc.

## Development Principles for AI Implementation

1. **Document Before Code**: Write detailed documentation before implementation
2. **Test Before Implementation**: Write comprehensive tests before or alongside code
3. **Explicit Over Implicit**: Be explicit about types, errors, and behavior
4. **Edge Cases First**: Identify and handle edge cases explicitly
5. **Fail Fast**: Validate inputs early and provide clear error messages
6. **Example-Driven Development**: Include examples in documentation that act as tests
7. **Modular Design**: Keep components small and focused on a single responsibility
8. **Type-Driven Development**: Use types to guide implementation 