"""Environment module for the VirtualLife simulation.

This module provides the Environment class, which represents the 2D grid world
where entities exist and interact. It manages entity positions, resources,
and defines the boundaries of the simulation space.
"""

from dataclasses import dataclass, field
from typing import Dict, Set, Tuple, List, Optional
from uuid import UUID


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
        resources: Dictionary mapping resource types to resource values at positions
    """
    width: int
    height: int
    boundary_condition: str = "wrapped"
    entities: Dict[UUID, "Entity"] = field(default_factory=dict)
    entity_positions: Dict[Tuple[int, int], Set[UUID]] = field(
        default_factory=lambda: {}
    )
    resources: Dict[str, Dict[Tuple[int, int], float]] = field(
        default_factory=lambda: {}
    )

    def add_entity(self, entity: "Entity") -> None:
        """Add an entity to the environment.
        
        Args:
            entity: The entity to add
            
        Raises:
            ValueError: If the entity is already in the environment
        """
        if entity.id in self.entities:
            raise ValueError(f"Entity {entity.id} already exists in environment")
        
        self.entities[entity.id] = entity
        pos = entity.position
        if pos not in self.entity_positions:
            self.entity_positions[pos] = set()
        self.entity_positions[pos].add(entity.id)
    
    def remove_entity(self, entity_id: UUID) -> None:
        """Remove an entity from the environment.
        
        Args:
            entity_id: The ID of the entity to remove
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
        """
        if position in self.entity_positions:
            return [self.entities[entity_id] for entity_id in self.entity_positions[position]]
        return []
    
    def get_neighborhood(
        self, position: Tuple[int, int], radius: int = 1
    ) -> Dict[Tuple[int, int], List["Entity"]]:
        """Get a view of the environment around a position.
        
        Args:
            position: The center (x, y) position
            radius: The radius of the neighborhood (default: 1)
            
        Returns:
            A dictionary mapping positions to lists of entities
        """
        x, y = position
        neighborhood = {}
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                pos = self.normalize_position((x + dx, y + dy))
                entities = self.get_entities_at(pos)
                if entities:
                    neighborhood[pos] = entities
        
        return neighborhood
    
    def normalize_position(self, position: Tuple[int, int]) -> Tuple[int, int]:
        """Normalize a position based on boundary conditions.
        
        Args:
            position: The (x, y) position to normalize
            
        Returns:
            The normalized (x, y) position
        """
        x, y = position
        
        match self.boundary_condition:
            case "wrapped":
                return (x % self.width, y % self.height)
            case "bounded":
                return (
                    max(0, min(x, self.width - 1)),
                    max(0, min(y, self.height - 1))
                )
            case "infinite":
                return position
            case _:
                return (x % self.width, y % self.height)  # Default to wrapped
    
    def add_resource(
        self, resource_type: str, position: Tuple[int, int], value: float
    ) -> None:
        """Add or update a resource at a specific position.
        
        Args:
            resource_type: The type of resource
            position: The (x, y) position
            value: The resource value
        """
        if resource_type not in self.resources:
            self.resources[resource_type] = {}
        self.resources[resource_type][position] = value
    
    def get_resource(
        self, resource_type: str, position: Tuple[int, int]
    ) -> float:
        """Get the resource value at a specific position.
        
        Args:
            resource_type: The type of resource
            position: The (x, y) position
            
        Returns:
            The resource value (0.0 if no resource exists)
        """
        return self.resources.get(resource_type, {}).get(position, 0.0)
    
    def remove_resource(
        self, resource_type: str, position: Tuple[int, int]
    ) -> None:
        """Remove a resource from a specific position.
        
        Args:
            resource_type: The type of resource
            position: The (x, y) position
        """
        if resource_type in self.resources and position in self.resources[resource_type]:
            del self.resources[resource_type][position]
            if not self.resources[resource_type]:
                del self.resources[resource_type] 