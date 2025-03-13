"""Boundary condition handlers for the simulation environment.

This module provides classes for handling different types of boundary conditions
for the simulation environment, such as wrapped, bounded, and infinite boundaries.

Examples:
    >>> from virtuallife.environment.boundary import WrappedBoundary
    >>> from virtuallife.types import Position
    >>> 
    >>> # Create a wrapped boundary handler for a 100x100 grid
    >>> boundary = WrappedBoundary(100, 100)
    >>> 
    >>> # Normalize a position that's outside the grid
    >>> position: Position = (110, 120)
    >>> normalized = boundary.normalize_position(position)
    >>> normalized
    (10, 20)
"""

from abc import ABC, abstractmethod
from typing import Protocol, Literal, TypeVar, Type
from enum import Enum

from virtuallife.types import Position


class BoundaryCondition(str, Enum):
    """Enumeration of boundary condition types."""
    
    WRAPPED = "wrapped"
    """Positions wrap around to the other side of the grid."""
    
    BOUNDED = "bounded"
    """Positions are clamped to the grid boundaries."""
    
    INFINITE = "infinite"
    """Positions can be outside the grid."""


class BoundaryHandler(ABC):
    """Abstract base class for boundary condition handlers.
    
    Boundary handlers are responsible for normalizing positions based on
    different boundary conditions.
    """
    
    def __init__(self, width: int, height: int) -> None:
        """Initialize the boundary handler.
        
        Args:
            width: The width of the environment grid
            height: The height of the environment grid
        """
        self.width = width
        self.height = height
    
    @abstractmethod
    def normalize_position(self, position: Position) -> Position:
        """Normalize a position based on the boundary condition.
        
        Args:
            position: The position to normalize
            
        Returns:
            The normalized position
        """
        pass


class WrappedBoundary(BoundaryHandler):
    """Boundary handler for wrapped boundary conditions.
    
    With wrapped boundaries, positions wrap around to the other side of the grid.
    This creates a toroidal (donut-shaped) topology where the left edge connects
    to the right edge, and the top edge connects to the bottom edge.
    
    Examples:
        >>> boundary = WrappedBoundary(100, 100)
        >>> boundary.normalize_position((110, 120))
        (10, 20)
        >>> boundary.normalize_position((-10, -20))
        (90, 80)
    """
    
    def normalize_position(self, position: Position) -> Position:
        """Normalize a position by wrapping it around the grid.
        
        Args:
            position: The position to normalize
            
        Returns:
            The normalized position
        """
        x, y = position
        normalized_x = x % self.width
        normalized_y = y % self.height
        return (normalized_x, normalized_y)


class BoundedBoundary(BoundaryHandler):
    """Boundary handler for bounded boundary conditions.
    
    With bounded boundaries, positions are clamped to the grid boundaries.
    This creates a finite space with hard edges.
    
    Examples:
        >>> boundary = BoundedBoundary(100, 100)
        >>> boundary.normalize_position((110, 120))
        (99, 99)
        >>> boundary.normalize_position((-10, -20))
        (0, 0)
    """
    
    def normalize_position(self, position: Position) -> Position:
        """Normalize a position by clamping it to the grid boundaries.
        
        Args:
            position: The position to normalize
            
        Returns:
            The normalized position
        """
        x, y = position
        normalized_x = max(0, min(x, self.width - 1))
        normalized_y = max(0, min(y, self.height - 1))
        return (normalized_x, normalized_y)


class InfiniteBoundary(BoundaryHandler):
    """Boundary handler for infinite boundary conditions.
    
    With infinite boundaries, positions can be outside the grid.
    This creates an unbounded space.
    
    Examples:
        >>> boundary = InfiniteBoundary(100, 100)
        >>> boundary.normalize_position((110, 120))
        (110, 120)
        >>> boundary.normalize_position((-10, -20))
        (-10, -20)
    """
    
    def normalize_position(self, position: Position) -> Position:
        """Return the position unchanged (no normalization).
        
        Args:
            position: The position to normalize
            
        Returns:
            The original position
        """
        return position


def create_boundary_handler(
    boundary_condition: BoundaryCondition | str, width: int, height: int
) -> BoundaryHandler:
    """Create a boundary handler based on the specified condition.
    
    Args:
        boundary_condition: The boundary condition to use
        width: The width of the environment grid
        height: The height of the environment grid
        
    Returns:
        The appropriate boundary handler
        
    Raises:
        ValueError: If the boundary condition is not valid
    """
    if isinstance(boundary_condition, str):
        try:
            boundary_condition = BoundaryCondition(boundary_condition.lower())
        except ValueError:
            raise ValueError(
                f"Invalid boundary condition: {boundary_condition}. "
                f"Valid options are: {', '.join([bc.value for bc in BoundaryCondition])}"
            )
    
    if boundary_condition == BoundaryCondition.WRAPPED:
        return WrappedBoundary(width, height)
    elif boundary_condition == BoundaryCondition.BOUNDED:
        return BoundedBoundary(width, height)
    elif boundary_condition == BoundaryCondition.INFINITE:
        return InfiniteBoundary(width, height)
    else:
        raise ValueError(
            f"Invalid boundary condition: {boundary_condition}. "
            f"Valid options are: {', '.join([bc.value for bc in BoundaryCondition])}"
        ) 