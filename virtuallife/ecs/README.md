# VirtualLife Entity-Component-System (ECS)

The Entity-Component-System (ECS) architecture is the core of the VirtualLife simulation. It provides a flexible, modular approach to modeling entities and their behaviors in the simulation.

## Core Components

### Entity

An Entity is a unique identifier with optional collections of Components. Entities represent objects in the simulation such as creatures, plants, or resources.

### Component

Components are data containers that define the properties and capabilities of entities. Each Component represents a specific aspect of an entity (e.g., position, energy, movement capabilities).

### System

Systems contain the logic that operates on entities with specific components. Each System processes only entities that have the required components for that system.

### World

The World is a container that manages all entities, components, and systems. It coordinates the interaction between these elements and ensures proper state management.

## Usage Examples

### Creating Entities and Components

```python
from virtuallife.ecs import World, Entity
from virtuallife.ecs.component import Component

# Define a component
class PositionComponent:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        
    def update(self, entity, world, dt):
        # Components can define update logic called each simulation step
        pass

# Create a world
world = World()

# Create an entity with a position component
entity = Entity()
entity.add_component(PositionComponent(10, 20))

# Add the entity to the world
world.add_entity(entity)

# Retrieve components
if entity.has_component(PositionComponent):
    position = entity.get_component(PositionComponent)
    print(f"Entity position: ({position.x}, {position.y})")
```

### Creating and Using Systems

```python
from virtuallife.ecs import System, World, Entity
from typing import List, Type

# Define components
class PositionComponent:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        
    def update(self, entity, world, dt):
        pass
        
class MovementComponent:
    def __init__(self, speed: float):
        self.speed = speed
        self.direction_x = 0
        self.direction_y = 0
        
    def update(self, entity, world, dt):
        pass

# Define a system that processes movement
class MovementSystem(System):
    @property
    def required_components(self) -> List[Type]:
        return [PositionComponent, MovementComponent]
        
    def process(self, world: World, dt: float) -> None:
        for entity_id in self.entities:
            entity = world.get_entity(entity_id)
            position = entity.get_component(PositionComponent)
            movement = entity.get_component(MovementComponent)
            
            # Update position based on movement
            position.x += movement.direction_x * movement.speed * dt
            position.y += movement.direction_y * movement.speed * dt

# Create world and system
world = World()
movement_system = MovementSystem()
world.add_system(movement_system)

# Create entity with position and movement
entity = Entity()
entity.add_component(PositionComponent(0, 0))
entity.add_component(MovementComponent(1.0))
entity.get_component(MovementComponent).direction_x = 1  # Move right

world.add_entity(entity)

# Update the world (processes all systems)
world.update(0.1)  # dt = 0.1
```

### Managing Entity Lifecycle

```python
# Create and add entity
entity = Entity()
entity.add_component(PositionComponent(0, 0))
entity_id = world.add_entity(entity)

# Check if entity exists
if world.has_entity(entity_id):
    # Retrieve entity
    entity = world.get_entity(entity_id)
    
    # Remove a component
    if entity.has_component(MovementComponent):
        entity.remove_component(MovementComponent)
    
    # Remove the entity
    world.remove_entity(entity_id)
```

## Architecture Decisions

### Type-Based Component Access

Instead of using string identifiers for components, we use type-based access:

```python
# Instead of:
entity.add_component("position", position_component)
position = entity.get_component("position")

# We use:
entity.add_component(position_component)
position = entity.get_component(PositionComponent)
```

This approach provides several benefits:
- Type safety (compile-time checks)
- Better IDE auto-completion
- Reduced risk of typos in component names
- Clearer code through explicit type references

### System-Based Processing

Logic is organized into systems that process entities with specific component combinations:

1. Each system declares the component types it requires
2. Entities register with systems based on their component composition
3. When components are added/removed, entity registration with systems is updated
4. Systems process only relevant entities rather than filtering all entities

This approach:
- Improves performance by avoiding unnecessary checks
- Organizes logic by functionality rather than entity type
- Facilitates component-based design patterns

### Entity Component Ownership

Entities own their components, with the following characteristics:
- Components are instances, not shared between entities
- When an entity is removed, all its components are automatically removed
- Components can be added and removed dynamically during simulation

## Best Practices

1. **Keep components focused**: Each component should represent a single aspect of an entity.
2. **Component data, system logic**: Components should primarily store data, while systems implement behavior.
3. **Avoid direct component-to-component dependencies**: Components should be self-contained.
4. **Use composition over inheritance**: Build complex entities by combining simple components.
5. **Implement the Component protocol**: All components should implement the `Component` protocol's interface.
6. **Properly handle entity/component removal**: Clean up resources when entities or components are removed.
7. **Register systems before entities**: Add systems to the world before adding entities to ensure proper registration. 