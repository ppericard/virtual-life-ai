"""Tests for the boundary handlers."""

import pytest
from typing import Type, Tuple

from virtuallife.environment.boundary import (
    BoundaryHandler,
    BoundaryCondition,
    WrappedBoundary,
    BoundedBoundary,
    InfiniteBoundary,
    create_boundary_handler,
)
from virtuallife.types import Position


def test_wrapped_boundary_inside_grid():
    """Test that positions inside the grid remain unchanged with wrapped boundaries."""
    # Arrange
    boundary = WrappedBoundary(100, 100)
    position: Position = (50, 60)
    
    # Act
    result = boundary.normalize_position(position)
    
    # Assert
    assert result == position


def test_wrapped_boundary_outside_grid_positive():
    """Test that positions outside the grid (positive) are wrapped correctly."""
    # Arrange
    boundary = WrappedBoundary(100, 100)
    position: Position = (150, 160)
    
    # Act
    result = boundary.normalize_position(position)
    
    # Assert
    assert result == (50, 60)


def test_wrapped_boundary_outside_grid_negative():
    """Test that positions outside the grid (negative) are wrapped correctly."""
    # Arrange
    boundary = WrappedBoundary(100, 100)
    position: Position = (-50, -40)
    
    # Act
    result = boundary.normalize_position(position)
    
    # Assert
    assert result == (50, 60)


def test_bounded_boundary_inside_grid():
    """Test that positions inside the grid remain unchanged with bounded boundaries."""
    # Arrange
    boundary = BoundedBoundary(100, 100)
    position: Position = (50, 60)
    
    # Act
    result = boundary.normalize_position(position)
    
    # Assert
    assert result == position


def test_bounded_boundary_outside_grid_positive():
    """Test that positions outside the grid (positive) are clamped correctly."""
    # Arrange
    boundary = BoundedBoundary(100, 100)
    position: Position = (150, 160)
    
    # Act
    result = boundary.normalize_position(position)
    
    # Assert
    assert result == (99, 99)


def test_bounded_boundary_outside_grid_negative():
    """Test that positions outside the grid (negative) are clamped correctly."""
    # Arrange
    boundary = BoundedBoundary(100, 100)
    position: Position = (-50, -40)
    
    # Act
    result = boundary.normalize_position(position)
    
    # Assert
    assert result == (0, 0)


def test_infinite_boundary():
    """Test that positions are unchanged with infinite boundaries."""
    # Arrange
    boundary = InfiniteBoundary(100, 100)
    positions = [(50, 60), (150, 160), (-50, -40)]
    
    # Act & Assert
    for position in positions:
        assert boundary.normalize_position(position) == position


@pytest.mark.parametrize(
    "boundary_condition,position,expected",
    [
        (BoundaryCondition.WRAPPED, (150, 160), (50, 60)),
        (BoundaryCondition.BOUNDED, (150, 160), (99, 99)),
        (BoundaryCondition.INFINITE, (150, 160), (150, 160)),
        ("wrapped", (150, 160), (50, 60)),
        ("bounded", (150, 160), (99, 99)),
        ("infinite", (150, 160), (150, 160)),
    ],
)
def test_create_boundary_handler(
    boundary_condition, position: Position, expected: Position
):
    """Test that the correct boundary handler is created and works as expected."""
    # Arrange
    handler = create_boundary_handler(boundary_condition, 100, 100)
    
    # Act
    result = handler.normalize_position(position)
    
    # Assert
    assert result == expected


def test_create_boundary_handler_with_invalid_string():
    """Test that an invalid boundary condition string raises a ValueError."""
    # Act & Assert
    with pytest.raises(ValueError):
        create_boundary_handler("invalid", 100, 100)


def test_create_boundary_handler_with_invalid_enum():
    """Test that an invalid boundary condition enum raises a ValueError."""
    # Arrange
    class InvalidEnum:
        pass
    
    invalid_enum = InvalidEnum()
    
    # Act & Assert
    with pytest.raises(ValueError):
        create_boundary_handler(invalid_enum, 100, 100)  # type: ignore


@pytest.mark.parametrize(
    "width,height,position,expected",
    [
        (10, 10, (15, 15), (5, 5)),  # Wrapped boundary, position outside grid
        (10, 10, (5, 5), (5, 5)),    # Wrapped boundary, position inside grid
        (10, 10, (-5, -5), (5, 5)),  # Wrapped boundary, negative position
    ],
)
def test_wrapped_boundary_parametrized(
    width: int, height: int, position: Position, expected: Position
):
    """Test wrapped boundary with different grid sizes and positions."""
    # Arrange
    boundary = WrappedBoundary(width, height)
    
    # Act
    result = boundary.normalize_position(position)
    
    # Assert
    assert result == expected


@pytest.mark.parametrize(
    "width,height,position,expected",
    [
        (10, 10, (15, 15), (9, 9)),  # Bounded boundary, position outside grid
        (10, 10, (5, 5), (5, 5)),    # Bounded boundary, position inside grid
        (10, 10, (-5, -5), (0, 0)),  # Bounded boundary, negative position
    ],
)
def test_bounded_boundary_parametrized(
    width: int, height: int, position: Position, expected: Position
):
    """Test bounded boundary with different grid sizes and positions."""
    # Arrange
    boundary = BoundedBoundary(width, height)
    
    # Act
    result = boundary.normalize_position(position)
    
    # Assert
    assert result == expected 