"""Entity module for the ECS architecture.

This module defines the Entity class which is the core of the ECS architecture.
Entities are containers for components and have a unique ID and position.

Examples:
    >>> from virtuallife.ecs.entity import Entity
    >>> from virtuallife.types.core import Position
    >>> entity = Entity(position=(10, 20))
    >>> entity.position
    (10, 20)
"""

from dataclasses import dataclass, field
from typing import Dict, Type, Optional, TypeVar, cast, Any, Set, List, Generic, ClassVar, TYPE_CHECKING, get_type_hints
import uuid
from uuid import UUID

from virtuallife.types.core import Position, Identifiable, Positionable
from virtuallife.ecs.component import Component, get_component_type

C = TypeVar('C', bound=Component)


@dataclass
class Entity:
    """Base entity class using composition for behaviors.
    
    Entities are the primary objects in the simulation. They exist in the environment
    and can have various components that define their behavior. Each entity has a
    unique ID and position.
    
    Attributes:
        id: Unique identifier for the entity
        position: The (x, y) position of the entity in the environment
        components: Dictionary mapping component types to components
    """
    
    id: UUID = field(default_factory=uuid.uuid4)
    position: Position = field(default=(0, 0))
    _components: Dict[Type[Any], Any] = field(default_factory=dict)
    _dirty: bool = field(default=True, init=False)
    
    def add_component(self, component: C) -> None:
        """Add a component to the entity.
        
        Args:
            component: The component to add
            
        Raises:
            ValueError: If a component of the same type already exists
        """
        component_type = get_component_type(component)
        if component_type in self._components:
            raise ValueError(f"Component of type {component_type.__name__} already exists on this entity")
            
        self._components[component_type] = component
        self._dirty = True
    
    def remove_component(self, component_type: Type[C]) -> None:
        """Remove a component from the entity.
        
        Args:
            component_type: The type of component to remove
        """
        if component_type in self._components:
            del self._components[component_type]
            self._dirty = True
    
    def has_component(self, component_type: Type[Any]) -> bool:
        """Check if the entity has a specific component type.
        
        Args:
            component_type: The type of component to check for
            
        Returns:
            True if the entity has the component, False otherwise
        """
        return component_type in self._components
    
    def get_component(self, component_type: Type[C]) -> Optional[C]:
        """Get a component by type.
        
        Args:
            component_type: The type of component to get
            
        Returns:
            The component if it exists, None otherwise
        """
        component = self._components.get(component_type)
        if component is not None:
            return cast(C, component)
        return None
    
    def get_components(self) -> List[Any]:
        """Get all components on this entity.
        
        Returns:
            List of all components
        """
        return list(self._components.values())
    
    def update(self, world: Any, dt: float) -> None:
        """Update all components on this entity.
        
        Args:
            world: The world the entity exists in
            dt: Time delta since last update
        """
        for component in self._components.values():
            if isinstance(component, Component):
                component.update(self, world, dt)
    
    @property
    def is_dirty(self) -> bool:
        """Check if the entity has been modified since last check.
        
        Returns:
            True if the entity has been modified, False otherwise
        """
        return self._dirty
    
    def mark_clean(self) -> None:
        """Mark the entity as clean (not modified)."""
        self._dirty = False 