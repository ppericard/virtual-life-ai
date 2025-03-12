# VirtualLife Technical Specifications

This document outlines the technical architecture, design patterns, and implementation details for the VirtualLife project.

## Architecture Overview

VirtualLife follows a modular, component-based architecture with clear separation of concerns. The system is composed of several core modules:

```
virtuallife/
├── core/                  # Core simulation components
│   ├── interfaces/        # Protocol definitions
│   │   ├── entity.py      # Entity interface
│   │   └── environment.py # Environment interface
│   ├── environment.py     # Environment implementation
│   ├── entity.py          # Base entity classes
│   ├── species.py         # Species definitions
│   └── simulation.py      # Simulation engine
├── behaviors/             # Entity behavior implementations
├── components/            # Entity component implementations
├── web/                   # Web interface components
│   ├── static/            # Static assets (CSS, JS)
│   │   ├── css/           # Stylesheets
│   │   ├── js/            # JavaScript files
│   │   └── img/           # Images
│   ├── templates/         # HTML templates
│   ├── routes.py          # Web routes
│   ├── socket.py          # WebSocket handlers
│   └── app.py             # Flask application
├── visualization/         # Visualization components
│   ├── renderer.py        # Base renderer
│   └── web_renderer.py    # Web-specific rendering
├── utils/                 # Utility functions and helpers
└── cli.py                 # Command-line interface
```

## Development Approach

### Test-Driven Development

**All development must follow a strict test-first approach:**

1. Write a failing test for the feature/functionality
2. Implement the minimum code needed to pass the test
3. Refactor while keeping tests passing
4. Repeat for the next feature/functionality

### File Size Limits

To ensure maintainability and ease of understanding:

1. **Maximum file size: 200-300 lines** (excluding comments and blank lines)
2. **Maximum function/method size: 50 lines**
3. When a file approaches the size limit, refactor and split functionalities

### Module Organization

1. Each module should have a **single responsibility**
2. **Explicit interfaces** between modules should be clearly defined
3. **Dependencies between modules** should be minimized and explicit

## Comprehensive Testing Strategy

### 1. Test Structure

The testing suite follows a pyramid structure:

```
tests/
├── unit/                   # Unit tests (70% of tests)
│   ├── core/               # Tests for core modules
│   │   ├── test_entity.py
│   │   ├── test_environment.py
│   │   ├── test_simulation.py
│   │   └── test_species.py
│   ├── components/         # Tests for components
│   ├── behaviors/          # Tests for behaviors
│   ├── web/                # Tests for web components
│   │   ├── test_routes.py
│   │   └── test_socket.py
│   └── utils/              # Tests for utilities
├── integration/            # Integration tests (20% of tests)
│   ├── test_entity_environment.py
│   ├── test_species_entity.py
│   └── test_web_simulation.py
├── functional/             # Functional tests (10% of tests)
│   ├── test_predator_prey.py
│   ├── test_advanced_ecology.py
│   └── test_web_interface.py
└── conftest.py             # Shared test fixtures
```

### 2. Test Coverage Requirements

- **Unit test coverage**: Minimum 90% line coverage for each module
- **Branch coverage**: Minimum 80% for conditional logic
- **Integration test coverage**: All module interactions must be tested
- **Functional test coverage**: All user-facing features must have tests

## Web Interface Architecture

The web interface is a core component of VirtualLife, providing real-time visualization and control of simulations.

### 1. Server-Side Components

#### Flask Application Structure

```python
# web/app.py
from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config.from_object('config.Config')
socketio = SocketIO(app)

# Import routes and socket handlers
from virtuallife.web import routes, socket

def create_app():
    return app

def run_app(host='0.0.0.0', port=5000, debug=False):
    socketio.run(app, host=host, port=port, debug=debug)
```

#### Route Handlers

```python
# web/routes.py
from flask import render_template, jsonify, request
from virtuallife.web.app import app
from virtuallife.core.simulation import SimulationManager

simulation_manager = SimulationManager()

@app.route('/')
def index():
    """Render the main simulation page."""
    return render_template('index.html')

@app.route('/api/simulations', methods=['GET'])
def list_simulations():
    """List all active simulations."""
    return jsonify({
        'simulations': simulation_manager.get_all_simulations()
    })

@app.route('/api/simulations', methods=['POST'])
def create_simulation():
    """Create a new simulation."""
    config = request.json
    simulation_id = simulation_manager.create_simulation(config)
    return jsonify({
        'simulation_id': simulation_id
    })

@app.route('/api/simulations/<simulation_id>', methods=['GET'])
def get_simulation(simulation_id):
    """Get details of a specific simulation."""
    simulation = simulation_manager.get_simulation(simulation_id)
    return jsonify(simulation.to_dict())
```

#### WebSocket Handlers

```python
# web/socket.py
from flask_socketio import emit
from virtuallife.web.app import socketio
from virtuallife.core.simulation import SimulationManager

simulation_manager = SimulationManager()

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    emit('connection_response', {'status': 'connected'})

@socketio.on('simulation_control')
def handle_simulation_control(data):
    """Handle simulation control commands."""
    simulation_id = data.get('simulation_id')
    command = data.get('command')
    params = data.get('params', {})
    
    simulation = simulation_manager.get_simulation(simulation_id)
    result = simulation.execute_command(command, **params)
    
    emit('simulation_control_response', {
        'simulation_id': simulation_id,
        'command': command,
        'result': result
    })

@socketio.on('request_state')
def handle_request_state(data):
    """Send current simulation state to client."""
    simulation_id = data.get('simulation_id')
    simulation = simulation_manager.get_simulation(simulation_id)
    state = simulation.get_current_state()
    
    emit('simulation_state_update', {
        'simulation_id': simulation_id,
        'state': state
    })
```

### 2. Client-Side Components

#### HTML Structure

```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VirtualLife Simulator</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
</head>
<body>
    <div class="container">
        <header>
            <h1>VirtualLife Simulator</h1>
        </header>
        
        <div class="simulation-controls">
            <button id="start-btn">Start</button>
            <button id="pause-btn">Pause</button>
            <button id="step-btn">Step</button>
            <button id="reset-btn">Reset</button>
            <div class="speed-control">
                <label for="speed-slider">Speed:</label>
                <input type="range" id="speed-slider" min="1" max="100" value="50">
            </div>
        </div>
        
        <div class="simulation-container">
            <canvas id="simulation-canvas"></canvas>
        </div>
        
        <div class="metrics-panel">
            <h2>Simulation Metrics</h2>
            <div id="metrics-container"></div>
        </div>
        
        <div class="configuration-panel">
            <h2>Configuration</h2>
            <form id="config-form">
                <!-- Configuration options will be dynamically generated -->
            </form>
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
```

#### JavaScript Client

```javascript
// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Connect to WebSocket server
    const socket = io();
    
    // Canvas setup
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    let simulationId = null;
    let simulationState = null;
    
    // Resize canvas to fit container
    function resizeCanvas() {
        const container = document.querySelector('.simulation-container');
        canvas.width = container.clientWidth;
        canvas.height = container.clientHeight;
        renderSimulation();
    }
    
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();
    
    // Socket event handlers
    socket.on('connect', function() {
        console.log('Connected to server');
    });
    
    socket.on('simulation_state_update', function(data) {
        if (data.simulation_id === simulationId) {
            simulationState = data.state;
            renderSimulation();
            updateMetrics(data.state.metrics);
        }
    });
    
    socket.on('simulation_control_response', function(data) {
        console.log('Control response:', data);
    });
    
    // UI event handlers
    document.getElementById('start-btn').addEventListener('click', function() {
        if (simulationId) {
            socket.emit('simulation_control', {
                simulation_id: simulationId,
                command: 'start'
            });
        } else {
            createNewSimulation();
        }
    });
    
    document.getElementById('pause-btn').addEventListener('click', function() {
        if (simulationId) {
            socket.emit('simulation_control', {
                simulation_id: simulationId,
                command: 'pause'
            });
        }
    });
    
    document.getElementById('step-btn').addEventListener('click', function() {
        if (simulationId) {
            socket.emit('simulation_control', {
                simulation_id: simulationId,
                command: 'step'
            });
        }
    });
    
    document.getElementById('reset-btn').addEventListener('click', function() {
        if (simulationId) {
            socket.emit('simulation_control', {
                simulation_id: simulationId,
                command: 'reset'
            });
        }
    });
    
    // Rendering functions
    function renderSimulation() {
        if (!simulationState) return;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Calculate cell size
        const cellWidth = canvas.width / simulationState.width;
        const cellHeight = canvas.height / simulationState.height;
        
        // Draw entities
        simulationState.entities.forEach(entity => {
            const x = entity.position[0] * cellWidth;
            const y = entity.position[1] * cellHeight;
            
            // Color based on entity type
            let color;
            switch(entity.type) {
                case 'Plant':
                    color = '#3CB371'; // Medium Sea Green
                    break;
                case 'Herbivore':
                    color = '#4682B4'; // Steel Blue
                    break;
                case 'Predator':
                    color = '#B22222'; // Firebrick
                    break;
                default:
                    color = '#3498db'; // Default blue
            }
            
            ctx.fillStyle = color;
            ctx.fillRect(x, y, cellWidth, cellHeight);
        });
    }
    
    function updateMetrics(metrics) {
        if (!metrics) return;
        
        const container = document.getElementById('metrics-container');
        container.innerHTML = '';
        
        // Create metrics display
        for (const [key, value] of Object.entries(metrics)) {
            const metricElement = document.createElement('div');
            metricElement.className = 'metric';
            metricElement.innerHTML = `<span class="metric-name">${key}:</span> <span class="metric-value">${value}</span>`;
            container.appendChild(metricElement);
        }
    }
    
    // Simulation creation
    function createNewSimulation() {
        // Get configuration from form
        const config = getConfigFromForm();
        
        // Create simulation via API
        fetch('/api/simulations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        })
        .then(response => response.json())
        .then(data => {
            simulationId = data.simulation_id;
            
            // Request initial state
            socket.emit('request_state', {
                simulation_id: simulationId
            });
        });
    }
    
    function getConfigFromForm() {
        // Default configuration for predator-prey simulation
        return {
            type: 'predator_prey',
            width: 50,
            height: 50,
            plant_growth_rate: 0.1,
            initial_plants: 100,
            initial_herbivores: 20,
            initial_predators: 5
        };
    }
});
```

## Core Components

### 1. Environment

The `Environment` class represents the world where entities exist and interact.

```python
class Environment:
    """A 2D grid-based environment for the simulation."""
    
    def __init__(self, width, height, boundary_condition="wrapped"):
        """Initialize a new environment.
        
        Args:
            width (int): Width of the environment grid
            height (int): Height of the environment grid
            boundary_condition (str): How boundaries are handled ("wrapped", "bounded", or "infinite")
        """
        self.width = width
        self.height = height
        self.boundary_condition = boundary_condition
        self.entities = {}  # entity_id -> Entity
        self.entity_positions = {}  # (x, y) -> set of entity_ids
        self.resources = {}  # resource_type -> 2D numpy array
        
    def add_entity(self, entity):
        """Add an entity to the environment.
        
        Args:
            entity (Entity): The entity to add
            
        Returns:
            UUID: The entity's ID
        """
        # Implementation details
        
    def remove_entity(self, entity_id):
        """Remove an entity from the environment.
        
        Args:
            entity_id (UUID): The ID of the entity to remove
        """
        # Implementation details
        
    def get_entities_at(self, position):
        """Get all entities at a specific position.
        
        Args:
            position (tuple): The (x, y) position to check
            
        Returns:
            list: List of entities at the position
        """
        # Implementation details
        
    def get_neighborhood(self, position, radius=1):
        """Get a view of the environment around a position.
        
        Args:
            position (tuple): The center (x, y) position
            radius (int): The radius of the neighborhood
            
        Returns:
            dict: Dictionary of positions and their contents
        """
        # Implementation details
        
    def normalize_position(self, position):
        """Normalize a position based on boundary conditions.
        
        Args:
            position (tuple): The (x, y) position to normalize
            
        Returns:
            tuple: The normalized (x, y) position
        """
        # Handle wrapped, bounded, or infinite boundaries
```

### 2. Entity

The `Entity` class represents objects that exist in the environment.

```python
class Entity:
    """Base class for all entities in the simulation."""
    
    def __init__(self, entity_id, position):
        """Initialize a new entity.
        
        Args:
            entity_id (UUID): Unique identifier for the entity
            position (tuple): Initial (x, y) position
        """
        self.id = entity_id
        self.position = position
        self.components = {}
        
    def add_component(self, component_name, component):
        """Add a component to the entity.
        
        Args:
            component_name (str): Name of the component
            component: Component instance
        """
        self.components[component_name] = component
        
    def has_component(self, component_name):
        """Check if the entity has a specific component.
        
        Args:
            component_name (str): Name of the component
            
        Returns:
            bool: True if the entity has the component
        """
        return component_name in self.components
        
    def get_component(self, component_name):
        """Get a component by name.
        
        Args:
            component_name (str): Name of the component
            
        Returns:
            Component instance or None
        """
        return self.components.get(component_name)
        
    def update(self, environment):
        """Update the entity state.
        
        Args:
            environment (Environment): Environment where the entity exists
        """
        for component in self.components.values():
            if hasattr(component, 'update'):
                component.update(self, environment)
```

### 3. Simulation

The `Simulation` class controls time progression and entity updates.

```python
class Simulation:
    """Controls the simulation execution."""
    
    def __init__(self, environment, config=None):
        """Initialize a new simulation.
        
        Args:
            environment (Environment): The simulation environment
            config (dict): Configuration parameters
        """
        self.environment = environment
        self.config = config or {}
        self.current_step = 0
        self.observers = []
        self.running = False
        
    def add_observer(self, observer):
        """Add an observer to the simulation.
        
        Args:
            observer (Observer): The observer to add
        """
        self.observers.append(observer)
        
    def notify_observers(self, event_type, **kwargs):
        """Notify all observers of an event.
        
        Args:
            event_type (str): Type of event
            **kwargs: Event data
        """
        for observer in self.observers:
            if hasattr(observer, f"on_{event_type}"):
                getattr(observer, f"on_{event_type}")(self, **kwargs)
        
    def step(self):
        """Execute a single simulation step."""
        self.current_step += 1
        self.notify_observers("step_start")
        
        # Update all entities
        entities = list(self.environment.entities.values())
        for entity in entities:
            entity.update(self.environment)
            
        self.notify_observers("step_end")
        
    def start(self):
        """Start the simulation."""
        self.running = True
        
    def pause(self):
        """Pause the simulation."""
        self.running = False
        
    def reset(self):
        """Reset the simulation to its initial state."""
        # Implementation details
        
    def get_current_state(self):
        """Get the current state of the simulation.
        
        Returns:
            dict: Current simulation state
        """
        return {
            'step': self.current_step,
            'width': self.environment.width,
            'height': self.environment.height,
            'entities': [
                {
                    'id': str(entity.id),
                    'position': entity.position,
                    'type': entity.__class__.__name__
                }
                for entity in self.environment.entities.values()
            ],
            'metrics': self.collect_metrics()
        }
        
    def collect_metrics(self):
        """Collect metrics about the current simulation state.
        
        Returns:
            dict: Metrics data
        """
        return {
            'entity_count': len(self.environment.entities),
            # Other metrics
        }
```

### 4. SimulationManager

The `SimulationManager` class manages multiple simulation instances.

```python
class SimulationManager:
    """Manages multiple simulation instances."""
    
    def __init__(self):
        """Initialize the simulation manager."""
        self.simulations = {}
        
    def create_simulation(self, config):
        """Create a new simulation.
        
        Args:
            config (dict): Simulation configuration
            
        Returns:
            str: Simulation ID
        """
        # Create environment
        environment = Environment(
            config.get('width', 50),
            config.get('height', 50),
            config.get('boundary_condition', 'wrapped')
        )
        
        # Create simulation
        simulation = Simulation(environment, config)
        
        # Generate ID
        simulation_id = str(uuid.uuid4())
        self.simulations[simulation_id] = simulation
        
        # Initialize simulation based on type
        if config.get('type') == 'predator_prey':
            self._initialize_predator_prey(simulation, config)
        
        return simulation_id
        
    def get_simulation(self, simulation_id):
        """Get a simulation by ID.
        
        Args:
            simulation_id (str): Simulation ID
            
        Returns:
            Simulation: Simulation instance
        """
        return self.simulations.get(simulation_id)
        
    def get_all_simulations(self):
        """Get all simulations.
        
        Returns:
            dict: Dictionary of simulation IDs to basic info
        """
        return {
            sim_id: {
                'id': sim_id,
                'step': sim.current_step,
                'running': sim.running,
                'type': sim.config.get('type', 'custom')
            }
            for sim_id, sim in self.simulations.items()
        }
        
    def _initialize_predator_prey(self, simulation, config):
        """Initialize a predator-prey simulation.
        
        Args:
            simulation (Simulation): Simulation to initialize
            config (dict): Configuration parameters
        """
        # Get configuration parameters with defaults
        plant_growth_rate = config.get('plant_growth_rate', 0.1)
        initial_plants = config.get('initial_plants', 100)
        initial_herbivores = config.get('initial_herbivores', 20)
        initial_predators = config.get('initial_predators', 5)
        
        width = simulation.environment.width
        height = simulation.environment.height
        
        # Add plants (static resource entities)
        for _ in range(initial_plants):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            
            entity_id = uuid.uuid4()
            plant = Entity(entity_id, (x, y))
            plant.add_component('plant', PlantComponent(growth_rate=plant_growth_rate))
            simulation.environment.add_entity(plant)
        
        # Add herbivores
        for _ in range(initial_herbivores):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            
            entity_id = uuid.uuid4()
            herbivore = Entity(entity_id, (x, y))
            herbivore.add_component('energy', EnergyComponent(initial_energy=100, decay_rate=0.5))
            herbivore.add_component('movement', MovementComponent(speed=1))
            herbivore.add_component('herbivore', HerbivoreComponent())
            herbivore.add_component('reproduction', ReproductionComponent(
                threshold=120, offspring_energy=50, chance=0.05))
            simulation.environment.add_entity(herbivore)
        
        # Add predators
        for _ in range(initial_predators):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            
            entity_id = uuid.uuid4()
            predator = Entity(entity_id, (x, y))
            predator.add_component('energy', EnergyComponent(initial_energy=150, decay_rate=0.7))
            predator.add_component('movement', MovementComponent(speed=1.5))
            predator.add_component('predator', PredatorComponent())
            predator.add_component('reproduction', ReproductionComponent(
                threshold=200, offspring_energy=80, chance=0.03))
            simulation.environment.add_entity(predator)
```

## Predator-Prey Implementation

The predator-prey ecosystem will be implemented with components for different entity types:

```python
class PlantComponent:
    """Component for plants that can grow and be consumed."""
    
    def __init__(self, growth_rate=0.1, max_energy=100):
        """Initialize a plant component.
        
        Args:
            growth_rate (float): Rate at which the plant grows energy
            max_energy (float): Maximum energy the plant can store
        """
        self.growth_rate = growth_rate
        self.max_energy = max_energy
        self.energy = max_energy / 2  # Start at half capacity
        
    def update(self, entity, environment):
        """Update the plant's energy.
        
        Args:
            entity (Entity): The entity this component belongs to
            environment (Environment): The environment
        """
        # Plants grow over time up to their maximum energy
        self.energy = min(self.energy + self.growth_rate, self.max_energy)


class EnergyComponent:
    """Component representing an entity's energy level."""
    
    def __init__(self, initial_energy=100, decay_rate=0.1):
        """Initialize an energy component.
        
        Args:
            initial_energy (float): Starting energy level
            decay_rate (float): Rate at which energy decays per step
        """
        self.energy = initial_energy
        self.decay_rate = decay_rate
        
    def update(self, entity, environment):
        """Update the entity's energy.
        
        Args:
            entity (Entity): The entity this component belongs to
            environment (Environment): The environment
        """
        # Energy decreases over time
        self.energy -= self.decay_rate
        
        # If energy is depleted, the entity dies
        if self.energy <= 0:
            environment.remove_entity(entity.id)


class MovementComponent:
    """Component allowing an entity to move."""
    
    def __init__(self, speed=1.0):
        """Initialize a movement component.
        
        Args:
            speed (float): Movement speed
        """
        self.speed = speed
        
    def update(self, entity, environment):
        """Move the entity.
        
        Args:
            entity (Entity): The entity this component belongs to
            environment (Environment): The environment
        """
        # Only move if the entity has energy
        if entity.has_component('energy'):
            energy = entity.get_component('energy')
            if energy.energy <= 0:
                return
                
            # Movement costs energy
            energy.energy -= 0.1 * self.speed
            
            # Move in a random direction
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            
            # Calculate new position
            x, y = entity.position
            new_x = x + dx
            new_y = y + dy
            
            # Update position with boundary normalization
            entity.position = environment.normalize_position((new_x, new_y))


class HerbivoreComponent:
    """Component for herbivores that eat plants."""
    
    def update(self, entity, environment):
        """Look for and consume plants.
        
        Args:
            entity (Entity): The entity this component belongs to
            environment (Environment): The environment
        """
        if not entity.has_component('energy'):
            return
            
        # Check current position for plants
        entities_here = environment.get_entities_at(entity.position)
        for other_entity in entities_here:
            if other_entity.id != entity.id and other_entity.has_component('plant'):
                plant = other_entity.get_component('plant')
                
                # Consume some of the plant's energy
                consumed = min(plant.energy, 10)
                plant.energy -= consumed
                
                # Convert to herbivore energy
                entity.get_component('energy').energy += consumed * 0.8
                
                # If plant is depleted, remove it
                if plant.energy <= 0:
                    environment.remove_entity(other_entity.id)
                    
                # Stop after eating one plant
                break


class PredatorComponent:
    """Component for predators that hunt herbivores."""
    
    def update(self, entity, environment):
        """Look for and hunt herbivores.
        
        Args:
            entity (Entity): The entity this component belongs to
            environment (Environment): The environment
        """
        if not entity.has_component('energy'):
            return
            
        # Check current position for herbivores
        entities_here = environment.get_entities_at(entity.position)
        for other_entity in entities_here:
            if other_entity.id != entity.id and other_entity.has_component('herbivore'):
                if other_entity.has_component('energy'):
                    herbivore_energy = other_entity.get_component('energy')
                    
                    # Transfer energy from prey to predator
                    consumed = herbivore_energy.energy
                    entity.get_component('energy').energy += consumed * 0.6
                    
                    # Remove the consumed herbivore
                    environment.remove_entity(other_entity.id)
                    
                    # Stop after eating one herbivore
                    break


class ReproductionComponent:
    """Component allowing entities to reproduce."""
    
    def __init__(self, threshold=100, offspring_energy=50, chance=0.05):
        """Initialize a reproduction component.
        
        Args:
            threshold (float): Energy threshold required for reproduction
            offspring_energy (float): Energy given to offspring
            chance (float): Probability of reproduction per step when above threshold
        """
        self.threshold = threshold
        self.offspring_energy = offspring_energy
        self.chance = chance
        
    def update(self, entity, environment):
        """Check conditions and possibly reproduce.
        
        Args:
            entity (Entity): The entity this component belongs to
            environment (Environment): The environment
        """
        if not entity.has_component('energy'):
            return
            
        energy = entity.get_component('energy')
        
        # Only reproduce if enough energy is available
        if energy.energy >= self.threshold and random.random() < self.chance:
            # Create offspring (copy of parent)
            offspring_id = uuid.uuid4()
            offspring = Entity(offspring_id, entity.position)
            
            # Copy components (simplified version)
            for name, component in entity.components.items():
                if name == 'energy':
                    # Offspring gets a new energy component
                    offspring.add_component('energy', EnergyComponent(
                        initial_energy=self.offspring_energy,
                        decay_rate=component.decay_rate
                    ))
                else:
                    # Other components are simply copied
                    offspring.add_component(name, copy.deepcopy(component))
            
            # Parent loses energy to offspring
            energy.energy -= self.offspring_energy
            
            # Add offspring to environment
            environment.add_entity(offspring)
```

## Command-Line Interface

The command-line interface will support running the predator-prey simulation:

```python
@click.group()
def cli():
    """VirtualLife: An artificial life simulator."""
    pass


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind the web server")
@click.option("--port", "-p", default=5000, help="Port to bind the web server")
@click.option("--debug", is_flag=True, help="Run in debug mode")
def web(host, port, debug):
    """Start the web interface."""
    from virtuallife.web.app import run_app
    run_app(host=host, port=port, debug=debug)


@cli.command()
@click.option("--width", "-w", default=50, help="Width of the grid")
@click.option("--height", "-h", default=50, help="Height of the grid")
@click.option("--plant-growth", "-p", default=0.1, help="Plant growth rate")
@click.option("--herbivore-count", default=20, help="Initial number of herbivores")
@click.option("--predator-count", default=5, help="Initial number of predators")
@click.option("--steps", "-s", default=1000, help="Number of steps to simulate")
@click.option("--web", is_flag=True, help="Open in web interface")
def predator_prey(width, height, plant_growth, herbivore_count, predator_count, steps, web):
    """Run a predator-prey simulation."""
    if web:
        # Start web server with predator-prey configuration
        from virtuallife.web.app import run_app
        import webbrowser
        import threading
        import json
        
        # Start web server in a separate thread
        threading.Thread(target=run_app, kwargs={'port': 5000, 'debug': False}, daemon=True).start()
        
        # Open browser with predator-prey configuration
        url = f"http://localhost:5000/?config={json.dumps({
            'type': 'predator_prey',
            'width': width,
            'height': height,
            'plant_growth_rate': plant_growth,
            'initial_plants': width * height // 10,  # ~10% coverage
            'initial_herbivores': herbivore_count,
            'initial_predators': predator_count
        })}"
        webbrowser.open(url)
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Web server stopped")
    else:
        # Create and run simulation in terminal (simplified version)
        print("Terminal-based visualization is deprecated. Please use --web flag for web interface.")
        print("Continuing with simplified output...")
        
        # Create environment and simulation
        environment = Environment(width, height)
        simulation = Simulation(environment)
        
        # Initialize with predator-prey configuration
        config = {
            'plant_growth_rate': plant_growth,
            'initial_plants': width * height // 10,
            'initial_herbivores': herbivore_count,
            'initial_predators': predator_count
        }
        SimulationManager()._initialize_predator_prey(simulation, config)
        
        # Run simulation with basic output
        for _ in range(steps):
            # Count entities by type
            plants = sum(1 for e in environment.entities.values() if e.has_component('plant'))
            herbivores = sum(1 for e in environment.entities.values() if e.has_component('herbivore'))
            predators = sum(1 for e in environment.entities.values() if e.has_component('predator'))
            
            print(f"Step {simulation.current_step}: Plants={plants}, Herbivores={herbivores}, Predators={predators}")
            simulation.step()


@cli.command()
@click.option("--config", "-c", required=True, help="Path to configuration file")
@click.option("--output", "-o", help="Path to output file")
@click.option("--web", is_flag=True, help="Open in web interface")
def run(config, output, web):
    """Run a simulation using the specified configuration."""
    config_dict = load_config(config)
    
    if web:
        # Start web server with configuration
        from virtuallife.web.app import run_app
        import webbrowser
        import threading
        import json
        
        # Start web server in a separate thread
        threading.Thread(target=run_app, kwargs={'port': 5000, 'debug': False}, daemon=True).start()
        
        # Open browser with configuration
        url = f"http://localhost:5000/?config={json.dumps(config_dict)}"
        webbrowser.open(url)
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Web server stopped")
    else:
        # Run simulation and save results
        simulation, data = run_simulation(config_dict)
        
        if output:
            # Save results
            with open(output, 'w') as f:
                json.dump(data, f, indent=2)


if __name__ == "__main__":
    cli()
```

## Conclusion

This technical specification provides a blueprint for implementing the VirtualLife project with a web-based interface and a predator-prey ecosystem as the first implementation example. The focus is on creating a clear, modular architecture that can be incrementally enhanced through the phases outlined in the roadmap.

The predator-prey ecosystem provides a richer first implementation than a simple cellular automaton, showcasing more of the system's capabilities including resource management, entity behaviors, and population dynamics. The web interface will make the platform accessible to a wide audience, while the modular design will allow for continuous improvement and extension. 