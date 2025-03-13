"""Type definitions for the VirtualLife simulation.

This package provides common type definitions used throughout the VirtualLife project.
These types enhance type safety and make the code more readable.

Examples:
    >>> from virtuallife.types import Position
    >>> position: Position = (10, 20)
    >>> x, y = position
"""

from virtuallife.types.core import (
    Position,
    EntityId,
    Identifiable,
    Positionable,
    T,
    C,
)

__all__ = [
    'Position',
    'EntityId',
    'Identifiable',
    'Positionable',
    'T',
    'C',
]
