# VirtualLife Project Setup

This document provides instructions for setting up the development environment for the VirtualLife project and outlines the project's dependencies and requirements.

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

This will create a virtual environment and install all the required dependencies.

4. **Activate the virtual environment**

```bash
poetry shell
```

5. **Configure pre-commit hooks**

```bash
pre-commit install
```

## Project Structure

The project structure follows a strict modular design with small, focused files:

```
virtual-life-ai/
├── docs/                  # Documentation
├── tests/                 # Test suite
│   ├── unit/              # Unit tests (70% of tests)
│   │   ├── core/          # Tests for core modules
│   │   ├── components/    # Tests for components
│   │   ├── behaviors/     # Tests for behaviors
│   │   └── utils/         # Tests for utilities
│   ├── integration/       # Integration tests (20% of tests)
│   ├── functional/        # Functional tests (10% of tests)
│   └── conftest.py        # Shared test fixtures
├── virtuallife/           # Main package
│   ├── __init__.py
│   ├── core/              # Core simulation components
│   │   ├── __init__.py
│   │   ├── interfaces/    # Protocol definitions
│   │   │   ├── __init__.py
│   │   │   ├── entity.py
│   │   │   └── environment.py
│   │   ├── environment/   # Environment implementation
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── boundary.py
│   │   ├── entity.py      # Entity implementation
│   │   ├── species.py     # Species implementation
│   │   └── simulation.py  # Simulation engine
│   ├── components/        # Entity component implementations
│   │   ├── __init__.py
│   │   ├── registry.py
│   │   ├── base.py
│   │   ├── energy.py
│   │   └── movement.py
│   ├── behaviors/         # Entity behavior implementations
│   │   ├── __init__.py
│   │   ├── random_movement.py
│   │   └── reproduction.py
│   ├── visualization/     # Visualization components
│   │   ├── __init__.py
│   │   ├── terminal.py    # Terminal-based visualization
│   │   └── gui.py         # GUI visualization (Pygame)
│   ├── utils/             # Utility functions and helpers
│   │   ├── __init__.py
│   │   ├── spatial.py
│   │   └── config.py      # Configuration utilities
│   └── cli.py             # Command-line interface
├── examples/              # Example simulations
│   ├── conway.yaml        # Conway's Game of Life configuration
│   └── predator_prey.yaml # Predator-prey simulation
├── .github/               # GitHub actions and workflows
├── .gitignore
├── pyproject.toml         # Project metadata and dependencies
├── README.md
├── ROADMAP.md
└── TECHNICAL_SPECS.md
```

## Code Organization Guidelines

### File Size Limits

- **Maximum file size**: 200-300 lines of code (excluding comments and blank lines)
- **Maximum function/method size**: 50 lines
- **Maximum class size**: 200 lines

When a file approaches these limits, split it into smaller, focused modules.

### Module Organization

1. Each module should have a **single responsibility**
2. Create **explicit interfaces** between components using Protocol classes
3. Minimize **dependencies between modules**
4. Maintain a **strict dependency hierarchy** to prevent circular imports

## Dependencies

The project uses the following dependencies:

### Production Dependencies

- **NumPy**: Efficient numerical operations
- **PyYAML**: Configuration file handling
- **Click**: Command-line interface
- **Pygame**: Interactive visualization (optional)
- **tqdm**: Progress bars for long-running simulations

### Development Dependencies

- **pytest**: Testing framework
- **pytest-cov**: Test coverage
- **pytest-mock**: Mocking support
- **hypothesis**: Property-based testing
- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Static type checking
- **pre-commit**: Git hooks

## Test-Driven Development Workflow

VirtualLife follows a strict test-first approach:

### 1. Test-First Development Cycle

For each new feature or bug fix:

1. **Write test first**: Create a failing test that defines the expected behavior
2. **Implement minimum code**: Write just enough code to make the test pass
3. **Refactor**: Clean up the code while keeping tests passing
4. **Commit**: Commit changes with clear, descriptive messages

### 2. Running Tests

Run the full test suite:

```bash
pytest
```

Run specific test categories:

```bash
# Run only unit tests
pytest tests/unit/

# Run tests for a specific module
pytest tests/unit/core/test_environment.py

# Run with coverage report
pytest --cov=virtuallife --cov-report=term-missing

# Run with verbose output
pytest -v
```

### 3. Test Coverage Requirements

- **Unit test coverage**: Minimum 90% line coverage
- **Branch coverage**: Minimum 80% for conditional logic
- **Integration test coverage**: All module interactions must be tested
- **Functional test coverage**: All user-facing features must have tests

Check test coverage with:

```bash
pytest --cov=virtuallife --cov-report=html
```

This generates a report in `htmlcov/index.html`.

### 4. Property-Based Testing

For complex behaviors, use property-based testing with Hypothesis:

```python
from hypothesis import given, strategies as st

@given(
    width=st.integers(min_value=1, max_value=100),
    height=st.integers(min_value=1, max_value=100)
)
def test_environment_creation(width, height):
    """Test that environments of various sizes can be created."""
    env = Environment(width, height)
    assert env.width == width
    assert env.height == height
    assert len(env.entities) == 0
```

## Running the Application

Run Conway's Game of Life:

```bash
python -m virtuallife.cli conway --width 50 --height 50 --pattern glider
```

Run a custom simulation:

```bash
python -m virtuallife.cli run --config examples/predator_prey.yaml
```

## Code Style

This project follows these style guidelines:

- **Code Formatting**: Black with line length 88
- **Import Sorting**: isort with Black compatibility
- **Type Annotations**: All functions and methods must include type annotations
- **Docstrings**: Google-style docstrings for all public APIs
- **Naming Conventions**:
  - Classes: `CamelCase`
  - Functions and variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
  - Private methods/attributes: `_leading_underscore`
  - Interface protocols: `EntityInterface`, `EnvironmentInterface`

## Implementation Plan

Follow the phased approach outlined in the [ROADMAP.md](ROADMAP.md):

1. Start with the core simulation framework (environment, entities, simulation engine)
2. Implement Conway's Game of Life as a proof of concept
3. Add resources and basic entity behaviors
4. Implement species concept and simple genetics
5. Add advanced ecology and analysis tools

### Implementation Principles

1. **Test first**: Always write tests before implementation
2. **Interfaces first**: Define interfaces before implementation
3. **Keep it simple**: Implement the minimum required functionality
4. **Small modules**: Split code into small, focused modules
5. **Complete documentation**: Document all public APIs
6. **Continuous refactoring**: Refactor code as needed while keeping tests passing

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for information on how to contribute to the project. 