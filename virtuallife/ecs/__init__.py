"""Entity-Component-System (ECS) architecture for the VirtualLife simulation.

This package implements a modern Entity-Component-System architecture that serves
as the foundation for the VirtualLife simulation. It provides a flexible, modular
approach to modeling entities and their behaviors.

The ECS pattern separates:
- Entities (unique identifiers with collections of components)
- Components (data containers that define properties and capabilities)
- Systems (logic that operates on entities with specific components)

This separation allows for better code organization, improved performance through
specialized processing, and greater flexibility through component composition.

Examples:
    >>> from virtuallife.ecs import World, Entity, System
    >>> 
    >>> # Create a world
    >>> world = World()
    >>> 
    >>> # Create an entity
    >>> entity = Entity()
    >>> 
    >>> # Define a simple component
    >>> class PositionComponent:
    ...     def __init__(self, x, y):
    ...         self.x = x
    ...         self.y = y
    ...     
    ...     def update(self, entity, world, dt):
    ...         pass
    >>> 
    >>> # Add component to entity
    >>> entity.add_component(PositionComponent(10, 20))
    >>> 
    >>> # Add entity to world
    >>> world.add_entity(entity)
"""

from virtuallife.ecs.entity import Entity
from virtuallife.ecs.component import Component
from virtuallife.ecs.system import System
from virtuallife.ecs.world import World

__all__ = [
    'Entity',
    'Component',
    'System',
    'World',
]
