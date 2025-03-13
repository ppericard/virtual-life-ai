"""Tests for the core types module."""

from typing import Any
import pytest

from virtuallife.types.core import Position, EntityId, Identifiable, Positionable


def test_position_type():
    """Test that the Position type works as expected."""
    # Arrange
    pos: Position = (10, 20)
    
    # Act
    x, y = pos
    
    # Assert
    assert x == 10
    assert y == 20
    assert isinstance(pos, tuple)
    assert len(pos) == 2


def test_entity_id_type():
    """Test that the EntityId type works as expected."""
    # Arrange & Act
    entity_id = EntityId(123)
    
    # Assert
    assert entity_id == 123
    assert isinstance(entity_id, int)


class IdentifiableImpl:
    """Test implementation of the Identifiable protocol."""
    
    def __init__(self, id_val: int):
        """Initialize with the given id.
        
        Args:
            id_val: The identifier value
        """
        self._id = EntityId(id_val)
    
    @property
    def id(self) -> EntityId:
        """Get the unique identifier.
        
        Returns:
            The identifier
        """
        return self._id


def test_identifiable_protocol():
    """Test that the Identifiable protocol works as expected."""
    # Arrange
    obj = IdentifiableImpl(456)
    
    # Act
    result: Identifiable = obj  # Type checker should accept this
    
    # Assert
    assert result.id == EntityId(456)


class PositionableImpl:
    """Test implementation of the Positionable protocol."""
    
    def __init__(self, x: int, y: int):
        """Initialize with the given position.
        
        Args:
            x: The x coordinate
            y: The y coordinate
        """
        self._position: Position = (x, y)
    
    @property
    def position(self) -> Position:
        """Get the position.
        
        Returns:
            The position
        """
        return self._position
    
    @position.setter
    def position(self, value: Position) -> None:
        """Set the position.
        
        Args:
            value: The new position
        """
        self._position = value


def test_positionable_protocol():
    """Test that the Positionable protocol works as expected."""
    # Arrange
    obj = PositionableImpl(30, 40)
    
    # Act
    result: Positionable = obj  # Type checker should accept this
    new_position: Position = (50, 60)
    result.position = new_position
    
    # Assert
    assert result.position == (50, 60) 