"""System module for the ECS architecture.

This module defines the System abstract base class which is the basis for all
systems in the ECS architecture. Systems process entities that have specific components.

Examples:
    >>> from typing import List, Type
    >>> from virtuallife.ecs.system import System
    >>> from virtuallife.ecs.component import Component
    >>> from dataclasses import dataclass
    >>> 
    >>> @dataclass
    >>> class HealthComponent:
    >>>     health: int = 100
    >>>     
    >>>     def update(self, entity, world, dt):
    >>>         pass
    >>> 
    >>> class HealthSystem(System):
    >>>     @property
    >>>     def required_components(self) -> List[Type[Component]]:
    >>>         return [HealthComponent]
    >>>         
    >>>     def process(self, world, dt):
    >>>         for entity_id in self.entities:
    >>>             entity = world.get_entity(entity_id)
    >>>             if entity:
    >>>                 health_comp = entity.get_component(HealthComponent)
    >>>                 # Process health component
    >>>                 if health_comp and health_comp.health <= 0:
    >>>                     world.remove_entity(entity.id)
"""

from abc import ABC, abstractmethod
from typing import Set, Type, List, Dict, Any, Optional, TypeVar, cast, final, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from virtuallife.ecs.entity import Entity
    from virtuallife.ecs.world import World
    from virtuallife.ecs.component import Component

# Define a type variable for generic system types
S = TypeVar('S', bound='System')


class System(ABC):
    """Base class for systems that process entities with specific components.
    
    Systems are responsible for updating entities that have specific components.
    They provide a way to organize game logic by functionality rather than by entity.
    
    Systems register themselves with entities that have all of their required components,
    and then process those entities during the update cycle.
    """
    
    def __init__(self) -> None:
        """Initialize the system with an empty set of entities."""
        self.entities: Set[UUID] = set()
        self.enabled: bool = True
        self.priority: int = 0
    
    @property
    @abstractmethod
    def required_components(self) -> List[Type["Component"]]:
        """Get the component types required for an entity to be processed by this system.
        
        Returns:
            A list of component types that an entity must have to be processed
        """
        pass
    
    def matches_entity(self, entity: "Entity") -> bool:
        """Check if the entity should be processed by this system.
        
        An entity matches if it has all the required components for this system.
        
        Args:
            entity: The entity to check
            
        Returns:
            True if the entity has all required components, False otherwise
        """
        if not self.enabled:
            return False
            
        return all(entity.has_component(component_type) for component_type in self.required_components)
    
    def register_entity(self, entity: "Entity") -> None:
        """Register an entity with this system.
        
        This method is called when an entity is added to the world or when
        it gains all the required components for this system.
        
        Args:
            entity: The entity to register
        """
        if self.matches_entity(entity):
            self.entities.add(entity.id)
            self._on_entity_added(entity)
    
    def unregister_entity(self, entity_id: UUID) -> None:
        """Unregister an entity from this system.
        
        This method is called when an entity is removed from the world or when
        it loses one of the required components for this system.
        
        Args:
            entity_id: The ID of the entity to unregister
        """
        if entity_id in self.entities:
            self.entities.remove(entity_id)
            self._on_entity_removed(entity_id)
    
    def _on_entity_added(self, entity: "Entity") -> None:
        """Called when an entity is added to this system.
        
        This method can be overridden by subclasses to perform custom logic
        when an entity is added.
        
        Args:
            entity: The entity that was added
        """
        pass
    
    def _on_entity_removed(self, entity_id: UUID) -> None:
        """Called when an entity is removed from this system.
        
        This method can be overridden by subclasses to perform custom logic
        when an entity is removed.
        
        Args:
            entity_id: The ID of the entity that was removed
        """
        pass
    
    @abstractmethod
    def process(self, world: "World", dt: float) -> None:
        """Process all registered entities.
        
        This method is called during the world update cycle and should update
        all entities registered with this system.
        
        Args:
            world: The world containing the entities
            dt: Time delta since last update in seconds
        """
        pass
    
    def enable(self) -> None:
        """Enable this system.
        
        When a system is enabled, it will process entities during the world update cycle.
        """
        self.enabled = True
    
    def disable(self) -> None:
        """Disable this system.
        
        When a system is disabled, it will not process entities during the world update cycle.
        """
        self.enabled = False
    
    @property
    def is_enabled(self) -> bool:
        """Check if this system is enabled.
        
        Returns:
            True if the system is enabled, False otherwise
        """
        return self.enabled
    
    def set_priority(self, priority: int) -> None:
        """Set the priority of this system.
        
        Systems with higher priority are processed first.
        
        Args:
            priority: The priority value (higher is processed first)
        """
        self.priority = priority
    
    @property
    def get_priority(self) -> int:
        """Get the priority of this system.
        
        Returns:
            The priority value
        """
        return self.priority 