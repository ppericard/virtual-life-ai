"""Environment management for the VirtualLife simulation.

This package contains modules for managing the spatial environment of the simulation,
including boundary conditions, spatial grid, and resource management.

The environment module provides:
- Spatial tracking of entities with efficient queries
- Different boundary condition options (wrapped, bounded, infinite)
- Resource management with creation, consumption, and distribution

Examples:
    >>> from virtuallife.environment import SpatialGrid, ResourceManager
    >>> from virtuallife.environment.boundary import BoundaryCondition, create_boundary_handler
    >>> 
    >>> # Create boundary handler and spatial grid
    >>> boundary = create_boundary_handler(BoundaryCondition.WRAPPED, (100, 100))
    >>> grid = SpatialGrid(100, 100, boundary)
    >>> 
    >>> # Add entity to grid
    >>> from uuid import uuid4
    >>> entity_id = uuid4()
    >>> grid.add_entity(entity_id, (10, 20))
    >>> 
    >>> # Find entities in area
    >>> nearby = grid.get_entities_in_radius((10, 20), radius=5)
    >>> 
    >>> # Create resource manager
    >>> resources = ResourceManager()
    >>> resources.add_resource("food", (10, 20), amount=100.0)
    >>> resources.consume_resource("food", (10, 20), amount=25.0)
"""

from virtuallife.environment.boundary import (
    BoundaryCondition,
    BoundaryHandler,
    WrappedBoundary,
    BoundedBoundary,
    InfiniteBoundary,
    create_boundary_handler,
)

from virtuallife.environment.grid import SpatialGrid
from virtuallife.environment.resources import ResourceManager

__all__ = [
    "BoundaryCondition",
    "BoundaryHandler",
    "WrappedBoundary",
    "BoundedBoundary",
    "InfiniteBoundary",
    "create_boundary_handler",
    "SpatialGrid",
    "ResourceManager",
]
