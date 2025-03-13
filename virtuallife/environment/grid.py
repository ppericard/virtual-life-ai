"""Spatial grid for efficient entity position tracking and spatial queries.

This module provides the SpatialGrid class, which is responsible for managing
entity positions and providing efficient spatial queries. It uses a spatial
partitioning approach to improve performance.

Examples:
    >>> from virtuallife.environment.grid import SpatialGrid
    >>> from virtuallife.environment.boundary import WrappedBoundary
    >>> from uuid import uuid4
    >>> from virtuallife.types import Position
    >>> 
    >>> # Create a spatial grid with wrapped boundary
    >>> grid = SpatialGrid(100, 100, WrappedBoundary(100, 100))
    >>> 
    >>> # Add some entities
    >>> entity_id = uuid4()
    >>> grid.add_entity(entity_id, (10, 20))
    >>> 
    >>> # Get entities in radius
    >>> nearby_entities = grid.get_entities_in_radius((11, 21), 2)
    >>> entity_id in nearby_entities
    True
"""

from dataclasses import dataclass, field
from typing import Dict, Set, Tuple, List, Optional, Any, Iterator
from uuid import UUID
from collections import defaultdict
import math

from virtuallife.types import Position
from virtuallife.environment.boundary import BoundaryHandler


@dataclass
class SpatialGrid:
    """A spatial grid for efficient entity lookups.
    
    The SpatialGrid class uses spatial partitioning to efficiently track entity
    positions and perform spatial queries. It divides the environment into cells
    and stores entities in those cells based on their position.
    
    Attributes:
        width: Width of the grid
        height: Height of the grid
        boundary_handler: Handler for boundary conditions
        cell_size: Size of each grid cell for spatial partitioning
        cells: Dictionary mapping cell coordinates to sets of entity IDs
        entity_positions: Dictionary mapping entity IDs to positions
    """
    
    width: int
    height: int
    boundary_handler: BoundaryHandler
    cell_size: int = 10
    _cells: Dict[Tuple[int, int], Set[UUID]] = field(default_factory=lambda: defaultdict(set))
    _entity_positions: Dict[UUID, Position] = field(default_factory=dict)
    
    def position_to_cell(self, position: Position) -> Tuple[int, int]:
        """Convert a position to a cell coordinate.
        
        Args:
            position: The position to convert
            
        Returns:
            The cell coordinate
        """
        x, y = position
        return (x // self.cell_size, y // self.cell_size)
    
    def add_entity(self, entity_id: UUID, position: Position) -> None:
        """Add an entity to the grid.
        
        Args:
            entity_id: The ID of the entity to add
            position: The position of the entity
        """
        # Normalize position based on boundary conditions
        position = self.boundary_handler.normalize_position(position)
        
        # Add to entity positions
        self._entity_positions[entity_id] = position
        
        # Add to cell
        cell = self.position_to_cell(position)
        self._cells[cell].add(entity_id)
    
    def remove_entity(self, entity_id: UUID, position: Optional[Position] = None) -> None:
        """Remove an entity from the grid.
        
        Args:
            entity_id: The ID of the entity to remove
            position: The position of the entity (optional, will be looked up if not provided)
        """
        if entity_id not in self._entity_positions:
            return
        
        # Get position if not provided
        if position is None:
            position = self._entity_positions[entity_id]
        
        # Remove from cell
        cell = self.position_to_cell(position)
        if cell in self._cells and entity_id in self._cells[cell]:
            self._cells[cell].remove(entity_id)
            if not self._cells[cell]:
                del self._cells[cell]
        
        # Remove from entity positions
        del self._entity_positions[entity_id]
    
    def update_entity_position(self, entity_id: UUID, new_position: Position) -> None:
        """Update an entity's position.
        
        Args:
            entity_id: The ID of the entity to update
            new_position: The new position
        """
        if entity_id not in self._entity_positions:
            self.add_entity(entity_id, new_position)
            return
        
        old_position = self._entity_positions[entity_id]
        normalized_new_position = self.boundary_handler.normalize_position(new_position)
        
        # If position hasn't changed, do nothing
        if old_position == normalized_new_position:
            return
        
        # Remove from old cell
        old_cell = self.position_to_cell(old_position)
        if old_cell in self._cells and entity_id in self._cells[old_cell]:
            self._cells[old_cell].remove(entity_id)
            if not self._cells[old_cell]:
                del self._cells[old_cell]
        
        # Add to new cell
        new_cell = self.position_to_cell(normalized_new_position)
        self._cells[new_cell].add(entity_id)
        
        # Update entity position
        self._entity_positions[entity_id] = normalized_new_position
    
    def get_entity_position(self, entity_id: UUID) -> Optional[Position]:
        """Get the position of an entity.
        
        Args:
            entity_id: The ID of the entity
            
        Returns:
            The position of the entity, or None if the entity is not in the grid
        """
        return self._entity_positions.get(entity_id)
    
    def get_entities_at_position(self, position: Position) -> Set[UUID]:
        """Get all entities at a specific position.
        
        Args:
            position: The position to check
            
        Returns:
            A set of entity IDs at the position
        """
        normalized_position = self.boundary_handler.normalize_position(position)
        cell = self.position_to_cell(normalized_position)
        
        result = set()
        if cell in self._cells:
            for entity_id in self._cells[cell]:
                if self._entity_positions[entity_id] == normalized_position:
                    result.add(entity_id)
        
        return result
    
    def get_entities_in_cell(self, cell: Tuple[int, int]) -> Set[UUID]:
        """Get all entities in a specific cell.
        
        Args:
            cell: The cell coordinates
            
        Returns:
            A set of entity IDs in the cell
        """
        return self._cells.get(cell, set())
    
    def get_entities_in_radius(self, position: Position, radius: int) -> Set[UUID]:
        """Get all entities within a radius of the position.
        
        Args:
            position: The center position
            radius: The radius to search
            
        Returns:
            A set of entity IDs within the radius
        """
        normalized_position = self.boundary_handler.normalize_position(position)
        center_cell = self.position_to_cell(normalized_position)
        
        # Calculate the number of cells to check in each direction
        # Add 1 to ensure we check all cells that might contain entities within the radius
        cell_radius = math.ceil(radius / self.cell_size) + 1
        
        result = set()
        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                if cell in self._cells:
                    for entity_id in self._cells[cell]:
                        entity_pos = self._entity_positions[entity_id]
                        distance = self._calculate_distance(normalized_position, entity_pos)
                        if distance <= radius:
                            result.add(entity_id)
        
        return result
    
    def get_entities_in_rectangle(
        self, top_left: Position, bottom_right: Position
    ) -> Set[UUID]:
        """Get all entities within a rectangular area.
        
        Args:
            top_left: The top-left corner of the rectangle
            bottom_right: The bottom-right corner of the rectangle
            
        Returns:
            A set of entity IDs within the rectangle
        """
        normalized_top_left = self.boundary_handler.normalize_position(top_left)
        normalized_bottom_right = self.boundary_handler.normalize_position(bottom_right)
        
        min_x = min(normalized_top_left[0], normalized_bottom_right[0])
        max_x = max(normalized_top_left[0], normalized_bottom_right[0])
        min_y = min(normalized_top_left[1], normalized_bottom_right[1])
        max_y = max(normalized_top_left[1], normalized_bottom_right[1])
        
        min_cell_x = min_x // self.cell_size
        max_cell_x = max_x // self.cell_size
        min_cell_y = min_y // self.cell_size
        max_cell_y = max_y // self.cell_size
        
        result = set()
        for cell_x in range(min_cell_x, max_cell_x + 1):
            for cell_y in range(min_cell_y, max_cell_y + 1):
                cell = (cell_x, cell_y)
                if cell in self._cells:
                    for entity_id in self._cells[cell]:
                        entity_pos = self._entity_positions[entity_id]
                        if (
                            min_x <= entity_pos[0] <= max_x
                            and min_y <= entity_pos[1] <= max_y
                        ):
                            result.add(entity_id)
        
        return result
    
    def get_nearest_entities(
        self, position: Position, count: int = 1
    ) -> List[Tuple[UUID, float]]:
        """Get the nearest entities to a position.
        
        Args:
            position: The reference position
            count: The maximum number of entities to return
            
        Returns:
            A list of (entity_id, distance) tuples, sorted by distance
        """
        normalized_position = self.boundary_handler.normalize_position(position)
        
        # Start with a small radius and expand until we find enough entities
        radius = self.cell_size
        entities = self.get_entities_in_radius(normalized_position, radius)
        
        while len(entities) < count and radius < max(self.width, self.height):
            radius *= 2
            entities = self.get_entities_in_radius(normalized_position, radius)
        
        # Calculate distances and sort
        distances = []
        for entity_id in entities:
            entity_pos = self._entity_positions[entity_id]
            distance = self._calculate_distance(normalized_position, entity_pos)
            distances.append((entity_id, distance))
        
        # Sort by distance and return the closest 'count' entities
        distances.sort(key=lambda x: x[1])
        return distances[:count]
    
    def get_all_entities(self) -> Set[UUID]:
        """Get all entities in the grid.
        
        Returns:
            A set of all entity IDs in the grid
        """
        return set(self._entity_positions.keys())
    
    def get_all_positions(self) -> Dict[UUID, Position]:
        """Get all entity positions.
        
        Returns:
            A dictionary mapping entity IDs to positions
        """
        return self._entity_positions.copy()
    
    def clear(self) -> None:
        """Clear all entities from the grid."""
        self._cells.clear()
        self._entity_positions.clear()
    
    def _calculate_distance(self, pos1: Position, pos2: Position) -> float:
        """Calculate the Euclidean distance between two positions.
        
        Args:
            pos1: The first position
            pos2: The second position
            
        Returns:
            The distance between the positions
        """
        x1, y1 = pos1
        x2, y2 = pos2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def __iter__(self) -> Iterator[UUID]:
        """Iterate over all entity IDs in the grid.
        
        Returns:
            An iterator of entity IDs
        """
        return iter(self._entity_positions)
    
    def __len__(self) -> int:
        """Get the number of entities in the grid.
        
        Returns:
            The number of entities
        """
        return len(self._entity_positions)
    
    def __contains__(self, entity_id: UUID) -> bool:
        """Check if an entity is in the grid.
        
        Args:
            entity_id: The ID of the entity
            
        Returns:
            True if the entity is in the grid, False otherwise
        """
        return entity_id in self._entity_positions 