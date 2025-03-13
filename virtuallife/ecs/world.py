"""World module for the ECS architecture.

This module defines the World class which is a container for entities and systems.
The World manages the relationships between entities and systems and provides
methods for updating the simulation state.

Examples:
    >>> from virtuallife.ecs.world import World
    >>> from virtuallife.ecs.entity import Entity
    >>> from virtuallife.ecs.system import System
    >>> 
    >>> # Create a world
    >>> world = World()
    >>> 
    >>> # Create an entity
    >>> entity = Entity(position=(10, 20))
    >>> 
    >>> # Add the entity to the world
    >>> world.add_entity(entity)
    >>> 
    >>> # Create a system
    >>> class MovementSystem(System):
    >>>     @property
    >>>     def required_components(self):
    >>>         return [MovementComponent]
    >>>         
    >>>     def process(self, world, dt):
    >>>         # Process entities
    >>>         pass
    >>> 
    >>> # Add the system to the world
    >>> world.add_system(MovementSystem())
    >>> 
    >>> # Update the world
    >>> world.update(0.016)  # 16ms time step
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Type, Optional, Any, TypeVar, cast, final, TYPE_CHECKING
from uuid import UUID
import uuid
import logging
from operator import attrgetter

if TYPE_CHECKING:
    from virtuallife.ecs.entity import Entity
    from virtuallife.ecs.system import System
    from virtuallife.ecs.component import Component

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class World:
    """Container for entities, systems, and their relationships.
    
    The World class manages entities and systems, and provides methods for
    updating the simulation state. It serves as the central hub for the ECS architecture.
    
    Attributes:
        entities: Dictionary mapping entity IDs to entities
        systems: List of systems that process entities
        _entities_pending_add: List of entities waiting to be added
        _entity_ids_pending_removal: Set of entity IDs waiting to be removed
    """
    
    entities: Dict[UUID, "Entity"] = field(default_factory=dict)
    systems: List["System"] = field(default_factory=list)
    _entities_pending_add: List["Entity"] = field(default_factory=list)
    _entity_ids_pending_removal: Set[UUID] = field(default_factory=set)
    _is_processing: bool = field(default=False)
    _next_entity_id: int = field(default=0)
    _spatial_grid: Optional[Any] = field(default=None)
    
    def add_entity(self, entity: "Entity") -> None:
        """Add an entity to the world.
        
        If the world is currently processing entities, the entity will be added
        after the current update cycle completes.
        
        Args:
            entity: The entity to add
        """
        if self._is_processing:
            self._entities_pending_add.append(entity)
            return
            
        self._add_entity_immediate(entity)
    
    def _add_entity_immediate(self, entity: "Entity") -> None:
        """Add an entity to the world immediately.
        
        Args:
            entity: The entity to add
        """
        self.entities[entity.id] = entity
        
        # Register with spatial grid if available
        if self._spatial_grid is not None:
            self._spatial_grid.add_entity(entity.id, entity.position)
            
        # Register with systems
        for system in self.systems:
            system.register_entity(entity)
            
        logger.debug(f"Added entity {entity.id} to world")
    
    def remove_entity(self, entity_id: UUID) -> None:
        """Remove an entity from the world.
        
        If the world is currently processing entities, the entity will be removed
        after the current update cycle completes.
        
        Args:
            entity_id: The ID of the entity to remove
        """
        if self._is_processing:
            self._entity_ids_pending_removal.add(entity_id)
            return
            
        self._remove_entity_immediate(entity_id)
    
    def _remove_entity_immediate(self, entity_id: UUID) -> None:
        """Remove an entity from the world immediately.
        
        Args:
            entity_id: The ID of the entity to remove
        """
        if entity_id not in self.entities:
            return
            
        entity = self.entities[entity_id]
        
        # Unregister from spatial grid if available
        if self._spatial_grid is not None:
            self._spatial_grid.remove_entity(entity_id)
            
        # Unregister from systems
        for system in self.systems:
            system.unregister_entity(entity_id)
            
        # Remove from entities
        del self.entities[entity_id]
        
        logger.debug(f"Removed entity {entity_id} from world")
    
    def get_entity(self, entity_id: UUID) -> Optional["Entity"]:
        """Get an entity by ID.
        
        Args:
            entity_id: The ID of the entity to get
            
        Returns:
            The entity if it exists, None otherwise
        """
        return self.entities.get(entity_id)
    
    def get_entities(self) -> List["Entity"]:
        """Get all entities in the world.
        
        Returns:
            List of all entities
        """
        return list(self.entities.values())
    
    def add_system(self, system: "System") -> None:
        """Add a system to the world.
        
        Systems are processed in order of priority (higher priority first).
        
        Args:
            system: The system to add
        """
        self.systems.append(system)
        
        # Sort systems by priority (higher priority first)
        self.systems.sort(key=attrgetter('priority'), reverse=True)
        
        # Register existing entities with the system
        for entity in self.entities.values():
            system.register_entity(entity)
            
        logger.debug(f"Added system {type(system).__name__} to world")
    
    def remove_system(self, system_type: Type["System"]) -> None:
        """Remove a system from the world.
        
        Args:
            system_type: The type of system to remove
        """
        self.systems = [s for s in self.systems if not isinstance(s, system_type)]
        logger.debug(f"Removed system {system_type.__name__} from world")
    
    def update(self, dt: float) -> None:
        """Update the world state.
        
        This method processes all systems and updates the world state. After processing,
        any pending entity additions or removals are applied.
        
        Args:
            dt: Time delta since last update in seconds
        """
        self._is_processing = True
        
        # Process all systems
        for system in self.systems:
            if system.is_enabled:
                system.process(self, dt)
                
        self._is_processing = False
        
        # Handle pending entity additions and removals
        self._process_pending_entity_changes()
    
    def _process_pending_entity_changes(self) -> None:
        """Process any pending entity additions or removals."""
        # Add pending entities
        for entity in self._entities_pending_add:
            self._add_entity_immediate(entity)
            
        self._entities_pending_add.clear()
        
        # Remove pending entities
        for entity_id in self._entity_ids_pending_removal:
            self._remove_entity_immediate(entity_id)
            
        self._entity_ids_pending_removal.clear()
    
    def set_spatial_grid(self, grid: Any) -> None:
        """Set the spatial grid for this world.
        
        The spatial grid is used for efficient entity lookups based on position.
        
        Args:
            grid: The spatial grid to use
        """
        self._spatial_grid = grid
        
        # Register existing entities with the grid
        for entity in self.entities.values():
            grid.add_entity(entity.id, entity.position)
            
        logger.debug("Set spatial grid for world")
    
    def clear(self) -> None:
        """Clear all entities from the world."""
        # Clear spatial grid if available
        if self._spatial_grid is not None:
            self._spatial_grid.clear()
            
        # Clear entities
        self.entities.clear()
        self._entities_pending_add.clear()
        self._entity_ids_pending_removal.clear()
        
        logger.debug("Cleared all entities from world")
    
    def __len__(self) -> int:
        """Get the number of entities in the world.
        
        Returns:
            The number of entities
        """
        return len(self.entities)
    
    @property
    def entity_count(self) -> int:
        """Get the number of entities in the world.
        
        Returns:
            The number of entities
        """
        return len(self.entities)
    
    @property
    def system_count(self) -> int:
        """Get the number of systems in the world.
        
        Returns:
            The number of systems
        """
        return len(self.systems) 