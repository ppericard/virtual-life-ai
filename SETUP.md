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

For optional dependency groups (available in Phase 2+):

```bash
# Web interface dependencies
poetry install --with web

# Data analysis dependencies
poetry install --with data
```

4. **Activate the virtual environment**

```bash
poetry shell
```

5. **Configure pre-commit hooks**

```bash
pre-commit install
```

## Simplified Project Structure

The project has been streamlined for easier development while maintaining a clear path to advanced features:

```
virtual-life-ai/
├── tests/                  # Comprehensive test suite
│   ├── unit/              # Unit tests for all components
│   ├── integration/       # Integration tests for component interactions
│   ├── functional/        # Functional tests for features
│   └── conftest.py        # Shared test fixtures
├── virtuallife/           # Main package
│   ├── __init__.py
│   ├── simulation/        # Core simulation engine
│   │   ├── __init__.py
│   │   ├── environment.py # Environment implementation
│   │   ├── entity.py      # Entity implementation
│   │   ├── component.py   # Components for entities
│   │   └── runner.py      # Simulation runner
│   ├── models/            # Data models using Pydantic
│   │   ├── __init__.py
│   │   ├── config.py      # Configuration schemas
│   │   ├── entity.py      # Entity schemas
│   │   └── state.py       # Simulation state models
│   ├── visualize/         # Visualization tools
│   │   ├── __init__.py
│   │   ├── console.py     # Console visualization
│   │   ├── plotting.py    # Matplotlib visualization
│   │   └── web/           # Web visualization (Phase 2+)
│   ├── api/               # API layer (Phase 2+)
│   │   ├── __init__.py
│   │   └── routes.py      # API endpoints
│   ├── cli.py             # Command-line interface
│   └── config/            # Default configurations
├── docs/                  # Documentation
│   ├── user/              # User documentation
│   ├── developer/         # Developer documentation
│   └── api/               # API documentation
├── pyproject.toml         # Project metadata and dependencies
├── README.md              # Project overview
├── ROADMAP.md             # Development roadmap
└── TECHNICAL_SPECS.md     # Technical specifications
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

4. **Code Comments**
   - Use comments to explain "why" not just "what"
   - Comment complex or non-obvious logic
   - Explain design decisions and tradeoffs

5. **Configuration Documentation**
   - Document all configuration options
   - Provide examples of different configurations
   - Explain the effects of each configuration option

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

3. **Property-Based Testing**
   - Use property-based testing for algorithms with invariants
   - Test statistically correct behavior for randomized operations
   - Verify genetic algorithms with property tests

4. **Documentation Testing**
   - Examples in docstrings must be tested
   - README examples must be verified
   - Configuration examples must be tested

### Code Quality Standards

1. **Type Annotations**
   - Every function, method, and variable must have type annotations
   - Use generics where appropriate
   - Use Literal types for constrained values
   - Leverage TypedDict and Protocol for clear interfaces

2. **Error Handling**
   - Validate inputs at function boundaries
   - Provide clear error messages
   - Use appropriate exception types
   - Handle edge cases explicitly

3. **Code Style**
   - Follow Black/isort formatting
   - Use descriptive variable names
   - Keep functions focused on a single task
   - Use appropriate design patterns

## Phased Development Guidelines

### Phase 1: Core Simulation (Weeks 1-2)

Focus on:
- Basic environment and entity implementation
- Simple predator-prey ecosystem
- CLI interface and matplotlib visualization
- Core data structures and algorithms
- **Comprehensive testing of all components**
- **Thorough documentation of all functions and classes**

Development workflow:
1. **Document First**: Define interface with detailed docstrings
2. **Test Second**: Write comprehensive tests before implementation
3. **Implement Third**: Implement functionality to match docs and pass tests
4. **Refactor Fourth**: Improve implementation while maintaining tests

### Phase 2: API and Enhanced Visualization (Weeks 3-4)

Focus on:
- REST API with FastAPI
- Simple web visualization
- More sophisticated entity behaviors
- Data collection for analysis
- **API documentation with examples**
- **Tests for all API endpoints**

### Phase 3: Advanced Features (Weeks 5-8)

Focus on:
- Species concept and simple genetics
- More complex behaviors
- Enhanced web visualization
- WebSocket support for real-time updates
- **Property-based tests for genetics**
- **Technical design documentation**

### Phase 4: Evolution and Analysis (Weeks 9-12)

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
pytest tests/unit/simulation/test_environment.py

# Run tests with verbose output
pytest -v

# Run tests and output test duration
pytest --durations=10
```

### Documentation Testing

Verify docstring examples:

```bash
# Test docstrings
pytest --doctest-modules virtuallife

# Check specific module docstrings
pytest --doctest-modules virtuallife/simulation/environment.py
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
    >>> from virtuallife.simulation import environment
    >>> env = environment.Environment(50, 50)
    
Attributes:
    MODULE_CONSTANT: Description of any module-level constants
"""
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

## Development Principles for AI Implementation

1. **Document Before Code**: Write detailed documentation before implementation
2. **Test Before Implementation**: Write comprehensive tests before or alongside code
3. **Explicit Over Implicit**: Be explicit about types, errors, and behavior
4. **Edge Cases First**: Identify and handle edge cases explicitly
5. **Fail Fast**: Validate inputs early and provide clear error messages
6. **Example-Driven Development**: Include examples in documentation that act as tests 