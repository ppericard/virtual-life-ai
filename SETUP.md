# VirtualLife Project Setup

This document provides instructions for setting up the development environment for the VirtualLife project and outlines the project's dependencies and requirements.

## Development Environment Setup

### Prerequisites

- Python 3.10 or higher
- Git
- Poetry (dependency management)
- Node.js and npm (for frontend development, optional)

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

6. **Install frontend dependencies (optional)**

If you want to customize the web interface beyond the provided templates:

```bash
cd frontend
npm install
npm run build
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
│   │   ├── web/           # Tests for web components
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
│   │   ├── environment.py # Environment implementation
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
│   ├── web/               # Web interface components
│   │   ├── __init__.py
│   │   ├── static/        # Static assets (CSS, JS)
│   │   │   ├── css/       # Stylesheets
│   │   │   ├── js/        # JavaScript files
│   │   │   └── img/       # Images
│   │   ├── templates/     # HTML templates
│   │   ├── routes.py      # Web routes
│   │   ├── socket.py      # WebSocket handlers
│   │   └── app.py         # Flask application
│   ├── visualization/     # Visualization components
│   │   ├── __init__.py
│   │   ├── renderer.py    # Base renderer
│   │   └── web_renderer.py # Web-specific rendering
│   ├── utils/             # Utility functions and helpers
│   │   ├── __init__.py
│   │   ├── spatial.py
│   │   └── config.py      # Configuration utilities
│   └── cli.py             # Command-line interface
├── examples/              # Example simulations
│   ├── predator_prey.yaml # Predator-prey simulation (default)
│   └── advanced_ecosystem.yaml # More complex ecosystem
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
- **Flask**: Web framework
- **Flask-SocketIO**: Real-time communication
- **PyYAML**: Configuration file handling
- **Click**: Command-line interface
- **D3.js**: Data visualization (client-side)
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

## Running the Web Interface

Start the web interface:

```bash
python -m virtuallife.cli web --port 5000
```

This will start the Flask web server on port 5000. You can then access the web interface by navigating to `http://localhost:5000` in your web browser.

## Running the Predator-Prey Simulation

Run the predator-prey simulation with the web interface:

```bash
python -m virtuallife.cli predator-prey --width 50 --height 50 --plant-growth 0.1 --herbivore-count 20 --predator-count 5 --web
```

This will start the web server and open a browser window with the predator-prey simulation configured with the specified parameters.

## Running a Custom Simulation

Run a custom simulation from a configuration file:

```bash
python -m virtuallife.cli run --config examples/advanced_ecosystem.yaml --web
```

This will start the web server and open a browser window with the advanced ecosystem simulation.

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

1. Start with the core simulation framework and web interface
2. Implement predator-prey ecosystem as a proof of concept
3. Add resources and enhanced entity behaviors
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