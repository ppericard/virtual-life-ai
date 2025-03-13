# Type System

## Overview

The VirtualLife simulation uses a comprehensive type system to enhance code readability, maintainability, and reliability. By leveraging Python's type annotations and the `typing` module, we've created domain-specific types and protocols that document the expected structure and behavior of objects throughout the codebase.

This document explains the type system design, its key components, and how to use them effectively.

## Core Types

The type system defines several core types used throughout the application:

### Position

```python
Position = Tuple[int, int]
```

Represents a 2D position in the grid as a tuple of (x, y) coordinates. This type is used extensively for entity positions, resource locations, and spatial calculations.

### EntityId

```python
EntityId = NewType('EntityId', int)
```

A unique identifier for entities in the simulation. Using `NewType` allows the type checker to distinguish EntityId from regular integers, preventing accidental mixing.

### Generic Type Variables

```python
T = TypeVar('T')
C = TypeVar('C', bound='Component')
```

Generic type variables are used for flexibility in type annotations:
- `T` is a general-purpose type variable
- `C` is a type variable bound to Component types

## Protocol Definitions

The type system uses Protocol classes (from typing_extensions in Python <3.8) to define interfaces:

### Identifiable

```python
class Identifiable(Protocol):
    """Protocol for objects that have a unique identifier."""
    
    @property
    def id(self) -> EntityId:
        """Get the unique identifier for this object."""
        ...
```

The Identifiable protocol defines the interface for any object that has a unique identifier, such as entities and systems.

### Positionable

```python
class Positionable(Protocol):
    """Protocol for objects that have a position in 2D space."""
    
    @property
    def position(self) -> Position:
        """Get the position of this object."""
        ...
        
    @position.setter
    def position(self, value: Position) -> None:
        """Set the position of this object."""
        ...
```

The Positionable protocol defines the interface for any object that has a position in the 2D grid, such as entities.

## Design Decisions

### Domain-Specific Types

**Decision**: Create domain-specific types using type aliases and NewType

**Rationale**:
- Improves code readability by making the meaning of values clear
- Enables better static analysis by the type checker
- Documents the purpose of values in the code
- Prevents accidental misuse of related but distinct types

**Implementation**:
```python
# Instead of:
def add_entity(entity_id: int, position: Tuple[int, int]) -> None:
    ...

# We use:
from virtuallife.types import EntityId, Position

def add_entity(entity_id: EntityId, position: Position) -> None:
    ...
```

### Protocol-Based Interfaces

**Decision**: Use Protocol classes for interface definitions instead of abstract base classes

**Rationale**:
- Enables structural typing rather than nominal typing
- Makes it easier to adapt existing classes to conform to interfaces
- Reduces coupling between interface definitions and implementations
- Better matches Python's "duck typing" philosophy

**Implementation**:
```python
# Define the interface
from typing import Protocol

class Movable(Protocol):
    def move(self, dx: int, dy: int) -> None:
        ...

# Use the interface
def process_movement(entity: Movable) -> None:
    entity.move(1, 0)  # Move right
```

### Type Exports in __init__.py

**Decision**: Re-export all types through the package's `__init__.py`

**Rationale**:
- Provides a clean, consistent import interface
- Hides implementation details
- Makes imports shorter and more readable
- Makes it easier to refactor type definitions

**Implementation**:
```python
# In virtuallife/types/__init__.py
from virtuallife.types.core import (
    Position,
    EntityId,
    Identifiable,
    Positionable,
)

__all__ = [
    'Position',
    'EntityId',
    'Identifiable',
    'Positionable',
]

# In user code
from virtuallife.types import Position, EntityId
```

### Event Type Organization

**Decision**: Separate event type constants from core types

**Rationale**:
- Keeps the core type definitions focused on structural types
- Allows event types to evolve independently
- Groups related constants together
- Provides a clear, centralized location for event type definitions

**Implementation**:
```python
# In virtuallife/events/types.py
class EntityEvents:
    """Constants for entity-related events."""
    
    CREATED: Final[str] = "entity:created"
    DESTROYED: Final[str] = "entity:destroyed"
    # ...

# In user code
from virtuallife.events.types import EntityEvents

dispatcher.subscribe(EntityEvents.CREATED, on_entity_created)
```

## Usage Examples

### Basic Type Annotations

```python
from virtuallife.types import Position, EntityId

def get_entities_at_position(position: Position) -> List[EntityId]:
    """Get all entities at the specified position.
    
    Args:
        position: The (x, y) position to check
        
    Returns:
        A list of entity IDs at the position
    """
    # Implementation
    ...
```

### Using Protocols for Dependency Injection

```python
from typing import List, Protocol
from virtuallife.types import Position

class SpatialIndex(Protocol):
    """Protocol for spatial index implementations."""
    
    def add_entity(self, entity_id: int, position: Position) -> None:
        """Add an entity to the spatial index."""
        ...
        
    def remove_entity(self, entity_id: int, position: Position) -> None:
        """Remove an entity from the spatial index."""
        ...
        
    def get_entities_in_radius(self, center: Position, radius: int) -> List[int]:
        """Get all entities within the specified radius."""
        ...

# Class that depends on any SpatialIndex implementation
class MovementSystem:
    def __init__(self, spatial_index: SpatialIndex):
        self.spatial_index = spatial_index
        
    def move_entity(self, entity_id: int, from_pos: Position, to_pos: Position) -> None:
        """Move an entity from one position to another."""
        self.spatial_index.remove_entity(entity_id, from_pos)
        self.spatial_index.add_entity(entity_id, to_pos)
```

### Generic Component Functions

```python
from typing import TypeVar, Type, Optional
from virtuallife.ecs import Entity, Component

C = TypeVar('C', bound=Component)

def get_component_or_create(entity: Entity, component_type: Type[C], **kwargs) -> C:
    """Get a component from an entity or create it if it doesn't exist.
    
    Args:
        entity: The entity to get the component from
        component_type: The type of component to get or create
        **kwargs: Arguments to pass to the component constructor if created
        
    Returns:
        The existing or newly created component
    """
    if entity.has_component(component_type):
        return entity.get_component(component_type)
    else:
        component = component_type(**kwargs)
        entity.add_component(component)
        return component
```

### Type-Safe Event Subscriptions

```python
from typing import Protocol, Any, Callable, TypeVar

T = TypeVar('T')

class EventSource(Protocol[T]):
    """Protocol for objects that can be event sources."""
    pass

# Type for event callbacks
EventCallback = Callable[[EventSource, Any], None]

def subscribe_to_entity_events(
    dispatcher: EventDispatcher,
    entity_id: EntityId,
    callback: EventCallback
) -> None:
    """Subscribe to all events for a specific entity.
    
    Args:
        dispatcher: The event dispatcher
        entity_id: The ID of the entity to monitor
        callback: The callback to invoke for events
    """
    dispatcher.subscribe(EntityEvents.COMPONENT_ADDED, callback, 
                         filter_func=lambda sender, **kwargs: kwargs.get('entity_id') == entity_id)
    dispatcher.subscribe(EntityEvents.COMPONENT_REMOVED, callback,
                         filter_func=lambda sender, **kwargs: kwargs.get('entity_id') == entity_id)
    dispatcher.subscribe(EntityEvents.POSITION_CHANGED, callback,
                         filter_func=lambda sender, **kwargs: kwargs.get('entity_id') == entity_id)
```

## Working with Types

### Type Checking

The codebase is designed to be fully type-checked with tools like mypy. Here's how to run the type checker:

```bash
# Check the entire codebase
mypy virtuallife

# Check a specific module
mypy virtuallife/types
```

### Adding New Types

When adding new types to the system:

1. Place domain-specific types in the appropriate module
2. For general types, add them to `virtuallife/types/core.py`
3. For event types, add them to `virtuallife/events/types.py`
4. Export the new types through the package's `__init__.py`
5. Add type documentation with examples

Example:
```python
# In virtuallife/types/core.py
Direction = Literal['north', 'east', 'south', 'west']
"""Cardinal direction in the grid."""

# In virtuallife/types/__init__.py
from virtuallife.types.core import (
    Position,
    EntityId,
    Identifiable,
    Positionable,
    Direction,  # Add the new type
)

__all__ = [
    'Position',
    'EntityId',
    'Identifiable',
    'Positionable',
    'Direction',  # Add the new type
]
```

### Adding New Protocols

When adding new protocols:

1. Define the protocol in the appropriate module
2. Document all required methods and properties
3. Include examples of how to implement the protocol
4. Export the protocol through the package's `__init__.py`

Example:
```python
# In virtuallife/types/core.py
class Movable(Protocol):
    """Protocol for objects that can move in the grid.
    
    Examples:
        >>> class MovableEntity:
        ...     def __init__(self, position: Position):
        ...         self.position = position
        ...     def move(self, dx: int, dy: int) -> None:
        ...         self.position = (self.position[0] + dx, self.position[1] + dy)
        >>> entity = MovableEntity((0, 0))
        >>> entity.move(1, 2)
        >>> entity.position
        (1, 2)
    """
    
    @property
    def position(self) -> Position:
        """Get the current position."""
        ...
        
    def move(self, dx: int, dy: int) -> None:
        """Move by the specified delta.
        
        Args:
            dx: Change in x coordinate
            dy: Change in y coordinate
        """
        ...
```

## Relation to the Event System

The type system and the event system work together:

### Event Type Constants

The event system defines event type constants in `virtuallife/events/types.py`:

```python
class EntityEvents:
    """Constants for entity-related events."""
    
    # Entity lifecycle events
    CREATED: Final[str] = "entity:created"
    DESTROYED: Final[str] = "entity:destroyed"
    
    # Entity component events
    COMPONENT_ADDED: Final[str] = "entity:component_added"
    COMPONENT_REMOVED: Final[str] = "entity:component_removed"
    COMPONENT_UPDATED: Final[str] = "entity:component_updated"
    
    # Entity position events
    POSITION_CHANGED: Final[str] = "entity:position_changed"
```

These constants are separate from the core type definitions because they serve a different purpose. While the core types define structural interfaces, the event types define string constants used by the event system.

### Event Callback Types

The event system uses the core type system for callback signatures:

```python
from typing import TypeVar, Callable, Any

T = TypeVar('T')
EventCallback = Callable[[T, Any], None]

def subscribe(self, event_type: str, callback: EventCallback[T]) -> None:
    """Subscribe to an event type."""
    self.subscribers[event_type].append(callback)
```

## Type Safety Best Practices

To maximize the benefits of the type system:

1. **Always Use Type Annotations**
   - Add type annotations to all function parameters and return values
   - Annotate instance variables in `__init__` methods
   - Use appropriate container types (List, Dict, Set, etc.)

2. **Leverage Type Narrowing**
   - Use type guards to narrow types
   - Check for specific types or attributes when necessary
   - Use conditional statements to handle different types

   ```python
   def process_entity(entity: Entity) -> None:
       if entity.has_component(MovementComponent):
           movement = entity.get_component(MovementComponent)
           # Now the type checker knows movement is a MovementComponent
   ```

3. **Use Protocols for Interface Definition**
   - Define interfaces using Protocol classes
   - Use structural typing instead of inheritance when appropriate
   - Focus on behavior rather than implementation details

4. **Make Use of Generic Types**
   - Use TypeVar to create flexible, reusable functions
   - Constrain type variables when needed
   - Use Generic classes for containers

   ```python
   T = TypeVar('T', bound=Component)
   
   def find_components(components: List[Component], component_type: Type[T]) -> List[T]:
       """Find all components of the specified type."""
       return [c for c in components if isinstance(c, component_type)]
   ```

5. **Document Type Usage**
   - Include examples of type usage in docstrings
   - Document complex type constraints
   - Explain why specific types were chosen

## Conclusion

The type system in VirtualLife provides a solid foundation for reliable, maintainable code. By defining domain-specific types and protocols, we've made the code more readable, easier to understand, and less prone to errors. The type system also serves as living documentation, expressing the expected structure and behavior of objects throughout the codebase.

As the project evolves, we'll continue to refine and expand the type system to better capture the domain concepts and ensure code reliability. 