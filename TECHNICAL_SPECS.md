# VirtualLife Technical Specifications (Simplified for AI Implementation)

## AI Implementation Requirements

Since this project will be implemented by an AI agent, the following standards for testing and documentation are **mandatory** at every step:

### Testing Requirements

1. **Comprehensive Unit Tests**:
   - Every function and method must have corresponding tests
   - Tests must cover normal operation, edge cases, and error conditions
   - 90% minimum line coverage for all components
   - All boundary conditions must be explicitly tested

2. **Integration Tests**:
   - All component interactions must be verified
   - System state consistency must be tested
   - Configuration handling must be verified

3. **Documentation Tests**:
   - All examples in docstrings must be verifiable and tested
   - README examples must be verified
   - API documentation must match implementation
   - Configuration examples must be tested

4. **Property-Based Testing**:
   - Randomized behaviors must have property-based tests
   - Invariants must be identified and tested
   - Genetic algorithms must have statistical correctness tests

### Documentation Requirements

1. **Module Documentation**:
   - Every module must have a detailed docstring explaining purpose and content
   - Architecture relationships must be documented
   - Usage examples must be included

2. **Function/Method Documentation**:
   - Every public function must have comprehensive docstrings
   - All parameters must be documented with types and descriptions
   - Return values must be documented
   - Exceptions must be documented
   - Examples must be included

3. **Class Documentation**:
   - Class purpose and behavior must be documented
   - Initialization parameters must be explained
   - Class attributes must be documented
   - Relationships with other classes must be explained

4. **Code Comments**:
   - Complex algorithms must have detailed explanations
   - Design decisions and tradeoffs must be documented
   - Non-obvious code must be commented

## Architecture Overview

VirtualLife follows a modern Entity-Component-System (ECS) architecture focused on the core simulation concepts. The system is organized into these main modules:

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

## Development Approach

### Incremental Complexity with Comprehensive Testing

1. Start with a minimal viable implementation with complete tests
2. Add features incrementally, led by tests
3. Refactor as patterns emerge, protected by tests
4. Document thoroughly at every step

### Testing-First Development

1. **Write documentation**: Define interface and behavior with docstrings
2. **Write tests**: Create comprehensive tests for the interface
3. **Implement code**: Write code to match documentation and pass tests
4. **Refactor**: Improve implementation while maintaining test coverage

### Comprehensive Documentation

1. **Module Documentation**: Every module must have detailed docstrings
2. **Function Documentation**: Every function must have complete docstrings
3. **Type Annotations**: All parameters, return values, and variables must be annotated
4. **Examples**: Include executable examples in docstrings
5. **Internal Comments**: Explain complex algorithms or non-obvious choices

## Core Components

### 1. ECS Core

The Entity-Component-System (ECS) architecture forms the foundation of the simulation.

#### 1.1 Entity

Entities are lightweight containers for components with a unique identifier.

```python
from dataclasses import dataclass, field
from typing import Dict, Protocol, TypeVar, cast, Optional, Type, TYPE_CHECKING
from uuid import UUID, uuid4

from virtuallife.types import Position

@dataclass
class Entity:
    """Base entity class using composition for behaviors.
    
    Entities are the primary objects in the simulation. They exist in the environment
    and can have various components that define their behavior.
    
    Attributes:
        id: Unique identifier for the entity
        position: The (x, y) position of the entity in the environment
        components: Dictionary mapping component types to components
    """
    id: UUID = field(default_factory=uuid4)
    position: Position = field(default=(0, 0))
    _components: Dict[Type["Component"], "Component"] = field(default_factory=dict)
    
    def add_component(self, component: "Component") -> None:
        """Add a component to the entity.
        
        Args:
            component: The component to add
            
        Raises:
            ValueError: If a component of the same type already exists
        """
        component_type = type(component)
        if component_type in self._components:
            raise ValueError(f"Component of type {component_type.__name__} already exists on this entity")
        self._components[component_type] = component
    
    def has_component(self, component_type: Type["Component"]) -> bool:
        """Check if the entity has a specific component type.
        
        Args:
            component_type: The type of component to check for
            
        Returns:
            True if the entity has the component, False otherwise
        """
        return component_type in self._components
    
    def get_component(self, component_type: Type[TypeVar("C", bound="Component")]) -> Optional[TypeVar("C")]:
        """Get a component by type.
        
        Args:
            component_type: The type of component to get
            
        Returns:
            The component if it exists, None otherwise
        """
        component = self._components.get(component_type)
        if component is not None:
            return cast(component_type, component)
        return None
```

#### 1.2 Component Protocol

Components define the data and behavior for entities.

```python
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from virtuallife.ecs.entity import Entity
    from virtuallife.ecs.world import World

class Component(Protocol):
    """Protocol defining the interface for entity components.
    
    All components must implement this protocol to be usable with the Entity class.
    The update method is called on each simulation step.
    """
    def update(self, entity: "Entity", world: "World", dt: float) -> None:
        """Update the component state.
        
        Args:
            entity: The entity this component belongs to
            world: The world the entity exists in
            dt: Time delta since last update
        """
        ...
```

#### 1.3 System

Systems process entities with specific components.

```python
from abc import ABC, abstractmethod
from typing import Set, Type, List, TYPE_CHECKING

if TYPE_CHECKING:
    from virtuallife.ecs.entity import Entity
    from virtuallife.ecs.world import World
    from virtuallife.ecs.component import Component

class System(ABC):
    """Base class for systems that process entities with specific components.
    
    Systems are responsible for updating entities that have specific components.
    They provide a way to organize game logic by functionality rather than by entity.
    """
    
    def __init__(self) -> None:
        """Initialize the system."""
        self.entities: Set[UUID] = set()
        
    @property
    @abstractmethod
    def required_components(self) -> List[Type["Component"]]:
        """Get the component types required for an entity to be processed by this system.
        
        Returns:
            A list of component types that an entity must have to be processed
        """
        pass
        
    def should_process(self, entity: "Entity") -> bool:
        """Check if the entity should be processed by this system.
        
        Args:
            entity: The entity to check
            
        Returns:
            True if the entity has all required components, False otherwise
        """
        return all(entity.has_component(component_type) for component_type in self.required_components)
        
    def register_entity(self, entity: "Entity") -> None:
        """Register an entity with this system.
        
        Args:
            entity: The entity to register
        """
        if self.should_process(entity):
            self.entities.add(entity.id)
            
    def unregister_entity(self, entity_id: UUID) -> None:
        """Unregister an entity from this system.
        
        Args:
            entity_id: The ID of the entity to unregister
        """
        if entity_id in self.entities:
            self.entities.remove(entity_id)
            
    @abstractmethod
    def process(self, world: "World", dt: float) -> None:
        """Process all registered entities.
        
        Args:
            world: The world containing the entities
            dt: Time delta since last update
        """
        pass
```

#### 1.4 World

The World manages entities, systems, and their relationships.

```python
from dataclasses import dataclass, field
from typing import Dict, List, Set, Type, Optional, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from virtuallife.ecs.entity import Entity
    from virtuallife.ecs.system import System
    from virtuallife.environment.grid import SpatialGrid
    from virtuallife.events.dispatcher import EventDispatcher

@dataclass
class World:
    """Container for entities, systems, and their relationships.
    
    The World class manages entities and systems, and provides methods for
    updating the simulation state.
    
    Attributes:
        entities: Dictionary mapping entity IDs to entities
        systems: List of systems that process entities
        grid: Spatial grid for efficient entity lookups
        event_dispatcher: Event dispatcher for simulation events
    """
    entities: Dict[UUID, "Entity"] = field(default_factory=dict)
    systems: List["System"] = field(default_factory=list)
    grid: Optional["SpatialGrid"] = None
    event_dispatcher: Optional["EventDispatcher"] = None
    
    def add_entity(self, entity: "Entity") -> None:
        """Add an entity to the world.
        
        Args:
            entity: The entity to add
        """
        self.entities[entity.id] = entity
        
        # Register with spatial grid if available
        if self.grid is not None:
            self.grid.add_entity(entity.id, entity.position)
            
        # Register with systems
        for system in self.systems:
            system.register_entity(entity)
            
        # Dispatch event
        if self.event_dispatcher is not None:
            self.event_dispatcher.dispatch("entity_added", entity=entity)
            
    def remove_entity(self, entity_id: UUID) -> None:
        """Remove an entity from the world.
        
        Args:
            entity_id: The ID of the entity to remove
        """
        if entity_id not in self.entities:
            return
            
        entity = self.entities[entity_id]
        
        # Unregister from spatial grid if available
        if self.grid is not None:
            self.grid.remove_entity(entity_id, entity.position)
            
        # Unregister from systems
        for system in self.systems:
            system.unregister_entity(entity_id)
            
        # Dispatch event
        if self.event_dispatcher is not None:
            self.event_dispatcher.dispatch("entity_removed", entity=entity)
            
        # Remove from entities
        del self.entities[entity_id]
        
    def add_system(self, system: "System") -> None:
        """Add a system to the world.
        
        Args:
            system: The system to add
        """
        self.systems.append(system)
        
        # Register existing entities with the system
        for entity in self.entities.values():
            system.register_entity(entity)
            
    def update(self, dt: float) -> None:
        """Update the world state.
        
        Args:
            dt: Time delta since last update
        """
        # Process all systems
        for system in self.systems:
            system.process(self, dt)
```

### 2. Environment

The environment module provides specialized classes for managing the simulation space.

#### 2.1 Spatial Grid

The SpatialGrid manages entity positions and provides efficient spatial queries.

```python
from dataclasses import dataclass, field
from typing import Dict, Set, Tuple, List, Optional, TYPE_CHECKING
from uuid import UUID
from collections import defaultdict

from virtuallife.types import Position
from virtuallife.environment.boundary import BoundaryHandler

@dataclass
class SpatialGrid:
    """A spatial grid for efficient entity lookups.
    
    The SpatialGrid class manages entity positions and provides methods for
    efficient spatial queries.
    
    Attributes:
        width: Width of the grid
        height: Height of the grid
        boundary_handler: Handler for boundary conditions
        cell_size: Size of each grid cell for spatial partitioning
        cells: Dictionary mapping cell coordinates to sets of entity IDs
        entity_positions: Dictionary mapping entity IDs to positions
    """
    width: int
    height: int
    boundary_handler: BoundaryHandler
    cell_size: int = 10
    cells: Dict[Tuple[int, int], Set[UUID]] = field(default_factory=lambda: defaultdict(set))
    entity_positions: Dict[UUID, Position] = field(default_factory=dict)
    
    def position_to_cell(self, position: Position) -> Tuple[int, int]:
        """Convert a position to a cell coordinate.
        
        Args:
            position: The position to convert
            
        Returns:
            The cell coordinate
        """
        x, y = position
        return (x // self.cell_size, y // self.cell_size)
        
    def add_entity(self, entity_id: UUID, position: Position) -> None:
        """Add an entity to the grid.
        
        Args:
            entity_id: The ID of the entity to add
            position: The position of the entity
        """
        # Normalize position based on boundary conditions
        position = self.boundary_handler.normalize_position(position)
        
        # Add to entity positions
        self.entity_positions[entity_id] = position
        
        # Add to cell
        cell = self.position_to_cell(position)
        self.cells[cell].add(entity_id)
        
    def remove_entity(self, entity_id: UUID, position: Optional[Position] = None) -> None:
        """Remove an entity from the grid.
        
        Args:
            entity_id: The ID of the entity to remove
            position: The position of the entity (optional, will be looked up if not provided)
        """
        if entity_id not in self.entity_positions:
            return
            
        # Get position if not provided
        if position is None:
            position = self.entity_positions[entity_id]
            
        # Remove from cell
        cell = self.position_to_cell(position)
        if cell in self.cells and entity_id in self.cells[cell]:
            self.cells[cell].remove(entity_id)
            if not self.cells[cell]:
                del self.cells[cell]
                
        # Remove from entity positions
        del self.entity_positions[entity_id]
        
    def get_entities_in_radius(self, position: Position, radius: int) -> Set[UUID]:
        """Get all entities within a radius of the position.
        
        Args:
            position: The center position
            radius: The radius to search
            
        Returns:
            A set of entity IDs within the radius
        """
        entities = set()
        center_cell = self.position_to_cell(position)
        cell_radius = (radius // self.cell_size) + 1
        
        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                if cell in self.cells:
                    entities.update(self.cells[cell])
                    
        return entities
```

### 3. Components

Components define the data and behavior for entities.

#### 3.1 Energy Component

```python
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from virtuallife.ecs.entity import Entity
    from virtuallife.ecs.world import World

@dataclass
class EnergyComponent:
    """Component that manages an entity's energy level.
    
    Attributes:
        energy: Current energy level
        max_energy: Maximum energy level
        decay_rate: Rate at which energy decreases per step
        death_threshold: Energy level at which the entity dies
    """
    energy: float
    max_energy: float
    decay_rate: float
    death_threshold: float = 0.0
    
    def update(self, entity: "Entity", world: "World", dt: float) -> None:
        """Update the entity's energy level.
        
        Args:
            entity: The entity this component belongs to
            world: The world the entity exists in
            dt: Time delta since last update
        """
        self.energy -= self.decay_rate * dt
        
        if self.energy <= self.death_threshold:
            world.remove_entity(entity.id)
            
    def consume_energy(self, amount: float) -> bool:
        """Consume some energy.
        
        Args:
            amount: The amount of energy to consume
            
        Returns:
            True if the energy was consumed, False if there wasn't enough
        """
        if amount > self.energy:
            return False
            
        self.energy -= amount
        return True
        
    def add_energy(self, amount: float) -> None:
        """Add energy up to the maximum.
        
        Args:
            amount: The amount of energy to add
        """
        self.energy = min(self.energy + amount, self.max_energy)
```

### 4. Systems

Systems process entities with specific components.

#### 4.1 Movement System

```python
from typing import List, Type, Dict, Set, TYPE_CHECKING
import random

from virtuallife.ecs.system import System
from virtuallife.components.movement import MovementComponent
from virtuallife.components.energy import EnergyComponent

if TYPE_CHECKING:
    from virtuallife.ecs.component import Component
    from virtuallife.ecs.world import World

class MovementSystem(System):
    """System for processing entity movement.
    
    This system updates the positions of entities with movement components.
    """
    
    @property
    def required_components(self) -> List[Type["Component"]]:
        """Get the component types required for an entity to be processed by this system.
        
        Returns:
            A list of component types that an entity must have to be processed
        """
        return [MovementComponent]
        
    def process(self, world: "World", dt: float) -> None:
        """Process all registered entities.
        
        Args:
            world: The world containing the entities
            dt: Time delta since last update
        """
        for entity_id in self.entities:
            entity = world.entities.get(entity_id)
            if entity is None:
                continue
                
            # Get required components
            movement = entity.get_component(MovementComponent)
            if movement is None:
                continue
                
            # Check if entity has energy
            energy = entity.get_component(EnergyComponent)
            
            # Calculate movement
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            
            # Skip if no movement
            if dx == 0 and dy == 0:
                continue
                
            # Calculate energy cost
            if energy is not None:
                energy_cost = movement.movement_cost * movement.speed * dt
                if not energy.consume_energy(energy_cost):
                    continue
                    
            # Update position
            old_position = entity.position
            new_position = (old_position[0] + dx, old_position[1] + dy)
            
            # Update spatial grid if available
            if world.grid is not None:
                world.grid.remove_entity(entity_id, old_position)
                world.grid.add_entity(entity_id, new_position)
                
            # Update entity position
            entity.position = new_position
```

## Testing Strategy

A comprehensive approach to testing that ensures correctness and reliability:

### 1. Unit Testing Every Component

```python
# Example unit test for Environment class
def test_environment_add_entity():
    """Test that entities can be added to the environment.
    
    This test verifies that:
    1. The entity is added to the entities dictionary
    2. The entity's ID is added to entity_positions at the correct position
    3. The entity can be retrieved by its position
    """
    # Arrange
    env = Environment(50, 50)
    entity = Entity(position=(10, 20))
    
    # Act
    env.add_entity(entity)
    
    # Assert
    assert entity.id in env.entities
    assert entity.id in env.entity_positions[(10, 20)]
    assert entity in env.get_entities_at((10, 20))

# Example parameterized test for boundary conditions
@pytest.mark.parametrize("boundary,position,expected", [
    ("wrapped", (60, 70), (10, 20)),  # 50x50 grid, wrapped boundary
    ("bounded", (60, 70), (49, 49)),  # 50x50 grid, bounded boundary
    ("infinite", (60, 70), (60, 70))  # 50x50 grid, infinite boundary
])
def test_environment_normalize_position(boundary, position, expected):
    """Test that positions are normalized correctly for different boundary conditions.
    
    This test verifies that:
    1. "wrapped" boundary wraps positions around the grid
    2. "bounded" boundary clamps positions to the grid
    3. "infinite" boundary allows positions outside the grid
    """
    # Arrange
    env = Environment(50, 50, boundary_condition=boundary)
    
    # Act
    result = env.normalize_position(position)
    
    # Assert
    assert result == expected
```

### 2. Property-Based Testing for Invariants

```python
# Example property-based test for entity movement
@given(
    width=st.integers(min_value=10, max_value=100),
    height=st.integers(min_value=10, max_value=100),
    entity_x=st.integers(min_value=0, max_value=9),
    entity_y=st.integers(min_value=0, max_value=9),
    dx=st.integers(min_value=-1, max_value=1),
    dy=st.integers(min_value=-1, max_value=1)
)
def test_entity_movement_property(width, height, entity_x, entity_y, dx, dy):
    """Test that entity movement works correctly for any valid grid and position.
    
    This test verifies that:
    1. The entity's position is updated correctly after movement
    2. The entity's position is always within the grid bounds for wrapped boundary
    3. The entity's energy decreases by the correct amount after movement
    """
    # Arrange
    env = Environment(width, height, boundary_condition="wrapped")
    entity = Entity(position=(entity_x, entity_y))
    energy = EnergyComponent(energy=100.0, decay_rate=0.0)
    movement = MovementComponent(speed=1.0, movement_cost=0.1)
    entity.add_component("energy", energy)
    entity.add_component("movement", movement)
    env.add_entity(entity)
    
    # Set up the movement
    old_position = entity.position
    old_energy = energy.energy
    
    # Act - manually trigger the movement in a specific direction
    x, y = entity.position
    new_pos = env.normalize_position((x + dx, y + dy))
    energy.energy -= movement.movement_cost * movement.speed
    
    # Update position in environment
    env.entity_positions[entity.position].remove(entity.id)
    if not env.entity_positions[entity.position]:
        del env.entity_positions[entity.position]
    
    entity.position = new_pos
    
    if new_pos not in env.entity_positions:
        env.entity_positions[new_pos] = set()
    env.entity_positions[new_pos].add(entity.id)
    
    # Assert
    assert entity.position == new_pos
    assert 0 <= entity.position[0] < width
    assert 0 <= entity.position[1] < height
    assert energy.energy == old_energy - movement.movement_cost * movement.speed
    assert entity.id in env.entity_positions[new_pos]
```

### 3. Integration Testing for Component Interactions

```python
# Example integration test for predator-prey interaction
def test_predator_prey_interaction():
    """Test that predators can hunt and consume herbivores.
    
    This test verifies that:
    1. A predator at the same position as a herbivore will consume it
    2. The predator's energy increases by the correct amount
    3. The herbivore is removed from the environment
    """
    # Arrange
    env = Environment(50, 50)
    
    # Create a herbivore
    herbivore = Entity(position=(10, 10))
    herbivore_energy = EnergyComponent(energy=50.0)
    herbivore.add_component("energy", herbivore_energy)
    herbivore.add_component("herbivore", HerbivoreComponent())
    env.add_entity(herbivore)
    
    # Create a predator
    predator = Entity(position=(10, 10))
    predator_energy = EnergyComponent(energy=100.0)
    predator.add_component("energy", predator_energy)
    predator.add_component("predator", PredatorComponent(energy_efficiency=0.6))
    env.add_entity(predator)
    
    # Store IDs and initial energy
    herbivore_id = herbivore.id
    predator_id = predator.id
    initial_predator_energy = predator_energy.energy
    herbivore_energy_value = herbivore_energy.energy
    
    # Act
    predator.update(env)
    
    # Assert
    assert herbivore_id not in env.entities  # Herbivore should be consumed
    assert predator_id in env.entities  # Predator should still exist
    assert predator_energy.energy == pytest.approx(initial_predator_energy + herbivore_energy_value * 0.6)
```

### 4. Documentation Tests

```python
# Example doctest verification
def test_environment_doctest():
    """Verify that the doctest examples in Environment are correct."""
    import doctest
    import io
    output = io.StringIO()
    result = doctest.testfile(
        "environment.py",
        package="virtuallife.simulation",
        verbose=True,
        raise_on_error=True,
        optionflags=doctest.ELLIPSIS,
        name="environment",
        globs={'Environment': Environment, 'Entity': Entity},
        out=output
    )
    assert result.failed == 0
```

## End-to-End Testing

```python
# Example end-to-end test for a predator-prey ecosystem
def test_predator_prey_ecosystem():
    """Test a complete predator-prey ecosystem over multiple time steps.
    
    This test verifies that:
    1. The ecosystem evolves according to expected patterns
    2. Population dynamics follow expected trends
    3. The simulation can run for many steps without errors
    """
    # Arrange
    config = SimulationConfig(
        width=50,
        height=50,
        initial_plants=100,
        initial_herbivores=20,
        initial_predators=5,
        plant_growth_rate=0.1,
    )
    
    # Create environment and simulation
    env = Environment(config.width, config.height)
    sim = Simulation(env, config.dict())
    
    # Initialize simulation with entities
    initialize_simulation_with_test_entities(sim, config)
    
    # Act - run for 100 steps
    sim.run(100)
    
    # Assert
    # Count each type of entity
    plants = sum(1 for e in env.entities.values() if e.has_component("plant"))
    herbivores = sum(1 for e in env.entities.values() if e.has_component("herbivore"))
    predators = sum(1 for e in env.entities.values() if e.has_component("predator"))
    
    # Check that we still have entities of each type
    # (Exact numbers will vary due to randomness, so we just check for existence)
    assert plants > 0, "Plants should still exist after 100 steps"
    assert herbivores > 0, "Herbivores should still exist after 100 steps"
    assert predators > 0, "Predators should still exist after 100 steps"
```

## Documentation Strategy

### Module Documentation

Every module must have a comprehensive docstring explaining:

1. Purpose and functionality
2. How it fits into the overall architecture
3. Key concepts and abstractions
4. Usage examples

### Function Documentation

Every function must have a docstring explaining:

1. What the function does
2. Parameters (with types and constraints)
3. Return values (with types)
4. Exceptions that may be raised
5. Usage examples
6. Implementation notes for complex algorithms

### Class Documentation

Every class must have a docstring explaining:

1. Purpose and behavior
2. Attributes (with types)
3. Class invariants
4. Relationships with other classes
5. Lifecycle (initialization, update, cleanup)
6. Usage examples

## Implementation Plan

### Phase 1: Core Simulation (Weeks 1-2)

1. Set up project structure and dependencies
2. Implement core simulation components with comprehensive tests
3. Create simple predator-prey ecosystem
4. Add basic visualization options

### Phase 2: API and Enhanced Visualization (Weeks 3-4)

1. Implement FastAPI endpoints with complete documentation and tests
2. Create basic web visualization
3. Enhance entity behaviors with comprehensive tests
4. Add data collection capabilities

### Phase 3: Advanced Features (Weeks 5-8)

1. Add species concept and simple genetics with property-based tests
2. Create more sophisticated behaviors with comprehensive tests
3. Enhance web visualization
4. Implement WebSocket support for real-time updates

### Phase 4: Evolution and Analysis (Weeks 9-12)

1. Implement evolutionary mechanisms with comprehensive tests
2. Add comprehensive analysis tools
3. Create visualization dashboards
4. Optimize performance for larger simulations

## Conclusion

This simplified technical specification provides a blueprint for implementing the VirtualLife project in a way that is tailored for AI development. The comprehensive testing requirements and detailed documentation standards are essential to ensure the correctness and reliability of the implementation.

By using dataclasses, Pydantic models, type annotations, and a focus on explicit error handling, the codebase becomes more maintainable, understandable, and robust. The phased approach allows for incremental development while maintaining a clear direction. 