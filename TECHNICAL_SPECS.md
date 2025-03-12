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

VirtualLife follows a simplified domain-driven architecture focused on the core simulation concepts. The system is organized into these main modules:

```
virtuallife/
├── simulation/                # Core simulation engine
│   ├── environment.py         # Environment implementation
│   ├── entity.py              # Entity system
│   ├── component.py           # Components for entities
│   └── runner.py              # Simulation runner
├── models/                    # Data models using Pydantic
│   ├── config.py              # Configuration schemas
│   ├── entity.py              # Entity schemas
│   └── state.py               # Simulation state models
├── visualize/                 # Visualization tools
│   ├── console.py             # Console output
│   ├── plotting.py            # Matplotlib visualization
│   └── web/                   # Web visualization (Phase 2+)
├── api/                       # API layer (Phase 2+)
│   └── routes.py              # API endpoints
├── tests/                     # Comprehensive test suite
│   ├── unit/                  # Unit tests for components
│   ├── integration/           # Integration tests
│   ├── functional/            # Functional tests
│   └── performance/           # Performance tests
├── docs/                      # Documentation
│   ├── user/                  # User documentation
│   ├── developer/             # Developer documentation
│   └── api/                   # API documentation
├── cli.py                     # Command-line interface
└── config/                    # Default configurations
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

### 1. Environment

A 2D grid-based environment where entities exist and interact.

```python
from dataclasses import dataclass, field
from typing import Dict, Set, Tuple, Optional, List, UUID
import numpy as np

@dataclass
class Environment:
    """A 2D grid environment for the simulation.
    
    The Environment class represents the world where entities exist and interact.
    It manages entity positions, resources, and defines the boundaries of the
    simulation space.
    
    Attributes:
        width: Width of the environment grid
        height: Height of the environment grid
        boundary_condition: How boundaries are handled ("wrapped", "bounded", or "infinite")
        entities: Dictionary mapping entity IDs to entities
        entity_positions: Dictionary mapping positions to sets of entity IDs
        resources: Dictionary mapping resource types to numpy arrays
        
    Examples:
        >>> env = Environment(50, 50)
        >>> env.width
        50
    """
    width: int
    height: int
    boundary_condition: str = "wrapped"
    entities: Dict[UUID, "Entity"] = field(default_factory=dict)
    entity_positions: Dict[Tuple[int, int], Set[UUID]] = field(default_factory=lambda: {})
    resources: Dict[str, np.ndarray] = field(default_factory=dict)
    
    def add_entity(self, entity: "Entity") -> None:
        """Add an entity to the environment.
        
        Args:
            entity: The entity to add
            
        Raises:
            ValueError: If the entity is already in the environment
            
        Examples:
            >>> env = Environment(50, 50)
            >>> entity = Entity()
            >>> env.add_entity(entity)
            >>> entity.id in env.entities
            True
        """
        self.entities[entity.id] = entity
        pos = entity.position
        if pos not in self.entity_positions:
            self.entity_positions[pos] = set()
        self.entity_positions[pos].add(entity.id)
    
    def remove_entity(self, entity_id: UUID) -> None:
        """Remove an entity from the environment.
        
        Args:
            entity_id: The ID of the entity to remove
            
        Examples:
            >>> env = Environment(50, 50)
            >>> entity = Entity()
            >>> env.add_entity(entity)
            >>> env.remove_entity(entity.id)
            >>> entity.id in env.entities
            False
        """
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            pos = entity.position
            if pos in self.entity_positions and entity_id in self.entity_positions[pos]:
                self.entity_positions[pos].remove(entity_id)
                if not self.entity_positions[pos]:
                    del self.entity_positions[pos]
            del self.entities[entity_id]
    
    def get_entities_at(self, position: Tuple[int, int]) -> List["Entity"]:
        """Get all entities at a specific position.
        
        Args:
            position: The (x, y) position to check
            
        Returns:
            A list of entities at the specified position
            
        Examples:
            >>> env = Environment(50, 50)
            >>> entity = Entity(position=(10, 10))
            >>> env.add_entity(entity)
            >>> entities = env.get_entities_at((10, 10))
            >>> len(entities)
            1
        """
        if position in self.entity_positions:
            return [self.entities[entity_id] for entity_id in self.entity_positions[position]]
        return []
    
    def get_neighborhood(self, position: Tuple[int, int], radius: int = 1) -> Dict[Tuple[int, int], List["Entity"]]:
        """Get a view of the environment around a position.
        
        Args:
            position: The center (x, y) position
            radius: The radius of the neighborhood
            
        Returns:
            A dictionary mapping positions to lists of entities
            
        Examples:
            >>> env = Environment(50, 50)
            >>> entity = Entity(position=(10, 10))
            >>> env.add_entity(entity)
            >>> neighborhood = env.get_neighborhood((10, 10), 1)
            >>> (10, 10) in neighborhood
            True
        """
        x, y = position
        neighborhood = {}
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                pos = self.normalize_position((x + dx, y + dy))
                if pos in self.entity_positions:
                    neighborhood[pos] = [self.entities[entity_id] for entity_id in self.entity_positions[pos]]
        
        return neighborhood
    
    def normalize_position(self, position: Tuple[int, int]) -> Tuple[int, int]:
        """Normalize a position based on boundary conditions.
        
        Args:
            position: The (x, y) position to normalize
            
        Returns:
            The normalized (x, y) position
            
        Examples:
            >>> env = Environment(50, 50, "wrapped")
            >>> env.normalize_position((60, 60))
            (10, 10)
        """
        x, y = position
        
        match self.boundary_condition:
            case "wrapped":
                return (x % self.width, y % self.height)
            case "bounded":
                return (max(0, min(x, self.width - 1)), max(0, min(y, self.height - 1)))
            case "infinite":
                return position
            case _:
                return (x % self.width, y % self.height)  # Default to wrapped
```

### 2. Entity Component System

A simplified entity component system using composition rather than inheritance.

```python
from dataclasses import dataclass, field
from typing import Dict, Protocol, Tuple, UUID, Any, Optional, TypeVar, cast
from uuid import uuid4

# Define a Protocol for components
class Component(Protocol):
    """Protocol defining the interface for entity components.
    
    All components must implement this protocol to be usable with the Entity class.
    The update method is called on each simulation step.
    """
    def update(self, entity: "Entity", environment: "Environment") -> None:
        """Update the component state.
        
        Args:
            entity: The entity this component belongs to
            environment: The environment the entity exists in
        """
        ...

# Define a type variable for components
C = TypeVar('C', bound=Component)

@dataclass
class Entity:
    """Base entity class using composition for behaviors.
    
    Entities are the primary objects in the simulation. They exist in the environment
    and can have various components that define their behavior.
    
    Attributes:
        id: Unique identifier for the entity
        position: The (x, y) position of the entity in the environment
        components: Dictionary mapping component names to components
        
    Examples:
        >>> entity = Entity(position=(10, 20))
        >>> entity.position
        (10, 20)
    """
    id: UUID = field(default_factory=uuid4)
    position: Tuple[int, int] = (0, 0)
    components: Dict[str, Component] = field(default_factory=dict)
    
    def add_component(self, name: str, component: Component) -> None:
        """Add a component to the entity.
        
        Args:
            name: The name of the component
            component: The component to add
            
        Raises:
            ValueError: If a component with the same name already exists
            
        Examples:
            >>> from dataclasses import dataclass
            >>> @dataclass
            ... class TestComponent:
            ...     def update(self, entity, environment): pass
            >>> entity = Entity()
            >>> component = TestComponent()
            >>> entity.add_component("test", component)
            >>> entity.has_component("test")
            True
        """
        if name in self.components:
            raise ValueError(f"Component {name} already exists on this entity")
        self.components[name] = component
    
    def has_component(self, name: str) -> bool:
        """Check if the entity has a specific component.
        
        Args:
            name: The name of the component
            
        Returns:
            True if the entity has the component, False otherwise
            
        Examples:
            >>> entity = Entity()
            >>> entity.has_component("nonexistent")
            False
        """
        return name in self.components
    
    def get_component(self, name: str) -> Optional[Component]:
        """Get a component by name.
        
        Args:
            name: The name of the component
            
        Returns:
            The component if it exists, None otherwise
            
        Examples:
            >>> from dataclasses import dataclass
            >>> @dataclass
            ... class TestComponent:
            ...     value: int = 42
            ...     def update(self, entity, environment): pass
            >>> entity = Entity()
            >>> component = TestComponent()
            >>> entity.add_component("test", component)
            >>> entity.get_component("test").value
            42
        """
        return self.components.get(name)
    
    def get_component_typed(self, name: str, component_type: type[C]) -> Optional[C]:
        """Get a component by name with the correct type.
        
        Args:
            name: The name of the component
            component_type: The expected type of the component
            
        Returns:
            The component cast to the specified type if it exists, None otherwise
            
        Examples:
            >>> from dataclasses import dataclass
            >>> @dataclass
            ... class TestComponent:
            ...     value: int = 42
            ...     def update(self, entity, environment): pass
            >>> entity = Entity()
            >>> component = TestComponent()
            >>> entity.add_component("test", component)
            >>> comp = entity.get_component_typed("test", TestComponent)
            >>> comp.value
            42
        """
        component = self.get_component(name)
        if component is not None:
            return cast(component_type, component)
        return None
    
    def update(self, environment: "Environment") -> None:
        """Update the entity state by updating all components.
        
        Args:
            environment: The environment the entity exists in
            
        Examples:
            >>> from dataclasses import dataclass
            >>> @dataclass
            ... class CounterComponent:
            ...     count: int = 0
            ...     def update(self, entity, environment): 
            ...         self.count += 1
            >>> entity = Entity()
            >>> component = CounterComponent()
            >>> entity.add_component("counter", component)
            >>> entity.update(None)  # Environment is None for this example
            >>> entity.get_component_typed("counter", CounterComponent).count
            1
        """
        for component in self.components.values():
            component.update(self, environment)
```

### 3. Standard Components

A set of basic components for common entity behaviors, with comprehensive documentation and built-in tests.

```python
from dataclasses import dataclass
from typing import Tuple, Optional, List, cast
import random

@dataclass
class EnergyComponent:
    """Component handling entity energy.
    
    This component manages an entity's energy level, which decreases over time.
    If energy reaches zero, the entity is removed from the environment.
    
    Attributes:
        energy: Current energy level
        decay_rate: Rate at which energy decreases per step
        
    Examples:
        >>> component = EnergyComponent(energy=100.0, decay_rate=0.5)
        >>> component.energy
        100.0
    """
    energy: float = 100.0
    decay_rate: float = 0.1
    
    def update(self, entity: "Entity", environment: "Environment") -> None:
        """Update the entity's energy.
        
        Args:
            entity: The entity this component belongs to
            environment: The environment
            
        Examples:
            >>> from unittest.mock import MagicMock
            >>> entity = MagicMock()
            >>> environment = MagicMock()
            >>> component = EnergyComponent(energy=1.0, decay_rate=0.5)
            >>> component.update(entity, environment)
            >>> component.energy
            0.5
        """
        self.energy -= self.decay_rate
        if self.energy <= 0:
            environment.remove_entity(entity.id)

@dataclass
class MovementComponent:
    """Component for entity movement.
    
    This component allows an entity to move around the environment.
    Movement consumes energy if the entity has an EnergyComponent.
    
    Attributes:
        speed: Movement speed
        movement_cost: Energy cost per unit of movement
        
    Examples:
        >>> component = MovementComponent(speed=2.0, movement_cost=0.2)
        >>> component.speed
        2.0
    """
    speed: float = 1.0
    movement_cost: float = 0.1
    
    def update(self, entity: "Entity", environment: "Environment") -> None:
        """Move the entity.
        
        Args:
            entity: The entity this component belongs to
            environment: The environment
            
        Note:
            This implementation uses simple random movement.
            The entity will not move if it does not have enough energy.
            
        Examples:
            >>> # This example cannot be easily tested in a doctest
            >>> # See unit tests for complete testing
        """
        if not entity.has_component("energy"):
            return
            
        energy_component = entity.get_component("energy")
        assert energy_component is not None  # For type checking
        if energy_component.energy <= 0:
            return
            
        # Simple random movement
        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])
        
        # Calculate new position and cost
        x, y = entity.position
        new_pos = environment.normalize_position((x + dx, y + dy))
        
        # Update position and energy
        energy_component.energy -= self.movement_cost * self.speed
        
        # Update position in environment
        if entity.position in environment.entity_positions:
            environment.entity_positions[entity.position].remove(entity.id)
            if not environment.entity_positions[entity.position]:
                del environment.entity_positions[entity.position]
                
        entity.position = new_pos
        
        if new_pos not in environment.entity_positions:
            environment.entity_positions[new_pos] = set()
        environment.entity_positions[new_pos].add(entity.id)
```

### 4. Simulation Runner

Controls the simulation state and execution flow. Full documentation and extensive error checking.

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, TypeVar, Generic, cast
import time
from uuid import UUID

# Type for simulation event handlers
T = TypeVar('T')
EventHandler = Callable[["Simulation", T], None]

@dataclass
class Simulation:
    """Controls the simulation execution.
    
    The Simulation class manages the execution of the simulation, including
    advancing the simulation state, managing entities, and notifying listeners
    of events.
    
    Attributes:
        environment: The environment for the simulation
        config: Configuration parameters
        current_step: The current simulation step
        running: Whether the simulation is currently running
        last_update_time: Timestamp of the last update
        listeners: Dictionary mapping event types to lists of callback functions
        
    Examples:
        >>> from unittest.mock import MagicMock
        >>> env = MagicMock()
        >>> sim = Simulation(environment=env)
        >>> sim.current_step
        0
    """
    environment: "Environment"
    config: Dict[str, Any] = field(default_factory=dict)
    current_step: int = 0
    running: bool = False
    last_update_time: float = field(default_factory=time.time)
    listeners: Dict[str, List[Callable]] = field(default_factory=lambda: {
        "step_start": [],
        "step_end": [],
        "entity_added": [],
        "entity_removed": []
    })
    
    def add_listener(self, event_type: str, callback: Callable) -> None:
        """Add a listener for a specific event type.
        
        Args:
            event_type: The type of event to listen for
            callback: The function to call when the event occurs
            
        Raises:
            ValueError: If the event type is not supported
            
        Examples:
            >>> from unittest.mock import MagicMock
            >>> env = MagicMock()
            >>> sim = Simulation(environment=env)
            >>> callback = lambda sim, **kwargs: None
            >>> sim.add_listener("step_start", callback)
            >>> len(sim.listeners["step_start"])
            1
        """
        if event_type not in self.listeners:
            raise ValueError(f"Unsupported event type: {event_type}")
            
        self.listeners[event_type].append(callback)
    
    def notify_listeners(self, event_type: str, **kwargs) -> None:
        """Notify all listeners of an event.
        
        Args:
            event_type: The type of event that occurred
            **kwargs: Additional data to pass to the listeners
            
        Examples:
            >>> from unittest.mock import MagicMock
            >>> env = MagicMock()
            >>> sim = Simulation(environment=env)
            >>> data = {"called": False}
            >>> def callback(sim, **kwargs):
            ...     data["called"] = True
            >>> sim.add_listener("step_start", callback)
            >>> sim.notify_listeners("step_start")
            >>> data["called"]
            True
        """
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                callback(self, **kwargs)
    
    def step(self) -> None:
        """Execute a single simulation step.
        
        This advances the simulation by one step, updating all entities
        and notifying listeners of the step start and end events.
        
        Examples:
            >>> from unittest.mock import MagicMock
            >>> env = MagicMock()
            >>> env.entities = {}
            >>> sim = Simulation(environment=env)
            >>> sim.step()
            >>> sim.current_step
            1
        """
        self.current_step += 1
        self.notify_listeners("step_start")
        
        # Update all entities (make a copy to handle removals during iteration)
        entities = list(self.environment.entities.values())
        for entity in entities:
            entity.update(self.environment)
        
        self.notify_listeners("step_end")
    
    def run(self, steps: Optional[int] = None) -> None:
        """Run the simulation for a number of steps or indefinitely.
        
        Args:
            steps: Number of steps to run, or None to run indefinitely
            
        Examples:
            >>> from unittest.mock import MagicMock
            >>> env = MagicMock()
            >>> env.entities = {}
            >>> sim = Simulation(environment=env)
            >>> # Run for 5 steps
            >>> sim.run(5)
            >>> sim.current_step
            5
        """
        self.running = True
        step_count = 0
        
        try:
            while self.running and (steps is None or step_count < steps):
                self.step()
                step_count += 1
                
                # Optional sleep for real-time visualization
                if "step_delay" in self.config:
                    time.sleep(self.config["step_delay"])
        finally:
            self.running = False
    
    def stop(self) -> None:
        """Stop the simulation.
        
        Examples:
            >>> from unittest.mock import MagicMock
            >>> env = MagicMock()
            >>> sim = Simulation(environment=env)
            >>> sim.running = True
            >>> sim.stop()
            >>> sim.running
            False
        """
        self.running = False
```

### 5. Configuration System

A Pydantic-based configuration system to validate inputs and provide defaults. Full type checking and validation.

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Literal

class SimulationConfig(BaseModel):
    """Configuration for a simulation.
    
    This class defines the configuration parameters for a simulation,
    with validation and default values.
    
    Attributes:
        width: Width of the environment grid
        height: Height of the environment grid
        boundary_condition: How boundaries are handled
        step_delay: Delay between steps for visualization
        random_seed: Random seed for reproducibility
        initial_plants: Initial number of plants
        initial_herbivores: Initial number of herbivores
        initial_predators: Initial number of predators
        plant_growth_rate: Rate at which plants grow
        plant_max_energy: Maximum energy for plants
        herbivore_initial_energy: Initial energy for herbivores
        herbivore_speed: Movement speed for herbivores
        herbivore_energy_decay: Energy decay rate for herbivores
        predator_initial_energy: Initial energy for predators
        predator_speed: Movement speed for predators
        predator_energy_decay: Energy decay rate for predators
        
    Examples:
        >>> config = SimulationConfig(width=100, height=100)
        >>> config.width
        100
        >>> config.boundary_condition
        'wrapped'
    """
    width: int = Field(50, ge=1, description="Width of the environment grid")
    height: int = Field(50, ge=1, description="Height of the environment grid")
    boundary_condition: Literal["wrapped", "bounded", "infinite"] = "wrapped"
    step_delay: Optional[float] = Field(None, ge=0, description="Delay between steps for visualization")
    random_seed: Optional[int] = None
    
    # Entity initialization
    initial_plants: int = Field(100, ge=0)
    initial_herbivores: int = Field(20, ge=0)
    initial_predators: int = Field(5, ge=0)
    
    # Plant parameters
    plant_growth_rate: float = Field(0.1, ge=0)
    plant_max_energy: float = Field(100.0, ge=0)
    
    # Herbivore parameters
    herbivore_initial_energy: float = Field(100.0, ge=0)
    herbivore_speed: float = Field(1.0, ge=0)
    herbivore_energy_decay: float = Field(0.1, ge=0)
    
    # Predator parameters
    predator_initial_energy: float = Field(150.0, ge=0)
    predator_speed: float = Field(1.5, ge=0)
    predator_energy_decay: float = Field(0.2, ge=0)
    
    @validator("width", "height")
    def ensure_reasonable_dimensions(cls, v, field):
        """Ensure grid dimensions are reasonable for performance.
        
        Args:
            v: The value to validate
            field: The field being validated
            
        Returns:
            The validated value
            
        Raises:
            ValueError: If dimensions are too large
        """
        if v > 1000:
            raise ValueError(f"{field.name} should be less than 1000 for performance reasons")
        return v
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