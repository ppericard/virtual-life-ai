"""Entity-Component-System (ECS) architecture for VirtualLife.

This package provides the core classes for the ECS architecture used in the
VirtualLife simulation. The ECS architecture is a design pattern that emphasizes
composition over inheritance, separating data (components) from logic (systems).

Core Components:
- Entity: Container for components with a position and ID
- Component: Data containers that can be attached to entities
- System: Logic that processes entities with specific components
- World: Container for entities and systems, manages simulation updates

Examples:
    >>> from virtuallife.ecs import World, Entity, System
    >>> from dataclasses import dataclass
    >>> 
    >>> # Create a world to manage entities and systems
    >>> world = World()
    >>> 
    >>> # Create an entity
    >>> entity = Entity(position=(10, 20))
    >>> 
    >>> # Define a component
    >>> @dataclass
    >>> class PositionComponent:
    >>>     x: int = 0
    >>>     y: int = 0
    >>>     
    >>>     def update(self, entity, world, dt):
    >>>         pass
    >>> 
    >>> # Add the component to the entity
    >>> entity.add_component(PositionComponent(x=10, y=20))
    >>> 
    >>> # Add the entity to the world
    >>> world.add_entity(entity)
"""

from virtuallife.ecs.entity import Entity
from virtuallife.ecs.component import Component, register_component, get_component_class, get_component_type
from virtuallife.ecs.system import System
from virtuallife.ecs.world import World

__all__ = [
    'Entity',
    'Component',
    'System',
    'World',
    'register_component',
    'get_component_class',
    'get_component_type',
]
