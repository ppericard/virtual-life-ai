"""Environment management for the VirtualLife simulation.

This package contains modules for managing the spatial environment of the simulation,
including boundary conditions, spatial grid, and resource management.
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
