"""Core type definitions for the VirtualLife simulation.

This module defines common types used throughout the VirtualLife project.
These type definitions provide better type safety and documentation.

Examples:
    >>> from virtuallife.types.core import Position
    >>> position: Position = (10, 20)
    >>> x, y = position
    >>> x
    10
"""

from typing import Tuple, NewType, TypeVar, Protocol, Generic

# Type definitions
Position = Tuple[int, int]
"""A 2D position represented as a (x, y) tuple of integers."""

EntityId = NewType('EntityId', int)
"""A unique identifier for an entity."""

# Generic type variables
T = TypeVar('T')
"""Generic type variable for use in type annotations."""

C = TypeVar('C', bound='Component')
"""Type variable bound to Component types for use in type annotations."""

# Protocol definitions
class Identifiable(Protocol):
    """Protocol for objects that have a unique identifier."""
    
    @property
    def id(self) -> EntityId:
        """Get the unique identifier for this object.
        
        Returns:
            The unique identifier
        """
        ...

class Positionable(Protocol):
    """Protocol for objects that have a position in 2D space."""
    
    @property
    def position(self) -> Position:
        """Get the position of this object.
        
        Returns:
            The (x, y) position
        """
        ...
        
    @position.setter
    def position(self, value: Position) -> None:
        """Set the position of this object.
        
        Args:
            value: The new (x, y) position
        """
        ... 