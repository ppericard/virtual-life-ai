# Entity-Component-System (ECS) Architecture

## Overview

The Entity-Component-System (ECS) architecture is a pattern used for organizing game and simulation objects. It's particularly suited for the VirtualLife simulation because it allows for flexible entity composition, efficient processing, and clear separation of concerns.

This document explains the ECS architecture implementation in VirtualLife, including key design decisions, component interactions, and usage examples.

## Core Concepts

### Entity

An entity represents a single simulation object (like a creature, plant, or resource). In our implementation:

- Entities are essentially containers for components
- Each entity has a unique ID and a position
- Entities don't contain behavior logic

### Component

Components are data containers that define what properties an entity has:

- Each component represents a specific aspect or capability
- Components contain data but no behavior logic
- Components are reusable across different types of entities

### System

Systems contain the behavior logic that processes entities with specific components:

- Each system processes entities with a particular set of components
- Systems are specialized for specific simulation aspects (movement, energy, reproduction)
- Systems can efficiently batch-process similar entities

### World

The World is a container that manages entities and systems:

- It coordinates the processing of systems
- It tracks entity creation, modification, and destruction
- It manages the relationships between entities and systems

## Design Decisions

### Type-Based Component Registry

**Decision**: Use types rather than string identifiers for component registration

**Rationale**:
- Provides compile-time safety
- Enables better IDE support with autocompletion
- Eliminates string typos
- Simplifies component retrieval with direct type association

**Implementation**:
```python
# Instead of:
entity.add_component("energy", EnergyComponent())
energy = entity.get_component("energy")

# We use:
entity.add_component(EnergyComponent())
energy = entity.get_component(EnergyComponent)
```

### System-Based Processing

**Decision**: Process entities in batches by system rather than updating each entity individually

**Rationale**:
- Significantly improves performance with many entities
- Enables better data locality and cache optimization
- Allows for easier parallelization in the future
- Simplifies complex interactions between entities

**Implementation**:
```python
# Each system processes only relevant entities
class MovementSystem(System):
    def process(self, world: World, dt: float) -> None:
        # Process all entities with movement and position components
        for entity in self.entities:
            # Update entity position based on movement parameters
            pass
```

### Event-Driven Architecture

**Decision**: Use an event system for communication between components

**Rationale**:
- Reduces coupling between systems
- Makes it easier to add new features without modifying existing code
- Enables monitoring and debugging
- Allows for extensible event handling

**Implementation**:
```python
# System publishes events when entities move
dispatcher.publish(EntityEvents.POSITION_CHANGED, 
                  self, entity_id=entity.id, 
                  old_position=old_pos, new_position=new_pos)

# Other systems subscribe to those events
dispatcher.subscribe(EntityEvents.POSITION_CHANGED, self.on_entity_moved)
```

### Component Composition Over Inheritance

**Decision**: Use component composition for entity behaviors rather than class inheritance

**Rationale**:
- Avoids complex inheritance hierarchies
- Makes it easy to add/remove capabilities from entities
- Enables more flexible entity configurations
- Simplifies testing as components can be tested in isolation

**Implementation**:
```python
# Create a predator by composing components
predator = Entity(position=(10, 10))
predator.add_component(EnergyComponent(energy=100.0, max_energy=150.0))
predator.add_component(MovementComponent(speed=2.0))
predator.add_component(VisionComponent(range=5))
predator.add_component(PredatorBehaviorComponent())
```

## Component Interactions

### Component Dependencies

Components can depend on each other's data:

1. **Explicit Dependencies**:
   - Some components require others to function
   - These dependencies are enforced in systems

   ```python
   # MovementSystem requires both movement and position components
   def can_process(self, entity: Entity) -> bool:
       return entity.has_component(MovementComponent) and entity.has_component(PositionComponent)
   ```

2. **Implicit Dependencies**:
   - Components may work better with others but don't strictly require them
   - Enhanced functionality when certain combinations exist

   ```python
   # EnergySystem checks for optional metabolism component
   if entity.has_component(MetabolismComponent):
       metabolism = entity.get_component(MetabolismComponent)
       # Apply metabolism effects to energy consumption
   ```

### System Processing Order

The order in which systems process entities can impact simulation results:

- Systems are processed in the order they are registered with the world
- Critical systems (like lifecycle) may need to run before or after others
- Some systems may have dependencies on the results of other systems

```python
# Register systems in a specific order
world.register_system(ResourceSystem())     # First: Update resources
world.register_system(SensorySystem())      # Second: Update what entities can sense
world.register_system(BehaviorSystem())     # Third: Decide what to do
world.register_system(MovementSystem())     # Fourth: Move entities
world.register_system(ConsumptionSystem())  # Fifth: Consume resources at new positions
world.register_system(LifecycleSystem())    # Sixth: Handle births/deaths
```

## Usage Examples

### Creating the Basic ECS Architecture

```python
from virtuallife.ecs import Entity, World
from virtuallife.ecs.system import System
from virtuallife.components import EnergyComponent, MovementComponent
from virtuallife.systems import MovementSystem, EnergySystem

# Create a world to manage entities and systems
world = World()

# Register systems with the world
world.register_system(MovementSystem())
world.register_system(EnergySystem())

# Create entities with components
entity1 = Entity(position=(10, 10))
entity1.add_component(EnergyComponent(energy=100.0))
entity1.add_component(MovementComponent(speed=1.0))

entity2 = Entity(position=(20, 20))
entity2.add_component(EnergyComponent(energy=50.0))

# Add entities to the world
world.add_entity(entity1)
world.add_entity(entity2)

# Update the world (process all systems)
world.update(dt=1.0)
```

### Extending the Architecture with New Components and Systems

```python
from virtuallife.ecs import Component, System

# Define a new component
class ReproductionComponent(Component):
    def __init__(self, reproduction_rate: float = 0.01):
        self.reproduction_rate = reproduction_rate
        self.reproduction_cooldown = 0

# Define a new system to use the component
class ReproductionSystem(System):
    def __init__(self):
        super().__init__()
        # Set which components this system requires
        self.required_components = [EnergyComponent, ReproductionComponent]
    
    def process(self, world: World, dt: float) -> None:
        for entity_id in self.entities:
            entity = world.get_entity(entity_id)
            energy = entity.get_component(EnergyComponent)
            reproduction = entity.get_component(ReproductionComponent)
            
            # Update reproduction cooldown
            if reproduction.reproduction_cooldown > 0:
                reproduction.reproduction_cooldown -= dt
            
            # Check if entity can reproduce
            if reproduction.reproduction_cooldown <= 0 and energy.energy > energy.max_energy * 0.7:
                # Create new entity
                child = Entity(position=entity.position)
                child.add_component(EnergyComponent(energy=energy.max_energy * 0.3))
                child.add_component(ReproductionComponent(reproduction_rate=reproduction.reproduction_rate))
                
                # Consume energy for reproduction
                energy.energy -= energy.max_energy * 0.3
                
                # Set cooldown
                reproduction.reproduction_cooldown = 1.0 / reproduction.reproduction_rate
                
                # Add child to world
                world.add_entity(child)
```

## Performance Considerations

The ECS architecture is designed for performance with large numbers of entities:

1. **Component Storage**:
   - Components of the same type are stored together for better memory locality
   - Component data is optimized for cache efficiency

2. **System Filtering**:
   - Systems only process entities with relevant components
   - Entity filtering is optimized to avoid unnecessary checks

3. **Batch Processing**:
   - Similar operations are processed together
   - Allows for potential parallelization in future versions

4. **Memory Management**:
   - Entity and component creation/destruction is optimized
   - Recycling of entity IDs and component storage

## Extending the Architecture

The ECS architecture is designed to be extended:

1. **Adding New Components**:
   - Create a new class inheriting from Component
   - Add appropriate properties and initialization
   - Register with any systems that need to process it

2. **Adding New Systems**:
   - Create a new class inheriting from System
   - Define required components
   - Implement the process method
   - Register with the World

3. **Adding New Entity Types**:
   - No need to create new classes
   - Use factory functions to create entities with specific component combinations

## Conclusion

The Entity-Component-System architecture provides a flexible and efficient foundation for the VirtualLife simulation. By separating data (components) from behavior (systems), it enables complex entity interactions while maintaining clean, modular code. This architecture will scale well as we add more features and increase the complexity of the simulation. 