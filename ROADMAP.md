# VirtualLife: Artificial Life Simulator

## Project Overview

VirtualLife is an artificial life simulator designed to model the emergence of complex behaviors from simple rules. Unlike detailed biological simulations, VirtualLife focuses on computational generations/turns within a virtual environment, starting with simple cells and parameterized rules to observe emergent patterns and behaviors.

The project aims to create a flexible framework capable of simulating scenarios ranging from simple predator-prey ecosystems to complex ecological systems featuring mutualism, territorial behaviors, and other emergent phenomena.

## Technical Vision

### Core Principles

- **Modularity**: Separate components for environment, entities, rules, and visualization
- **Extensibility**: Easy to add new entity types, behaviors, and environmental features
- **Observability**: Built-in tools for data collection, analysis, and visualization
- **Performance**: Efficient algorithms with potential for optimization in critical areas
- **Testability**: Comprehensive test coverage with test-first development approach
- **Maintainability**: Small, focused modules with clear responsibilities and interfaces

### Technology Stack

- **Primary Language**: Python 3.10+
- **Core Libraries**: NumPy/SciPy for vectorized operations
- **Web Framework**: Flask with Flask-SocketIO for real-time communication
- **Visualization**: D3.js for interactive web visualization
- **Testing**: Pytest for unit and integration tests, Hypothesis for property-based testing
- **Documentation**: Google-style docstrings
- **Package Management**: Poetry for dependency management
- **CI/CD**: GitHub Actions

## Simplified Roadmap

### Phase 1: Core Simulation Framework with Web Interface (Weeks 1-4)

**Goal**: Create the foundational simulation system with a web interface and implement a simple predator-prey ecosystem as proof of concept.

#### Development Approach:
- **Test-First Development**: Every module must have comprehensive tests before implementation
- **Interface-First Design**: Define clear interfaces using Protocol classes before implementation
- **Small Files**: Keep each module under 300 lines for maintainability and easy understanding
- **Continuous Testing**: Run tests frequently and maintain high coverage throughout development

#### Deliverables:
- [ ] Project structure with Poetry setup
- [ ] Core interfaces (first develop these):
  - [ ] `EnvironmentInterface`: Protocol defining environment operations
  - [ ] `EntityInterface`: Protocol defining entity capabilities
  - [ ] `ComponentInterface`: Protocol defining component behavior
  - [ ] `SimulationInterface`: Protocol defining simulation control
- [ ] Core modules (implement against interfaces):
  - [ ] `Environment`: A 2D grid with boundary conditions
    - [ ] Test coverage: min 90%
    - [ ] Should handle wrapped, bounded, and infinite boundaries
    - [ ] Entity positioning and tracking
    - [ ] Resource generation and distribution
  - [ ] `Entity`: Component-based entities
    - [ ] Test coverage: min 90%
    - [ ] Component management system
    - [ ] Position tracking
    - [ ] Basic attributes (energy, age)
  - [ ] `Simulation`: Controls time progression and updates
    - [ ] Test coverage: min 90%
    - [ ] Step-by-step execution
    - [ ] Observer pattern for monitoring
- [ ] Web interface components:
  - [ ] Basic Flask application structure
  - [ ] WebSocket communication for real-time updates
  - [ ] Grid visualization using HTML5 Canvas or SVG
  - [ ] Basic simulation controls (start, stop, step, reset)
  - [ ] Configuration form for simulation parameters
- [ ] Predator-Prey Ecosystem implementation
  - [ ] Test coverage: min 90%
  - [ ] Plants (static resource entities)
  - [ ] Herbivores (consume plants)
  - [ ] Predators (consume herbivores)
  - [ ] Energy metabolism
  - [ ] Basic movement strategies
  - [ ] Simple reproduction mechanics
- [ ] Basic configuration system (YAML-based)
  - [ ] Test coverage: min 90%
  - [ ] Tests for valid and invalid configurations
- [ ] Command-line interface for running simulations
  - [ ] Test coverage: min 80%
  - [ ] Tests for all commands and options

**Acceptance Criteria**:
- All tests pass with minimum 90% overall coverage
- Implementation of Predator-Prey system shows expected population dynamics
- Web interface correctly displays simulation state with different entity types
- Web interface allows basic control of simulation
- Configuration can be loaded from YAML files
- All modules adhere to the file size limits and interface contracts
- No circular dependencies between modules

**Phase 1 Milestones**:
1. Week 1: Interface definitions and initial test framework
2. Week 2: Core implementation and entity components
3. Week 3: Basic web interface structure and visualization
4. Week 4: Web controls, configuration, and final testing

### Phase 2: Resources and Simple Behaviors (Weeks 5-7)

**Goal**: Add more advanced resources, entity behaviors, and enhanced web visualization.

#### Deliverables:
- [ ] Enhanced resource system:
  - [ ] Multiple resource types
  - [ ] Resource consumption efficiency
  - [ ] Environmental factors affecting resource growth
- [ ] Expanded component-based entity system:
  - [ ] Additional trait components (speed, perception, etc.)
  - [ ] More behavior components
- [ ] Advanced behaviors:
  - [ ] Smart movement (pathfinding, obstacle avoidance)
  - [ ] Predator hunting strategies
  - [ ] Prey escape behaviors
  - [ ] Improved reproduction strategies
- [ ] Enhanced web visualization:
  - [ ] Entity and resource rendering with different colors/shapes
  - [ ] Interactive controls (pause, step, speed)
  - [ ] Zoom and pan capabilities
- [ ] Data collection system:
  - [ ] Population statistics
  - [ ] Resource distribution charts
  - [ ] Real-time data visualization in web interface

**Acceptance Criteria**:
- Entities exhibit more sophisticated behaviors
- Resource distribution and regeneration has more realistic patterns
- Web visualization correctly renders entities and resources with distinguishing features
- Data collection produces accurate time series data
- Web interface displays real-time statistics

### Phase 3: Species and Simple Genetics (Weeks 8-10)

**Goal**: Implement species concept and basic genetic inheritance.

#### Deliverables:
- [ ] Species implementation:
  - [ ] Species as entity templates
  - [ ] Factory method for entity creation
- [ ] Simple genetics:
  - [ ] Trait inheritance with variation
  - [ ] Mutation mechanisms
  - [ ] Selection based on fitness
- [ ] Species relationships:
  - [ ] Predator-prey relationships
  - [ ] Competition for resources
- [ ] Enhanced data collection:
  - [ ] Species population tracking
  - [ ] Genetic diversity metrics
- [ ] Web interface enhancements:
  - [ ] Species configuration panel
  - [ ] Species statistics and charts
  - [ ] Visual differentiation of species

**Acceptance Criteria**:
- Species maintain consistent traits with controlled variation
- Genetic inheritance and mutation work correctly
- Population dynamics show expected patterns
- Data collection accurately tracks species and genetic information
- Web interface allows species configuration and monitoring

### Phase 4: Advanced Ecology and Analysis (Weeks 11-13)

**Goal**: Add more complex ecological dynamics and analysis tools.

#### Deliverables:
- [ ] Enhanced environmental factors:
  - [ ] Temperature, moisture, etc.
  - [ ] Environmental cycles
- [ ] Advanced entity interactions:
  - [ ] Mutualism/symbiosis
  - [ ] Territorial behaviors
- [ ] Analysis system:
  - [ ] Population dynamics analysis
  - [ ] Spatial distribution analysis
  - [ ] Simple phylogenetic tracking
- [ ] Enhanced visualization:
  - [ ] Environmental factor visualization (heat maps)
  - [ ] Data visualization dashboards
  - [ ] Time controls (rewind, timelapses)
  - [ ] Simulation state export/import

**Acceptance Criteria**:
- Environmental factors meaningfully impact entity behaviors
- Complex interactions produce emergent patterns
- Analysis tools provide useful insights
- Visualization system effectively communicates results
- Users can save and load simulation states

### Phase 5: Advanced Genetics and Evolution (Weeks 14-16)

**Goal**: Implement more complex genetic systems and evolutionary dynamics.

#### Deliverables:
- [ ] Advanced genetic system:
  - [ ] Gene expression mechanisms
  - [ ] Sexual reproduction
  - [ ] Genetic recombination
- [ ] Evolutionary mechanisms:
  - [ ] Speciation
  - [ ] Adaptive radiation
  - [ ] Co-evolution
- [ ] Enhanced analysis:
  - [ ] Phylogenetic tree visualization
  - [ ] Genetic drift analysis
  - [ ] Selection pressure analysis
- [ ] Web interface enhancements:
  - [ ] Interactive phylogenetic tree
  - [ ] Genetic visualization tools
  - [ ] Advanced simulation parameter controls

**Acceptance Criteria**:
- Genetic system produces realistic inheritance patterns
- Evolutionary mechanisms lead to appropriate adaptations
- Analysis tools accurately track evolutionary changes
- System can model and visualize long-term evolutionary patterns
- Web interface provides comprehensive visualization of genetic data

## Technical Implementation

### Web Interface Architecture

The web interface will be built using Flask and Flask-SocketIO with the following components:

1. **Server-Side Components**:
   - Flask application for serving web pages and API endpoints
   - Flask-SocketIO for real-time communication
   - Simulation manager for handling multiple simulation instances
   - Data collection and processing for visualization

2. **Client-Side Components**:
   - HTML5/CSS3 for page structure and styling
   - JavaScript with D3.js for visualization
   - Socket.IO client for real-time updates
   - Form handling for simulation configuration

3. **Communication Flow**:
   - Initial page load: Server renders template with basic structure
   - WebSocket connection established for real-time updates
   - Client sends commands (start, stop, step, etc.)
   - Server processes commands and sends simulation state updates
   - Client renders updates in real-time

### Core Components

#### 1. Environment

**Description**: Represents the world where entities exist and interact.

**Key Features**:
- Grid-based spatial representation (2D initially, extensible to 3D)
- Resource generation and distribution mechanisms
- Environmental conditions (variables affecting entities)
- Boundary conditions (wrapped, bounded, or infinite)

**Technical Implementation**:
- Class hierarchy with `Environment` base class
- Numpy arrays for efficient grid operations
- Customizable update rules for environmental processes
- Spatial indexing for efficient entity queries

#### 2. Entities

**Description**: Objects that exist in the environment, including organisms and resources.

**Key Features**:
- Position and movement capabilities
- Internal state (energy, age, health, etc.)
- Sensory perception of environment
- Decision-making based on rules or adaptive systems
- Reproduction mechanisms

**Technical Implementation**:
- Abstract `Entity` base class with specialized subclasses
- Component-based architecture for behavior composition
- Efficient state update methods
- Event-driven interaction system

#### 3. Species

**Description**: Templates defining properties and behaviors for groups of entities.

**Key Features**:
- Trait definitions with allowed variations
- Behavior parameters
- Evolutionary constraints
- Interspecies relationship definitions

**Technical Implementation**:
- Factory pattern for entity creation
- Parameter validation and constraint checking
- Inheritance mechanisms for evolution simulation
- Metrics for species diversity and fitness

#### 4. Simulation Engine

**Description**: Core system controlling time progression and entity updates.

**Key Features**:
- Time step management
- Update ordering and synchronization
- Event queuing and processing
- State saving and loading

**Technical Implementation**:
- Event-driven architecture
- Configurable update strategies (synchronous or asynchronous)
- Deterministic random number generation for reproducibility
- Checkpointing system for state management

#### 5. Web Visualization

**Description**: System for rendering simulation state in a web browser.

**Key Features**:
- Real-time grid visualization
- Entity and resource rendering
- Interactive controls
- Data visualization dashboards

**Technical Implementation**:
- HTML5 Canvas or SVG for grid rendering
- D3.js for data visualization
- WebSocket for real-time updates
- Responsive design for different screen sizes

### Data Structures

#### 1. Environment Grid
```python
# Conceptual structure
environment_grid = {
    'entities': numpy.ndarray,  # Entity references
    'resources': {
        'resource_type': numpy.ndarray,  # Resource levels
    },
    'conditions': {
        'condition_type': numpy.ndarray,  # Environmental conditions
    }
}
```

#### 2. Entity Schema
```python
# Conceptual structure
entity = {
    'id': UUID,
    'position': (x, y),
    'species': Species,
    'state': {
        'energy': float,
        'age': int,
        'health': float,
        # Other state variables
    },
    'genome': {
        # Genetic information
    },
    'behavior': {
        # Current behavior state
    }
}
```

#### 3. Species Definition
```python
# Conceptual structure
species = {
    'id': UUID,
    'name': str,
    'traits': {
        'trait_name': {
            'base_value': float,
            'variation': float,
            'mutation_rate': float,
        }
    },
    'behaviors': [
        {
            'name': str,
            'conditions': callable,
            'actions': callable,
            'priority': int,
        }
    ],
    'reproduction': {
        'type': str,  # 'asexual', 'sexual'
        'energy_threshold': float,
        'offspring_count': int,
        # Other reproduction parameters
    }
}
```

#### 4. Simulation Data
```python
# Conceptual structure
simulation_data = {
    'metadata': {
        'timestamp': datetime,
        'parameters': dict,
        'version': str,
    },
    'time_series': {
        'population': DataFrame,  # Population metrics over time
        'resources': DataFrame,  # Resource metrics over time
        'environmental': DataFrame,  # Environmental metrics over time
    },
    'genetic_data': {
        'diversity': DataFrame,  # Genetic diversity metrics over time
        'trait_distribution': DataFrame,  # Trait distributions over time
    },
    'spatial_data': [
        {
            'step': int,
            'entities': array,  # Spatial distribution of entities
            'resources': dict,  # Spatial distribution of resources
            'conditions': dict,  # Spatial distribution of conditions
        }
    ],
    'events': [
        {
            'step': int,
            'type': str,
            'data': dict,  # Event-specific data
        }
    ]
}
```

### API Design

#### 1. Simulation Control API
```python
# Core simulation methods
initialize(config: SimulationConfig) -> Simulation
step(count: int = 1) -> SimulationState
run(steps: int = None, condition: callable = None) -> SimulationResult
save_state(path: str) -> None
load_state(path: str) -> Simulation
```

#### 2. Entity Management API
```python
# Entity manipulation methods
add_entity(entity: Entity, position: tuple) -> UUID
remove_entity(entity_id: UUID) -> None
get_entities(filter_func: callable = None) -> List[Entity]
get_entities_at(position: tuple) -> List[Entity]
```

#### 3. Environment Manipulation API
```python
# Environment control methods
add_resource(resource_type: str, amount: float, position: tuple = None) -> None
set_condition(condition_type: str, value: float, position: tuple = None) -> None
get_neighborhood(position: tuple, radius: int = 1) -> EnvironmentView
```

#### 4. Analysis API
```python
# Analysis methods
collect_metrics() -> Dict[str, any]
get_population_stats() -> DataFrame
get_resource_distribution() -> Dict[str, numpy.ndarray]
get_phylogenetic_tree() -> PhylogeneticTree
export_data(format: str = 'csv') -> str
```

#### 5. Web API
```python
# Web API endpoints
GET /api/simulations - List all simulations
POST /api/simulations - Create a new simulation
GET /api/simulations/{id} - Get simulation details
PUT /api/simulations/{id}/control - Control simulation (start, stop, step)
GET /api/simulations/{id}/state - Get current simulation state
GET /api/simulations/{id}/metrics - Get simulation metrics
```

#### 6. WebSocket Events
```python
# WebSocket events
simulation_state_update - Sent when simulation state changes
simulation_metrics_update - Sent when metrics are updated
simulation_control_response - Sent in response to control commands
simulation_error - Sent when an error occurs
```

## Testing Strategy

### Unit Testing

- Test individual components in isolation
- Mock dependencies for controlled testing
- Validate mathematical correctness of algorithms
- Ensure proper error handling

### Integration Testing

- Test component interactions
- Validate event propagation
- Verify state consistency across components
- Test configuration loading and application

### System Testing

- Run end-to-end simulations with known outcomes
- Validate resource conservation laws
- Test performance under various loads
- Verify deterministic behavior with fixed random seeds

### Web Interface Testing

- Test API endpoints
- Verify WebSocket communication
- Test browser compatibility
- Validate responsive design
- Test user interactions

## Conclusion

VirtualLife aims to create a flexible, extensible platform for artificial life simulation with a focus on emergent behaviors. By following this roadmap, the project will evolve from a simple predator-prey ecosystem to a sophisticated ecosystem simulation capable of modeling complex interactions and evolutionary processes.

The web-based interface will make the platform accessible to a wide audience, while the modular design will allow for continuous improvement and extension. The emphasis on analysis and visualization will make the platform valuable for both educational and research purposes. 